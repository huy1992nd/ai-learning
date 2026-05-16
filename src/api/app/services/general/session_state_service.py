from __future__ import annotations

from app.core.medassist_session_state import (
    clear_medassist_state,
    try_get_medassist_state,
)
from app.core.session_language import clear_session_language
from app.core.session_store import get_session_store
from app.models.session.patient_info_response import PatientInfoResponse


def get_patient_info_draft(session_id: str) -> PatientInfoResponse | None:
    """Return the session-scoped patient draft used by the registration form."""
    state = try_get_medassist_state(session_id)
    if state is None:
        return None
    return PatientInfoResponse(
        session_id=session_id,
        patient_info=dict(state.patient_info),
        flow_stage=state.flow_stage,
        selected_slot_start=state.selected_slot_start,
        registration_link_sent=state.registration_link_sent,
    )


def clear_chat_session_context(session_id: str) -> dict[str, bool]:
    """Clear all in-memory chat context tied to a frontend session id."""
    return {
        "chat_history": get_session_store().clear(session_id),
        "medassist_state": clear_medassist_state(session_id),
        "language": clear_session_language(session_id),
    }


def clear_registration_draft(session_id: str) -> bool:
    """Clear only the registration draft/enrichment state after successful booking."""
    return clear_medassist_state(session_id)
