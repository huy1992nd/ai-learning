from __future__ import annotations

from app.services.ai.chat_pipeline.models import ChatPipelineContext, PipelineStep
from app.services.ai.chat_pipeline.stages import FLOW_PII_DONE
from app.services.ai.chat_pipeline.steps.messages import REGISTRATION_READY_INSTRUCTION_DICT


class RegistrationReadyStep(PipelineStep):
    async def run(self, ctx: ChatPipelineContext) -> None:
        if ctx.state.resolved_department_id is None:
            return
        if ctx.state.flow_stage != FLOW_PII_DONE:
            return
        ctx.add_instruction(REGISTRATION_READY_INSTRUCTION_DICT[ctx.language])
