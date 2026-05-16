from __future__ import annotations

import json
from pathlib import Path


class TextExtractError(Exception):
    pass


def extract_text_from_file(path: Path, mime_type: str | None) -> str:
    suffix = path.suffix.lower()
    mt = (mime_type or "").lower()

    if suffix == ".txt" or mt.startswith("text/plain"):
        return path.read_text(encoding="utf-8", errors="replace")

    if suffix == ".md" or mt in ("text/markdown", "text/x-markdown"):
        return path.read_text(encoding="utf-8", errors="replace")

    if suffix == ".json" or mt.endswith("json"):
        raw = path.read_text(encoding="utf-8", errors="replace")
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            raise TextExtractError(f"Invalid JSON: {e}") from e
        if isinstance(data, str):
            return data
        return json.dumps(data, ensure_ascii=False, indent=2)

    if suffix == ".pdf" or mt == "application/pdf":
        try:
            from pypdf import PdfReader
        except ImportError as e:
            raise TextExtractError("pypdf is not installed") from e
        reader = PdfReader(str(path))
        parts: list[str] = []
        for page in reader.pages:
            t = page.extract_text() or ""
            parts.append(t)
        return "\n\n".join(parts).strip()

    if suffix == ".docx" or mt == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        try:
            from docx import Document  # type: ignore[import-untyped]
        except ImportError as e:
            raise TextExtractError("python-docx is not installed") from e
        document = Document(str(path))
        return "\n".join(p.text for p in document.paragraphs if p.text).strip()

    raise TextExtractError(f"Unsupported file type: {suffix or mime_type}")
