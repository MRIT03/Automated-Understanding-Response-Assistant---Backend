from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import PriorityLevel
from app.schemas.common import ORMModel


class IncidentTypeCreate(BaseModel):
    code: str = Field(min_length=2, max_length=50)
    name: str = Field(min_length=2, max_length=120)
    category: str = Field(min_length=2, max_length=50)
    description: str | None = None
    default_priority: PriorityLevel = PriorityLevel.MEDIUM
    is_active: bool = True


class IncidentTypeRead(ORMModel):
    id: int
    code: str
    name: str
    category: str
    description: str | None
    default_priority: PriorityLevel
    is_active: bool
    created_at: datetime
    updated_at: datetime
