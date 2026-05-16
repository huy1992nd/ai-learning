from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class KnowledgeDocumentPublic(BaseModel):
    id: int
    title: str
    category: str
    original_filename: str
    file_path: str | None
    mime_type: str | None
    status: str
    total_chunks: int
    metadata_json: str | None = None
    processing_error: str | None = None
    uploaded_by: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    is_active: bool = True
    content_text: str | None = Field(
        default=None,
        description="Only populated on single-document GET when requested.",
    )


class KnowledgeDocumentsListResponse(BaseModel):
    items: list[KnowledgeDocumentPublic]
    total: int
    page: int
    page_size: int


class KnowledgeDocumentPatch(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=512)
    category: str | None = None
    is_active: bool | None = None


class RagChatRequest(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=128)
    message: str = Field(..., min_length=1)


class VectorSearchBody(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=8, ge=1, le=50)
    category: str | None = Field(
        default=None,
        description="Optional KnowledgeCategory filter for metadata.",
    )


class VectorSearchHit(BaseModel):
    chunk_id: int
    document_id: int
    category: str
    title: str
    content: str
    distance: float
    similarity: float


class ImportJsonItem(BaseModel):
    title: str = Field(..., min_length=1)
    category: str
    content_text: str = Field(..., min_length=1)
    original_filename: str | None = Field(default="import.json")


class ImportJsonBody(BaseModel):
    documents: list[ImportJsonItem] = Field(..., min_length=1)


class BulkUploadResult(BaseModel):
    accepted: int
    errors: list[dict[str, Any]] = Field(default_factory=list)
