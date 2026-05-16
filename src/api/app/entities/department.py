from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.orm import Base


class DepartmentEntity(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    specialty: Mapped[str | None] = mapped_column(Text, nullable=True)
    symptoms_keywords: Mapped[str | None] = mapped_column(Text, nullable=True)
    common_diseases: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
    )

    doctors: Mapped[list["DoctorEntity"]] = relationship(
        "DoctorEntity",
        back_populates="department",
    )
    disease_mappings: Mapped[list["DiseaseDepartmentMappingEntity"]] = relationship(
        "DiseaseDepartmentMappingEntity",
        back_populates="department",
    )
    appointments: Mapped[list["AppointmentEntity"]] = relationship(
        "AppointmentEntity",
        back_populates="department",
    )
