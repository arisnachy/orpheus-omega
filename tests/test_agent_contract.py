from __future__ import annotations

import importlib.util
import unittest


def _module_is_available(module_name: str) -> bool:
    """Return False when either the module or a parent namespace is absent."""
    try:
        return importlib.util.find_spec(module_name) is not None
    except (ImportError, ModuleNotFoundError, AttributeError, ValueError):
        return False


ADK_AVAILABLE = _module_is_available("google.adk")


@unittest.skipUnless(ADK_AVAILABLE, "google-adk not installed")
class AgentContractTests(unittest.TestCase):
    def test_adk_agent_exports_app_and_tools(self) -> None:
        from agent_app.agent import app, root_agent

        self.assertEqual("orpheus_omega", root_agent.name)
        self.assertEqual("agent_app", app.name)
        self.assertGreaterEqual(len(root_agent.tools), 5)


if __name__ == "__main__":
    unittest.main()
