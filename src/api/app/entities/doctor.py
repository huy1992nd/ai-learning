from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.orm import Base


class DoctorEntity(Base):
    __tablename__ = "doctors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(Text, nullable=False)
    department_id: Mapped[int] = mapped_column(
        ForeignKey("departments.id"),
        nullable=False,
    )
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    specialty: Mapped[str | None] = mapped_column(Text, nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    photo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    email: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    phone: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[int | None] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
    )

    department: Mapped["DepartmentEntity"] = relationship(
        "DepartmentEntity",
        back_populates="doctors",
    )
    working_hours: Mapped[list["DoctorWorkingHourEntity"]] = relationship(
        "DoctorWorkingHourEntity",
        back_populates="doctor",
    )
    appointments: Mapped[list["AppointmentEntity"]] = relationship(
        "AppointmentEntity",
        back_populates="doctor",
    )
    examination_schedules: Mapped[list["MedicalExaminationScheduleEntity"]] = relationship(
        "MedicalExaminationScheduleEntity",
        back_populates="doctor",
    )
    user_accounts: Mapped[list["UserAccountEntity"]] = relationship(
        "UserAccountEntity",
        back_populates="doctor",
    )
