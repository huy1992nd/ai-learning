"""ORM reads/writes for departments and doctors (UC-04)."""

from __future__ import annotations

from typing import Any, NoReturn

from sqlalchemy import func, select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.entities.department import DepartmentEntity
from app.entities.doctor import DoctorEntity
from app.models.department.department_public import DepartmentPublic
from app.models.doctor.doctor_public import DoctorPublic


class DatabaseUnavailableError(RuntimeError):
    """Raised when the configured DB exists but is not queryable or initialized."""


def _raise_database_unavailable(db: Session, exc: OperationalError) -> NoReturn:
    db.rollback()
    raise DatabaseUnavailableError("Database is not available or schema is not initialized") from exc


def _department_to_public(entity: DepartmentEntity) -> DepartmentPublic:
    return DepartmentPublic(
        id=int(entity.id),
        name=str(entity.name),
        description=entity.description,
        specialty=entity.specialty,
        symptoms_keywords=entity.symptoms_keywords,
        common_diseases=entity.common_diseases,
    )


def _doctor_to_public(entity: DoctorEntity) -> DoctorPublic:
    return DoctorPublic(
        id=int(entity.id),
        full_name=str(entity.full_name),
        department_id=int(entity.department_id),
        title=entity.title,
        specialty=entity.specialty,
        bio=entity.bio,
        photo_url=entity.photo_url,
        email=str(entity.email),
        phone=entity.phone,
        is_active=bool(entity.is_active),
    )


def list_departments(db: Session) -> list[DepartmentPublic]:
    try:
        rows = db.execute(select(DepartmentEntity).order_by(DepartmentEntity.id)).scalars().all()
    except OperationalError as exc:
        _raise_database_unavailable(db, exc)
    return [_department_to_public(entity) for entity in rows]


def get_department(db: Session, department_id: int) -> DepartmentPublic | None:
    try:
        entity = db.get(DepartmentEntity, department_id)
    except OperationalError as exc:
        _raise_database_unavailable(db, exc)
    return _department_to_public(entity) if entity else None


def list_doctors(
    db: Session,
    *,
    department_id: int | None = None,
    is_active: bool | None = True,
) -> list[DoctorPublic]:
    stmt = select(DoctorEntity)
    if department_id is not None:
        stmt = stmt.where(DoctorEntity.department_id == department_id)
    if is_active is not None:
        stmt = stmt.where(DoctorEntity.is_active == (1 if is_active else 0))
    try:
        rows = db.execute(stmt.order_by(DoctorEntity.id)).scalars().all()
    except OperationalError as exc:
        _raise_database_unavailable(db, exc)
    return [_doctor_to_public(entity) for entity in rows]


def get_doctor(db: Session, doctor_id: int) -> DoctorPublic | None:
    try:
        entity = db.get(DoctorEntity, doctor_id)
    except OperationalError as exc:
        _raise_database_unavailable(db, exc)
    return _doctor_to_public(entity) if entity else None


def find_department_id_by_name_case_insensitive(
    db: Session,
    name: str,
    *,
    exclude_id: int | None = None,
) -> int | None:
    stmt = select(DepartmentEntity.id).where(
        func.lower(DepartmentEntity.name) == name.strip().lower()
    )
    if exclude_id is not None:
        stmt = stmt.where(DepartmentEntity.id != exclude_id)
    try:
        row = db.execute(stmt.limit(1)).first()
    except OperationalError as exc:
        _raise_database_unavailable(db, exc)
    return int(row[0]) if row else None


def insert_department(
    db: Session,
    *,
    name: str,
    description: str | None,
    specialty: str | None,
    symptoms_keywords: str | None,
    common_diseases: str | None,
) -> DepartmentPublic:
    entity = DepartmentEntity(
        name=name.strip(),
        description=description,
        specialty=specialty,
        symptoms_keywords=symptoms_keywords,
        common_diseases=common_diseases,
    )
    try:
        db.add(entity)
        db.commit()
        db.refresh(entity)
    except OperationalError as exc:
        _raise_database_unavailable(db, exc)
    return _department_to_public(entity)


def update_department_fields(
    db: Session,
    department_id: int,
    fields: dict[str, Any],
) -> DepartmentPublic | None:
    allowed = {
        "name",
        "description",
        "specialty",
        "symptoms_keywords",
        "common_diseases",
    }
    updates = {k: v for k, v in fields.items() if k in allowed}
    if not updates:
        return get_department(db, department_id)
    try:
        entity = db.get(DepartmentEntity, department_id)
    except OperationalError as exc:
        _raise_database_unavailable(db, exc)
    if entity is None:
        return None
    for key, value in updates.items():
        setattr(entity, key, value)
    try:
        db.commit()
        db.refresh(entity)
    except OperationalError as exc:
        _raise_database_unavailable(db, exc)
    return _department_to_public(entity)
