from __future__ import annotations

from functools import lru_cache

from app.core.config import get_settings


@lru_cache(maxsize=1)
def _encoder():
    import tiktoken

    return tiktoken.get_encoding("cl100k_base")


def chunk_text_by_tokens(text: str) -> list[tuple[str, int]]:
    """Return list of (chunk_text, token_count)."""
    settings = get_settings()
    enc = _encoder()
    tokens = enc.encode(text or "")
    target = max(settings.rag_chunk_target_tokens, 64)
    overlap = max(min(settings.rag_chunk_overlap_tokens, target // 2), 0)

    if not tokens:
        return []

    chunks: list[tuple[str, int]] = []
    start = 0
    n = len(tokens)
    while start < n:
        end = min(start + target, n)
        piece = tokens[start:end]
        decoded = enc.decode(piece)
        chunks.append((decoded, len(piece)))
        if end >= n:
            break
        start = max(end - overlap, start + 1)

    return chunks
