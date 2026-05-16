"""Lightweight SQLite migrations for KB tables (no Alembic)."""

from __future__ import annotations

import logging

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)


def apply_knowledge_documents_sqlite_patches(engine: Engine) -> None:
    """Align older `knowledge_documents` tables with current ORM (e.g. `content_text`)."""
    try:
        insp = inspect(engine)
        if "knowledge_documents" not in insp.get_table_names():
            return
        col_names = {c["name"] for c in insp.get_columns("knowledge_documents")}
        if "content_text" in col_names:
            return
        with engine.begin() as conn:
            conn.execute(
                text(
                    "ALTER TABLE knowledge_documents "
                    "ADD COLUMN content_text TEXT NOT NULL DEFAULT ''"
                ),
            )
        logger.info("SQLite: added knowledge_documents.content_text")
    except Exception:
        logger.exception("KB SQLite migration failed")
