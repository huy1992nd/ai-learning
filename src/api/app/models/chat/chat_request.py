from __future__ import annotations

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Body cho POST /api/chat/stream (SSE)."""

    session_id: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="UUID phiên hội thoại; frontend tạo và gửi kèm mỗi lần.",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    message: str = Field(
        ...,
        min_length=1,
        description="Nội dung tin nhắn người dùng.",
        examples=["Xin chào!"],
    )
    language: str | None = Field(
        None,
        description="Ngôn ngữ UI/chat tùy chọn (en, vi, jp). Khi có, backend dùng cho template cố định và đồng bộ cache phiên.",
        examples=["en"],
    )
