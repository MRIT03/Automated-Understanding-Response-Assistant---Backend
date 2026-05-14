# app/api/v1/endpoints/settings.py

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Literal

router = APIRouter()

_SETTINGS = {
    "performance": "moderate",
    "operator_name": None,
}


class SettingsRead(BaseModel):
    performance: Literal["high", "moderate"] = "moderate"
    operator_name: str | None = None


class SettingsUpdate(BaseModel):
    performance: Literal["high", "moderate"]
    operator_name: str | None = None


@router.get("", response_model=SettingsRead)
def get_settings() -> SettingsRead:
    return SettingsRead(**_SETTINGS)


@router.put("", response_model=SettingsRead)
def update_settings(payload: SettingsUpdate) -> SettingsRead:
    _SETTINGS["performance"] = payload.performance
    _SETTINGS["operator_name"] = payload.operator_name
    return SettingsRead(**_SETTINGS)