from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.appointments import router as appointments_router
from app.api.routes.catalog import router as catalog_router
from app.api.routes.sessions import router as sessions_router
from app.api.routes.admin.admin_portal import router as admin_router
from app.api.routes.admin.analytics_kb import router as analytics_kb_router
from app.api.routes.admin.auth import router as auth_router
from app.api.routes.admin.departments import router as admin_departments_router
from app.api.routes.admin.knowledge_documents import router as knowledge_documents_router
from app.api.routes.admin.vector_store import router as vector_store_router
from app.api.routes.unauthorize_usecase.audio import router as audio_router
from app.api.routes.unauthorize_usecase.chat import router as chat_router
from app.api.routes.unauthorize_usecase.knowledge_chat import router as knowledge_chat_router
from app.core.config import get_settings
from app.db.health import check_database_via_orm
from app.db.kb_sqlite_migrations import apply_knowledge_documents_sqlite_patches
from app.db.orm import Base, engine
from app.entities.knowledge_chunk import KnowledgeChunkEntity
from app.entities.knowledge_document import KnowledgeDocumentEntity
from app.entities.rag_query_log import RagQueryLogEntity


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)


@asynccontextmanager
async def _lifespan(_app: FastAPI):
    """Ensure SRS v3 KB tables exist on existing SQLite files (CREATE IF NOT EXISTS)."""
    from dummy.seed import seed_if_missing

    await asyncio.to_thread(seed_if_missing)
    Base.metadata.create_all(
        bind=engine,
        tables=[
            KnowledgeDocumentEntity.__table__,
            KnowledgeChunkEntity.__table__,
            RagQueryLogEntity.__table__,
        ],
    )
    apply_knowledge_documents_sqlite_patches(engine)
    yield


def create_app() -> FastAPI:
    settings = get_settings()

    tags_metadata = [
        {
            "name": "meta",
            "description": "Kiểm tra sống (health), DB ping (ops).",
        },
        {
            "name": "chat",
            "description": (
                "**Giao diện chính cho FE:** `POST /api/chat/stream` (SSE). "
                "MedAssist (UC-00…UC-08) trong luồng chat; STT/TTS (UC-12) ở tag **audio**."
            ),
        },
        {"name": "sessions", "description": "UC-05 — patient draft cho form pre-fill."},
        {"name": "catalog", "description": "UC-04 — danh mục khoa / bác sĩ."},
        {"name": "doctors", "description": "UC-06/UC-07 — slot trống & bác sĩ thay thế."},
        {"name": "appointments", "description": "UC-08 — đặt lịch từ form."},
        {"name": "auth", "description": "UC-09 — JWT đăng nhập Admin/Doctor (demo)."},
        {"name": "doctor", "description": "UC-10 — lịch khám theo bác sĩ."},
        {"name": "admin", "description": "UC-11 — tổng quan admin."},
        {
            "name": "audio",
            "description": "UC-12 — `POST /api/audio/speech-to-text` và `POST /api/audio/text-to-speech`.",
        },
        {
            "name": "knowledge",
            "description": (
                "UC-16 — RAG tra cứu bách khoa y tế: `POST /api/knowledge/chat/stream` (SSE). "
                "Độc lập luồng MedAssist UC-00…UC-12."
            ),
        },
        {
            "name": "admin-kb",
            "description": (
                "UC-13…UC-15, UC-18 — Knowledge Base admin: `/api/admin/knowledge-base/*`, "
                "`/api/admin/vector-store/*`, `/api/admin/analytics/*` (JWT ADMIN)."
            ),
        },
    ]

    app = FastAPI(
        title="AI Chatbot API",
        version="0.1.0",
        description=(
            "Backend FastAPI + OpenAI-compatible API. **Chat:** `POST /api/chat/stream` (SSE) với MedAssist UC-00…UC-08 "
            "(gợi ý khoa/bác sĩ, slot, thu thập patient dictionary, link form đăng ký). "
            "**REST:** patient-info, catalog, appointments, auth (JWT), STT `POST /api/audio/speech-to-text`, "
            "TTS `POST /api/audio/text-to-speech`.\n\n"
            "Swagger: [`/docs`](./docs), ReDoc: [`/redoc`](./redoc)."
        ),
        openapi_tags=tags_metadata,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=_lifespan,
    )

    _cors_regex = (settings.cors_origin_regex or "").strip() or None
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_origin_regex=_cors_regex,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

    @app.get("/api/health", tags=["meta"])
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/db/ping", tags=["meta"])
    async def db_ping() -> dict[str, Any]:
        """Kiểm tra kết nối DB qua SQLAlchemy ORM engine."""
        return await asyncio.to_thread(check_database_via_orm)

    app.include_router(chat_router, prefix="/api")
    app.include_router(audio_router, prefix="/api")
    app.include_router(sessions_router, prefix="/api")
    app.include_router(catalog_router, prefix="/api")
    app.include_router(appointments_router, prefix="/api")
    app.include_router(auth_router, prefix="/api")
    app.include_router(admin_router, prefix="/api")
    app.include_router(admin_departments_router, prefix="/api")
    app.include_router(knowledge_documents_router, prefix="/api")
    app.include_router(vector_store_router, prefix="/api")
    app.include_router(analytics_kb_router, prefix="/api")
    app.include_router(knowledge_chat_router, prefix="/api")

    return app


app = create_app()
