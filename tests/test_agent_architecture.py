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
                "forja_squad",
                "spark",
                "audit_squad",
                "helix_8",
                "decision_squad",
                "kira",
            ],
        )

    def test_parallel_specialist_groups_are_real_adk_agents(self):
        groups = {
            agent.name: agent
            for agent in root_agent.sub_agents
            if isinstance(agent, ParallelAgent)
        }
        self.assertEqual(
            set(groups),
            {"evidence_squad", "forja_squad", "audit_squad", "decision_squad"},
        )
        self.assertEqual(
            [agent.name for agent in groups["evidence_squad"].sub_agents],
            ["vigia", "nyx_7", "vega"],
        )
        self.assertEqual(
            [agent.name for agent in groups["forja_squad"].sub_agents],
            ["forja_core", "forja_test", "forja_ux"],
        )
        self.assertEqual(
            [agent.name for agent in groups["audit_squad"].sub_agents],
            ["recursor_omega", "nemesis_omega"],
        )
        self.assertEqual(
            [agent.name for agent in groups["decision_squad"].sub_agents],
            ["aureus_7", "bastion", "echo", "rift", "vanta_0"],
        )

    def test_all_specialists_are_llm_agents_with_unique_state_outputs(self):
        specialists = [
            agent for agent in walk_agents(root_agent) if isinstance(agent, LlmAgent)
        ]
        self.assertEqual(len(specialists), 18)

        output_keys = [agent.output_key for agent in specialists]
        self.assertTrue(all(output_keys))
        self.assertEqual(len(output_keys), len(set(output_keys)))
        for required in (
            "mission_contract",
            "forja_core_contract",
            "forja_test_gate",
            "forja_ux_spec",
            "execution_result",
            "recursion_audit",
            "adversarial_verdict",
            "judge_scorecard",
            "kira_decision",
        ):
            self.assertIn(required, output_keys)

    def test_helix_runs_after_both_evolutionary_auditors(self):
        root_names = [agent.name for agent in root_agent.sub_agents]
        self.assertLess(root_names.index("audit_squad"), root_names.index("helix_8"))
        self.assertLess(root_names.index("helix_8"), root_names.index("decision_squad"))

        helix = next(agent for agent in walk_agents(root_agent) if agent.name == "helix_8")
        self.assertIn("{recursion_audit}", helix.instruction)
        self.assertIn("{adversarial_verdict}", helix.instruction)
        self.assertIn("maximum is 5", helix.instruction)

    def test_recursor_and_nemesis_have_enforced_boundaries(self):
        recursor = next(
            agent for agent in walk_agents(root_agent) if agent.name == "recursor_omega"
        )
        nemesis = next(
            agent for agent in walk_agents(root_agent) if agent.name == "nemesis_omega"
        )
        self.assertIn("technical debt", recursor.instruction)
        self.assertIn("resolved without proof", recursor.instruction)
        self.assertIn("may not bypass", nemesis.instruction)
        self.assertIn("hackathon requirements", nemesis.instruction)

    def test_spark_has_deterministic_execution_tools(self):
        spark = next(agent for agent in walk_agents(root_agent) if agent.name == "spark")
        tool_names = {
            getattr(tool, "name", None) or getattr(tool, "__name__", "")
            for tool in spark.tools
        }
        self.assertIn("plan_human_benefit", tool_names)
        self.assertIn("run_reference_mission", tool_names)
        self.assertIn("{forja_test_gate}", spark.instruction)

    def test_public_topology_matches_runtime_architecture(self):
        topology = get_agent_topology()
        self.assertEqual(topology["root"]["type"], "SequentialAgent")
        self.assertEqual(topology["specialist_agent_count"], 18)
        self.assertEqual(topology["parallel_groups"], 4)
        self.assertEqual(
            [stage["name"] for stage in topology["stages"]],
            [
                "orion",
                "evidence_squad",
                "atlas_9",
                "forja_squad",
                "spark",
                "audit_squad",
                "helix_8",
                "decision_squad",
                "kira",
            ],
        )
        self.assertIn("recursor_omega", topology["evolutionary_control"])
        self.assertIn("forja_test", topology["engineering_contract"])

    def test_api_exposes_v09_topology(self):
        self.assertEqual(health()["version"], "0.9.0")
        payload = architecture_agents()
        self.assertEqual(payload["framework"], "Google Agent Development Kit (ADK)")
        self.assertEqual(payload["specialist_agent_count"], 18)
        self.assertEqual(payload["version"], "0.9.0")


if __name__ == "__main__":
    unittest.main()
