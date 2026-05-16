"""UC-08: create appointment + block slot (ORM transaction)."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.entities.appointment import AppointmentEntity
from app.entities.department import DepartmentEntity
from app.entities.doctor import DoctorEntity
from app.entities.medical_examination_schedule import MedicalExaminationScheduleEntity
from app.entities.patient import PatientEntity
from app.models.appointment.appointment_create_request import AppointmentCreateRequest
from app.services.general.patient_validators import FIELD_VALIDATORS, normalize_phone

logger = logging.getLogger(__name__)


class AppointmentValidationError(ValueError):
    pass


class SlotUnavailableError(ValueError):
    pass


def _to_sql_date(dob: str | None) -> str | None:
    if not dob:
        return None
    s = dob.strip()
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt).date().isoformat()
        except ValueError:
            continue
    return None


def _parse_scheduled_at(value: str) -> datetime:
    s = value.strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
        try:
            dt = datetime.strptime(s, fmt)
            if fmt == "%Y-%m-%d %H:%M":
                return dt.replace(second=0)
            return dt
        except ValueError:
            continue
    raise ValueError("scheduled_at must be in format YYYY-MM-DD HH:MM[:SS]")


def _validate_field(field: str, value: Any, lang: str) -> None:
    ok, err = FIELD_VALIDATORS[field](value, lang)
    if not ok:
        raise AppointmentValidationError(err or f"{field} is invalid")


def create_appointment_from_request(db: Session, body: AppointmentCreateRequest) -> dict[str, Any]:
    lang = "vi"
    phone = normalize_phone(body.phone)
    _validate_field("phone", phone, lang)
    _validate_field("full_name", body.full_name, lang)
    if body.gender:
        _validate_field("gender", body.gender, lang)
    if body.email:
        _validate_field("email", body.email, lang)
    if body.cccd:
        _validate_field("cccd", body.cccd, lang)
    if body.bhyt:
        _validate_field("bhyt", body.bhyt, lang)
    if body.address:
        _validate_field("address", body.address, lang)
    if body.date_of_birth:
        _validate_field("date_of_birth", body.date_of_birth, lang)

    return create_appointment(
        db=db,
        full_name=body.full_name.strip(),
        dob=_to_sql_date(body.date_of_birth) if body.date_of_birth else None,
        gender=body.gender,
        phone=phone,
        email=body.email,
        id_number=body.cccd,
        insurance_id=body.bhyt,
        address=body.address,
        doctor_id=body.doctor_id,
        department_id=body.department_id,
        scheduled_at=body.scheduled_at.strip(),
        symptoms=body.symptoms,
        predicted_diseases=body.predicted_diseases,
        severity=(body.severity or "MILD").upper(),
    )


def _next_appointment_code(db: Session) -> str:
    today = datetime.now().strftime("%Y%m%d")
    prefix = f"MA-{today}-"
    row = db.execute(
        select(AppointmentEntity.appointment_code)
        .where(AppointmentEntity.appointment_code.like(f"{prefix}%"))
        .order_by(AppointmentEntity.id.desc())
        .limit(1)
    ).scalar_one_or_none()
    if not row:
        seq = 1
    else:
        try:
            seq = int(str(row).split("-")[-1]) + 1
        except (ValueError, IndexError):
            seq = 1
    return f"{prefix}{seq:04d}"


def create_appointment(
    *,
    db: Session,
    full_name: str,
    dob: str | None,
    gender: str | None,
    phone: str,
    email: str | None,
    id_number: str | None,
    insurance_id: str | None,
    address: str | None,
    doctor_id: int,
    department_id: int,
    scheduled_at: str,
    symptoms: str | None,
    predicted_diseases: str | None,
    severity: str,
) -> dict[str, Any]:
    scheduled_at_dt = _parse_scheduled_at(scheduled_at)
    end_dt = scheduled_at_dt + timedelta(hours=1)
    code = ""
    appt_id = 0
    try:
        patient = PatientEntity(
            full_name=full_name,
            dob=datetime.strptime(dob, "%Y-%m-%d").date() if dob else None,
            gender=gender,
            phone=phone,
            email=email,
            id_number=id_number,
            insurance_id=insurance_id,
            address=address,
        )
        db.add(patient)
        db.flush()

        code = _next_appointment_code(db)
        diseases_json = predicted_diseases
        if diseases_json and not diseases_json.strip().startswith("["):
            diseases_json = json.dumps([{"name": predicted_diseases}], ensure_ascii=False)

        appointment = AppointmentEntity(
            appointment_code=code,
            patient_id=int(patient.id),
            doctor_id=doctor_id,
            department_id=department_id,
            symptoms=symptoms,
            predicted_diseases=diseases_json,
            severity=severity,
            scheduled_at=scheduled_at_dt,
            status="CONFIRMED",
            notes=None,
        )
        db.add(appointment)
        db.flush()
        appt_id = int(appointment.id)

        clash = db.execute(
            select(MedicalExaminationScheduleEntity.id)
            .where(MedicalExaminationScheduleEntity.doctor_id == doctor_id)
            .where(MedicalExaminationScheduleEntity.start_datetime < end_dt)
            .where(MedicalExaminationScheduleEntity.end_datetime > scheduled_at_dt)
            .limit(1)
        ).first()
        if clash:
            raise SlotUnavailableError("slot_unavailable")

        db.add(
            MedicalExaminationScheduleEntity(
                doctor_id=doctor_id,
                start_datetime=scheduled_at_dt,
                end_datetime=end_dt,
                status="BOOKED",
                appointment_id=appt_id,
            )
        )
        db.commit()
    except Exception:
        db.rollback()
        raise

    row = get_appointment_public(db, appt_id)
    return row or {"id": appt_id, "appointment_code": code}


def get_appointment_public(db: Session, appointment_id: int) -> dict[str, Any] | None:
    row = db.execute(
        select(
            AppointmentEntity.id,
            AppointmentEntity.appointment_code,
            AppointmentEntity.scheduled_at,
            AppointmentEntity.severity,
            AppointmentEntity.symptoms,
            AppointmentEntity.status,
            PatientEntity.full_name.label("patient_name"),
            PatientEntity.phone.label("patient_phone"),
            DoctorEntity.full_name.label("doctor_name"),
            DepartmentEntity.name.label("department_name"),
        )
        .join(PatientEntity, PatientEntity.id == AppointmentEntity.patient_id)
        .join(DoctorEntity, DoctorEntity.id == AppointmentEntity.doctor_id)
        .join(DepartmentEntity, DepartmentEntity.id == AppointmentEntity.department_id)
        .where(AppointmentEntity.id == appointment_id)
    ).first()
    if not row:
        return None
    return {
        "id": row.id,
        "appointment_code": row.appointment_code,
        "scheduled_at": row.scheduled_at,
        "severity": row.severity,
        "symptoms": row.symptoms,
        "status": row.status,
        "patient_name": row.patient_name,
        "patient_phone": row.patient_phone,
        "doctor_name": row.doctor_name,
        "department_name": row.department_name,
    }
