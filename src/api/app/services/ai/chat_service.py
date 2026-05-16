from __future__ import annotations

import logging
from typing import Any, AsyncIterator, Union

from app.core.config import Settings, get_settings
from app.core.session_store import ChatMessage, SessionStore, get_session_store
from app.services.ai.azure_client import get_async_openai_client
from app.services.ai.healthcare_workflow import run_healthcare_preprocess

logger = logging.getLogger(__name__)


def _build_messages(
    settings: Settings,
    history: list[ChatMessage],
    user_message: str,
    *,
    system_content: str | None = None,
) -> list[ChatMessage]:
    system = system_content if system_content is not None else settings.system_prompt
    messages: list[ChatMessage] = [{"role": "system", "content": system}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})
    return messages


async def _stream_plain_text_words(text: str) -> AsyncIterator[str]:
    """Yield whitespace-separated chunks for SSE token frames."""
    words = text.split()
    for i, w in enumerate(words):
        yield w + (" " if i < len(words) - 1 else "")


async def stream_chat(
    session_id: str,
    user_message: str,
    store: SessionStore | None = None,
    *,
    explicit_language: str | None = None,
) -> AsyncIterator[Union[str, dict[str, Any]]]:
    """Stream side-effect dicts (SSE) then assistant text tokens—healthcare v2 pipeline."""

    settings = get_settings()
    store = store or get_session_store()

    rejection, augmentation, out_events, direct_reply = await run_healthcare_preprocess(
        session_id, user_message, explicit_language=explicit_language
    )
    for ev in out_events:
        yield ev
    if rejection:
        async for chunk in _stream_plain_text_words(rejection):
            yield chunk
        store.extend(
            session_id,
            [
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": rejection.strip()},
            ],
        )
        return
    if direct_reply:
        async for chunk in _stream_plain_text_words(direct_reply):
            yield chunk
        if direct_reply.strip():
            store.extend(
                session_id,
                [
                    {"role": "user", "content": user_message},
                    {"role": "assistant", "content": direct_reply.strip()},
                ],
            )
        return

    history = store.get_history(session_id)
    system_content = settings.system_prompt
    if augmentation.strip():
        system_content = f"{settings.system_prompt}\n\n{augmentation}"

    payload = _build_messages(
        settings, history, user_message, system_content=system_content
    )

    client = get_async_openai_client()
    assistant_buffer: list[str] = []

    try:
        stream = await client.chat.completions.create(
            model=settings.openai_deployment,
            messages=payload,
            stream=True,
        )
        async for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            token = getattr(delta, "content", None)
            if token:
                assistant_buffer.append(token)
                yield token
    except Exception:
        logger.exception("OpenAI streaming failed for session %s", session_id)
        raise

    if not assistant_buffer:
        logger.warning(
            "OpenAI returned zero content chunks (deployment=%s). "
            "Check OPENAI_DEPLOYMENT, endpoint, and API key.",
            settings.openai_deployment,
        )

    full_reply = "".join(assistant_buffer).strip()
    if full_reply:
        store.extend(
            session_id,
            [
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": full_reply},
            ],
        )
