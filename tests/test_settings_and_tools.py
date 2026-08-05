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

    def test_catalog_has_bounded_primary_source_provenance(self):
        catalog = list_historical_concepts()

        self.assertEqual(catalog["count"], 5)
        self.assertGreaterEqual(catalog["source_count"], 10)
        self.assertTrue(catalog["provenance_complete"])
        self.assertFalse(catalog["source_verification_pending"])
        self.assertEqual(
            set(catalog["application_validation_pending"]),
            {concept["id"] for concept in catalog["concepts"]},
        )

        for concept in catalog["concepts"]:
            self.assertEqual(concept["source_verification"], "verified")
            self.assertEqual(concept["application_validation"], "pending")
            self.assertTrue(concept["evidence_scope"])
            self.assertGreaterEqual(len(concept["sources"]), 2)
            for source in concept["sources"]:
                self.assertTrue(source["title"])
                self.assertTrue(source["url"].startswith("https://"))
                self.assertTrue(source["evidence_type"])
                self.assertTrue(source["supports"])

    def test_reference_mission_is_verified(self):
        result = run_reference_mission()
        self.assertEqual("CUMPLIDA", result["mission_status"])
        self.assertTrue(result["winner"]["verification"]["approved"])


if __name__ == "__main__":
    unittest.main()
