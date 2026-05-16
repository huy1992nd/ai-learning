"""Healthcare workflow facade backed by the chat pipeline."""

from __future__ import annotations

from app.services.ai.chat_pipeline.runner import run_chat_pipeline


async def run_healthcare_preprocess(
    session_id: str,
    user_message: str,
    *,
    explicit_language: str | None = None,
) -> tuple[str | None, str, list[dict[str, object]], str | None]:
    """Compatibility wrapper for existing chat_service call sites."""
    ctx = await run_chat_pipeline(
        session_id, user_message, explicit_language=explicit_language
    )
    return (
        ctx.result.rejection,
        ctx.result.augmentation,
        ctx.result.events,
        ctx.result.direct_reply,
    )
