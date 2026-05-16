from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from app.models.department.department_public import DepartmentPublic


class DepartmentMutationResponse(BaseModel):
    department: DepartmentPublic
    embedding_status: Literal["ok", "failed"]
    embedding_message: str | None = None
