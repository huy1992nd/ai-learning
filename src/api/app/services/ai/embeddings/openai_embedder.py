from __future__ import annotations

from functools import lru_cache

from openai import AsyncOpenAI

from app.core.config import get_settings


def _normalize_openai_compatible_base_url(url: str) -> str:
    """
    AsyncOpenAI appends `/embeddings` to base_url. If .env already ends with
    `/embeddings`, requests become `/v1/embeddings/embeddings` → 404.
    """
    u = url.strip().rstrip("/")
    while True:
        low = u.lower()
        if low.endswith("/embeddings"):
            u = u[: -len("/embeddings")].rstrip("/")
            continue
        break
    return u


def _normalize_openai_compatible_base_url(url: str) -> str:
    """
    AsyncOpenAI appends `/embeddings` to base_url. If .env already ends with
    `/embeddings`, requests become `/v1/embeddings/embeddings` → 404.
    """
    u = url.strip().rstrip("/")
    while True:
        low = u.lower()
        if low.endswith("/embeddings"):
            u = u[: -len("/embeddings")].rstrip("/")
            continue
        break
    return u


@lru_cache(maxsize=1)
def get_async_embedding_client() -> AsyncOpenAI:
    settings = get_settings()
    if not settings.embedding_configured():
        raise RuntimeError("Embedding not configured")
    endpoint = settings.effective_embedding_endpoint().strip()
    api_key = settings.effective_embedding_api_key()
    return AsyncOpenAI(
        base_url=_normalize_openai_compatible_base_url(endpoint),
        api_key=api_key,
    )


async def embed_texts(texts: list[str]) -> list[list[float]]:
    settings = get_settings()
    client = get_async_embedding_client()
    resp = await client.embeddings.create(
        model=settings.openai_embedding_model,
        input=texts,
    )
    return [d.embedding for d in resp.data]
