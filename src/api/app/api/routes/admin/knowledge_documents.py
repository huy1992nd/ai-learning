"""SRS v3 UC-13 / UC-14 — Knowledge Base documents (admin, JWT)."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Annotated, Any

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.enumerations.knowledge_enum import KnowledgeCategory, KnowledgeDocStatus
from app.db.orm import get_db
from app.models.knowledge.schemas import (
    BulkUploadResult,
    ImportJsonBody,
    KnowledgeDocumentPatch,
    KnowledgeDocumentPublic,
    KnowledgeDocumentsListResponse,
)
from app.services.crud import knowledge_repository as kr
from app.services.knowledge.kb_chroma import kb_delete_document_vectors
from app.services.knowledge.knowledge_ingest import run_ingest_sync, schedule_ingest

router = APIRouter(tags=["admin"])

AdminDep = Annotated[dict, Depends(require_roles("ADMIN"))]
DbDep = Annotated[Session, Depends(get_db)]


def _api_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _upload_dir() -> Path:
    from app.core.config import get_settings

    raw = (get_settings().kb_upload_dir or "").strip()
    if raw:
        p = Path(raw)
        d = p.resolve() if p.is_absolute() else (_api_root() / p).resolve()
    else:
        d = _api_root() / "dummy" / "kb_uploads"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _safe_filename(name: str) -> str:
    base = Path(name).name
    return re.sub(r"[^a-zA-Z0-9._-]+", "_", base).strip("._")[:180] or "upload"


def _rel_upload(path: Path) -> str:
    root = _api_root()
    try:
        return str(path.resolve().relative_to(root))
    except ValueError:
        return str(path.resolve())


def _admin_email(payload: dict) -> str | None:
    for key in ("email", "sub", "preferred_username"):
        v = payload.get(key)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None


def _parse_category(raw: str) -> str:
    try:
        return KnowledgeCategory(raw).value
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid category") from None


def _max_bytes() -> int:
    from app.core.config import get_settings

    return max(get_settings().kb_max_upload_mb, 1) * 1024 * 1024


def _read_inline_metadata(content_text: str) -> str:
    return json.dumps({"inline_content": content_text}, ensure_ascii=False)


@router.get(
    "/admin/knowledge-base/documents",
    response_model=KnowledgeDocumentsListResponse,
    summary="List KB documents (paginated)",
)
def list_kb_documents(
    db: DbDep,
    _: AdminDep,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    q: str | None = None,
    category: str | None = None,
    doc_status: str | None = Query(None, alias="status"),
) -> KnowledgeDocumentsListResponse:
    cat = _parse_category(category.strip()) if category and category.strip() else None
    rows, total = kr.list_documents(
        db,
        page=page,
        page_size=page_size,
        q=q,
        category=cat,
        status=doc_status,
        active_only=True,
    )
    items = [KnowledgeDocumentPublic.model_validate(kr.doc_to_public(r)) for r in rows]
    return KnowledgeDocumentsListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/admin/knowledge-base/documents/{document_id}",
    response_model=KnowledgeDocumentPublic,
    summary="Get KB document",
)
def get_kb_document(
    document_id: int,
    db: DbDep,
    _: AdminDep,
    include_content: bool = Query(False),
) -> KnowledgeDocumentPublic:
    row = kr.get_document(db, document_id)
    if not row or not row.is_active:
        raise HTTPException(status_code=404, detail="Document not found")
    body_text: str | None = None
    if include_content:
        if (row.content_text or "").strip():
            body_text = row.content_text
        elif row.metadata_json:
            try:
                meta = json.loads(row.metadata_json)
                if isinstance(meta, dict) and "inline_content" in meta:
                    body_text = str(meta.get("inline_content") or "")
            except json.JSONDecodeError:
                body_text = None
    data = kr.doc_to_public(row, content_text=body_text)
    return KnowledgeDocumentPublic.model_validate(data)


@router.post(
    "/admin/knowledge-base/documents",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Create KB document (upload file or inline text)",
)
async def create_kb_document(
    background_tasks: BackgroundTasks,
    db: DbDep,
    admin: AdminDep,
    category: str = Form(...),
    title: str | None = Form(None),
    file: UploadFile | None = File(None),
    content_text: str | None = Form(None),
) -> JSONResponse:
    cat = _parse_category(category.strip())
    if (file is None or not file.filename) and not (content_text and content_text.strip()):
        raise HTTPException(status_code=400, detail="Provide either file or content_text")
    if file and file.filename and content_text and content_text.strip():
        raise HTTPException(status_code=400, detail="Send only file or content_text, not both")

    uploaded_by = _admin_email(admin)
    max_b = _max_bytes()

    if file and file.filename:
        body = await file.read()
        if len(body) > max_b:
            raise HTTPException(status_code=413, detail="File too large")
        row = kr.create_document(
            db,
            title=(title or Path(file.filename).stem or "Untitled").strip(),
            category=cat,
            original_filename=file.filename,
            file_path="",
            mime_type=file.content_type,
            uploaded_by=uploaded_by,
            content_text="",
        )
        dest = _upload_dir() / f"{row.id}_{_safe_filename(file.filename)}"
        dest.write_bytes(body)
        row.file_path = _rel_upload(dest)
        row.mime_type = file.content_type
        db.add(row)
        db.commit()
        db.refresh(row)
    else:
        text = (content_text or "").strip()
        if len(text.encode("utf-8")) > max_b:
            raise HTTPException(status_code=413, detail="content_text too large")
        row = kr.create_document(
            db,
            title=(title or "Untitled").strip(),
            category=cat,
            original_filename="inline.txt",
            file_path=None,
            mime_type="text/plain",
            uploaded_by=uploaded_by,
            metadata_json=_read_inline_metadata(text),
            content_text=text,
        )

    background_tasks.add_task(schedule_ingest, row.id)
    payload = {"document": KnowledgeDocumentPublic.model_validate(kr.doc_to_public(row)).model_dump()}
    return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content=payload)


@router.patch(
    "/admin/knowledge-base/documents/{document_id}",
    response_model=KnowledgeDocumentPublic,
    summary="Update KB document metadata",
)
def patch_kb_document(
    document_id: int,
    body: KnowledgeDocumentPatch,
    db: DbDep,
    _: AdminDep,
) -> KnowledgeDocumentPublic:
    row = kr.get_document(db, document_id)
    if not row:
        raise HTTPException(status_code=404, detail="Document not found")
    raw_cat = (body.category or "").strip()
    cat = _parse_category(raw_cat) if raw_cat else None
    row = kr.patch_document(
        db,
        row,
        title=body.title,
        category=cat,
        is_active=body.is_active,
    )
    return KnowledgeDocumentPublic.model_validate(kr.doc_to_public(row))


@router.delete(
    "/admin/knowledge-base/documents/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft-delete KB document and remove vectors",
)
def delete_kb_document(document_id: int, db: DbDep, _: AdminDep) -> None:
    row = kr.get_document(db, document_id)
    if not row:
        raise HTTPException(status_code=404, detail="Document not found")
    kb_delete_document_vectors(document_id)
    kr.patch_document(db, row, title=None, category=None, is_active=False)
    return None


@router.post(
    "/admin/knowledge-base/documents/{document_id}/retry",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Retry failed processing",
)
def retry_kb_document(
    document_id: int,
    background_tasks: BackgroundTasks,
    db: DbDep,
    _: AdminDep,
) -> JSONResponse:
    row = kr.get_document(db, document_id)
    if not row or not row.is_active:
        raise HTTPException(status_code=404, detail="Document not found")
    kr.delete_chunks_for_document(db, document_id)
    kb_delete_document_vectors(document_id)
    kr.update_document_status(
        db,
        document_id,
        status=KnowledgeDocStatus.PENDING.value,
        processing_error=None,
        total_chunks=0,
    )
    db.refresh(row)
    background_tasks.add_task(schedule_ingest, document_id)
    payload = {"document": KnowledgeDocumentPublic.model_validate(kr.doc_to_public(row)).model_dump()}
    return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content=payload)


@router.post(
    "/admin/knowledge-base/documents/bulk-upload",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Upload multiple files sharing one category",
)
async def bulk_upload_kb_documents(
    background_tasks: BackgroundTasks,
    db: DbDep,
    admin: AdminDep,
    category: str = Form(...),
    files: list[UploadFile] = File(...),
) -> JSONResponse:
    cat = _parse_category(category.strip())
    uploaded_by = _admin_email(admin)
    max_b = _max_bytes()
    accepted = 0
    errors: list[dict[str, Any]] = []
    doc_ids: list[int] = []

    if len(files) > 50:
        raise HTTPException(status_code=400, detail="Too many files (max 50)")

    for uf in files:
        if not uf.filename:
            errors.append({"filename": "", "error": "missing_filename"})
            continue
        body = await uf.read()
        if len(body) > max_b:
            errors.append({"filename": uf.filename, "error": "file_too_large"})
            continue
        row = kr.create_document(
            db,
            title=Path(uf.filename).stem or "Untitled",
            category=cat,
            original_filename=uf.filename,
            file_path="",
            mime_type=uf.content_type,
            uploaded_by=uploaded_by,
            content_text="",
        )
        dest = _upload_dir() / f"{row.id}_{_safe_filename(uf.filename)}"
        dest.write_bytes(body)
        row.file_path = _rel_upload(dest)
        row.mime_type = uf.content_type
        db.add(row)
        db.commit()
        db.refresh(row)
        doc_ids.append(row.id)
        accepted += 1

    for did in doc_ids:
        background_tasks.add_task(schedule_ingest, did)

    result = BulkUploadResult(accepted=accepted, errors=errors)
    return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content=result.model_dump())


@router.post(
    "/admin/knowledge-base/import-json",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Import structured documents as JSON",
)
def import_kb_json(
    body: ImportJsonBody,
    background_tasks: BackgroundTasks,
    db: DbDep,
    admin: AdminDep,
) -> JSONResponse:
    uploaded_by = _admin_email(admin)
    max_b = _max_bytes()
    doc_ids: list[int] = []

    for item in body.documents:
        cat = _parse_category(item.category.strip())
        raw = item.content_text.encode("utf-8")
        if len(raw) > max_b:
            raise HTTPException(status_code=413, detail=f"Item too large: {item.title}")
        row = kr.create_document(
            db,
            title=item.title.strip(),
            category=cat,
            original_filename=item.original_filename or "import.json",
            file_path=None,
            mime_type="application/json",
            uploaded_by=uploaded_by,
            metadata_json=_read_inline_metadata(item.content_text),
            content_text=item.content_text,
        )
        doc_ids.append(row.id)

    for did in doc_ids:
        background_tasks.add_task(schedule_ingest, did)

    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={"imported": len(doc_ids), "document_ids": doc_ids},
    )
