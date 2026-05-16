from __future__ import annotations


def _normalize_optional_str(v: object | None) -> str | None:
    if v is None:
        return None
    s = str(v).strip()
    return s if s else None
