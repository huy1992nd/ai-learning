"""Cached list of all departments (names + descriptions) for healthcare chat workflow."""

from __future__ import annotations

import threading
from typing import Any

import asyncio

from cachetools import TTLCache
from sqlalchemy.orm import Session

from app.db.orm import SessionLocal
from app.services.crud import clinical_repository

_lock = threading.Lock()
# One key "all" — TTL 5 minutes
_dept_cache: TTLCache[str, list[dict[str, Any]]] = TTLCache(maxsize=2, ttl=300)


def _load_from_db(db: Session) -> list[dict[str, Any]]:
    try:
        rows = clinical_repository.list_departments(db)
    except clinical_repository.DatabaseUnavailableError:
        return []
    return [
        {
            "id": d.id,
            "name": d.name,
            "description": d.description,
            "specialty": d.specialty,
            "symptoms_keywords": d.symptoms_keywords,
            "common_diseases": d.common_diseases,
        }
        for d in rows
    ]


def get_departments_cached(db: Session | None = None) -> list[dict[str, Any]]:
    """Return all departments; refresh from SQLite at most every 5 minutes."""
    key = "all"
    with _lock:
        if key in _dept_cache:
            return _dept_cache[key]
    if db is not None:
        data = _load_from_db(db)
    else:
        with SessionLocal() as local_db:
            data = _load_from_db(local_db)
    with _lock:
        _dept_cache[key] = data
    return data


def invalidate_departments_cache() -> None:
    with _lock:
        _dept_cache.clear()


async def get_departments_cached_async() -> list[dict[str, Any]]:
    return await asyncio.to_thread(get_departments_cached)
