from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.incident_type import IncidentType
from app.schemas.incident_type import IncidentTypeCreate, IncidentTypeRead

router = APIRouter()


@router.post("", response_model=IncidentTypeRead, status_code=status.HTTP_201_CREATED)
def create_incident_type(payload: IncidentTypeCreate, db: Session = Depends(get_db)) -> IncidentType:
    existing = db.execute(
        select(IncidentType).where((IncidentType.code == payload.code) | (IncidentType.name == payload.name))
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Incident type with that code or name already exists")

    incident_type = IncidentType(**payload.model_dump())
    db.add(incident_type)
    db.commit()
    db.refresh(incident_type)
    return incident_type


@router.get("", response_model=list[IncidentTypeRead])
def list_incident_types(db: Session = Depends(get_db)) -> list[IncidentType]:
    return list(db.execute(select(IncidentType).order_by(IncidentType.category, IncidentType.name)).scalars().all())
