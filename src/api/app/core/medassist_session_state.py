"""Per-session MedAssist state. Cleared with chat session."""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Any

from cachetools import TTLCache

from app.core.config import get_settings
from app.services.ai.chat_pipeline.stages import FLOW_MEDICAL_SCREEN

_lock = threading.Lock()
_cache: TTLCache[str, "MedAssistSessionState"] | None = None


@dataclass
class MedAssistSessionState:
    # UC-04 / UC-06 — primary suggestion (first catalog match)
    primary_department_id: int | None = None
    primary_doctor_id: int | None = None
    # UC-06 — chosen slot (local VN wall time, naive ISO string "YYYY-MM-DD HH:MM:SS")
    selected_slot_start: str | None = None
    # UC-05 — session-scoped patient draft (BR-13); expires with this cache entry
    patient_info: dict[str, Any] = field(default_factory=dict)
    # healthcare v2 only
    # triaging | ... | medical_screen | department_triage | awaiting_booking |
    # collecting_pii | pii_done | thread_closed
    flow_stage: str = FLOW_MEDICAL_SCREEN
    registration_link_sent: bool = False
    # --- Healthcare chat v2 ---
    thread_closed: bool = False
    close_reason: str | None = None
    user_message_count: int = 0
    medical_screen_passed: bool = False
    # Rounds in department triage without resolution (force General Internal at >= 3)
    triage_exchange_count: int = 0
    resolved_department_id: int | None = None
    booking_prompt_shown: bool = False
    awaiting_booking_response: bool = False
    appointment_setup_event_sent: bool = False


def _get_cache() -> TTLCache[str, MedAssistSessionState]:
    global _cache
    if _cache is None:
        settings = get_settings()
        _cache = TTLCache(maxsize=10_000, ttl=settings.session_ttl_seconds)
    return _cache


def try_get_medassist_state(session_id: str) -> MedAssistSessionState | None:
    """Return state if session already has an entry; do **not** create a new one."""
    with _lock:
        return _get_cache().get(session_id)


def get_medassist_state(session_id: str) -> MedAssistSessionState:
    with _lock:
        c = _get_cache()
        if session_id not in c:
            c[session_id] = MedAssistSessionState()
        return c[session_id]


def clear_medassist_state(session_id: str) -> bool:
    with _lock:
        return _get_cache().pop(session_id, None) is not None
