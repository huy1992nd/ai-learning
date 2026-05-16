from __future__ import annotations

from pydantic import BaseModel

from app.models.chat.role import Role


class Message(BaseModel):
    role: Role
    content: str
