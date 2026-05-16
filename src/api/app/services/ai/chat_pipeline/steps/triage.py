from __future__ import annotations

import logging

from app.core.config import get_settings
from app.services.ai.chat_pipeline.llm_helpers import triage_department_from_shortlist
from app.services.ai.chat_pipeline.models import ChatPipelineContext, PipelineStep
from app.services.ai.chat_pipeline.steps.constants import GENERAL_INTERNAL_ID, MAX_TRIAGE_EXCHANGES
from app.services.ai.chat_pipeline.steps.department_keyword_triage import resolve_department_by_keywords
from app.services.ai.chat_pipeline.steps.helpers import finalize_department
from app.services.ai.chat_pipeline.steps.messages import (
    TRIAGE_CAP_REACHED_INSTRUCTION_DICT,
    TRIAGE_CLARIFICATION_INSTRUCTION_DICT,
    TRIAGE_SHORT_QUESTION_FALLBACK_DICT,
)
from app.services.ai.embeddings.department_index import query_departments
from app.services.crud.department_catalog import get_departments_cached

logger = logging.getLogger(__name__)


class DepartmentTriageStep(PipelineStep):
    async def run(self, ctx: ChatPipelineContext) -> None:
        if ctx.state.resolved_department_id is not None:
            return
        depts = get_departments_cached()
        valid_ids = {d["id"] for d in depts}
        if ctx.state.triage_exchange_count >= MAX_TRIAGE_EXCHANGES:
            finalize_department(ctx, GENERAL_INTERNAL_ID)
            ctx.add_instruction(TRIAGE_CAP_REACHED_INSTRUCTION_DICT[ctx.language])
            return

        settings = get_settings()
        try:
            top = await query_departments(
                ctx.user_message,
                top_k=settings.triage_embedding_top_k,
            )
            if not top:
                raise RuntimeError("embedding shortlist is empty")

            if top[0]["distance"] <= settings.triage_embedding_confidence_distance:
                did = int(top[0]["department_id"])
                if did in valid_ids:
                    finalize_department(ctx, did)
                    return
                raise RuntimeError("embedding top-1 not in valid ids")

            shortlist_by_id = {int(d["id"]): d for d in depts}
            enriched_shortlist = [
                {
                    "department_id": int(item["department_id"]),
                    "name": item["name"],
                    "distance": item["distance"],
                    "description": shortlist_by_id.get(int(item["department_id"]), {}).get("description"),
                    "symptoms_keywords": shortlist_by_id.get(int(item["department_id"]), {}).get(
                        "symptoms_keywords"
                    ),
                }
                for item in top
            ]
            tri = await triage_department_from_shortlist(enriched_shortlist, ctx.user_message)
            did = tri.get("department_id")
            shortlist_ids = {item["department_id"] for item in enriched_shortlist}
            if did is not None and isinstance(did, int) and did in shortlist_ids and did in valid_ids:
                finalize_department(ctx, did)
                return

            kw_strong = resolve_department_by_keywords(
                depts, ctx.user_message, valid_ids, strong_only=True
            )
            if kw_strong is not None:
                finalize_department(ctx, kw_strong)
                return

            ctx.state.triage_exchange_count += 1
            question = (tri.get("short_question") or TRIAGE_SHORT_QUESTION_FALLBACK_DICT[ctx.language]).strip()
            ctx.add_instruction(TRIAGE_CLARIFICATION_INSTRUCTION_DICT[ctx.language].format(question))
            return
        except Exception as exc:
            logger.warning(
                "embedding triage failed; attempting keyword fallback: %s",
                exc,
                exc_info=logger.isEnabledFor(logging.DEBUG),
            )
            kw = resolve_department_by_keywords(depts, ctx.user_message, valid_ids, strong_only=False)
            if kw is not None:
                finalize_department(ctx, kw)
                return
            ctx.state.triage_exchange_count += 1
            ctx.add_instruction(
                TRIAGE_CLARIFICATION_INSTRUCTION_DICT[ctx.language].format(
                    TRIAGE_SHORT_QUESTION_FALLBACK_DICT[ctx.language]
                )
            )
