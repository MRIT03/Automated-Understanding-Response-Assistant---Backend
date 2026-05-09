from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel
from app.schemas.employee import EmployeeRead


class PhoneCallCreate(BaseModel):
    incident_id: int
    employee_id: int
    caller_phone: str | None = Field(default=None, max_length=30)
    started_at: datetime
    ended_at: datetime | None = None
    duration_seconds: int | None = None
    call_recording_url: str | None = None
    whisper_transcript: str | None = None
    notes: str | None = None


class PhoneCallUpdate(BaseModel):
    ended_at: datetime | None = None
    duration_seconds: int | None = None
    call_recording_url: str | None = None
    whisper_transcript: str | None = None
    notes: str | None = None


class PhoneCallRead(ORMModel):
    id: int
    incident_id: int
    employee_id: int
    caller_phone: str | None
    started_at: datetime
    ended_at: datetime | None
    duration_seconds: int | None
    call_recording_url: str | None
    whisper_transcript: str | None
    notes: str | None
    created_at: datetime
    employee: EmployeeRead | None = None
