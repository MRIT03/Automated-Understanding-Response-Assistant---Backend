from __future__ import annotations

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin


class Dispatcher(TimestampMixin, Base):
    __tablename__ = "dispatchers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255))
    badge_number: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    phone_number: Mapped[str | None] = mapped_column(String(30), nullable=True)
    shift_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    rank: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    hashed_password: Mapped[str] = mapped_column(String(255))

    calls = relationship("Call", back_populates="dispatcher", passive_deletes=True)
