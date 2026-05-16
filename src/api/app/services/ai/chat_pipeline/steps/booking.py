from __future__ import annotations

import logging

from app.services.ai.chat_pipeline.llm_helpers import classify_booking, run_pii_pass
from app.services.ai.chat_pipeline.models import ChatPipelineContext, PipelineStep
from app.services.ai.chat_pipeline.stages import FLOW_AWAITING_BOOKING, FLOW_COLLECTING_PII
from app.services.ai.chat_pipeline.steps.constants import BOOKING_MIN_SCORE
from app.services.ai.chat_pipeline.steps.helpers import close_thread, emit_appointment_ready_if_complete
from app.services.ai.chat_pipeline.steps.messages import (
    BOOKING_ACCEPTED_PII_INSTRUCTION_DICT,
    APPOINTMENT_FORM_READY_DIRECT_DICT,
    DIRECT_REPLY_PII_COLLECTION_DICT,
    BOOKING_PROMPT_DIRECT_REPLY_DICT,
    THANKS_CLOSE_MSC_DICT,
)

logger = logging.getLogger(__name__)


class BookingPromptStep(PipelineStep):
    async def run(self, ctx: ChatPipelineContext) -> None:
        if ctx.state.resolved_department_id is None:
            return
        if ctx.state.booking_prompt_shown:
            return
        ctx.state.booking_prompt_shown = True
        ctx.state.awaiting_booking_response = True
        ctx.state.flow_stage = FLOW_AWAITING_BOOKING
        label = ctx.state.patient_info.get("department_name") or "selected department"
        ctx.stop_with_direct_reply(BOOKING_PROMPT_DIRECT_REPLY_DICT[ctx.language].format(label))


class BookingResponseStep(PipelineStep):
    async def run(self, ctx: ChatPipelineContext) -> None:
        if not ctx.started_awaiting_booking_response:
            return
        if ctx.state.resolved_department_id is None:
            return
        if not ctx.state.awaiting_booking_response:
            return
        if ctx.state.user_message_count < 2:
            return
        try:
            booking = await classify_booking(ctx.user_message)
        except Exception:
            logger.exception("booking classify failed")
            booking = {"agreement_score": 50, "intent": "unclear"}
        agreement = int(booking.get("agreement_score", 0) or 0)
        intent = str(booking.get("intent", "unclear")).lower()
        say_yes = intent == "yes" or agreement >= BOOKING_MIN_SCORE
        say_no = intent == "no" or (intent != "yes" and agreement < 30)
        if say_no and not say_yes:
            ctx.state.awaiting_booking_response = False
            close_thread(ctx, "user_declined_booking", THANKS_CLOSE_MSC_DICT[ctx.language])
            return
        if not say_yes:
            return
        ctx.state.awaiting_booking_response = False
        ctx.state.flow_stage = FLOW_COLLECTING_PII
        try:
            direct = await run_pii_pass(ctx.session_id, ctx.user_message, ctx.state)
        except Exception:
            logger.exception("pii at booking yes failed")
            direct = DIRECT_REPLY_PII_COLLECTION_DICT[ctx.language]
        emit_appointment_ready_if_complete(ctx)
        ctx.add_instruction(BOOKING_ACCEPTED_PII_INSTRUCTION_DICT[ctx.language])
        if ctx.state.appointment_setup_event_sent:
            direct = APPOINTMENT_FORM_READY_DIRECT_DICT[ctx.language]
        ctx.stop_with_direct_reply(direct)
