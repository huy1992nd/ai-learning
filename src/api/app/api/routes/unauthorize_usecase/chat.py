from __future__ import annotations

import asyncio
import json
import logging
from typing import AsyncIterator

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import StreamingResponse

from app.models.chat.chat_request import ChatRequest
from app.services.ai.chat_service import stream_chat
from app.services.general.session_state_service import clear_chat_session_context

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])


def _sse(event: str | None, data: dict | str) -> str:
    payload = data if isinstance(data, str) else json.dumps(data, ensure_ascii=False)
    prefix = f"event: {event}\n" if event else ""
    return f"{prefix}data: {payload}\n\n"


async def _event_stream(
    request: Request,
    session_id: str,
    message: str,
    *,
    explicit_language: str | None,
) -> AsyncIterator[str]:
    try:
        async for item in stream_chat(
            session_id, message, explicit_language=explicit_language
        ):
            if await request.is_disconnected():
                logger.info("Client disconnected; aborting stream for %s", session_id)
                break
            if isinstance(item, dict) and "event" in item and "data" in item:
                yield _sse(str(item["event"]), item["data"])
            else:
                yield _sse(None, {"token": item})
        yield _sse("done", "[DONE]")
    except asyncio.CancelledError:
        raise
    except Exception as exc:
        logger.exception("Streaming failed")
        yield _sse("error", {"message": str(exc)})


_SSE_STREAM_DESC = (
    "Luồng **text/event-stream** (SSE). Có thể: `event: thread_closed` (đóng thread), `event: appointment` "
    "(`appointmentSetupDone`, `sessionId`); rồi `data: {\"token\": \"...\"}`; kết: `event: done` + `[DONE]`. "
    "Lỗi: `event: error`.\n\n"
    "Healthcare v2: độ liên quan y tế, gợi khoa, hỏi đặt lịch, thu hồ sơ (function calling) — stream model."
)


@router.post(
    "/chat/stream",
    summary="Stream chat (SSE)",
    description=_SSE_STREAM_DESC,
    response_description="SSE: các frame `data` chứa JSON token; kết thúc bằng event `done`.",
    responses={
        200: {
            "description": "Luồng SSE thành công.",
            "content": {
                "text/event-stream": {
                    "schema": {"type": "string"},
                    "examples": {
                        "token_then_done": {
                            "summary": "Vài token rồi kết thúc",
                            "value": (
                                'data: {"token": "Xin"}\n\n'
                                'data: {"token": " chào"}\n\n'
                                "event: done\ndata: [DONE]\n\n"
                            ),
                        }
                    },
                },
            },
        }
    },
)
async def chat_stream(payload: ChatRequest, request: Request) -> StreamingResponse:
    generator = _event_stream(
        request,
        payload.session_id,
        payload.message,
        explicit_language=payload.language,
    )
    return StreamingResponse(
        generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.delete(
    "/sessions/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa context session",
    description="Xóa lịch sử hội thoại trong bộ nhớ cho `session_id` (nếu có).",
    response_description="Không có body khi thành công.",
)
async def clear_session(session_id: str) -> None:
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id is required")
    clear_chat_session_context(session_id)
    return None
