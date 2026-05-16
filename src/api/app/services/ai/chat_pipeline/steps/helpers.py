from __future__ import annotations

from app.db.orm import SessionLocal
from app.services.ai.chat_pipeline.events import appointment_ready_event, thread_closed_event_data
from app.services.ai.chat_pipeline.models import ChatPipelineContext
from app.services.ai.chat_pipeline.stages import FLOW_AWAITING_BOOKING, FLOW_PII_DONE, FLOW_THREAD_CLOSED
from app.services.crud.clinical_repository import DatabaseUnavailableError, get_department
from app.services.general.patient_validators import pii_draft_minimal_complete


def close_thread(ctx: ChatPipelineContext, reason: str, message: str) -> None:
    ctx.state.thread_closed = True
    ctx.state.close_reason = reason
    ctx.state.flow_stage = FLOW_THREAD_CLOSED
    ctx.result.events.append(thread_closed_event_data(reason))
    ctx.stop_with_rejection(message)


def emit_appointment_ready_if_complete(ctx: ChatPipelineContext) -> None:
    if not pii_draft_minimal_complete(ctx.state.patient_info):
        return
    if not ctx.state.patient_info.get("department_id"):
        return
    if ctx.state.appointment_setup_event_sent:
        return
    ctx.state.appointment_setup_event_sent = True
    ctx.state.flow_stage = FLOW_PII_DONE
    ctx.result.events.append(appointment_ready_event(ctx.session_id))


def finalize_department(ctx: ChatPipelineContext, did: int) -> None:
    ctx.state.resolved_department_id = did
    with SessionLocal() as db:
        try:
            dep = get_department(db, did)
        except DatabaseUnavailableError:
            dep = None
    if dep:
        ctx.state.patient_info["department_id"] = dep.id
        ctx.state.patient_info["department_name"] = dep.name
    ctx.state.primary_department_id = did
    ctx.state.flow_stage = FLOW_AWAITING_BOOKING
