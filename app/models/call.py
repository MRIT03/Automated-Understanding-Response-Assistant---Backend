from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import CallStatus, PriorityLevel


class Call(Base):
    __tablename__ = "calls"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    call_reference: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    dispatcher_id: Mapped[int] = mapped_column(ForeignKey("dispatchers.id", ondelete="RESTRICT"), index=True)
    incident_id: Mapped[int | None] = mapped_column(ForeignKey("incidents.id", ondelete="SET NULL"), nullable=True, index=True)
    caller_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    caller_phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    callback_required: Mapped[bool] = mapped_column(Boolean, default=False)
    source_channel: Mapped[str] = mapped_column(String(50), default="phone")
    call_status: Mapped[CallStatus] = mapped_column(Enum(CallStatus), default=CallStatus.RECEIVED, index=True)
    priority: Mapped[PriorityLevel] = mapped_column(Enum(PriorityLevel), default=PriorityLevel.MEDIUM, index=True)
    reported_location: Mapped[str] = mapped_column(String(255), index=True)
    transcript: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    dispatcher_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    recording_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    dispatcher = relationship("Dispatcher", back_populates="calls")
    incident = relationship("Incident", back_populates="calls")
