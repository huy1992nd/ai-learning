from __future__ import annotations

import logging
from functools import lru_cache
from typing import Any

from app.core.config import get_settings
from app.services.ai.embeddings.department_index import get_chroma_client

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _collection_name() -> str:
    return get_settings().kb_collection_name.strip() or "medassist_knowledge_v1"


def get_kb_collection():
    """Persistent Chroma collection for KB chunks (cosine)."""
    settings = get_settings()
    client = get_chroma_client()
    name = _collection_name()
    try:
        return client.get_collection(name)
    except Exception:
        return client.create_collection(
            name=name,
            metadata={
                "hnsw:space": "cosine",
                "embedding_model": settings.openai_embedding_model,
            },
        )


def kb_delete_document_vectors(document_id: int) -> None:
    coll = get_kb_collection()
    try:
        coll.delete(where={"document_id": document_id})
    except Exception:
        logger.exception("Chroma delete failed for document_id=%s", document_id)


def kb_upsert_chunks(
    *,
    chunk_ids: list[int],
    embeddings: list[list[float]],
    documents: list[str],
    metadatas: list[dict[str, Any]],
) -> None:
    coll = get_kb_collection()
    chroma_ids = [f"kc-{cid}" for cid in chunk_ids]
    coll.upsert(
        ids=chroma_ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
    )


def kb_query(
    query_embedding: list[float],
    *,
    top_k: int,
    category: str | None,
    max_distance: float | None,
) -> tuple[list[dict[str, Any]], list[float]]:
    coll = get_kb_collection()
    kwargs: dict[str, Any] = {
        "query_embeddings": [query_embedding],
        "n_results": top_k,
        "include": ["documents", "distances", "metadatas"],
    }
    if category:
        kwargs["where"] = {"category": category}

    raw = coll.query(**kwargs)
    metas = (raw.get("metadatas") or [[]])[0]
    dists = (raw.get("distances") or [[]])[0]
    docs = (raw.get("documents") or [[]])[0]

    hits: list[dict[str, Any]] = []
    scores: list[float] = []
    for meta, dist, doc in zip(metas, dists, docs):
        if not meta:
            continue
        d = float(dist)
        if max_distance is not None and d > max_distance:
            continue
        hits.append(
            {
                "chunk_id": int(meta["chunk_id"]),
                "document_id": int(meta["document_id"]),
                "category": str(meta.get("category") or ""),
                "title": str(meta.get("title") or ""),
                "content": doc or "",
                "distance": d,
            },
        )
        scores.append(d)
    return hits, scores


def kb_collection_count() -> int:
    coll = get_kb_collection()
    try:
        return int(coll.count())
    except Exception:
        return 0


def kb_reset_collection() -> Any:
    settings = get_settings()
    client = get_chroma_client()
    name = _collection_name()
    try:
        client.delete_collection(name)
    except Exception:
        pass
    return client.create_collection(
        name=name,
        metadata={
            "hnsw:space": "cosine",
            "embedding_model": settings.openai_embedding_model,
        },
    )
