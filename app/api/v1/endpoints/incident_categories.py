from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.incident_category import IncidentCategory
from app.schemas.incident_category import IncidentCategoryCreate, IncidentCategoryRead

router = APIRouter()


@router.post("", response_model=IncidentCategoryRead, status_code=status.HTTP_201_CREATED)
def create_incident_category(payload: IncidentCategoryCreate, db: Session = Depends(get_db)) -> IncidentCategory:
    existing = db.execute(
        select(IncidentCategory).where(IncidentCategory.name == payload.name)
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Incident category with that name already exists")

    category = IncidentCategory(**payload.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.get("", response_model=list[IncidentCategoryRead])
def list_incident_categories(db: Session = Depends(get_db)) -> list[IncidentCategory]:
    return list(db.execute(select(IncidentCategory).order_by(IncidentCategory.name)).scalars().all())
