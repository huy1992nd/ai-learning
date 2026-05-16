from __future__ import annotations

from pydantic import BaseModel, Field


class AppointmentCreateRequest(BaseModel):
    """UC-08 — payload from registration form (may differ from chat-collected draft)."""

    full_name: str = Field(..., min_length=3)
    date_of_birth: str | None = None
    gender: str | None = None
    phone: str
    email: str | None = None
    cccd: str | None = None
    bhyt: str | None = None
    address: str | None = None
    doctor_id: int
    department_id: int
    scheduled_at: str = Field(..., description="Naive local datetime YYYY-MM-DD HH:MM:SS")
    symptoms: str | None = None
    predicted_diseases: str | None = None
    severity: str = "MILD"
    session_id: str | None = Field(
        default=None,
        description="Optional chat session — cleared from server draft after successful booking.",
    )
