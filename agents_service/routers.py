from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from agents_service.agents import (
    run_localization,
    run_record_generator,
    run_transcript_cleaner,
)

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
    confidence: str | None = None


class RecordIncident(BaseModel):
    incident_type_code: str
    priority: str
    location_address: str
    location_details: str | None = None
    description: str
    units_requested: int


class RecordCall(BaseModel):
    caller_name: str | None = None
    caller_phone: str | None = None
    reported_location: str
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
        raise HTTPException(status_code=500, detail=f"Transcript cleaning failed: {exc}") from exc


@router.post("/localize", response_model=LocalizationResponse)
async def localize(payload: LocalizationRequest) -> LocalizationResponse:
    try:
        result = await run_localization(payload.transcript)
        return LocalizationResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Localization failed: {exc}") from exc


@router.post("/generate-record", response_model=RecordResponse)
async def generate_record(payload: RecordRequest) -> RecordResponse:
    try:
        result = await run_record_generator(payload.transcript)
        return RecordResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Record generation failed: {exc}") from exc