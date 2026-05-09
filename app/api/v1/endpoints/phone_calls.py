from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_db
from app.models.employee import Employee
from app.models.incident import Incident
from app.models.phone_call import PhoneCall
from app.schemas.phone_call import PhoneCallCreate, PhoneCallRead, PhoneCallUpdate

router = APIRouter()


@router.post("", response_model=PhoneCallRead, status_code=status.HTTP_201_CREATED)
def create_phone_call(payload: PhoneCallCreate, db: Session = Depends(get_db)) -> PhoneCall:
    if not db.get(Incident, payload.incident_id):
        raise HTTPException(status_code=404, detail="Incident not found")
    if not db.get(Employee, payload.employee_id):
        raise HTTPException(status_code=404, detail="Employee not found")

    phone_call = PhoneCall(**payload.model_dump())
    db.add(phone_call)
    db.commit()
    db.refresh(phone_call)
    return phone_call


@router.get("", response_model=list[PhoneCallRead])
def list_phone_calls(db: Session = Depends(get_db)) -> list[PhoneCall]:
    stmt = select(PhoneCall).options(joinedload(PhoneCall.employee)).order_by(PhoneCall.started_at.desc())
    return list(db.execute(stmt).scalars().unique().all())


@router.get("/{phone_call_id}", response_model=PhoneCallRead)
def get_phone_call(phone_call_id: int, db: Session = Depends(get_db)) -> PhoneCall:
    stmt = (
        select(PhoneCall)
        .options(joinedload(PhoneCall.employee))
        .where(PhoneCall.id == phone_call_id)
    )
    phone_call = db.execute(stmt).scalars().unique().one_or_none()
    if not phone_call:
        raise HTTPException(status_code=404, detail="Phone call not found")
    return phone_call


@router.patch("/{phone_call_id}", response_model=PhoneCallRead)
def update_phone_call(phone_call_id: int, payload: PhoneCallUpdate, db: Session = Depends(get_db)) -> PhoneCall:
    phone_call = db.get(PhoneCall, phone_call_id)
    if not phone_call:
        raise HTTPException(status_code=404, detail="Phone call not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(phone_call, field, value)

    db.add(phone_call)
    db.commit()
    db.refresh(phone_call)
    return phone_call
