from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_db
from app.models.call import Call
from app.models.dispatcher import Dispatcher
from app.models.incident import Incident
from app.schemas.call import CallCreate, CallRead, CallUpdate

router = APIRouter()


@router.post("", response_model=CallRead, status_code=status.HTTP_201_CREATED)
def create_call(payload: CallCreate, db: Session = Depends(get_db)) -> Call:
    dispatcher = db.get(Dispatcher, payload.dispatcher_id)
    if not dispatcher:
        raise HTTPException(status_code=404, detail="Dispatcher not found")

    if payload.incident_id is not None and not db.get(Incident, payload.incident_id):
        raise HTTPException(status_code=404, detail="Incident not found")

    existing = db.execute(select(Call).where(Call.call_reference == payload.call_reference)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Call reference already exists")

    values = payload.model_dump(exclude_none=True)
    call = Call(**values)
    db.add(call)
    db.commit()
    db.refresh(call)
    return call


@router.get("", response_model=list[CallRead])
def list_calls(db: Session = Depends(get_db)) -> list[Call]:
    stmt = (
        select(Call)
        .options(joinedload(Call.dispatcher), joinedload(Call.incident).joinedload(Incident.incident_type))
        .order_by(Call.received_at.desc())
    )
    return list(db.execute(stmt).scalars().unique().all())


@router.get("/{call_id}", response_model=CallRead)
def get_call(call_id: int, db: Session = Depends(get_db)) -> Call:
    stmt = (
        select(Call)
        .options(joinedload(Call.dispatcher), joinedload(Call.incident).joinedload(Incident.incident_type))
        .where(Call.id == call_id)
    )
    call = db.execute(stmt).scalars().unique().one_or_none()
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    return call


@router.patch("/{call_id}", response_model=CallRead)
def update_call(call_id: int, payload: CallUpdate, db: Session = Depends(get_db)) -> Call:
    call = db.get(Call, call_id)
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")

    updates = payload.model_dump(exclude_unset=True)
    if "incident_id" in updates and updates["incident_id"] is not None and not db.get(Incident, updates["incident_id"]):
        raise HTTPException(status_code=404, detail="Incident not found")

    for field, value in updates.items():
        setattr(call, field, value)

    db.add(call)
    db.commit()
    db.refresh(call)
    return call
