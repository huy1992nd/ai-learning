from __future__ import annotations

# Keep string values stable for compatibility with persisted/in-memory session state.
FLOW_MEDICAL_SCREEN = "medical_screen"
FLOW_DEPARTMENT_TRIAGE = "department_triage"
FLOW_AWAITING_BOOKING = "awaiting_booking"
FLOW_COLLECTING_PII = "collecting_pii"
FLOW_PII_DONE = "pii_done"
FLOW_THREAD_CLOSED = "thread_closed"
