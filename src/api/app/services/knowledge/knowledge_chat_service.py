from __future__ import annotations

import logging
import time
from typing import Any, AsyncIterator

from app.core.config import get_settings
from app.db.orm import SessionLocal
from app.services.ai.azure_client import get_async_openai_client, openai_configured
from app.services.ai.embeddings.openai_embedder import embed_texts
from app.services.crud import knowledge_repository as kr
from app.services.knowledge.kb_chroma import kb_query

logger = logging.getLogger(__name__)


async def stream_knowledge_chat(session_id: str, message: str) -> AsyncIterator[str | dict[str, Any]]:
    """
    Yields plain strings (answer tokens) for SSE framing by the route,
    or dict events {"event":..., "data":...} for rare side-channel events.
    """
    settings = get_settings()
    t0 = time.perf_counter()

    if not openai_configured():
        yield {"event": "error", "data": {"message": "OpenAI chat is not configured"}}
        return

    if not settings.embedding_configured():
        yield {"event": "error", "data": {"message": "Embedding API is not configured"}}
        return

    try:
        query_emb = (await embed_texts([message]))[0]
        hits, dists = kb_query(
            query_emb,
            top_k=settings.rag_retrieval_top_k,
            category=None,
            max_distance=settings.rag_similarity_max_distance,
        )
    except Exception as exc:
        logger.exception("KB retrieval failed")
        yield {"event": "error", "data": {"message": str(exc)}}
        return

    chunk_ids = [int(h["chunk_id"]) for h in hits]
    context_blocks = []
    for h in hits:
        context_blocks.append(
            f"[document_id={h['document_id']} chunk_id={h['chunk_id']}]\n{h['content']}",
        )
    context = "\n\n---\n\n".join(context_blocks) if context_blocks else "(no matching chunks)"

    system = (
        "You are a medical knowledge assistant. Answer using ONLY the CONTEXT excerpts below. "
        "These are encyclopedic reference snippets, not patient-specific facts. "
        "If context is insufficient, say clearly that the knowledge base does not contain enough detail — "
        "do not invent clinical facts. "
        "Do NOT diagnose the user, do NOT prescribe treatment, and do NOT offer appointment booking — "
        "those belong to the main MedAssist chat flow.\n\n"
        f"CONTEXT:\n{context}\n\n"
        f"Disclaimer (communicate when relevant): {settings.medical_disclaimer}"
    )

    client = get_async_openai_client()
    stream = await client.chat.completions.create(
        model=settings.openai_deployment,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": message},
        ],
        stream=True,
        temperature=0.2,
    )

    full_response: list[str] = []
    async for part in stream:
        delta = part.choices[0].delta.content or ""
        if delta:
            full_response.append(delta)
            yield delta

    latency_ms = int((time.perf_counter() - t0) * 1000)
    text = "".join(full_response)
    try:
        with SessionLocal() as db:
            kr.insert_rag_log(
                db,
                session_id=session_id,
                query_text=message,
                retrieved_chunk_ids=chunk_ids,
                retrieved_scores=[float(x) for x in dists],
                final_response=text,
                latency_ms=latency_ms,
            )
    except Exception:
        logger.exception("Failed to persist rag_query_log")
