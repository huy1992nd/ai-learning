from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.orm import Base


class DiseaseDepartmentMappingEntity(Base):
    __tablename__ = "disease_department_mapping"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    disease_name: Mapped[str] = mapped_column(Text, nullable=False)
    department_id: Mapped[int] = mapped_column(
        ForeignKey("departments.id"),
        nullable=False,
    )

    department: Mapped["DepartmentEntity"] = relationship(
        "DepartmentEntity",
        back_populates="disease_mappings",
    )
