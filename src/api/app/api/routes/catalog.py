"""UC-04 catalog — departments & doctors (REST)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.orm import get_db
from app.services.crud import clinical_repository
from app.services.crud.slot_calendar import list_available_slots_for_doctor

router = APIRouter(tags=["catalog"])


def _database_unavailable(exc: clinical_repository.DatabaseUnavailableError) -> HTTPException:
    return HTTPException(status_code=503, detail=str(exc))


@router.get("/departments", summary="List departments")
async def list_departments(db: Session = Depends(get_db)):
    try:
        return clinical_repository.list_departments(db)
    except clinical_repository.DatabaseUnavailableError as exc:
        raise _database_unavailable(exc) from exc


@router.get("/departments/{department_id}", summary="Department by id")
async def get_department(department_id: int, db: Session = Depends(get_db)):
    try:
        dept = clinical_repository.get_department(db, department_id)
    except clinical_repository.DatabaseUnavailableError as exc:
        raise _database_unavailable(exc) from exc
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    return dept


@router.get("/doctors", summary="List all doctors (catalog)")
async def list_all_doctors(db: Session = Depends(get_db)):
    try:
        return clinical_repository.list_doctors(db, department_id=None, is_active=True)
    except clinical_repository.DatabaseUnavailableError as exc:
        raise _database_unavailable(exc) from exc


@router.get("/doctors/{doctor_id}", summary="Doctor profile by id")
async def get_doctor_profile(doctor_id: int, db: Session = Depends(get_db)):
    try:
        doc = clinical_repository.get_doctor(db, doctor_id)
    except clinical_repository.DatabaseUnavailableError as exc:
        raise _database_unavailable(exc) from exc
    if not doc:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doc


@router.get("/departments/{department_id}/doctors", summary="Doctors in department")
async def list_department_doctors(department_id: int, db: Session = Depends(get_db)):
    try:
        dept = clinical_repository.get_department(db, department_id)
    except clinical_repository.DatabaseUnavailableError as exc:
        raise _database_unavailable(exc) from exc
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    try:
        return clinical_repository.list_doctors(db, department_id=department_id, is_active=True)
    except clinical_repository.DatabaseUnavailableError as exc:
        raise _database_unavailable(exc) from exc


@router.get(
    "/bookable-slots",
    summary="Next 7 weekdays, 8 one-hour slots per day, excluding booked (VN time)",
)
async def bookable_slots(
    doctor_id: int = Query(..., description="Active doctor in catalog"),
    db: Session = Depends(get_db),
):
    try:
        doc = clinical_repository.get_doctor(db, doctor_id)
    except clinical_repository.DatabaseUnavailableError as exc:
        raise _database_unavailable(exc) from exc
    if not doc:
        raise HTTPException(status_code=404, detail="Doctor not found")
    slots = list_available_slots_for_doctor(db, doctor_id, from_now=True)
    return {
        "doctor_id": doctor_id,
        "slots": [
            {
                "slot_index": s.slot_index,
                "label": s.label,
                "storage_value": s.storage_value,
            }
            for s in slots
        ],
    }
