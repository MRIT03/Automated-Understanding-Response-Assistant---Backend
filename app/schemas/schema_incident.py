from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel
from app.schemas.incident_type import IncidentTypeRead


class IncidentCreate(BaseModel):
    incident_type_id: int
    occurred_at: datetime | None = None
    status: str = "reported"
    priority: str | None = None
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    caller_name: str | None = Field(default=None, max_length=150)
    caller_phone: str | None = Field(default=None, max_length=30)
    description: str | None = None
    whisper_transcript: str | None = None


class IncidentUpdate(BaseModel):
    occurred_at: datetime | None = None
    status: str | None = None
    priority: str | None = None
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    caller_name: str | None = Field(default=None, max_length=150)
    caller_phone: str | None = Field(default=None, max_length=30)
    description: str | None = None
    whisper_transcript: str | None = None


class IncidentRead(ORMModel):
    id: int
    incident_type_id: int
    reported_at: datetime
    occurred_at: datetime | None
    status: str
    priority: str | None
    address: str | None
    latitude: float | None
    longitude: float | None
    caller_name: str | None
    caller_phone: str | None
    description: str | None
    whisper_transcript: str | None
    created_at: datetime
    updated_at: datetime
    incident_type: IncidentTypeRead | None = None
