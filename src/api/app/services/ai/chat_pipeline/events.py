from __future__ import annotations

THREAD_CLOSED_HINT = (
    "This thread was automatically closed by AI. Please open a new one if you need further support."
)


def thread_closed_event_data(reason: str) -> dict[str, object]:
    return {
        "event": "thread_closed",
        "data": {
            "reason": reason,
            "message": THREAD_CLOSED_HINT,
        },
    }


def appointment_ready_event(session_id: str) -> dict[str, object]:
    return {
        "event": "appointment",
        "data": {
            "appointmentSetupDone": True,
            "sessionId": session_id,
        },
    }
