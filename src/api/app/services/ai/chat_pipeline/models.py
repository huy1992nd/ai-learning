from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from app.core.medassist_session_state import MedAssistSessionState
from app.core.enumerations.languages_enum import Languages


@dataclass
class ChatPipelineResult:
    rejection: str | None = None
    augmentation: str = ""
    events: list[dict[str, Any]] = field(default_factory=list)
    direct_reply: str | None = None
    stop: bool = False


@dataclass
class ChatPipelineContext:
    session_id: str
    user_message: str
    state: MedAssistSessionState
    started_awaiting_booking_response: bool
    result: ChatPipelineResult = field(default_factory=ChatPipelineResult)
    augmentation_parts: list[str] = field(default_factory=list)
    language: Languages = "vi"

    def add_instruction(self, text: str) -> None:
        if text and text.strip():
            self.augmentation_parts.append(text)

    def stop_with_rejection(self, message: str) -> None:
        self.result.rejection = message
        self.result.stop = True

    def stop_with_direct_reply(self, message: str) -> None:
        self.result.direct_reply = message
        self.result.stop = True


class PipelineStep(Protocol):
    async def run(self, ctx: ChatPipelineContext) -> None:
        ...
