"""UC-05 — session patient draft for pre-filled registration form."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.models.session.patient_info_response import PatientInfoResponse
from app.services.general.session_state_service import get_patient_info_draft

router = APIRouter(tags=["sessions"])


@router.get(
    "/sessions/{session_id}/patient-info",
    response_model=PatientInfoResponse,
    summary="Patient info draft (pre-fill)",
)
async def get_patient_info(session_id: str) -> PatientInfoResponse:
    draft = get_patient_info_draft(session_id)
    if draft is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or expired.",
        )
    return draft
