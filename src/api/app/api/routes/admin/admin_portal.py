"""UC-11 — minimal admin overview."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.orm import get_db
from app.services.crud.doctor_portal_service import list_appointments_for_doctor

router = APIRouter(tags=["admin"])


@router.get(
    "/admin/doctors/{doctor_id}/appointments",
    summary="List appointments for a doctor (admin)",
)
async def admin_doctor_appointments(
    doctor_id: int,
    _: Annotated[dict[str, Any], Depends(require_roles("ADMIN"))],
    db: Session = Depends(get_db),
):
    return list_appointments_for_doctor(db, doctor_id)
