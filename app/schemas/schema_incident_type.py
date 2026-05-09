from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel
from app.schemas.incident_category import IncidentCategoryRead


class IncidentTypeCreate(BaseModel):
    category_id: int
    name: str = Field(min_length=2, max_length=150)
    description: str | None = None


class IncidentTypeRead(ORMModel):
    id: int
    category_id: int
    name: str
    description: str | None
    created_at: datetime
    category: IncidentCategoryRead | None = None
