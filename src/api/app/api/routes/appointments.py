"""UC-08 — book appointment from registration form."""

from __future__ import annotations

import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.orm import get_db
from app.models.appointment.appointment_create_request import AppointmentCreateRequest
from app.models.appointment.appointment_public import AppointmentPublic
from app.services.crud.appointment_service import (
    AppointmentValidationError,
    SlotUnavailableError,
    create_appointment_from_request,
)
from app.services.general.session_state_service import clear_registration_draft
from app.services.general.teams_notification_service import send_appointment_notification

logger = logging.getLogger(__name__)

router = APIRouter(tags=["appointments"])


@router.post(
    "/appointments",
    response_model=AppointmentPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Create appointment (UC-08)",
)
async def post_appointment(
    body: AppointmentCreateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    try:
        row = create_appointment_from_request(db, body)
    except SlotUnavailableError as exc:
        raise HTTPException(
            status_code=409,
            detail="Selected slot is no longer available. Please choose another time.",
        ) from exc
    except AppointmentValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception:
        logger.exception("Appointment create failed")
        raise HTTPException(status_code=500, detail="Could not create appointment") from None

    if body.session_id:
        clear_registration_draft(body.session_id.strip())

    background_tasks.add_task(send_appointment_notification, dict(row))

    return row
