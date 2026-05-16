from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class AppointmentPublic(BaseModel):
    model_config = {"extra": "allow"}

    id: int
    appointment_code: str
    scheduled_at: Any
    severity: str | None = None
    symptoms: str | None = None
    status: str | None = None
    patient_name: str | None = None
    patient_phone: str | None = None
    doctor_name: str | None = None
    department_name: str | None = None
