from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

TTSVoice = Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"]


class TtsRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Text to synthesize")
    voice: TTSVoice = "alloy"
    response_format: Literal["mp3", "opus", "aac", "flac", "wav", "pcm"] = "mp3"
