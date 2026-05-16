from __future__ import annotations

GENERAL_INTERNAL_ID = 4
EMERGENCY_DEPARTMENT_ID = 12
MEDICAL_MIN_SCORE = 75
BOOKING_MIN_SCORE = 70
MAX_TRIAGE_EXCHANGES = 3

# Keyword fallback triage (when embedding fails or as strong tie-breaker after LLM shortlist).
TRIAGE_KW_MIN_SCORE = 5
TRIAGE_KW_MIN_MARGIN = 2
TRIAGE_KW_STRONG_SCORE = 8
