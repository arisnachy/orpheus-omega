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
    def test_adk_app_exports_real_workflow_and_execution_tools(self) -> None:
        from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent

        from agent_app.agent import app, root_agent

        self.assertEqual("orpheus_omega", root_agent.name)
        self.assertEqual("agent_app", app.name)
        self.assertIsInstance(root_agent, SequentialAgent)
        self.assertEqual(len(root_agent.sub_agents), 9)

        all_agents = []

        def walk(agent):
            all_agents.append(agent)
            for child in getattr(agent, "sub_agents", []) or []:
                walk(child)

        walk(root_agent)
        self.assertEqual(
            len([agent for agent in all_agents if isinstance(agent, LlmAgent)]),
            18,
        )
        self.assertEqual(
            len([agent for agent in all_agents if isinstance(agent, ParallelAgent)]),
            4,
        )

        spark = next(agent for agent in all_agents if agent.name == "spark")
        self.assertGreaterEqual(len(spark.tools), 2)
        self.assertIsNotNone(next(agent for agent in all_agents if agent.name == "forja_core"))
        self.assertIsNotNone(next(agent for agent in all_agents if agent.name == "recursor_omega"))
        self.assertIsNotNone(next(agent for agent in all_agents if agent.name == "nemesis_omega"))
        self.assertIsNotNone(next(agent for agent in all_agents if agent.name == "helix_8"))


if __name__ == "__main__":
    unittest.main()
