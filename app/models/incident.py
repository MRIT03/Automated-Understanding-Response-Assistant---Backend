from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    incident_type_id: Mapped[int] = mapped_column(ForeignKey("incident_types.id"), index=True)

    status: Mapped[str] = mapped_column(String(50), default="reported", index=True)
    priority: Mapped[str | None] = mapped_column(String(50), nullable=True)

    address: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)

    caller_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    caller_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    whisper_transcript: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Absolute path to the call recording WAV file on the host machine.
    recording_path: Mapped[str | None] = mapped_column(Text, nullable=True)

    reported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    occurred_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    incident_type = relationship("IncidentType", back_populates="incidents")
    phone_calls = relationship(
        "PhoneCall",
        back_populates="incident",
    )
