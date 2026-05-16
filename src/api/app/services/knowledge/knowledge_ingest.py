from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path

from openai import APIConnectionError, APIStatusError, APITimeoutError, AuthenticationError, RateLimitError

from app.core.config import get_settings
from app.core.enumerations.knowledge_enum import ChunkEmbeddingStatus, KnowledgeDocStatus
from app.db.orm import SessionLocal
from app.services.ai.embeddings.openai_embedder import embed_texts
from app.services.crud import knowledge_repository as kr
from app.services.knowledge.chunking import chunk_text_by_tokens
from app.services.knowledge.kb_chroma import kb_delete_document_vectors, kb_upsert_chunks
from app.services.knowledge.text_extract import TextExtractError, extract_text_from_file

logger = logging.getLogger(__name__)


def _api_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _format_embedding_failure(exc: Exception) -> str:
    """Short message stored on the document for admins (full detail stays in logs)."""
    if isinstance(exc, APIConnectionError):
        return (
            "Embedding API: connection failed (no route to host, TLS, or wrong URL). "
            "Check network/VPN and .env: OPENAI_EMBEDDING_ENDPOINT (or OPENAI_ENDPOINT), "
            "OPENAI_EMBEDDING_API_KEY (or OPENAI_API_KEY), deployment name OPENAI_EMBEDDING_MODEL."
        )
    if isinstance(exc, APITimeoutError):
        return "Embedding API: request timed out. Retry later or increase client timeout."
    if isinstance(exc, AuthenticationError):
        return "Embedding API: authentication failed. Check OPENAI_EMBEDDING_API_KEY / OPENAI_API_KEY."
    if isinstance(exc, RateLimitError):
        return "Embedding API: rate limited. Retry later."
    if isinstance(exc, APIStatusError):
        return f"Embedding API HTTP error: {exc.status_code} — {str(exc)[:400]}"
    return f"Embedding / ingest error: {exc!s}"[:2000]


def _resolve_upload_path(rel: str | None) -> Path | None:
    if not rel:
        return None
    p = Path(rel)
    if p.is_absolute():
        return p
    return (_api_root() / p).resolve()


def run_ingest_sync(document_id: int) -> None:
    """Background task: extract → chunk → embed → Chroma upsert."""
    settings = get_settings()
    with SessionLocal() as db:
        doc = kr.get_document(db, document_id)
        if not doc or not doc.is_active:
            return

        kr.update_document_status(
            db,
            document_id,
            status=KnowledgeDocStatus.PROCESSING.value,
            processing_error=None,
        )

        text = ""
        try:
            if (doc.content_text or "").strip():
                text = doc.content_text.strip()
            elif doc.file_path:
                path = _resolve_upload_path(doc.file_path)
                if not path or not path.is_file():
                    raise TextExtractError("Uploaded file is missing on disk")
                text = extract_text_from_file(path, doc.mime_type)
            else:
                text = ""
                if doc.metadata_json:
                    try:
                        meta = json.loads(doc.metadata_json)
                        if isinstance(meta, dict):
                            text = str(meta.get("inline_content") or "")
                    except json.JSONDecodeError:
                        text = ""

            if not (text or "").strip():
                raise TextExtractError("No text content to index")

            pairs = chunk_text_by_tokens(text)
            if not pairs:
                raise TextExtractError("Chunking produced no segments")

            kr.delete_chunks_for_document(db, document_id)
            kb_delete_document_vectors(document_id)

            chunk_rows = kr.insert_chunks(
                db,
                document_id,
                [(i, c, tc) for i, (c, tc) in enumerate(pairs)],
            )

            if not settings.embedding_configured():
                kr.update_document_status(
                    db,
                    document_id,
                    status=KnowledgeDocStatus.FAILED.value,
                    processing_error="Embedding API is not configured",
                    total_chunks=len(chunk_rows),
                )
                return

            all_contents = [c.content for c in chunk_rows]
            all_embeddings = asyncio.run(embed_texts(all_contents))
            batch_size = 16
            for i in range(0, len(chunk_rows), batch_size):
                batch = chunk_rows[i : i + batch_size]
                embeddings = all_embeddings[i : i + batch_size]
                contents = [c.content for c in batch]
                metadatas = [
                    {
                        "chunk_id": c.id,
                        "document_id": document_id,
                        "category": doc.category,
                        "title": doc.title[:512],
                    }
                    for c in batch
                ]
                kb_upsert_chunks(
                    chunk_ids=[c.id for c in batch],
                    embeddings=embeddings,
                    documents=contents,
                    metadatas=metadatas,
                )
                for c in batch:
                    kr.update_chunk_embedding(
                        db,
                        c.id,
                        embedding_status=ChunkEmbeddingStatus.COMPLETED.value,
                        vector_id=f"kc-{c.id}",
                    )

            kr.update_document_status(
                db,
                document_id,
                status=KnowledgeDocStatus.COMPLETED.value,
                total_chunks=len(chunk_rows),
            )
        except Exception as exc:
            if isinstance(
                exc,
                (APIConnectionError, APITimeoutError, AuthenticationError, RateLimitError, APIStatusError),
            ):
                logger.warning("Ingest failed for document %s: %s", document_id, exc, exc_info=True)
            else:
                logger.exception("Ingest failed for document %s", document_id)
            msg = (
                _format_embedding_failure(exc)
                if isinstance(
                    exc,
                    (APIConnectionError, APITimeoutError, AuthenticationError, RateLimitError, APIStatusError),
                )
                else str(exc)[:2000]
            )
            kr.update_document_status(
                db,
                document_id,
                status=KnowledgeDocStatus.FAILED.value,
                processing_error=msg,
            )


def schedule_ingest(document_id: int) -> None:
    """Fire-and-forget from FastAPI BackgroundTasks."""
    run_ingest_sync(document_id)
