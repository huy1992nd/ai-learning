from __future__ import annotations

import asyncio
import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

import chromadb

from app.core.config import get_settings
from app.db.orm import SessionLocal
from app.services.ai.azure_client import get_async_openai_client, openai_configured
from app.services.ai.embeddings.openai_embedder import embed_texts
from app.services.crud import clinical_repository

logger = logging.getLogger(__name__)

COLLECTION_V2_NAME = "medassist_departments_v2"

_LANG_KEYS = ("vi", "en", "ja")


def _resolve_persist_dir() -> Path:
    settings = get_settings()
    raw = settings.chroma_persist_dir.strip()
    p = Path(raw)
    if p.is_absolute():
        return p
    api_root = Path(__file__).resolve().parents[4]
    return (api_root / p).resolve()


@lru_cache(maxsize=1)
def get_chroma_client():
    return chromadb.PersistentClient(path=str(_resolve_persist_dir()))


def _dept_to_dict(d: Any) -> dict[str, Any]:
    if hasattr(d, "model_dump"):
        return d.model_dump()
    return dict(d)


def _format_monolingual_doc(dept: dict[str, Any]) -> str:
    return (
        f"Name: {dept.get('name')}\n"
        f"Specialty: {dept.get('specialty')}\n"
        f"Description: {dept.get('description')}\n"
        f"Symptoms: {dept.get('symptoms_keywords')}\n"
        f"Common diseases: {dept.get('common_diseases')}"
    )


async def _translate_dept_docs_for_embedding(dept: dict[str, Any]) -> dict[str, str]:
    """Return embedding document strings for vi, en, ja. Uses LLM when configured."""
    if not openai_configured():
        mono = _format_monolingual_doc(dept)
        return {"vi": mono, "en": mono, "ja": mono}

    payload = {
        "name": dept.get("name"),
        "specialty": dept.get("specialty"),
        "description": dept.get("description"),
        "symptoms_keywords": dept.get("symptoms_keywords"),
        "common_diseases": dept.get("common_diseases"),
    }
    system = (
        "You prepare hospital department text for multilingual semantic search. "
        "Input is JSON with keys name, specialty, description, symptoms_keywords, common_diseases "
        "(values may be null). Output JSON only with keys vi, en, ja. "
        "Each value is one multi-line string using these labels translated into that language: "
        "Name, Specialty, Description, Symptoms, Common diseases — followed by the content in that language. "
        "If a field is missing, omit its line or use a short dash."
    )
    user = json.dumps(payload, ensure_ascii=False)
    client = get_async_openai_client()
    settings = get_settings()
    response = await client.chat.completions.create(
        model=settings.openai_deployment,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        response_format={"type": "json_object"},
        temperature=0.1,
    )
    raw = (response.choices[0].message.content or "").strip()
    data = json.loads(raw)
    out: dict[str, str] = {}
    for key in _LANG_KEYS:
        v = data.get(key)
        if not isinstance(v, str) or not v.strip():
            out[key] = _format_monolingual_doc(dept)
        else:
            out[key] = v.strip()
    return out


async def _ensure_v2_collection():
    settings = get_settings()
    client = get_chroma_client()
    try:
        return client.get_collection(COLLECTION_V2_NAME)
    except Exception:
        collection = client.create_collection(
            name=COLLECTION_V2_NAME,
            metadata={
                "hnsw:space": "cosine",
                "embedding_model": settings.openai_embedding_model,
            },
        )
        def _load_departments():
            with SessionLocal() as db:
                try:
                    return clinical_repository.list_departments(db)
                except clinical_repository.DatabaseUnavailableError:
                    return []

        depts = await asyncio.to_thread(_load_departments)
        for d in depts:
            try:
                await _upsert_department_into_collection(collection, _dept_to_dict(d))
            except Exception:
                logger.exception("Failed to index department %s during cold build", getattr(d, "id", d))
        return collection


async def get_or_build_department_collection():
    return await _ensure_v2_collection()


async def _upsert_department_into_collection(
    collection: Any,
    dept: dict[str, Any],
) -> None:
    dept_id = int(dept["id"])
    canonical_name = str(dept.get("name") or "")
    docs_map = await _translate_dept_docs_for_embedding(dept)
    ids = [f"dept-{dept_id}-{lang}" for lang in _LANG_KEYS]
    documents = [docs_map[lang] for lang in _LANG_KEYS]
    embeddings = await embed_texts(documents)
    metadatas = [
        {
            "department_id": dept_id,
            "name": canonical_name,
            "specialty": dept.get("specialty") or "",
        }
        for _ in _LANG_KEYS
    ]
    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )


async def upsert_department_chroma_v2(dept: dict[str, Any]) -> tuple[Literal["ok", "failed"], str | None]:
    settings = get_settings()
    if not settings.embedding_configured():
        return "failed", "Embedding API is not configured"
    try:
        collection = await _ensure_v2_collection()
        await _upsert_department_into_collection(collection, dept)
        return "ok", None
    except Exception as e:
        logger.exception("Department Chroma upsert failed")
        return "failed", str(e)[:500]


async def query_departments(user_text: str, top_k: int = 5) -> list[dict[str, Any]]:
    collection = await get_or_build_department_collection()
    query_emb = (await embed_texts([user_text]))[0]
    n_fetch = max(top_k * 8, top_k + 4)
    res = collection.query(query_embeddings=[query_emb], n_results=n_fetch)
    metas = (res.get("metadatas") or [[]])[0]
    dists = (res.get("distances") or [[]])[0]
    best: dict[int, tuple[float, dict[str, Any]]] = {}
    for meta, dist in zip(metas, dists):
        if not meta:
            continue
        did = int(meta["department_id"])
        d = float(dist)
        if did not in best or d < best[did][0]:
            best[did] = (d, meta)
    ranked = sorted(best.items(), key=lambda x: x[1][0])[:top_k]
    out: list[dict[str, Any]] = []
    for _did, (dist, meta) in ranked:
        out.append(
            {
                "department_id": int(meta["department_id"]),
                "name": str(meta["name"]),
                "distance": float(dist),
            }
        )
    return out


async def rebuild_department_collection():
    client = get_chroma_client()
    try:
        client.delete_collection(COLLECTION_V2_NAME)
    except Exception:
        pass
    return await get_or_build_department_collection()
