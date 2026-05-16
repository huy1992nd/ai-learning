from __future__ import annotations

import logging

from app.services.ai.azure_client import openai_configured
from app.services.ai.chat_pipeline.llm_helpers import classify_medical
from app.services.ai.chat_pipeline.models import ChatPipelineContext, PipelineStep
from app.services.ai.chat_pipeline.stages import FLOW_DEPARTMENT_TRIAGE
from app.services.ai.chat_pipeline.steps.constants import MEDICAL_MIN_SCORE
from app.services.ai.chat_pipeline.steps.helpers import close_thread
from app.services.ai.chat_pipeline.steps.messages import (
    BASE_ASSISTANT_INSTRUCTION_DICT,
    NON_MEDICAL_MSC_DICT,
    OPENAI_MISSING_MSC_DICT,
    THREAD_ALREADY_CLOSED_MSC_DICT,
)

logger = logging.getLogger(__name__)


class ClosedThreadStep(PipelineStep):
    async def run(self, ctx: ChatPipelineContext) -> None:
        if ctx.state.thread_closed:
            ctx.stop_with_rejection(THREAD_ALREADY_CLOSED_MSC_DICT[ctx.language])


class OpenAIConfigStep(PipelineStep):
    async def run(self, ctx: ChatPipelineContext) -> None:
        if not openai_configured():
            ctx.stop_with_rejection(OPENAI_MISSING_MSC_DICT[ctx.language])


class MessageCounterStep(PipelineStep):
    async def run(self, ctx: ChatPipelineContext) -> None:
        ctx.state.user_message_count += 1
        ctx.add_instruction(BASE_ASSISTANT_INSTRUCTION_DICT[ctx.language])


class MedicalRelevanceStep(PipelineStep):
    async def run(self, ctx: ChatPipelineContext) -> None:
        if ctx.state.booking_prompt_shown:
            return
        if ctx.state.user_message_count > 2:
            return
        try:
            score = await classify_medical(ctx.user_message)
        except Exception:
            logger.exception("medical classification failed")
            score = 50
        if score < MEDICAL_MIN_SCORE:
            close_thread(ctx, "non_medical", NON_MEDICAL_MSC_DICT[ctx.language])
            return
        if ctx.state.user_message_count == 1 or ctx.state.flow_stage in (
            "medical_screen",
            "triaging",
            "",
        ):
            ctx.state.flow_stage = FLOW_DEPARTMENT_TRIAGE
