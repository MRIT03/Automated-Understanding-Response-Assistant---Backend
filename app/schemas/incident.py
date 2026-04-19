from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import IncidentStatus, PriorityLevel
from app.schemas.common import ORMModel
from app.schemas.incident_type import IncidentTypeRead


class IncidentCreate(BaseModel):
    incident_number: str = Field(min_length=3, max_length=50)
    incident_type_id: int
    status: IncidentStatus = IncidentStatus.REPORTED
    priority: PriorityLevel = PriorityLevel.MEDIUM
    location_address: str = Field(min_length=3, max_length=255)
    location_details: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    description: str | None = None
    units_requested: int = Field(default=1, ge=1)
    units_dispatched: int = Field(default=0, ge=0)


class IncidentUpdate(BaseModel):
    status: IncidentStatus | None = None
    priority: PriorityLevel | None = None
    location_address: str | None = Field(default=None, min_length=3, max_length=255)
    location_details: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    description: str | None = None
    units_requested: int | None = Field(default=None, ge=1)
    units_dispatched: int | None = Field(default=None, ge=0)
    closed_at: datetime | None = None


class IncidentStatusUpdate(BaseModel):
    status: IncidentStatus


class IncidentRead(ORMModel):
    id: int
    incident_number: str
    incident_type_id: int
    status: IncidentStatus
    priority: PriorityLevel
    location_address: str
    location_details: str | None
    latitude: float | None
    longitude: float | None
    description: str | None
    units_requested: int
    units_dispatched: int
    opened_at: datetime
    updated_at: datetime
    closed_at: datetime | None
    incident_type: IncidentTypeRead | None = None
