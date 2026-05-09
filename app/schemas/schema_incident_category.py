from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class IncidentCategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    description: str | None = None


class IncidentCategoryRead(ORMModel):
    id: int
    name: str
    description: str | None
    created_at: datetime
