from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from orpheus.adk_bridge import serialize_runtime_exception
from orpheus.agent_topology import get_agent_topology
from orpheus.settings import Settings


class FreeSafeRuntimeTests(unittest.TestCase):
    def test_local_gemini_defaults_to_free_safe(self):
        env = {
            "ORPHEUS_RUNTIME_MODE": "local",
            "ORPHEUS_LLM_BACKEND": "gemini_api",
            "GEMINI_API_KEY": "test-only-key",
        }
        with patch.dict(os.environ, env, clear=True):
            settings = Settings.from_env()
            self.assertEqual(settings.execution_profile, "free_safe")
            self.assertTrue(settings.ready)
            self.assertEqual(
                settings.public_summary()["execution_behavior"]["squad_concurrency"],
                "sequential",
            )

    def test_parallel_profile_can_be_selected_explicitly(self):
        env = {
            "ORPHEUS_RUNTIME_MODE": "local",
            "ORPHEUS_LLM_BACKEND": "gemini_api",
            "ORPHEUS_EXECUTION_PROFILE": "parallel",
            "GEMINI_API_KEY": "test-only-key",
        }
        with patch.dict(os.environ, env, clear=True):
            settings = Settings.from_env()
            self.assertEqual(settings.execution_profile, "parallel")
            self.assertTrue(settings.ready)

    def test_free_safe_topology_preserves_agents_and_removes_burst_groups(self):
        env = {
            "ORPHEUS_RUNTIME_MODE": "local",
            "ORPHEUS_LLM_BACKEND": "gemini_api",
            "GEMINI_API_KEY": "test-only-key",
        }
        with patch.dict(os.environ, env, clear=True):
            topology = get_agent_topology()
            self.assertEqual(topology["specialist_agent_count"], 18)
            self.assertEqual(topology["execution_profile"], "free_safe")
            self.assertEqual(topology["parallel_groups"], 0)
            self.assertEqual(topology["potential_parallel_groups"], 4)
            squad_stages = [stage for stage in topology["stages"] if stage.get("sub_agents")]
            self.assertEqual(len(squad_stages), 4)
            self.assertTrue(all(stage["type"] == "SequentialAgent" for stage in squad_stages))
            self.assertTrue(all(stage["execution"] == "sequential" for stage in squad_stages))

    def test_taskgroup_error_is_flattened_and_classified(self):
        failure = ExceptionGroup(
            "unhandled errors in a TaskGroup",
            [
                RuntimeError("429 RESOURCE_EXHAUSTED: quota exceeded"),
                ValueError("secondary worker cancelled"),
            ],
        )
        diagnosis = serialize_runtime_exception(failure)
        self.assertEqual(diagnosis["error_code"], "quota_or_rate_limit")
        self.assertTrue(diagnosis["retryable"])
        self.assertGreaterEqual(len(diagnosis["error_details"]), 2)
        self.assertIn("free_safe", diagnosis["recovery"])
        self.assertNotEqual(diagnosis["error_message"], "unhandled errors in a TaskGroup (2 sub-exceptions)")

    def test_runtime_diagnostics_redact_key_shapes(self):
        failure = RuntimeError(
            "Authorization: AQ.Ab8RN6K3oAutVY3NCm5Zrm1l646EzONOThl27TiRU secret"
        )
        diagnosis = serialize_runtime_exception(failure)
        serialized = str(diagnosis)
        self.assertNotIn("AQ.Ab8RN6K3oAutVY3NCm5Zrm1l646EzONOThl27TiRU", serialized)
        self.assertIn("[redacted", serialized)

    def test_invalid_execution_profile_is_rejected(self):
        env = {
            "ORPHEUS_RUNTIME_MODE": "local",
            "ORPHEUS_LLM_BACKEND": "gemini_api",
            "ORPHEUS_EXECUTION_PROFILE": "reckless",
            "GEMINI_API_KEY": "test-only-key",
        }
        with patch.dict(os.environ, env, clear=True):
            errors = Settings.from_env().validation_errors()
            self.assertIn(
                "ORPHEUS_EXECUTION_PROFILE must be free_safe or parallel",
                errors,
            )


if __name__ == "__main__":
    unittest.main()
