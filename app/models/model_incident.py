from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    incident_type_id: Mapped[int] = mapped_column(ForeignKey("incident_types.id", ondelete="RESTRICT"), index=True)
    reported_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    occurred_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="reported", index=True)
    priority: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    latitude: Mapped[float | None] = mapped_column(Numeric(10, 7), nullable=True)
    longitude: Mapped[float | None] = mapped_column(Numeric(10, 7), nullable=True)
    caller_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    caller_phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    whisper_transcript: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    incident_type = relationship("IncidentType", back_populates="incidents")
    phone_calls = relationship("PhoneCall", back_populates="incident", cascade="all, delete-orphan")
