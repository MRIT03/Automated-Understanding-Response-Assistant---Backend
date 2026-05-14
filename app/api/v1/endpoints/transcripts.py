"""Transcripts endpoints.

Routes:
  GET    /live              — current live transcript chunks
  DELETE /live              — clear live transcript store
  GET    /live/incident     — poll post-call pipeline result
  POST   /live/end          — manually trigger call-end (from frontend button)
  GET    /audio/{filename}  — stream a recording WAV file to the frontend
"""
from __future__ import annotations

import os
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.services.offline_tcp_server import (
    clear_incident_result,
    get_latest_incident_result,
    set_latest_incident_result,
)
from app.services.transcript_store import transcript_store

router = APIRouter()

# The recordings directory as seen INSIDE the container.
# Mount the host SimulStreaming/audio/ folder here in docker-compose.
RECORDINGS_DIR = Path(os.getenv("RECORDINGS_DIR", "/recordings"))


# ---------------------------------------------------------------------------
# Live transcript
# ---------------------------------------------------------------------------


@router.get("/live")
async def get_live_transcript():
    items = await transcript_store.get_all()
    latest = items[-1] if items else None
    return {
        "count": len(items),
        "latest": latest,
        "text": " ".join(item["text"] for item in items if item.get("text")),
        "items": items,
    }


@router.delete("/live")
async def clear_live_transcript():
    await transcript_store.clear()
    await clear_incident_result()
    return {"ok": True}


# ---------------------------------------------------------------------------
# Post-call incident result (polled by frontend)
# ---------------------------------------------------------------------------


@router.get("/live/incident")
async def get_incident_result():
    return await get_latest_incident_result()


# ---------------------------------------------------------------------------
# Manual call-end trigger (called by frontend "End Call" button)
# ---------------------------------------------------------------------------


@router.post("/live/end")
async def manual_end_call():
    """Signal the backend that the dispatcher has ended the current call.

    The bridge's HTTP control server (port 5003) is the preferred path for
    actually stopping the bridge-side recording. This endpoint handles the
    backend side: it marks the pipeline as triggered so the frontend can
    show "processing" immediately, even if the bridge takes a moment to
    send the offline transcript.

    The frontend should ALSO POST to http://localhost:5003/end-call on the
    bridge machine to trigger the WAV finalization and offline Whisper run.
    """
    current = await get_latest_incident_result()

    # Only act if there is no pipeline already running.
    if current.get("status") in ("processing", "ready"):
        return {"ok": True, "note": "pipeline already active"}

    # Get the current call_id from the live transcript store (it is embedded
    # in transcript items by the TCP server).
    items = await transcript_store.get_all()
    call_id = None
    for item in reversed(items):
        call_id = item.get("call_id")
        if call_id:
            break

    if call_id:
        await set_latest_incident_result(
            {"status": "processing", "call_id": call_id}
        )

    return {"ok": True, "call_id": call_id}


# ---------------------------------------------------------------------------
# Audio playback
# ---------------------------------------------------------------------------


@router.get("/audio/{filename}")
async def stream_recording(filename: str):
    """Serve a call recording WAV file to the Streamlit frontend.

    Security: only files inside RECORDINGS_DIR are served; path traversal
    is blocked by checking that the resolved path starts with the recordings
    directory.
    """
    # Block path traversal.
    safe_name = Path(filename).name
    file_path = (RECORDINGS_DIR / safe_name).resolve()

    if not str(file_path).startswith(str(RECORDINGS_DIR.resolve())):
        raise HTTPException(status_code=400, detail="Invalid filename")

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Recording not found")

    return FileResponse(
        path=str(file_path),
        media_type="audio/wav",
        filename=safe_name,
    )
