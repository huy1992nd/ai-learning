from __future__ import annotations

from pydantic import BaseModel


class DepartmentPublic(BaseModel):
    id: int
    name: str
    description: str | None = None
    specialty: str | None = None
    symptoms_keywords: str | None = None
    common_diseases: str | None = None
