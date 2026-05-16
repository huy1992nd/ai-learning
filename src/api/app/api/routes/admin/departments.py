"""Admin CRUD for departments (JWT role ADMIN)."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.orm import get_db
from app.models.department.department_create_request import DepartmentCreateRequest
from app.models.department.department_mutation_response import DepartmentMutationResponse
from app.models.department.department_update_request import DepartmentUpdateRequest
from app.services.ai.embeddings.department_index import upsert_department_chroma_v2
from app.services.crud import clinical_repository
from app.services.crud.department_catalog import invalidate_departments_cache

router = APIRouter(tags=["admin"])


def _database_unavailable(exc: clinical_repository.DatabaseUnavailableError) -> HTTPException:
    return HTTPException(status_code=503, detail=str(exc))


@router.post(
    "/admin/departments",
    status_code=status.HTTP_201_CREATED,
    summary="Create department (admin)",
)
async def admin_create_department(
    body: DepartmentCreateRequest,
    _: Annotated[dict[str, Any], Depends(require_roles("ADMIN"))],
    db: Session = Depends(get_db),
) -> DepartmentMutationResponse:
    try:
        conflict = clinical_repository.find_department_id_by_name_case_insensitive(db, body.name)
    except clinical_repository.DatabaseUnavailableError as exc:
        raise _database_unavailable(exc) from exc
    if conflict is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Department name already exists",
        )

    try:
        dept = clinical_repository.insert_department(
            db,
            name=body.name,
            description=body.description,
            specialty=body.specialty,
            symptoms_keywords=body.symptoms_keywords,
            common_diseases=body.common_diseases,
        )
    except clinical_repository.DatabaseUnavailableError as exc:
        raise _database_unavailable(exc) from exc
    invalidate_departments_cache()
    emb_status, emb_msg = await upsert_department_chroma_v2(dept.model_dump())
    return DepartmentMutationResponse(
        department=dept,
        embedding_status=emb_status,
        embedding_message=emb_msg,
    )


@router.patch(
    "/admin/departments/{department_id}",
    summary="Update department (admin, partial)",
)
async def admin_patch_department(
    department_id: int,
    body: DepartmentUpdateRequest,
    _: Annotated[dict[str, Any], Depends(require_roles("ADMIN"))],
    db: Session = Depends(get_db),
) -> DepartmentMutationResponse:
    incoming = body.model_dump(exclude_unset=True)
    if not incoming:
        try:
            existing = clinical_repository.get_department(db, department_id)
        except clinical_repository.DatabaseUnavailableError as exc:
            raise _database_unavailable(exc) from exc
        if existing is None:
            raise HTTPException(status_code=404, detail="Department not found")
        return DepartmentMutationResponse(department=existing, embedding_status="ok")

    if "name" in incoming:
        try:
            conflict = clinical_repository.find_department_id_by_name_case_insensitive(
                db,
                incoming["name"],
                exclude_id=department_id,
            )
        except clinical_repository.DatabaseUnavailableError as exc:
            raise _database_unavailable(exc) from exc
        if conflict is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Department name already exists",
            )

    try:
        updated = clinical_repository.update_department_fields(db, department_id, incoming)
    except clinical_repository.DatabaseUnavailableError as exc:
        raise _database_unavailable(exc) from exc
    if updated is None:
        raise HTTPException(status_code=404, detail="Department not found")

    invalidate_departments_cache()
    emb_status, emb_msg = await upsert_department_chroma_v2(updated.model_dump())
    return DepartmentMutationResponse(
        department=updated,
        embedding_status=emb_status,
        embedding_message=emb_msg,
    )
