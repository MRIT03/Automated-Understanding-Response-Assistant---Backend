from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import CallStatus, PriorityLevel
from app.schemas.common import ORMModel
from app.schemas.dispatcher import DispatcherRead
from app.schemas.incident import IncidentRead


class CallCreate(BaseModel):
    call_reference: str = Field(min_length=3, max_length=50)
    dispatcher_id: int
    incident_id: int | None = None
    caller_name: str | None = Field(default=None, max_length=255)
    caller_phone: str | None = Field(default=None, max_length=30)
    callback_required: bool = False
    source_channel: str = Field(default="phone", max_length=50)
    call_status: CallStatus = CallStatus.RECEIVED
    priority: PriorityLevel = PriorityLevel.MEDIUM
    reported_location: str = Field(min_length=3, max_length=255)
    transcript: str | None = None
    summary: str | None = None
    dispatcher_notes: str | None = None
    recording_url: str | None = Field(default=None, max_length=500)
    received_at: datetime | None = None


class CallUpdate(BaseModel):
    incident_id: int | None = None
    callback_required: bool | None = None
    source_channel: str | None = Field(default=None, max_length=50)
    call_status: CallStatus | None = None
    priority: PriorityLevel | None = None
    reported_location: str | None = Field(default=None, min_length=3, max_length=255)
    transcript: str | None = None
    summary: str | None = None
    dispatcher_notes: str | None = None
    recording_url: str | None = Field(default=None, max_length=500)
    closed_at: datetime | None = None


class CallRead(ORMModel):
    id: int
    call_reference: str
    dispatcher_id: int
    incident_id: int | None
    caller_name: str | None
    caller_phone: str | None
    callback_required: bool
    source_channel: str
    call_status: CallStatus
    priority: PriorityLevel
    reported_location: str
    transcript: str | None
    summary: str | None
    dispatcher_notes: str | None
    recording_url: str | None
    received_at: datetime
    closed_at: datetime | None
    dispatcher: DispatcherRead | None = None
    incident: IncidentRead | None = None
