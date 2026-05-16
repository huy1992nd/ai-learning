from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.orm import Base


class AppointmentEntity(Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    appointment_code: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patients.id"),
        nullable=False,
    )
    doctor_id: Mapped[int] = mapped_column(
        ForeignKey("doctors.id"),
        nullable=False,
    )
    department_id: Mapped[int] = mapped_column(
        ForeignKey("departments.id"),
        nullable=False,
    )
    symptoms: Mapped[str | None] = mapped_column(Text, nullable=True)
    predicted_diseases: Mapped[str | None] = mapped_column(Text, nullable=True)
    severity: Mapped[str] = mapped_column(Text, nullable=False)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[str | None] = mapped_column(Text, default="PENDING")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
    )

    patient: Mapped["PatientEntity"] = relationship(
        "PatientEntity",
        back_populates="appointments",
    )
    doctor: Mapped["DoctorEntity"] = relationship(
        "DoctorEntity",
        back_populates="appointments",
    )
    department: Mapped["DepartmentEntity"] = relationship(
        "DepartmentEntity",
        back_populates="appointments",
    )
    examination_schedules: Mapped[list["MedicalExaminationScheduleEntity"]] = relationship(
        "MedicalExaminationScheduleEntity",
        back_populates="appointment",
    )
