from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_db
from app.models.incident import Incident
from app.models.incident_type import IncidentType
from app.schemas.incident import IncidentCreate, IncidentRead, IncidentStatusUpdate, IncidentUpdate

router = APIRouter()


@router.post("", response_model=IncidentRead, status_code=status.HTTP_201_CREATED)
def create_incident(payload: IncidentCreate, db: Session = Depends(get_db)) -> Incident:
    incident_type = db.get(IncidentType, payload.incident_type_id)
    if not incident_type:
        raise HTTPException(status_code=404, detail="Incident type not found")

    existing = db.execute(select(Incident).where(Incident.incident_number == payload.incident_number)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Incident number already exists")

    incident = Incident(**payload.model_dump())
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident


@router.get("", response_model=list[IncidentRead])
def list_incidents(db: Session = Depends(get_db)) -> list[Incident]:
    stmt = select(Incident).options(joinedload(Incident.incident_type)).order_by(Incident.opened_at.desc())
    return list(db.execute(stmt).scalars().unique().all())


@router.get("/{incident_id}", response_model=IncidentRead)
def get_incident(incident_id: int, db: Session = Depends(get_db)) -> Incident:
    stmt = select(Incident).options(joinedload(Incident.incident_type)).where(Incident.id == incident_id)
    incident = db.execute(stmt).scalars().unique().one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.patch("/{incident_id}", response_model=IncidentRead)
def update_incident(incident_id: int, payload: IncidentUpdate, db: Session = Depends(get_db)) -> Incident:
    incident = db.get(Incident, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(incident, field, value)

    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident


@router.patch("/{incident_id}/status", response_model=IncidentRead)
def update_incident_status(incident_id: int, payload: IncidentStatusUpdate, db: Session = Depends(get_db)) -> Incident:
    incident = db.get(Incident, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    incident.status = payload.status
    if payload.status.value == "closed" and incident.closed_at is None:
        incident.closed_at = datetime.now(timezone.utc)

    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident
