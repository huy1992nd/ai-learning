"""Triage keyword fallback, booking direct reply, and pipeline stop behavior."""

from __future__ import annotations

import asyncio
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from app.core.medassist_session_state import MedAssistSessionState
from app.services.ai.chat_pipeline.models import ChatPipelineContext
from app.services.ai.chat_pipeline.steps.booking import BookingPromptStep
from app.services.ai.chat_pipeline.steps.department_keyword_triage import (
    normalize_for_match,
    resolve_department_by_keywords,
)
from app.services.ai.chat_pipeline.steps.triage import DepartmentTriageStep


def _sample_catalog() -> list[dict]:
    return [
        {
            "id": 1,
            "name": "Department of Cardiology",
            "description": "Heart disease and hypertension.",
            "specialty": "Cardiology",
            "symptoms_keywords": (
                "chest pain, đau ngực, palpitations, shortness of breath, "
                "khó thở khi gắng sức, hypertension"
            ),
            "common_diseases": "Hypertension, Angina pectoris",
        },
        {
            "id": 3,
            "name": "Department of Pulmonology",
            "description": "Lung and airway diseases.",
            "specialty": "Pulmonology",
            "symptoms_keywords": (
                "cough, ho, wheezing, shortness of breath, khó thở, chest tightness, "
                "tức ngực, sputum, đàm, prolonged cough"
            ),
            "common_diseases": "Bronchitis, Asthma, Pneumonia",
        },
        {
            "id": 12,
            "name": "Department of Emergency Medicine",
            "description": "Urgent care.",
            "specialty": "Emergency Medicine",
            "symptoms_keywords": (
                "severe chest pain, đau ngực dữ dội, severe shortness of breath, "
                "khó thở cấp, loss of consciousness, bất tỉnh, heavy bleeding, chảy máu nhiều"
            ),
            "common_diseases": "Severe chest pain",
        },
    ]


class TestKeywordTriage(unittest.TestCase):
    def test_normalize_strips_accents(self) -> None:
        self.assertIn("kho tho", normalize_for_match("Khó thở"))

    def test_respiratory_resolves_pulmonology(self) -> None:
        depts = _sample_catalog()
        uid = resolve_department_by_keywords(
            depts,
            "Tôi bị khó thở và ho khoảng 3 ngày nay, có lúc thở gấp khi leo cầu thang.",
            {1, 3, 12},
            strong_only=False,
        )
        self.assertEqual(uid, 3)

    def test_emergency_overrides(self) -> None:
        depts = _sample_catalog()
        uid = resolve_department_by_keywords(
            depts,
            "Đau ngực dữ dội và khó thở cấp",
            {1, 3, 12},
            strong_only=False,
        )
        self.assertEqual(uid, 12)

    def test_strong_only_requires_high_signal(self) -> None:
        depts = _sample_catalog()
        vague = resolve_department_by_keywords(
            depts,
            "something vague about health",
            {1, 3, 12},
            strong_only=True,
        )
        self.assertIsNone(vague)


class TestBookingPromptDirectReply(unittest.IsolatedAsyncioTestCase):
    async def test_sets_direct_reply_and_stops(self) -> None:
        state = MedAssistSessionState()
        state.resolved_department_id = 3
        state.patient_info = {"department_id": 3, "department_name": "Department of Pulmonology"}
        ctx = ChatPipelineContext(
            session_id="sess-test",
            user_message="unused",
            state=state,
            started_awaiting_booking_response=False,
            language="vi",
        )
        step = BookingPromptStep()
        await step.run(ctx)
        self.assertTrue(ctx.result.stop)
        self.assertIsNotNone(ctx.result.direct_reply)
        self.assertIn("Pulmonology", ctx.result.direct_reply)
        self.assertIn("có/không", ctx.result.direct_reply.lower())


class TestDepartmentTriageEmbeddingFallback(unittest.IsolatedAsyncioTestCase):
    async def test_query_raises_resolves_via_keywords(self) -> None:
        state = MedAssistSessionState()
        ctx = ChatPipelineContext(
            session_id="sess-triage",
            user_message="Không sốt, đờm ít, ho nhiều về đêm.",
            state=state,
            started_awaiting_booking_response=False,
            language="vi",
        )
        catalog = _sample_catalog()
        with (
            patch(
                "app.services.ai.chat_pipeline.steps.triage.query_departments",
                new_callable=AsyncMock,
                side_effect=RuntimeError("401 unauthorized"),
            ),
            patch(
                "app.services.ai.chat_pipeline.steps.triage.get_departments_cached",
                return_value=catalog,
            ),
            patch(
                "app.services.ai.chat_pipeline.steps.helpers.get_department",
                return_value=SimpleNamespace(id=3, name="Department of Pulmonology"),
            ),
        ):
            await DepartmentTriageStep().run(ctx)
        self.assertEqual(ctx.state.resolved_department_id, 3)
        self.assertEqual(ctx.state.patient_info.get("department_id"), 3)


def main() -> None:
    unittest.main()


if __name__ == "__main__":
    main()
