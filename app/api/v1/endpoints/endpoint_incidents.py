from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_db
from app.models.incident import Incident
from app.models.incident_type import IncidentType
from app.schemas.incident import IncidentCreate, IncidentRead, IncidentUpdate

router = APIRouter()


@router.post("", response_model=IncidentRead, status_code=status.HTTP_201_CREATED)
def create_incident(payload: IncidentCreate, db: Session = Depends(get_db)) -> Incident:
    if not db.get(IncidentType, payload.incident_type_id):
        raise HTTPException(status_code=404, detail="Incident type not found")

    incident = Incident(**payload.model_dump())
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident


@router.get("", response_model=list[IncidentRead])
def list_incidents(db: Session = Depends(get_db)) -> list[Incident]:
    stmt = (
        select(Incident)
        .options(joinedload(Incident.incident_type).joinedload(IncidentType.category))
        .order_by(Incident.reported_at.desc())
    )
    return list(db.execute(stmt).scalars().unique().all())


@router.get("/{incident_id}", response_model=IncidentRead)
def get_incident(incident_id: int, db: Session = Depends(get_db)) -> Incident:
    stmt = (
        select(Incident)
        .options(joinedload(Incident.incident_type).joinedload(IncidentType.category))
        .where(Incident.id == incident_id)
    )
    incident = db.execute(stmt).scalars().unique().one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.patch("/{incident_id}", response_model=IncidentRead)
def update_incident(incident_id: int, payload: IncidentUpdate, db: Session = Depends(get_db)) -> Incident:
    incident = db.get(Incident, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(incident, field, value)

    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident
