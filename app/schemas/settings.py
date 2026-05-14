from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

PerformanceMode = Literal["high", "moderate"]


class AppSettingsRead(BaseModel):
    performance: PerformanceMode = "moderate"
    operator_name: str = "Operator"


class AppSettingsUpdate(BaseModel):
    performance: PerformanceMode | None = None
    operator_name: str | None = Field(default=None, min_length=1, max_length=100)
