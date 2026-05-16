from __future__ import annotations

from functools import lru_cache

from openai import AsyncOpenAI

from app.core.config import get_settings


def _normalize_chat_base_url(url: str) -> str:
    """Strip resource suffixes the SDK adds itself (avoids doubled path segments)."""
    u = url.strip().rstrip("/")
    for suffix in ("/chat/completions", "/completions"):
        while u.lower().endswith(suffix):
            u = u[: -len(suffix)].rstrip("/")
    return u


@lru_cache(maxsize=1)
def get_async_openai_client() -> AsyncOpenAI:
    settings = get_settings()
    if not settings.openai_endpoint or not settings.openai_api_key:
        raise RuntimeError(
            "OpenAI is not configured. Set OPENAI_ENDPOINT and OPENAI_API_KEY in your .env file."
        )
    return AsyncOpenAI(
        base_url=_normalize_chat_base_url(settings.openai_endpoint),
        api_key=settings.openai_api_key,
    )


def openai_configured() -> bool:
    s = get_settings()
    return bool(s.openai_endpoint and s.openai_api_key and s.openai_deployment)


def openai_stt_configured() -> bool:
    """Whisper trên cùng resource với chat (OPENAI_*), khi cấu hình OPENAI_STT_DEPLOYMENT."""
    s = get_settings()
    return bool(
        s.openai_endpoint
        and s.openai_api_key
        and (s.openai_stt_deployment or "").strip()
    )
