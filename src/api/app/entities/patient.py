from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.orm import Base


class PatientEntity(Base):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(Text, nullable=False)
    dob: Mapped[date | None] = mapped_column(Date, nullable=True)
    gender: Mapped[str | None] = mapped_column(Text, nullable=True)
    phone: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[str | None] = mapped_column(Text, nullable=True)
    id_number: Mapped[str | None] = mapped_column(Text, nullable=True)
    insurance_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
    )

    appointments: Mapped[list["AppointmentEntity"]] = relationship(
        "AppointmentEntity",
        back_populates="patient",
    )
    chat_sessions: Mapped[list["ChatSessionEntity"]] = relationship(
        "ChatSessionEntity",
        back_populates="patient",
    )
