from __future__ import annotations

from pathlib import Path

from app.core.config import get_settings

# Thư mục chứa app package: .../src/api
_API_ROOT = Path(__file__).resolve().parent.parent.parent


def resolve_sqlite_path() -> Path:
    """Đường dẫn tuyệt đối tới file SQLite (mặc định relative tới `src/api`)."""
    raw = get_settings().sqlite_database_path
    p = Path(raw)
    return p.resolve() if p.is_absolute() else (_API_ROOT / p).resolve()
