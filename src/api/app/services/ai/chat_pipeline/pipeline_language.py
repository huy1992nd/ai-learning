"""Resolve MedAssist chat pipeline language (en/vi/jp) for deterministic strings (booking, PII, guards)."""

from __future__ import annotations

import logging
import re

from langdetect import LangDetectException, detect

from app.core.enumerations.languages_enum import Languages
from app.core.session_language import get_session_language, set_session_language

logger = logging.getLogger(__name__)

_HIRA_KATA_RE = re.compile(r"[\u3040-\u30ff]")


def _has_japanese_kana(text: str) -> bool:
    return bool(_HIRA_KATA_RE.search(text))


def _canonical_language_tag(tag: str | None) -> Languages | None:
    """Map API / ISO / UI strings to pipeline Languages."""
    if not tag or not str(tag).strip():
        return None
    t = str(tag).lower().strip().replace("-", "_").split("_")[0]
    if t in ("en", "english"):
        return "en"
    if t in ("vi", "vietnamese"):
        return "vi"
    if t in ("jp", "ja", "japanese"):
        return "jp"
    return None


def _canonical_from_langdetect(code: str) -> Languages | None:
    c = (code or "").lower().strip()
    if c == "en":
        return "en"
    if c == "vi":
        return "vi"
    if c in ("ja", "jp"):
        return "jp"
    return None


def resolve_pipeline_language(
    session_id: str,
    user_message: str,
    *,
    explicit_language: str | None = None,
) -> Languages:
    """
    Order: explicit client locale → cached session language → script/heuristic → langdetect.

    Updates session language cache when an explicit or detected value is chosen so short
    follow-ups (e.g. \"yes\") stay in the same language as the first substantive message.
    """
    explicit = _canonical_language_tag(explicit_language)
    if explicit:
        set_session_language(session_id, explicit)
        return explicit

    cached = _canonical_language_tag(get_session_language(session_id))
    if cached:
        return cached

    text = (user_message or "").strip()
    if _has_japanese_kana(text):
        set_session_language(session_id, "jp")
        return "jp"

    if len(text) >= 2:
        try:
            raw = detect(text)
            mapped = _canonical_from_langdetect(raw)
            if mapped:
                set_session_language(session_id, mapped)
                return mapped
        except LangDetectException:
            logger.debug("langdetect skipped for session %s (short or ambiguous text)", session_id)
        except Exception:
            logger.warning("language detection failed for session %s", session_id, exc_info=True)

    # Product default when nothing else applies (SafeDict templates still have vi entries).
    return "vi"
