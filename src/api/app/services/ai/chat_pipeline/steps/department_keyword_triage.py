"""Rule-based department scoring when embedding triage is unavailable or ambiguous."""

from __future__ import annotations

import re
import unicodedata
from typing import Any

from app.services.ai.chat_pipeline.steps.constants import (
    EMERGENCY_DEPARTMENT_ID,
    TRIAGE_KW_MIN_MARGIN,
    TRIAGE_KW_MIN_SCORE,
    TRIAGE_KW_STRONG_SCORE,
)

_SYMPTOMS_PHRASE_SCORE = 5
_SYMPTOMS_TERM_SCORE = 3
_COMMON_DISEASE_SCORE = 3
_SPECIALTY_NAME_SCORE = 2
_DESCRIPTION_HIT_SCORE = 1
_DESCRIPTION_SCORE_CAP = 4

_VI_D_MARK = str.maketrans({"đ": "d", "Đ": "d"})

# Normalized (accent-stripped, lower) emergency phrases — must match emergency seed keywords.
_EMERGENCY_PHRASES_NORM: tuple[str, ...] = (
    "dau nguc du doi",
    "severe chest pain",
    "kho tho cap",
    "severe shortness of breath",
    "bat tinh",
    "loss of consciousness",
    "chay mau nhieu",
    "heavy bleeding",
    "anaphylaxis",
    "phan ve",
    "major trauma",
    "chan thuong nang",
)

# Extra phrases (normalized) boosting Pulmonology when embedding misses subtle wording.
_PULMONOLOGY_EXTRA_NORM: tuple[str, ...] = (
    "ho ve dem",
    "ho nhieu ve dem",
    "ho nhieu ve ban dem",
    "tho gap",
    "dom it",
    "dam it",
)

# Cardiology hint when exertional dyspnea is described without emergency wording.
_CARDIO_EXERTION_HINTS_NORM: tuple[str, ...] = (
    "leo cau thang",
    "gang suc",
    "van dong manh",
    "exertion",
    "climbing stairs",
)


def normalize_for_match(text: str) -> str:
    """Lowercase, strip Vietnamese accents, fold đ→d for robust substring match."""
    t = text.translate(_VI_D_MARK).lower()
    nfkd = unicodedata.normalize("NFKD", t)
    base = "".join(c for c in nfkd if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", base).strip()


def _csv_chunks(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [x.strip() for x in raw.split(",") if x.strip()]


def _description_chunks(raw: str | None) -> list[str]:
    if not raw:
        return []
    parts = re.split(r"[.;]", raw)
    out: list[str] = []
    for p in parts:
        for sub in p.split(","):
            s = sub.strip()
            if len(s) >= 4:
                out.append(s)
    return out


def _symptoms_weight(segment: str) -> int:
    s = segment.strip()
    return _SYMPTOMS_PHRASE_SCORE if (" " in s or len(s) > 10) else _SYMPTOMS_TERM_SCORE


def score_department_keywords(dept: dict[str, Any], user_normalized: str) -> int:
    """Accumulate match score for one department row from cached catalog dict."""
    score = 0
    did = int(dept["id"])

    for seg in _csv_chunks(dept.get("symptoms_keywords")):
        sn = normalize_for_match(seg)
        if len(sn) < 2:
            continue
        if sn in user_normalized:
            score += _symptoms_weight(seg)

    for seg in _csv_chunks(dept.get("common_diseases")):
        sn = normalize_for_match(seg)
        if len(sn) >= 3 and sn in user_normalized:
            score += _COMMON_DISEASE_SCORE

    for label in (dept.get("specialty"), dept.get("name")):
        if not label:
            continue
        sn = normalize_for_match(label)
        if len(sn) >= 4 and sn in user_normalized:
            score += _SPECIALTY_NAME_SCORE

    desc_hits = 0
    for chunk in _description_chunks(dept.get("description")):
        cn = normalize_for_match(chunk)
        if len(cn) >= 5 and cn in user_normalized:
            score += _DESCRIPTION_HIT_SCORE
            desc_hits += 1
            if desc_hits * _DESCRIPTION_HIT_SCORE >= _DESCRIPTION_SCORE_CAP:
                break

    if did == 3:
        for phrase in _PULMONOLOGY_EXTRA_NORM:
            if phrase in user_normalized:
                score += _SYMPTOMS_PHRASE_SCORE

    # Cardiology vs Pulmonology: dyspnea on exertion pattern (non-emergency).
    if did == 1:
        if any(h in user_normalized for h in _CARDIO_EXERTION_HINTS_NORM):
            if "dau nguc" in user_normalized or "chest pain" in user_normalized:
                score += _SYMPTOMS_PHRASE_SCORE
            if "kho tho" in user_normalized or "shortness of breath" in user_normalized:
                score += _SYMPTOMS_TERM_SCORE

    return score


def match_emergency_department(user_normalized: str, valid_ids: set[int]) -> int | None:
    if EMERGENCY_DEPARTMENT_ID not in valid_ids:
        return None
    for phrase in _EMERGENCY_PHRASES_NORM:
        if phrase in user_normalized:
            return EMERGENCY_DEPARTMENT_ID
    return None


def rank_departments_by_keywords(
    departments: list[dict[str, Any]], user_message: str
) -> list[tuple[int, int]]:
    user_n = normalize_for_match(user_message)
    scored: list[tuple[int, int]] = []
    for d in departments:
        sid = int(d["id"])
        sc = score_department_keywords(d, user_n)
        scored.append((sid, sc))
    scored.sort(key=lambda x: (-x[1], x[0]))
    return scored


def pick_department_from_scores(
    ranked: list[tuple[int, int]],
    *,
    strong_only: bool,
) -> int | None:
    """Return department id if confidence rules met; otherwise None."""
    if not ranked:
        return None
    top_id, top_score = ranked[0]
    second_score = ranked[1][1] if len(ranked) > 1 else 0
    margin = top_score - second_score

    if strong_only:
        if top_score >= TRIAGE_KW_STRONG_SCORE and margin >= TRIAGE_KW_MIN_MARGIN:
            return top_id
        return None

    if top_score >= TRIAGE_KW_STRONG_SCORE and top_score > second_score:
        return top_id
    if top_score >= TRIAGE_KW_MIN_SCORE and margin >= TRIAGE_KW_MIN_MARGIN:
        return top_id
    return None


def resolve_department_by_keywords(
    departments: list[dict[str, Any]],
    user_message: str,
    valid_ids: set[int],
    *,
    strong_only: bool,
) -> int | None:
    """Embedding-free triage: emergency override, then keyword scores."""
    user_n = normalize_for_match(user_message)
    emerg = match_emergency_department(user_n, valid_ids)
    if emerg is not None:
        return emerg
    ranked = rank_departments_by_keywords(departments, user_message)
    # Only consider departments present in DB snapshot.
    ranked = [(i, s) for i, s in ranked if i in valid_ids]
    if not ranked:
        return None
    return pick_department_from_scores(ranked, strong_only=strong_only)
