"""SRS v3 UC-16 — RAG knowledge chat (SSE), separate from MedAssist `/chat/stream`."""

from __future__ import annotations

import asyncio
import json
import logging
from typing import AsyncIterator

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from app.models.knowledge.schemas import RagChatRequest
from app.services.knowledge.knowledge_chat_service import stream_knowledge_chat

logger = logging.getLogger(__name__)

router = APIRouter(tags=["knowledge"])


def _sse(event: str | None, data: dict | str) -> str:
    payload = data if isinstance(data, str) else json.dumps(data, ensure_ascii=False)
    prefix = f"event: {event}\n" if event else ""
    return f"{prefix}data: {payload}\n\n"


async def _event_stream(
    request: Request,
    session_id: str,
    message: str,
) -> AsyncIterator[str]:
    try:
        async for item in stream_knowledge_chat(session_id, message):
            if await request.is_disconnected():
                logger.info("Client disconnected; aborting KB stream for %s", session_id)
                break
            if isinstance(item, dict):
                ev = str(item.get("event") or "error")
                data = item.get("data")
                if data is None:
                    data = {}
                yield _sse(ev, data)
            else:
                yield _sse(None, {"token": item})
        yield _sse("done", "[DONE]")
    except asyncio.CancelledError:
        raise
    except Exception as exc:
        logger.exception("KB stream failed")
        yield _sse("error", {"message": str(exc)})
        yield _sse("done", "[DONE]")


@router.post(
    "/knowledge/chat/stream",
    summary="RAG knowledge chat (SSE)",
    description=(
        "Luồng SSE giống `/api/chat/stream` (token JSON + `event: done`). "
        "Chỉ tra cứu kiến thức y tế từ Knowledge Base — không thay thế UC-00–UC-12."
    ),
)
async def knowledge_chat_stream(payload: RagChatRequest, request: Request) -> StreamingResponse:
    generator = _event_stream(request, payload.session_id, payload.message)
    return StreamingResponse(
        generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
