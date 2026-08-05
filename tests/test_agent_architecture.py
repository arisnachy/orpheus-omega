import unittest

from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent

from agent_app.agent import root_agent
from app.main import architecture_agents, health
from orpheus.agent_topology import get_agent_topology


def walk_agents(agent):
    yield agent
    for child in getattr(agent, "sub_agents", []) or []:
        yield from walk_agents(child)


class RealAdkArchitectureTests(unittest.TestCase):
    def test_root_is_a_real_sequential_workflow(self):
        self.assertIsInstance(root_agent, SequentialAgent)
        self.assertEqual(root_agent.name, "orpheus_omega")
        self.assertEqual(
            [agent.name for agent in root_agent.sub_agents],
            [
                "orion",
                "evidence_squad",
                "atlas_9",
                "spark",
                "decision_squad",
                "kira",
            ],
        )

    def test_parallel_specialist_groups_are_real_adk_agents(self):
        evidence_squad = root_agent.sub_agents[1]
        decision_squad = root_agent.sub_agents[4]

        self.assertIsInstance(evidence_squad, ParallelAgent)
        self.assertEqual(
            [agent.name for agent in evidence_squad.sub_agents],
            ["vigia", "nyx_7", "vega"],
        )

        self.assertIsInstance(decision_squad, ParallelAgent)
        self.assertEqual(
            [agent.name for agent in decision_squad.sub_agents],
            ["aureus_7", "bastion", "echo", "rift", "vanta_0"],
        )

    def test_all_specialists_are_llm_agents_with_unique_state_outputs(self):
        specialists = [
            agent for agent in walk_agents(root_agent) if isinstance(agent, LlmAgent)
        ]
        self.assertEqual(len(specialists), 12)

        output_keys = [agent.output_key for agent in specialists]
        self.assertTrue(all(output_keys))
        self.assertEqual(len(output_keys), len(set(output_keys)))
        self.assertIn("mission_contract", output_keys)
        self.assertIn("execution_result", output_keys)
        self.assertIn("kira_decision", output_keys)

    def test_spark_has_deterministic_execution_tools(self):
        spark = next(agent for agent in walk_agents(root_agent) if agent.name == "spark")
        tool_names = {
            getattr(tool, "name", None) or getattr(tool, "__name__", "")
            for tool in spark.tools
        }
        self.assertIn("plan_human_benefit", tool_names)
        self.assertIn("run_reference_mission", tool_names)

    def test_public_topology_matches_runtime_architecture(self):
        topology = get_agent_topology()
        self.assertEqual(topology["root"]["type"], "SequentialAgent")
        self.assertEqual(topology["specialist_agent_count"], 12)
        self.assertEqual(topology["parallel_groups"], 2)
        self.assertEqual(
            [stage["name"] for stage in topology["stages"]],
            [
                "orion",
                "evidence_squad",
                "atlas_9",
                "spark",
                "decision_squad",
                "kira",
            ],
        )

    def test_api_exposes_v05_topology(self):
        self.assertEqual(health()["version"], "0.5.0")
        payload = architecture_agents()
        self.assertEqual(payload["framework"], "Google Agent Development Kit (ADK)")
        self.assertEqual(payload["specialist_agent_count"], 12)


if __name__ == "__main__":
    unittest.main()
