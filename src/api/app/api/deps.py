from __future__ import annotations

from typing import Annotated, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.services.general.auth_service import decode_token

_bearer = HTTPBearer(auto_error=False)


def get_token_payload(
    cred: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> dict[str, Any]:
    if cred is None or cred.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
        )
    try:
        return decode_token(cred.credentials)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from None


def _role_from_payload(payload: dict[str, Any]) -> str:
    """Resolve role from common JWT / demo claim shapes."""
    for key in ("role", "Role"):
        v = payload.get(key)
        if v is not None and str(v).strip() != "":
            return str(v)
    raw = payload.get("roles")
    if isinstance(raw, (list, tuple)):
        for item in raw:
            if str(item).strip() != "":
                return str(item)
    return ""


def require_roles(*roles: str):
    allowed = {r.upper() for r in roles}

    async def checker(payload: Annotated[dict, Depends(get_token_payload)]) -> dict[str, Any]:
        if _role_from_payload(payload).upper() not in allowed:
            raise HTTPException(status_code=403, detail="Insufficient role")
        return payload

    return checker
