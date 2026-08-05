import os
import unittest
from unittest.mock import patch

from orpheus.providers import MockReasoningProvider, build_provider
from orpheus.settings import Settings
from orpheus.tools import list_historical_concepts, run_reference_mission


class SettingsAndToolsTests(unittest.TestCase):
    def test_default_mode_is_credential_free(self):
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings.from_env()
            self.assertEqual("local", settings.runtime_mode)
            self.assertEqual("mock", settings.llm_backend)
            self.assertTrue(settings.ready)

    def test_vertex_mode_requires_project(self):
        with patch.dict(
            os.environ,
            {
                "ORPHEUS_RUNTIME_MODE": "google_cloud",
                "ORPHEUS_LLM_BACKEND": "vertex_ai",
            },
            clear=True,
        ):
            settings = Settings.from_env()
            self.assertIn(
                "GOOGLE_CLOUD_PROJECT is required for Vertex AI",
                settings.validation_errors(),
            )

    def test_mock_provider_never_calls_network(self):
        with patch.dict(os.environ, {}, clear=True):
            provider = build_provider()
            self.assertIsInstance(provider, MockReasoningProvider)
            response = provider.generate("Revive a passive cooling concept")
            self.assertEqual("mock", response.backend)
            self.assertIn("no model call", response.text)

    def test_catalog_discloses_pending_sources(self):
        catalog = list_historical_concepts()
        self.assertGreaterEqual(catalog["count"], 3)
        self.assertTrue(catalog["source_verification_pending"])

    def test_reference_mission_is_verified(self):
        result = run_reference_mission()
        self.assertEqual("CUMPLIDA", result["mission_status"])
        self.assertTrue(result["winner"]["verification"]["approved"])


if __name__ == "__main__":
    unittest.main()
