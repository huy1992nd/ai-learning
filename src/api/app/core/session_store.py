from __future__ import annotations

import threading
from typing import Literal, TypedDict

from cachetools import TTLCache

from app.core.config import get_settings


Role = Literal["system", "user", "assistant"]


class ChatMessage(TypedDict):
    role: Role
    content: str


class SessionStore:
    """In-memory chat history store keyed by session_id with TTL-based eviction.

    Each session's history excludes the system prompt (which is prepended at
    request time) and is trimmed to keep only the most recent N messages so
    the prompt size stays bounded.
    """

    def __init__(self, ttl_seconds: int, max_messages: int, maxsize: int = 10_000) -> None:
        self._cache: TTLCache[str, list[ChatMessage]] = TTLCache(
            maxsize=maxsize, ttl=ttl_seconds
        )
        self._max_messages = max_messages
        self._lock = threading.Lock()

    def get_history(self, session_id: str) -> list[ChatMessage]:
        with self._lock:
            return list(self._cache.get(session_id, []))

    def append(self, session_id: str, role: Role, content: str) -> None:
        with self._lock:
            history = list(self._cache.get(session_id, []))
            history.append({"role": role, "content": content})
            if len(history) > self._max_messages:
                history = history[-self._max_messages:]
            self._cache[session_id] = history

    def extend(self, session_id: str, messages: list[ChatMessage]) -> None:
        with self._lock:
            history = list(self._cache.get(session_id, []))
            history.extend(messages)
            if len(history) > self._max_messages:
                history = history[-self._max_messages:]
            self._cache[session_id] = history

    def clear(self, session_id: str) -> bool:
        with self._lock:
            return self._cache.pop(session_id, None) is not None


_store: SessionStore | None = None


def get_session_store() -> SessionStore:
    global _store
    if _store is None:
        settings = get_settings()
        _store = SessionStore(
            ttl_seconds=settings.session_ttl_seconds,
            max_messages=settings.session_max_messages,
        )
    return _store
