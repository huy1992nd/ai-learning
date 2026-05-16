"""SRS v3 UC-15 — Vector store admin APIs."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any

from fastapi import APIRouter, BackgroundTasks, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import select

from app.api.deps import require_roles
from app.core.config import get_settings
from app.db.orm import SessionLocal
from app.entities.knowledge_document import KnowledgeDocumentEntity
from app.models.knowledge.schemas import VectorSearchBody, VectorSearchHit
from app.services.ai.embeddings.department_index import _resolve_persist_dir
from app.services.ai.embeddings.openai_embedder import embed_texts
from app.services.crud import knowledge_repository as kr
from app.services.knowledge.kb_chroma import kb_collection_count, kb_query, kb_reset_collection
from app.services.knowledge.knowledge_ingest import run_ingest_sync

router = APIRouter(tags=["admin"])

AdminDep = Annotated[dict, Depends(require_roles("ADMIN"))]


def _completed_docs_count() -> int:
    with SessionLocal() as db:
        return kr.count_completed_documents(db)


def _dir_size(p: Path) -> int:
    total = 0
    if not p.exists():
        return 0
    for child in p.rglob("*"):
        if child.is_file():
            try:
                total += child.stat().st_size
            except OSError:
                continue
    return total


@router.get("/admin/vector-store/stats", summary="Vector store dashboard metrics")
def vector_store_stats(_: AdminDep) -> dict[str, Any]:
    settings = get_settings()
    persist = _resolve_persist_dir()
    return {
        "collection_name": settings.kb_collection_name,
        "vector_count": kb_collection_count(),
        "documents_completed": _completed_docs_count(),
        "persist_directory": str(persist),
        "approx_disk_bytes_chroma": _dir_size(persist),
        "embedding_model": settings.openai_embedding_model,
        "rag_retrieval_top_k": settings.rag_retrieval_top_k,
        "rag_similarity_max_distance": settings.rag_similarity_max_distance,
    }


@router.post("/admin/vector-store/search", response_model=list[VectorSearchHit])
async def vector_store_search(body: VectorSearchBody, _: AdminDep) -> list[VectorSearchHit]:
    settings = get_settings()
    if not settings.embedding_configured():
        return []
    emb = (await embed_texts([body.query]))[0]
    hits, _scores = kb_query(
        emb,
        top_k=body.top_k,
        category=body.category,
        max_distance=None,
    )
    out: list[VectorSearchHit] = []
    for h in hits:
        dist = float(h["distance"])
        sim = max(0.0, 1.0 - dist)
        out.append(
            VectorSearchHit(
                chunk_id=int(h["chunk_id"]),
                document_id=int(h["document_id"]),
                category=h["category"],
                title=h["title"],
                content=h["content"],
                distance=dist,
                similarity=sim,
            ),
        )
    return out


def _run_kb_rebuild() -> None:
    kb_reset_collection()
    with SessionLocal() as db:
        ids = list(
            db.execute(
                select(KnowledgeDocumentEntity.id).where(KnowledgeDocumentEntity.is_active == 1),
            ).scalars().all(),
        )
    for doc_id in ids:
        run_ingest_sync(int(doc_id))


@router.post(
    "/admin/vector-store/rebuild",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Drop KB collection and re-ingest all active documents",
)
def vector_store_rebuild(_: AdminDep, background_tasks: BackgroundTasks) -> JSONResponse:
    background_tasks.add_task(_run_kb_rebuild)
    return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content={"status": "accepted"})


@router.get("/admin/vector-store/config", summary="Expose KB / embedding configuration")
def vector_store_config(_: AdminDep) -> dict[str, Any]:
    settings = get_settings()
    return {
        "kb_collection_name": settings.kb_collection_name,
        "chroma_persist_dir": settings.chroma_persist_dir,
        "openai_embedding_model": settings.openai_embedding_model,
        "embedding_configured": settings.embedding_configured(),
        "rag_retrieval_top_k": settings.rag_retrieval_top_k,
        "rag_similarity_max_distance": settings.rag_similarity_max_distance,
        "kb_max_upload_mb": settings.kb_max_upload_mb,
        "rag_chunk_target_tokens": settings.rag_chunk_target_tokens,
        "rag_chunk_overlap_tokens": settings.rag_chunk_overlap_tokens,
    }
