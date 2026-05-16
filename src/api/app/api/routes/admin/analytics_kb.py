"""SRS v3 UC-18 — Knowledge Base analytics (admin)."""

from __future__ import annotations

import json
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query

from app.api.deps import require_roles
from app.db.orm import SessionLocal
from app.services.crud import knowledge_repository as kr

router = APIRouter(tags=["admin"])

AdminDep = Annotated[dict, Depends(require_roles("ADMIN"))]


def _log_to_dict(row: Any) -> dict[str, Any]:
    return {
        "id": row.id,
        "session_id": row.session_id,
        "query_text": row.query_text,
        "retrieved_chunk_ids": json.loads(row.retrieved_chunk_ids or "[]"),
        "retrieved_scores": json.loads(row.retrieved_scores or "[]"),
        "final_response": row.final_response,
        "latency_ms": row.latency_ms,
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }


@router.get("/admin/analytics/rag-queries", summary="Recent RAG query logs")
def analytics_rag_queries(
    _: AdminDep,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> list[dict[str, Any]]:
    with SessionLocal() as db:
        rows = kr.list_rag_logs(db, limit=limit, offset=offset)
    return [_log_to_dict(r) for r in rows]


@router.get("/admin/analytics/knowledge-gaps", summary="Queries with weak / empty retrieval")
def analytics_knowledge_gaps(_: AdminDep, limit: int = Query(50, ge=1, le=500)) -> list[dict[str, Any]]:
    with SessionLocal() as db:
        rows = kr.list_rag_logs(db, limit=500, offset=0)
    gaps: list[dict[str, Any]] = []
    for r in rows:
        try:
            ids = json.loads(r.retrieved_chunk_ids or "[]")
        except json.JSONDecodeError:
            ids = []
        if not ids:
            gaps.append(_log_to_dict(r))
        if len(gaps) >= limit:
            break
    return gaps
