"""Per-session detected language (SRS UC-01 FR-01-02). Uses same TTL idea as chat SessionStore."""

from __future__ import annotations

import threading

from cachetools import TTLCache

from app.core.config import get_settings

_lock = threading.Lock()
_cache: TTLCache[str, str] | None = None


def _get_cache() -> TTLCache[str, str]:
    global _cache
    if _cache is None:
        settings = get_settings()
        _cache = TTLCache(maxsize=10_000, ttl=settings.session_ttl_seconds)
    return _cache


def get_session_language(session_id: str) -> str | None:
    with _lock:
        return _get_cache().get(session_id)


def resolve_stt_language(
    session_id: str, form_language: str | None = None
) -> str:
    """Ưu tiên cache theo session; nếu không, `language` từ form; cuối cùng `DEFAULT_STT_LANGUAGE`."""
    with _lock:
        cached = _get_cache().get(session_id)
    if cached and str(cached).strip():
        return str(cached).strip()
    if form_language and str(form_language).strip():
        return str(form_language).strip()
    d = (get_settings().default_stt_language or "vi").strip() or "vi"
    return d


def set_session_language(session_id: str, language_code: str) -> None:
    with _lock:
        _get_cache()[session_id] = language_code


def clear_session_language(session_id: str) -> bool:
    with _lock:
        return _get_cache().pop(session_id, None) is not None
