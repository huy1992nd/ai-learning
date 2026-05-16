# FE -> BE -> DB flow

This document summarizes the current runtime flow in this workshop repo.

## High-level sequence

1. Angular sends `POST /api/chat/stream` with `session_id` and `message`.
2. FastAPI runs healthcare preprocess stages and builds augmentation context.
3. FastAPI streams assistant tokens from the OpenAI-compatible backend over SSE.
4. Session context is stored in memory.
5. SQLite is used for catalog lookups (departments, doctors, schedule-related reads).

## Main files

- Route: `src/api/app/api/routes/unauthorize_usecase/chat.py`
- Chat orchestrator: `src/api/app/services/ai/chat_service.py`
- Healthcare workflow: `src/api/app/services/ai/healthcare_workflow.py`
- Chat pipeline stages: `src/api/app/services/ai/chat_pipeline/`
- Catalog repository: `src/api/app/services/crud/clinical_repository.py`
- Slot calendar logic: `src/api/app/services/crud/slot_calendar.py`
- SQLite connection: `src/api/app/db/connection.py`
- FE chat service: `src/webui/src/app/core/services/chat.service.ts`
