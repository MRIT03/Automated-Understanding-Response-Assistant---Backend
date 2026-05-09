from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_db
from app.models.incident_category import IncidentCategory
from app.models.incident_type import IncidentType
from app.schemas.incident_type import IncidentTypeCreate, IncidentTypeRead

router = APIRouter()


@router.post("", response_model=IncidentTypeRead, status_code=status.HTTP_201_CREATED)
def create_incident_type(payload: IncidentTypeCreate, db: Session = Depends(get_db)) -> IncidentType:
    if not db.get(IncidentCategory, payload.category_id):
        raise HTTPException(status_code=404, detail="Incident category not found")

    existing = db.execute(
        select(IncidentType).where(IncidentType.name == payload.name)
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Incident type with that name already exists")

    incident_type = IncidentType(**payload.model_dump())
    db.add(incident_type)
    db.commit()
    db.refresh(incident_type)
    return incident_type


@router.get("", response_model=list[IncidentTypeRead])
def list_incident_types(db: Session = Depends(get_db)) -> list[IncidentType]:
    stmt = select(IncidentType).options(joinedload(IncidentType.category)).order_by(IncidentType.name)
    return list(db.execute(stmt).scalars().unique().all())
