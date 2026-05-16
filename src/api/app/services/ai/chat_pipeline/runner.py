from __future__ import annotations

from app.core.medassist_session_state import get_medassist_state
from app.services.ai.chat_pipeline.models import ChatPipelineContext
from app.services.ai.chat_pipeline.pipeline_language import resolve_pipeline_language
from app.services.ai.chat_pipeline.steps import (
    BookingPromptStep,
    BookingResponseStep,
    ClosedThreadStep,
    DepartmentTriageStep,
    MedicalRelevanceStep,
    MessageCounterStep,
    OpenAIConfigStep,
    PiiCollectionStep,
    RegistrationReadyStep,
)


def _build_context(
    session_id: str,
    user_message: str,
    *,
    explicit_language: str | None = None,
) -> ChatPipelineContext:
    state = get_medassist_state(session_id)
    language = resolve_pipeline_language(
        session_id, user_message, explicit_language=explicit_language
    )
    return ChatPipelineContext(
        session_id=session_id,
        user_message=user_message,
        state=state,
        started_awaiting_booking_response=bool(state.awaiting_booking_response),
        language=language,
    )


async def run_chat_pipeline(
    session_id: str,
    user_message: str,
    *,
    explicit_language: str | None = None,
) -> ChatPipelineContext:
    ctx = _build_context(session_id, user_message, explicit_language=explicit_language)
    steps = [
        ClosedThreadStep(),
        OpenAIConfigStep(),
        MessageCounterStep(),
        MedicalRelevanceStep(),
        PiiCollectionStep(),
        DepartmentTriageStep(),
        BookingPromptStep(),
        BookingResponseStep(),
        RegistrationReadyStep(),
    ]
    for step in steps:
        if ctx.result.stop:
            break
        await step.run(ctx)
    if ctx.augmentation_parts:
        ctx.result.augmentation = "\n\n".join(ctx.augmentation_parts)
    return ctx
