from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.core.enumerations.knowledge_enum import KnowledgeDocStatus
from app.entities.knowledge_chunk import KnowledgeChunkEntity
from app.entities.knowledge_document import KnowledgeDocumentEntity
from app.entities.rag_query_log import RagQueryLogEntity


def _iso(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    return dt.isoformat()


def doc_to_public(row: KnowledgeDocumentEntity, *, content_text: str | None = None) -> dict[str, Any]:
    return {
        "id": row.id,
        "title": row.title,
        "category": row.category,
        "original_filename": row.original_filename,
        "file_path": row.file_path,
        "mime_type": row.mime_type,
        "status": row.status,
        "total_chunks": row.total_chunks,
        "metadata_json": row.metadata_json,
        "processing_error": row.processing_error,
        "uploaded_by": row.uploaded_by,
        "created_at": _iso(row.created_at),
        "updated_at": _iso(row.updated_at),
        "is_active": bool(row.is_active),
        "content_text": content_text,
    }


def _document_filters(
    *,
    active_only: bool,
    category: str | None,
    status: str | None,
    q: str | None,
) -> list[Any]:
    crit: list[Any] = []
    if active_only:
        crit.append(KnowledgeDocumentEntity.is_active == 1)
    if category:
        crit.append(KnowledgeDocumentEntity.category == category)
    if status:
        crit.append(KnowledgeDocumentEntity.status == status)
    if q and q.strip():
        like = f"%{q.strip()}%"
        crit.append(
            (KnowledgeDocumentEntity.title.ilike(like))
            | (KnowledgeDocumentEntity.original_filename.ilike(like)),
        )
    return crit


def list_documents(
    db: Session,
    *,
    page: int,
    page_size: int,
    q: str | None,
    category: str | None,
    status: str | None,
    active_only: bool = True,
) -> tuple[list[KnowledgeDocumentEntity], int]:
    crit = _document_filters(
        active_only=active_only,
        category=category,
        status=status,
        q=q,
    )
    count_stmt = select(func.count()).select_from(KnowledgeDocumentEntity).where(*crit)
    total = int(db.execute(count_stmt).scalar_one())

    stmt = select(KnowledgeDocumentEntity).where(*crit).order_by(KnowledgeDocumentEntity.id.desc())
    offset = max(page - 1, 0) * page_size
    stmt = stmt.offset(offset).limit(page_size)
    rows = list(db.execute(stmt).scalars().all())
    return rows, total


def get_document(db: Session, doc_id: int) -> KnowledgeDocumentEntity | None:
    return db.get(KnowledgeDocumentEntity, doc_id)


def create_document(
    db: Session,
    *,
    title: str,
    category: str,
    original_filename: str,
    file_path: str | None,
    mime_type: str | None,
    uploaded_by: str | None,
    metadata_json: str | None = None,
    content_text: str = "",
) -> KnowledgeDocumentEntity:
    row = KnowledgeDocumentEntity(
        title=title,
        category=category,
        original_filename=original_filename,
        content_text=content_text or "",
        file_path=file_path,
        mime_type=mime_type,
        status=KnowledgeDocStatus.PENDING.value,
        total_chunks=0,
        metadata_json=metadata_json,
        uploaded_by=uploaded_by,
        is_active=1,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def patch_document(
    db: Session,
    row: KnowledgeDocumentEntity,
    *,
    title: str | None,
    category: str | None,
    is_active: bool | None,
) -> KnowledgeDocumentEntity:
    if title is not None:
        row.title = title
    if category is not None:
        row.category = category
    if is_active is not None:
        row.is_active = 1 if is_active else 0
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def update_document_status(
    db: Session,
    doc_id: int,
    *,
    status: str,
    processing_error: str | None = None,
    total_chunks: int | None = None,
) -> None:
    row = db.get(KnowledgeDocumentEntity, doc_id)
    if not row:
        return
    row.status = status
    if processing_error is not None:
        row.processing_error = processing_error
    if total_chunks is not None:
        row.total_chunks = total_chunks
    db.add(row)
    db.commit()


def delete_chunks_for_document(db: Session, document_id: int) -> None:
    db.execute(
        delete(KnowledgeChunkEntity).where(KnowledgeChunkEntity.document_id == document_id),
    )
    db.commit()


def insert_chunks(
    db: Session,
    document_id: int,
    chunks: list[tuple[int, str, int]],
) -> list[KnowledgeChunkEntity]:
    """chunks: list of (chunk_index, content, token_count)."""
    out: list[KnowledgeChunkEntity] = []
    for idx, content, tc in chunks:
        ent = KnowledgeChunkEntity(
            document_id=document_id,
            chunk_index=idx,
            content=content,
            token_count=tc,
            embedding_status="PENDING",
        )
        db.add(ent)
        out.append(ent)
    db.commit()
    for e in out:
        db.refresh(e)
    return out


def update_chunk_embedding(
    db: Session,
    chunk_id: int,
    *,
    embedding_status: str,
    vector_id: str | None,
) -> None:
    row = db.get(KnowledgeChunkEntity, chunk_id)
    if not row:
        return
    row.embedding_status = embedding_status
    row.vector_id = vector_id
    db.add(row)
    db.commit()


def list_chunks_for_document(db: Session, document_id: int) -> list[KnowledgeChunkEntity]:
    stmt = (
        select(KnowledgeChunkEntity)
        .where(KnowledgeChunkEntity.document_id == document_id)
        .order_by(KnowledgeChunkEntity.chunk_index.asc())
    )
    return list(db.execute(stmt).scalars().all())


def count_completed_documents(db: Session) -> int:
    stmt = (
        select(func.count())
        .select_from(KnowledgeDocumentEntity)
        .where(
            KnowledgeDocumentEntity.status == KnowledgeDocStatus.COMPLETED.value,
            KnowledgeDocumentEntity.is_active == 1,
        )
    )
    return int(db.execute(stmt).scalar_one())


def insert_rag_log(
    db: Session,
    *,
    session_id: str | None,
    query_text: str,
    retrieved_chunk_ids: list[int],
    retrieved_scores: list[float],
    final_response: str,
    latency_ms: int,
) -> None:
    import json

    row = RagQueryLogEntity(
        session_id=session_id,
        query_text=query_text,
        retrieved_chunk_ids=json.dumps(retrieved_chunk_ids),
        retrieved_scores=json.dumps(retrieved_scores),
        final_response=final_response,
        latency_ms=latency_ms,
    )
    db.add(row)
    db.commit()


def list_rag_logs(db: Session, *, limit: int = 100, offset: int = 0) -> list[RagQueryLogEntity]:
    stmt = (
        select(RagQueryLogEntity)
        .order_by(RagQueryLogEntity.id.desc())
        .offset(offset)
        .limit(limit)
    )
    return list(db.execute(stmt).scalars().all())
