"""UC-09 minimal JWT login for Admin/Doctor demo accounts."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.entities.user_account import UserAccountEntity

logger = logging.getLogger(__name__)


def verify_credentials(db: Session, email: str, password: str) -> dict[str, Any] | None:
    row = db.execute(
        select(UserAccountEntity).where(
            func.lower(UserAccountEntity.email) == email.strip().lower(),
            UserAccountEntity.is_active == 1,
        )
    ).scalar_one_or_none()
    if not row:
        return None
    stored = str(row.password_hash).encode("utf-8")
    if not bcrypt.checkpw(password.encode("utf-8"), stored):
        return None
    return {
        "sub": str(row.email),
        "uid": int(row.id),
        "role": str(row.role),
        "doctor_id": int(row.doctor_id) if row.doctor_id is not None else None,
    }


def create_access_token(claims: dict[str, Any]) -> tuple[str, int]:
    settings = get_settings()
    expire_min = max(5, int(settings.jwt_expire_minutes))
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=expire_min)
    payload = {**claims, "exp": exp, "iat": now}
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token, expire_min


def decode_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
