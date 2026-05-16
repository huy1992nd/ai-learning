"""UC-09 — JWT login (demo Admin account from seed)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.orm import get_db
from app.models.auth.login_request import LoginRequest
from app.models.auth.token_response import TokenResponse
from app.services.general.auth_service import create_access_token, verify_credentials

router = APIRouter(tags=["auth"])


@router.post("/auth/login", response_model=TokenResponse, summary="Admin/Doctor login")
async def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = verify_credentials(db, body.email, body.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token, expire_min = create_access_token(
        {
            "sub": user["sub"],
            "uid": user["uid"],
            "role": user["role"],
            "doctor_id": user["doctor_id"],
        }
    )
    return TokenResponse(
        access_token=token,
        expires_in_minutes=expire_min,
        role=str(user["role"]),
    )
