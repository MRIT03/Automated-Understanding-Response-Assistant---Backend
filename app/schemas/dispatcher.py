from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import ORMModel


class DispatcherCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=255)
    badge_number: str = Field(min_length=2, max_length=50)
    phone_number: str | None = Field(default=None, max_length=30)
    shift_name: str | None = Field(default=None, max_length=100)
    rank: str | None = Field(default=None, max_length=100)
    password: str = Field(min_length=8, max_length=128)


class DispatcherUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=255)
    phone_number: str | None = Field(default=None, max_length=30)
    shift_name: str | None = Field(default=None, max_length=100)
    rank: str | None = Field(default=None, max_length=100)
    is_active: bool | None = None


class DispatcherRead(ORMModel):
    id: int
    username: str
    email: EmailStr
    full_name: str
    badge_number: str
    phone_number: str | None
    shift_name: str | None
    rank: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
