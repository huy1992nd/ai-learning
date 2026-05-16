from __future__ import annotations

from pydantic import BaseModel


class DoctorPublic(BaseModel):
    id: int
    full_name: str
    department_id: int
    title: str | None = None
    specialty: str | None = None
    bio: str | None = None
    photo_url: str | None = None
    email: str
    phone: str | None = None
    is_active: bool
