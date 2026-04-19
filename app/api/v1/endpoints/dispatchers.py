from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import get_password_hash
from app.models.dispatcher import Dispatcher
from app.schemas.dispatcher import DispatcherCreate, DispatcherRead, DispatcherUpdate

router = APIRouter()


@router.post("", response_model=DispatcherRead, status_code=status.HTTP_201_CREATED)
def create_dispatcher(payload: DispatcherCreate, db: Session = Depends(get_db)) -> Dispatcher:
    existing = db.execute(
        select(Dispatcher).where(
            (Dispatcher.username == payload.username)
            | (Dispatcher.email == payload.email)
            | (Dispatcher.badge_number == payload.badge_number)
        )
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Dispatcher with username, email, or badge number already exists")

    dispatcher = Dispatcher(
        username=payload.username,
        email=payload.email,
        full_name=payload.full_name,
        badge_number=payload.badge_number,
        phone_number=payload.phone_number,
        shift_name=payload.shift_name,
        rank=payload.rank,
        hashed_password=get_password_hash(payload.password),
    )
    db.add(dispatcher)
    db.commit()
    db.refresh(dispatcher)
    return dispatcher


@router.get("", response_model=list[DispatcherRead])
def list_dispatchers(db: Session = Depends(get_db)) -> list[Dispatcher]:
    return list(db.execute(select(Dispatcher).order_by(Dispatcher.id.desc())).scalars().all())


@router.get("/{dispatcher_id}", response_model=DispatcherRead)
def get_dispatcher(dispatcher_id: int, db: Session = Depends(get_db)) -> Dispatcher:
    dispatcher = db.get(Dispatcher, dispatcher_id)
    if not dispatcher:
        raise HTTPException(status_code=404, detail="Dispatcher not found")
    return dispatcher


@router.patch("/{dispatcher_id}", response_model=DispatcherRead)
def update_dispatcher(dispatcher_id: int, payload: DispatcherUpdate, db: Session = Depends(get_db)) -> Dispatcher:
    dispatcher = db.get(Dispatcher, dispatcher_id)
    if not dispatcher:
        raise HTTPException(status_code=404, detail="Dispatcher not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(dispatcher, field, value)

    db.add(dispatcher)
    db.commit()
    db.refresh(dispatcher)
    return dispatcher
