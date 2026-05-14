from __future__ import annotations

import logging
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, ValidationError

from agents_service.agents import (
    run_localization,
    run_record_generator,
    run_transcript_cleaner,
)

logger = logging.getLogger(__name__)

router = APIRouter()


class TranscriptRequest(BaseModel):
    raw_transcript: str


class TranscriptResponse(BaseModel):
    cleaned_transcript: str


class LocalizationRequest(BaseModel):
    transcript: str


class LocalizationResponse(BaseModel):
    location_text: str | None = None
    location_normalized: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    confidence: Literal["high", "medium", "low"] | None = None


class RecordIncident(BaseModel):
    incident_type_code: Literal[
        "FIRE_STRUCTURE",
        "FIRE_FIELD",
        "FIRE_FOREST",
        "FIRE_URBAN",
        "EMS_TRANSPORT",
        "HOSPITAL_TRANSPORT",
        "VEHICLE_TRANSPORT",
    ]
    priority: Literal["low", "medium", "high", "critical"]
    location_address: str | None = None
    location_details: str | None = None
    description: str
    units_requested: int = Field(ge=1)


class RecordCall(BaseModel):
    caller_name: str | None = None
    caller_phone: str | None = None
    reported_location: str | None = None
    summary: str


class RecordRequest(BaseModel):
    transcript: str


class RecordResponse(BaseModel):
    incident: RecordIncident
    call: RecordCall


@router.post("/clean-transcript", response_model=TranscriptResponse)
async def clean_transcript(payload: TranscriptRequest) -> TranscriptResponse:
    try:
        cleaned = await run_transcript_cleaner(payload.raw_transcript)
        return TranscriptResponse(cleaned_transcript=cleaned)

    except Exception as exc:
        logger.exception("Transcript cleaning failed")
        raise HTTPException(
            status_code=500,
            detail=f"Transcript cleaning failed: {exc}",
        ) from exc


@router.post("/localize", response_model=LocalizationResponse)
async def localize(payload: LocalizationRequest) -> LocalizationResponse:
    try:
        result = await run_localization(payload.transcript)
        logger.info("Localization agent result: %s", result)
        return LocalizationResponse(**result)

    except ValueError as exc:
        logger.exception("Localization agent returned invalid JSON")
        raise HTTPException(
            status_code=502,
            detail=f"Localization agent returned invalid JSON: {exc}",
        ) from exc

    except ValidationError as exc:
        logger.exception("Localization schema validation failed")
        raise HTTPException(
            status_code=422,
            detail=exc.errors(),
        ) from exc

    except Exception as exc:
        logger.exception("Localization failed")
        raise HTTPException(
            status_code=500,
            detail=f"Localization failed: {exc}",
        ) from exc


@router.post("/generate-record", response_model=RecordResponse)
async def generate_record(payload: RecordRequest) -> RecordResponse:
    try:
        result = await run_record_generator(payload.transcript)
        logger.info("Record generator result: %s", result)
        return RecordResponse(**result)

    except ValueError as exc:
        logger.exception("Record generator returned invalid JSON")
        raise HTTPException(
            status_code=502,
            detail=f"Record generator returned invalid JSON: {exc}",
        ) from exc

    except ValidationError as exc:
        logger.exception("Record generator schema validation failed")
        raise HTTPException(
            status_code=422,
            detail=exc.errors(),
        ) from exc

    except Exception as exc:
        logger.exception("Record generation failed")
        raise HTTPException(
            status_code=500,
            detail=f"Record generation failed: {exc}",
        ) from exc