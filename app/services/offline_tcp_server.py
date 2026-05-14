"""Offline TCP server — receives finalized transcripts from the bridge,
runs the agent pipeline, writes incidents to the database, and stores
the absolute recording path alongside the incident record.
"""
from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.incident import Incident
from app.models.incident_type import IncidentType
from app.services.transcript_store import transcript_store

logger = logging.getLogger("offline_tcp")

HOST = "0.0.0.0"
PORT = 5002

# ---------------------------------------------------------------------------
# In-memory incident result store (one entry — the most recent call)
# ---------------------------------------------------------------------------

_incident_store: dict[str, Any] = {}
_incident_store_lock = asyncio.Lock()


async def get_latest_incident_result() -> dict[str, Any]:
    async with _incident_store_lock:
        return dict(_incident_store)


async def set_latest_incident_result(data: dict[str, Any]) -> None:
    async with _incident_store_lock:
        _incident_store.clear()
        _incident_store.update(data)


async def clear_incident_result() -> None:
    async with _incident_store_lock:
        _incident_store.clear()


# ---------------------------------------------------------------------------
# Incident type code → DB name mapping
# ---------------------------------------------------------------------------

INCIDENT_TYPE_CODE_TO_NAME: dict[str, str] = {
    "FIRE_STRUCTURE": "House Fire",
    "FIRE_FIELD": "Field Fire",
    "FIRE_FOREST": "Forest Fire",
    "FIRE_URBAN": "Urban Fire",
    "EMS_TRANSPORT": "Patient Transportation",
    "HOSPITAL_TRANSPORT": "Hospital Transportation",
    "VEHICLE_TRANSPORT": "Vehicle Transportation",
}


# ---------------------------------------------------------------------------
# Agent service calls
# ---------------------------------------------------------------------------


async def _clean_transcript(client: httpx.AsyncClient, raw: str) -> str:
    resp = await client.post(
        f"{settings.agents_service_url}/dispatch/clean-transcript",
        json={"raw_transcript": raw},
        timeout=60.0,
    )
    resp.raise_for_status()
    return resp.json()["cleaned_transcript"]


async def _localize(client: httpx.AsyncClient, transcript: str) -> dict[str, Any]:
    resp = await client.post(
        f"{settings.agents_service_url}/dispatch/localize",
        json={"transcript": transcript},
        timeout=60.0,
    )
    resp.raise_for_status()
    return resp.json()


async def _generate_record(client: httpx.AsyncClient, transcript: str) -> dict[str, Any]:
    resp = await client.post(
        f"{settings.agents_service_url}/dispatch/generate-record",
        json={"transcript": transcript},
        timeout=60.0,
    )
    resp.raise_for_status()
    return resp.json()


# ---------------------------------------------------------------------------
# Database write
# ---------------------------------------------------------------------------


def _resolve_incident_type_id(db: Session, code: str) -> int:
    name = INCIDENT_TYPE_CODE_TO_NAME.get(code)
    if name:
        row = db.execute(
            select(IncidentType).where(IncidentType.name == name)
        ).scalar_one_or_none()
        if row:
            return row.id
    # Fallback — use whatever type is available rather than failing.
    fallback = db.execute(select(IncidentType)).scalar_one_or_none()
    return fallback.id if fallback else 1


def _write_incident(
    record: dict[str, Any],
    localization: dict[str, Any],
    cleaned_transcript: str,
    recording_path: str | None,
) -> Incident:
    db: Session = SessionLocal()
    try:
        incident_data = record["incident"]
        call_data = record["call"]

        incident_type_id = _resolve_incident_type_id(
            db, incident_data.get("incident_type_code", "")
        )

        incident = Incident(
            incident_type_id=incident_type_id,
            status="reported",
            priority=incident_data.get("priority"),
            address=(
                localization.get("location_normalized")
                or incident_data.get("location_address")
            ),
            latitude=localization.get("latitude"),
            longitude=localization.get("longitude"),
            caller_name=call_data.get("caller_name"),
            caller_phone=call_data.get("caller_phone"),
            description=incident_data.get("description"),
            whisper_transcript=cleaned_transcript,
            recording_path=recording_path,
            reported_at=datetime.now(timezone.utc),
        )

        db.add(incident)
        db.commit()
        db.refresh(incident)
        logger.info(f"Incident #{incident.id} written to DB (recording: {recording_path})")
        return incident

    finally:
        db.close()


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------


async def process_offline_transcript(event: dict[str, Any]) -> None:
    raw_text = event.get("text", "").strip()
    call_id = event.get("call_id")
    audio_path = event.get("audio_path")  # absolute path sent by bridge

    if not raw_text:
        return

    logger.info(f"[OFFLINE] Processing call {call_id} — {len(raw_text)} chars")
    await set_latest_incident_result({"status": "processing", "call_id": call_id})

    try:
        async with httpx.AsyncClient() as client:
            logger.info("[OFFLINE] Cleaning transcript")
            cleaned = await _clean_transcript(client, raw_text)

            logger.info("[OFFLINE] Localizing + generating record (parallel)")
            localization, record = await asyncio.gather(
                _localize(client, cleaned),
                _generate_record(client, cleaned),
            )

        # Resolve absolute recording path.
        recording_path: str | None = None
        if audio_path:
            resolved = Path(audio_path).resolve()
            recording_path = str(resolved) if resolved.exists() else audio_path

        logger.info("[OFFLINE] Writing to DB")
        incident = await asyncio.to_thread(
            _write_incident, record, localization, cleaned, recording_path
        )

        # Clear live transcript store — the call is archived.
        await transcript_store.clear()

        result: dict[str, Any] = {
            "status": "ready",
            "call_id": call_id,
            "incident_id": incident.id,
            "cleaned_transcript": cleaned,
            "localization": localization,
            "record": record,
            "recording_path": recording_path,
            "incident": {
                "id": incident.id,
                "incident_type_id": incident.incident_type_id,
                "status": incident.status,
                "priority": incident.priority,
                "address": incident.address,
                "latitude": float(incident.latitude) if incident.latitude else None,
                "longitude": float(incident.longitude) if incident.longitude else None,
                "caller_name": incident.caller_name,
                "caller_phone": incident.caller_phone,
                "description": incident.description,
                "whisper_transcript": incident.whisper_transcript,
                "recording_path": incident.recording_path,
                "reported_at": incident.reported_at.isoformat(),
            },
        }
        await set_latest_incident_result(result)
        logger.info(f"[OFFLINE] Complete — incident #{incident.id}")

    except httpx.HTTPError as exc:
        logger.error(f"[OFFLINE] Agent HTTP error: {exc}")
        await set_latest_incident_result(
            {"status": "error", "call_id": call_id, "detail": str(exc)}
        )
    except Exception as exc:
        logger.error(f"[OFFLINE] Pipeline error: {exc}", exc_info=True)
        await set_latest_incident_result(
            {"status": "error", "call_id": call_id, "detail": str(exc)}
        )


# ---------------------------------------------------------------------------
# TCP server
# ---------------------------------------------------------------------------


async def handle_offline_client(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
) -> None:
    addr = writer.get_extra_info("peername")
    logger.info(f"[OFFLINE TCP] Bridge connected from {addr}")

    try:
        while True:
            line = await reader.readline()
            if not line:
                break

            raw = line.decode("utf-8").strip()
            if not raw:
                continue

            try:
                event = json.loads(raw)
            except json.JSONDecodeError as exc:
                logger.warning(f"[OFFLINE TCP] Invalid JSON: {exc}")
                continue

            if event.get("type") != "offline_transcript":
                continue

            asyncio.create_task(process_offline_transcript(event))

    finally:
        logger.info(f"[OFFLINE TCP] Bridge disconnected from {addr}")
        writer.close()
        await writer.wait_closed()


async def start_offline_tcp_server() -> None:
    logger.info(f"[OFFLINE TCP] Starting on {HOST}:{PORT}")
    server = await asyncio.start_server(handle_offline_client, HOST, PORT)
    logger.info(f"[OFFLINE TCP] Listening on {HOST}:{PORT}")
    async with server:
        await server.serve_forever()
