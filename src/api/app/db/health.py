from __future__ import annotations

from typing import Any

from sqlalchemy import text

from app.db.connection import resolve_sqlite_path
from app.db.orm import engine
from app.entities import TABLE_NAMES


def check_database_via_orm() -> dict[str, Any]:
    path = resolve_sqlite_path()
    if not path.is_file():
        return {
            "ok": False,
            "path": str(path),
            "error": "database_file_missing",
        }
    try:
        with engine.connect() as conn:
            existing_tables = set(
                conn.execute(
                    text("SELECT name FROM sqlite_master WHERE type = 'table'")
                ).scalars()
            )
    except Exception as exc:
        return {"ok": False, "path": str(path), "error": str(exc)}
    missing_tables = sorted(TABLE_NAMES - existing_tables)
    if missing_tables:
        return {
            "ok": False,
            "path": str(path),
            "error": "database_schema_missing",
            "missing_tables": missing_tables,
        }
    return {"ok": True, "path": str(path)}
