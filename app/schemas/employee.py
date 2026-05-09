from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import ORMModel


class EmployeeCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    phone_number: str | None = Field(default=None, max_length=30)
    email: EmailStr | None = None
    employee_code: str | None = Field(default=None, max_length=50)
    is_active: bool = True


class EmployeeUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    phone_number: str | None = Field(default=None, max_length=30)
    email: EmailStr | None = None
    employee_code: str | None = Field(default=None, max_length=50)
    is_active: bool | None = None


class EmployeeRead(ORMModel):
    id: int
    first_name: str
    last_name: str
    phone_number: str | None
    email: str | None
    employee_code: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
