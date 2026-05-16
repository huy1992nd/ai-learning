"""Speech-to-text (ASR) bằng mô hình Hugging Face multimodal (Gemma-4) local — âm thanh → văn bản."""

from __future__ import annotations

import asyncio
import inspect
import logging
import os
import re
import shutil
import subprocess
import tempfile
import threading
from pathlib import Path

import librosa
import soundfile as sf
import torch

from app.core.config import get_settings, resolved_hf_speech_model_path
from app.core.hf_model_cache import ensure_hf_speech_model_files

logger = logging.getLogger(__name__)

# Giới hạn theo model card (audio tối đa ~30 giây)
_MAX_AUDIO_SECONDS = 30.0

_lock = threading.Lock()
_processor = None
_model = None


def _get_model():
    global _processor, _model
    with _lock:
        if _model is not None and _processor is not None:
            return _model, _processor
        from transformers import (
            AutoConfig,
            AutoModelForMultimodalLM,
            AutoProcessor,
            GenerationConfig,
        )

        ensure_hf_speech_model_files()
        s = get_settings()
        root = Path(resolved_hf_speech_model_path())
        path = str(root)
        hub = (s.hf_speech_model_id or "").strip() or "google/gemma-4-E4B-it"
        logger.info("Loading Hugging Face multimodal STT from %s (hub=%s)", path, hub)
        has_cfg = (root / "config.json").is_file()

        def _load_generation_config():
            if (root / "generation_config.json").is_file():
                return GenerationConfig.from_pretrained(
                    path, local_files_only=True, trust_remote_code=True
                )
            return GenerationConfig.from_pretrained(hub, trust_remote_code=True)

        gen_cfg = _load_generation_config()

        if has_cfg:
            _processor = AutoProcessor.from_pretrained(
                path, local_files_only=True, trust_remote_code=True
            )
            _model = AutoModelForMultimodalLM.from_pretrained(
                path,
                generation_config=gen_cfg,
                torch_dtype="auto",
                device_map="auto",
                local_files_only=True,
                trust_remote_code=True,
            )
        else:
            logger.info(
                "No config.json in %s — using Hub %s for processor/config; weights local only",
                path,
                hub,
            )
            _processor = AutoProcessor.from_pretrained(
                hub, local_files_only=False, trust_remote_code=True
            )
            cfg = AutoConfig.from_pretrained(hub, trust_remote_code=True)
            _model = AutoModelForMultimodalLM.from_pretrained(
                path,
                config=cfg,
                generation_config=gen_cfg,
                torch_dtype="auto",
                device_map="auto",
                local_files_only=True,
                trust_remote_code=True,
            )
        return _model, _processor


def _language_name(session_language: str | None) -> str:
    raw = (session_language or "").strip().lower().replace("_", "-")
    if not raw:
        return "its original language"
    primary = raw.split("-", 1)[0]
    if primary == "vi":
        return "Vietnamese"
    if primary == "en":
        return "English"
    return "its original language"


def _resolve_ffmpeg_exe() -> str | None:
    w = shutil.which("ffmpeg")
    if w:
        return w
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None


def _ffmpeg_to_wav_16k_mono(src: Path) -> Path | None:
    exe = _resolve_ffmpeg_exe()
    if not exe:
        return None
    fd, tmp = tempfile.mkstemp(suffix=".wav", prefix="hf_ff_")
    os.close(fd)
    out = Path(tmp)
    try:
        subprocess.run(
            [
                exe,
                "-nostdin",
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-i",
                str(src),
                "-ar",
                "16000",
                "-ac",
                "1",
                "-f",
                "wav",
                str(out),
            ],
            check=True,
            capture_output=True,
            timeout=180,
        )
        return out if out.is_file() and out.stat().st_size > 0 else None
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError):
        if out.exists():
            out.unlink(missing_ok=True)  # type: ignore[attr-defined]
        return None


def _load_audio_16k_numpy(src_path: Path):
    try:
        y, sr = librosa.load(str(src_path), sr=16_000, mono=True, dtype="float32")
        return (y, sr)
    except Exception as e:
        name = type(e).__name__
        if name != "NoBackendError" and "Backend" not in name and "NoBackend" not in name:
            raise
        ff_wav = _ffmpeg_to_wav_16k_mono(src_path)
        if ff_wav is None:
            raise RuntimeError(
                "Không đọc được định dạng âm thanh (thường là webm thiếu ffmpeg). "
                "Cài ffmpeg (https://ffmpeg.org) và thêm vào PATH Windows, hoặc gửi file WAV."
            ) from e
        try:
            y, sr = librosa.load(str(ff_wav), sr=16_000, mono=True, dtype="float32")
            return (y, sr)
        finally:
            if ff_wav.exists():
                ff_wav.unlink(missing_ok=True)  # type: ignore[attr-defined]


def _asr_prompt(session_language: str | None) -> str:
    lang = _language_name(session_language)
    base_rules = (
        "Follow these specific instructions for formatting the answer:\n"
        "* Only output the transcription, with no newlines.\n"
        "* When transcribing numbers, write the digits, i.e. write 1.7 and not one point seven, "
        "and write 3 instead of three."
    )
    if lang == "Vietnamese":
        return (
            "The audio is in Vietnamese (Tiếng Việt). Transcribe it into Vietnamese using "
            "Latin script with correct diacritics. Do not output Thai, other Southeast Asian "
            f"scripts, or languages other than Vietnamese.\n\n{base_rules}"
        )
    if lang == "its original language":
        return (
            "Transcribe the following speech segment in its original language. " + base_rules
        )
    return (
        f"Transcribe the following speech segment in {lang} into {lang} text.\n\n{base_rules}"
    )


def _prepare_wav_16k_mono_from_file(src_path: Path) -> Path:
    y, sr = _load_audio_16k_numpy(src_path)
    dur = librosa.get_duration(y=y, sr=sr)
    if dur > _MAX_AUDIO_SECONDS + 0.1:
        raise ValueError(
            f"Audio tối đa khoảng {_MAX_AUDIO_SECONDS:.0f} giây. Hãy ghi đoạn ngắn hơn."
        )
    fd, tmp = tempfile.mkstemp(suffix=".wav", prefix="hf_stt_")
    os.close(fd)
    out = Path(tmp)
    sf.write(str(out), y, 16_000, subtype="PCM_16")
    return out


def _transcribe_sync(wav_path: Path, session_language: str | None) -> str:
    model, processor = _get_model()
    device = next(model.parameters()).device
    text_instruction = _asr_prompt(session_language)
    audio_ref = str(wav_path.resolve())
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "audio", "audio": audio_ref},
                {"type": "text", "text": text_instruction},
            ],
        }
    ]
    apply_kwargs: dict = {
        "tokenize": True,
        "return_dict": True,
        "return_tensors": "pt",
        "add_generation_prompt": True,
    }
    if "enable_thinking" in inspect.signature(processor.apply_chat_template).parameters:
        apply_kwargs["enable_thinking"] = False
    inputs = processor.apply_chat_template(messages, **apply_kwargs)  # type: ignore[operator]

    if hasattr(inputs, "to"):
        inputs = inputs.to(device)

    in_dict = {k: v for k, v in dict(inputs).items() if v is not None}  # type: ignore[call-overload, arg-type]
    input_len = int(in_dict["input_ids"].shape[-1])  # type: ignore[union-attr, index]
    with torch.inference_mode():
        outputs = model.generate(
            max_new_tokens=512,
            do_sample=True,
            temperature=1.0,
            top_p=0.95,
            top_k=64,
            **in_dict,
        )
    raw = processor.decode(outputs[0][input_len:], skip_special_tokens=False)
    if hasattr(processor, "parse_response"):
        try:
            parsed = processor.parse_response(raw)
        except Exception:
            parsed = None
        if isinstance(parsed, str) and parsed.strip():
            return _strip_response_artifacts(parsed.strip())
        if isinstance(parsed, dict) and parsed:
            for key in ("text", "content", "assistant", "message"):
                v = parsed.get(key)
                if isinstance(v, str) and v.strip():
                    return _strip_response_artifacts(v.strip())
    return _strip_response_artifacts(
        re.sub(r"<\|[^|]*\|>", " ", str(raw).replace("<|think|>", ""))
    )


def _strip_response_artifacts(s: str) -> str:
    s = re.sub(r"<\|[^|]*\|>", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _transcribe_file_pipeline(src_path: Path, session_language: str | None) -> str:
    wav_path = _prepare_wav_16k_mono_from_file(src_path)
    try:
        return _transcribe_sync(wav_path, session_language)
    finally:
        if wav_path.exists() and wav_path != src_path:
            wav_path.unlink(missing_ok=True)  # type: ignore[attr-defined]


async def transcribe_from_bytes(
    *,
    data: bytes,
    filename: str,
    session_language: str | None,
) -> str:
    if len(data) > 25 * 1024 * 1024:
        raise ValueError("Audio file exceeds 25MB limit.")
    p = Path(filename or "clip.webm")
    ext = p.suffix.lower() or ".webm"
    if ext not in (".webm", ".wav", ".wave", ".ogg", ".mp3", ".flac", ".m4a"):
        ext = ".webm"
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as f:
        f.write(data)
        src = Path(f.name)
    try:
        return await asyncio.to_thread(_transcribe_file_pipeline, src, session_language)
    finally:
        if src.exists():
            src.unlink(missing_ok=True)  # type: ignore[attr-defined]
