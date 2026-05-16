"""UC-12: speech-to-text (Hugging Face local) và text-to-speech (edge-tts)."""

from __future__ import annotations

import logging
from io import BytesIO
from typing import Literal

import edge_tts

from app.core.config import get_settings, hf_speech_stt_dir_ready
from app.services.ai.azure_client import get_async_openai_client, openai_stt_configured

logger = logging.getLogger(__name__)

_ALLOWED_CT = frozenset(
    {
        "audio/webm",
        "video/webm",
        "audio/wav",
        "audio/x-wav",
        "audio/wave",
    }
)

TTSResponseFormat = Literal["mp3", "opus", "aac", "flac", "wav", "pcm"]


def _format_to_media_type(fmt: TTSResponseFormat) -> str:
    return {
        "mp3": "audio/mpeg",
        "opus": "audio/opus",
        "aac": "audio/aac",
        "flac": "audio/flac",
        "wav": "audio/wav",
        "pcm": "audio/pcm",
    }[fmt]


def stt_configured() -> bool:
    """Có thể dùng STT: mô hình HF local (ưu tiên) hoặc OpenAI/Whisper fallback."""
    if _hf_stt_available():
        return True
    if openai_stt_configured():
        return True
    return False


def _hf_stt_available() -> bool:
    return hf_speech_stt_dir_ready()


async def _transcribe_openai_whisper(
    *,
    filename: str,
    content_type: str | None,
    data: bytes,
    session_language: str | None,
    client: "object",
    deployment: str,
) -> str:
    if len(data) > 25 * 1024 * 1024:
        raise ValueError("Audio file exceeds 25MB limit.")

    ct = (content_type or "").split(";")[0].strip().lower()
    if ct and ct not in _ALLOWED_CT and not filename.lower().endswith((".webm", ".wav")):
        raise ValueError("Unsupported audio format. Use webm/opus or wav.")

    d = (deployment or "").strip()
    if not d:
        raise RuntimeError("STT: chưa có tên model/deployment Whisper.")

    lang = (session_language or "").lower()
    kwargs: dict = {
        "model": d,
        "file": (filename, BytesIO(data)),
    }
    if lang.startswith("vi"):
        kwargs["language"] = "vi"

    try:
        tr = await client.audio.transcriptions.create(**kwargs)  # type: ignore[union-attr]
    except Exception as exc:
        if type(exc).__name__ == "NotFoundError" or (
            hasattr(exc, "status_code") and getattr(exc, "status_code", None) == 404
        ):
            raise RuntimeError(
                "Speech-to-text: transcriptions API returned 404. "
                "Đặt OPENAI_STT_DEPLOYMENT = đúng tên Whisper (không dùng tên chat model)."
            ) from exc
        logger.exception("Speech transcription failed")
        raise

    text = (getattr(tr, "text", None) or "").strip()
    if not text:
        raise ValueError("empty_transcription")
    return text


async def transcribe_audio(
    *,
    filename: str,
    content_type: str | None,
    data: bytes,
    session_language: str | None,
) -> str:
    """Mô hình HF (HF_SPEECH_MODEL_ID) nếu PREFER_HF_LOCAL_STT; thất bại → Whisper OPENAI_STT nếu có."""
    if _hf_stt_available():
        from app.services.ai import hf_speech_stt

        try:
            return await hf_speech_stt.transcribe_from_bytes(
                data=data,
                filename=filename,
                session_language=session_language,
            )
        except Exception:
            logger.exception("Hugging Face local STT failed")
            if openai_stt_configured():
                s = get_settings()
                return await _transcribe_openai_whisper(
                    filename=filename,
                    content_type=content_type,
                    data=data,
                    session_language=session_language,
                    client=get_async_openai_client(),
                    deployment=(s.openai_stt_deployment or "").strip(),
                )
            raise

    if openai_stt_configured():
        s = get_settings()
        return await _transcribe_openai_whisper(
            filename=filename,
            content_type=content_type,
            data=data,
            session_language=session_language,
            client=get_async_openai_client(),
            deployment=(s.openai_stt_deployment or "").strip(),
        )

    raise RuntimeError(
        "Speech-to-text: bật PREFER_HF_LOCAL_STT và HF_SPEECH_MODEL_ID (tải vào thư mục gốc project /models/...), "
        "hoặc cấu hình fallback Whisper: OPENAI_ENDPOINT, OPENAI_API_KEY, OPENAI_STT_DEPLOYMENT."
    )


async def _text_to_speech_edge(*, text: str) -> tuple[bytes, str]:
    """TTS qua Microsoft Edge (edge-tts) — file mp3. Mô hình HF multimodal ở đây dùng cho STT, không tổng hợp giọng."""
    settings = get_settings()
    voice = (settings.tts_local_voice or "vi-VN-HoaiMyNeural").strip() or "vi-VN-HoaiMyNeural"
    com = edge_tts.Communicate(text, voice)
    out_mp3: list[bytes] = []
    async for chunk in com.stream():
        t = chunk.get("type") if isinstance(chunk, dict) else getattr(chunk, "type", None)
        if t == "audio":
            d = chunk.get("data") if isinstance(chunk, dict) else getattr(chunk, "data", b"")
            if d:
                out_mp3.append(d)
    buffer = b"".join(out_mp3)
    if not buffer:
        raise RuntimeError("edge-tts: không tạo được dữ liệu âm thanh.")
    return buffer, "audio/mpeg"


async def text_to_speech(
    *,
    text: str,
    voice: str = "alloy",
    response_format: TTSResponseFormat = "mp3",
) -> tuple[bytes, str]:
    _ = voice  # edge-tts: SPEECH_TTS_EDGE_VOICE / TTS_LOCAL_VOICE
    text = (text or "").strip()
    if not text:
        raise ValueError("Text must not be empty.")

    s = get_settings()
    eng = (s.audio_tts_engine or "auto").strip().lower()
    if eng not in ("auto", "edge"):
        eng = "auto"

    if eng == "edge":
        if response_format != "mp3":
            raise ValueError("edge-tts chỉ hỗ trợ response_format=mp3.")
        return await _text_to_speech_edge(text=text)

    # auto → edge-tts (mp3)
    if response_format != "mp3":
        raise ValueError(
            "TTS: chỉ hỗ trợ response_format=mp3 (edge-tts). "
            "Đặt response_format=mp3."
        )
    return await _text_to_speech_edge(text=text)
