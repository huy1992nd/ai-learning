from __future__ import annotations

import logging

from app.services.ai.chat_pipeline.llm_helpers import run_pii_pass
from app.services.ai.chat_pipeline.models import ChatPipelineContext, PipelineStep
from app.services.ai.chat_pipeline.stages import FLOW_COLLECTING_PII
from app.services.ai.chat_pipeline.steps.helpers import emit_appointment_ready_if_complete
from app.services.ai.chat_pipeline.steps.messages import (
    APPOINTMENT_FORM_READY_DIRECT_DICT,
    DIRECT_REPLY_PII_COLLECTION_DICT,
)

logger = logging.getLogger(__name__)


class PiiCollectionStep(PipelineStep):
    async def run(self, ctx: ChatPipelineContext) -> None:
        if ctx.state.flow_stage != FLOW_COLLECTING_PII:
            return
        try:
            direct = await run_pii_pass(ctx.session_id, ctx.user_message, ctx.state)
        except Exception:
            logger.exception("pii pass failed")
            direct = DIRECT_REPLY_PII_COLLECTION_DICT[ctx.language]
        emit_appointment_ready_if_complete(ctx)
        if ctx.state.appointment_setup_event_sent:
            direct = APPOINTMENT_FORM_READY_DIRECT_DICT[ctx.language]
        ctx.stop_with_direct_reply(direct)
