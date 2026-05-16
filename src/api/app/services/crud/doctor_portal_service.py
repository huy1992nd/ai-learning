"""UC-10 - doctor-facing read-only schedule list (demo)."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.entities.appointment import AppointmentEntity
from app.entities.patient import PatientEntity


def list_appointments_for_doctor(
    db: Session, doctor_id: int, *, limit: int = 50
) -> list[dict[str, Any]]:
    stmt = (
        select(
            AppointmentEntity.id,
            AppointmentEntity.appointment_code,
            AppointmentEntity.scheduled_at,
            AppointmentEntity.severity,
            AppointmentEntity.status,
            PatientEntity.full_name.label("patient_name"),
            PatientEntity.phone.label("patient_phone"),
        )
        .join(PatientEntity, PatientEntity.id == AppointmentEntity.patient_id)
        .where(AppointmentEntity.doctor_id == doctor_id)
        .order_by(AppointmentEntity.scheduled_at.desc())
        .limit(limit)
    )
    rows = db.execute(stmt).all()
    return [
        {
            "id": row.id,
            "appointment_code": row.appointment_code,
            "scheduled_at": row.scheduled_at,
            "severity": row.severity,
            "status": row.status,
            "patient_name": row.patient_name,
            "patient_phone": row.patient_phone,
        }
        for row in rows
    ]
