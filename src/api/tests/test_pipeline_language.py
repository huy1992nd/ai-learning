"""Tests for pipeline language resolution (session cache + detection + explicit locale)."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from app.core.session_language import clear_session_language, get_session_language
from app.services.ai.chat_pipeline.pipeline_language import resolve_pipeline_language


class TestResolvePipelineLanguage(unittest.TestCase):
    def tearDown(self) -> None:
        clear_session_language(self.id())

    def test_explicit_language_wins_and_caches(self) -> None:
        sid = self.id()
        lang = resolve_pipeline_language(
            sid, "任意のメッセージ", explicit_language="jp"
        )
        self.assertEqual(lang, "jp")
        self.assertEqual(get_session_language(sid), "jp")

    def test_cached_session_without_re_detect(self) -> None:
        sid = self.id()
        resolve_pipeline_language(sid, "Hello I need help", explicit_language="en")
        with patch(
            "app.services.ai.chat_pipeline.pipeline_language.detect",
            side_effect=AssertionError("detect should not run when cache hit"),
        ):
            lang = resolve_pipeline_language(sid, "yes")
        self.assertEqual(lang, "en")

    def test_langdetect_used_when_no_cache(self) -> None:
        sid = self.id()
        with patch(
            "app.services.ai.chat_pipeline.pipeline_language.detect",
            return_value="en",
        ):
            lang = resolve_pipeline_language(sid, "I have had a cough for three days.")
        self.assertEqual(lang, "en")

    def test_japanese_kana_short_circuits(self) -> None:
        sid = self.id()
        with patch(
            "app.services.ai.chat_pipeline.pipeline_language.detect",
            side_effect=AssertionError("detect not needed for kana"),
        ):
            lang = resolve_pipeline_language(sid, "せきがつらいです")
        self.assertEqual(lang, "jp")


if __name__ == "__main__":
    unittest.main()
