"""Tải / cache mô hình Hugging Face cho STT tại thư mục project <root>/models/..."""

from __future__ import annotations

import logging
import re
from pathlib import Path

from app.core.config import get_settings, resolved_hf_speech_model_path

logger = logging.getLogger(__name__)


def hf_repo_safe_dir_name(repo_id: str) -> str:
    """Tên thư mục an toàn: org/repo -> org__repo."""
    t = (repo_id or "").strip()
    if not t or "/" not in t:
        return re.sub(r"[^\w\-.]+", "_", t) or "model"
    a, b = t.split("/", 1)
    a = re.sub(r"[^\w\-.]+", "_", a.strip()) or "org"
    b = re.sub(r"[^\w\-.]+", "_", b.strip()) or "repo"
    return f"{a}__{b}"


def get_hf_speech_model_dir() -> Path:
    """Thư mục lưu snapshot cho `HF_SPEECH_MODEL_ID` (dưới project root)."""
    return resolved_hf_speech_model_path()


def _has_local_weights(p: Path) -> bool:
    if (p / "model.safetensors").is_file():
        return True
    return any(p.glob("*.safetensors"))


def ensure_hf_speech_model_files() -> Path:
    """
    Đảm bảo thư mục local có file weights. Nếu thiếu và không HF_OFFLINE, gọi snapshot_download.
    Idempotent: đã có .safetensors thì trả về path ngay.
    """
    s = get_settings()
    path = resolved_hf_speech_model_path()
    if path.is_dir() and _has_local_weights(path):
        return path
    if s.hf_offline:
        raise RuntimeError(
            f"HF_OFFLINE=1 nhưng chưa có file weights tại {path}. "
            "Tắt HF_OFFLINE để tải từ Hub, hoặc đặt HF_SPEECH_MODEL_LOCAL_DIR tới thư mục đã có model."
        )
    from huggingface_hub import snapshot_download

    repo = (s.hf_speech_model_id or "").strip() or "google/gemma-4-E4B-it"
    path.mkdir(parents=True, exist_ok=True)
    token = (s.hf_token or "").strip() or None
    logger.info("Downloading Hugging Face model %s into %s", repo, path)
    snapshot_download(
        repo_id=repo,
        local_dir=str(path),
        local_dir_use_symlinks=False,
        token=token,
    )
    if not _has_local_weights(path):
        raise RuntimeError(
            f"Đã tải {repo} nhưng không thấy .safetensors trong {path}. Kiểm tra quyền truy cập repo (HF_TOKEN nếu gated)."
        )
    return path
