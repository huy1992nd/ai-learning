from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.orm import Base


class MedicalExaminationScheduleEntity(Base):
    __tablename__ = "medical_examination_schedule"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    doctor_id: Mapped[int] = mapped_column(
        ForeignKey("doctors.id"),
        nullable=False,
    )
    start_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="BOOKED")
    appointment_id: Mapped[int | None] = mapped_column(
        ForeignKey("appointments.id"),
        nullable=True,
    )

    doctor: Mapped["DoctorEntity"] = relationship(
        "DoctorEntity",
        back_populates="examination_schedules",
    )
    appointment: Mapped["AppointmentEntity | None"] = relationship(
        "AppointmentEntity",
        back_populates="examination_schedules",
    )
