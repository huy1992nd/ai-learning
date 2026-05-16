from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class PatientInfoResponse(BaseModel):
    """UC-05 FR-05-05 — pre-fill payload for registration form."""

    session_id: str
    patient_info: dict[str, Any]
    flow_stage: str | None = None
    selected_slot_start: str | None = None
    registration_link_sent: bool = False
