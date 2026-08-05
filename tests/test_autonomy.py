import tempfile
import unittest
from pathlib import Path

from orpheus.autonomy import (
    AutonomousRuntime,
    build_opportunity_plan,
    classify_goal,
    render_decision_markdown,
)
from orpheus.tools import run_reference_mission


class GoalClassificationTests(unittest.TestCase):
    def test_passive_food_cooling_is_supported(self):
        result = classify_goal(
            "Diseña conservación de alimentos con enfriamiento pasivo sin electricidad"
        )
        self.assertTrue(result["supported"])
        self.assertEqual(result["mode"], "verification")

    def test_unrelated_goal_enters_discovery(self):
        result = classify_goal("Crear un tutor de matemáticas para estudiantes")
        self.assertFalse(result["supported"])
        self.assertEqual(result["mode"], "discovery")


class OpportunityPlanTests(unittest.TestCase):
    def test_verified_mission_produces_ranked_benefit_plan(self):
        classification = classify_goal(
            "Conservar alimentos mediante enfriamiento pasivo sin electricidad"
        )
        plan = build_opportunity_plan(
            run_reference_mission(),
            classification=classification,
        )

        self.assertGreaterEqual(len(plan["opportunities"]), 3)
        self.assertIn("selected_opportunity", plan)
        self.assertTrue(
            any(
                action["status"] == "completed"
                and not action["requires_human_approval"]
                for action in plan["actions"]
            )
        )
        self.assertTrue(
            any(
                action["status"] == "awaiting_approval"
                and action["requires_human_approval"]
                for action in plan["actions"]
            )
        )
        self.assertTrue(
            all(item["economics_status"] == "hypothesis" for item in plan["opportunities"])
        )

    def test_external_and_financial_actions_require_approval(self):
        plan = build_opportunity_plan(run_reference_mission())
        gated = [
            action
            for action in plan["actions"]
            if action["kind"] in {"external", "financial"}
        ]
        self.assertTrue(gated)
        self.assertTrue(all(action["requires_human_approval"] for action in gated))


class AutonomousRuntimeTests(unittest.IsolatedAsyncioTestCase):
    async def asyncTearDown(self):
        runtime = getattr(self, "runtime", None)
        if runtime is not None:
            await runtime.shutdown()

    async def test_supported_goal_returns_verified_output(self):
        self.runtime = AutonomousRuntime()
        await self.runtime.set_goal(
            "Conservar alimentos mediante enfriamiento pasivo sin electricidad"
        )
        state = await self.runtime.run_cycle("test")

        self.assertEqual(state["classification"]["mode"], "verification")
        self.assertEqual(state["mission_result"]["mission_status"], "CUMPLIDA")
        self.assertIsNotNone(state["decision_brief"])
        self.assertEqual(len(state["pipeline"]), 10)
        self.assertTrue(all(step["output_summary"] for step in state["pipeline"]))

    async def test_unsupported_goal_does_not_inherit_false_verification(self):
        self.runtime = AutonomousRuntime()
        await self.runtime.set_goal(
            "Crear un sistema de tutoría de matemáticas para adolescentes"
        )
        state = await self.runtime.run_cycle("test")

        self.assertEqual(state["classification"]["mode"], "discovery")
        self.assertEqual(state["mission_result"]["mission_status"], "DESCUBRIMIENTO")
        self.assertIsNone(state["mission_result"]["winner"])
        self.assertEqual(state["decision_brief"]["technical_status"], "discovery")

    async def test_action_can_be_approved_or_declined(self):
        self.runtime = AutonomousRuntime()
        await self.runtime.set_goal(
            "Conservar alimentos mediante enfriamiento pasivo sin electricidad"
        )
        await self.runtime.run_cycle("test")
        approved = await self.runtime.decide_action(
            "contact-pilot-partners",
            "approve",
            "Aprobado para preparar contacto, no para firmar.",
        )
        action = next(
            item
            for item in approved["benefit_plan"]["actions"]
            if item["id"] == "contact-pilot-partners"
        )
        self.assertEqual(action["status"], "approved")
        self.assertIn("preparar contacto", action["decision_note"])

        declined = await self.runtime.decide_action(
            "publish-commercial-offer",
            "decline",
        )
        action = next(
            item
            for item in declined["benefit_plan"]["actions"]
            if item["id"] == "publish-commercial-offer"
        )
        self.assertEqual(action["status"], "declined")

    async def test_run_key_prevents_duplicate_scheduler_cycle(self):
        self.runtime = AutonomousRuntime()
        await self.runtime.set_goal(
            "Conservar alimentos mediante enfriamiento pasivo sin electricidad"
        )
        first = await self.runtime.run_cycle("scheduler", run_key="2026-08-05T18:00")
        second = await self.runtime.run_cycle("scheduler", run_key="2026-08-05T18:00")
        self.assertEqual(first["cycle_number"], second["cycle_number"])

    async def test_state_persists_and_restores(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "state.json"
            self.runtime = AutonomousRuntime(state_path=path)
            await self.runtime.set_goal(
                "Conservar alimentos mediante enfriamiento pasivo sin electricidad"
            )
            await self.runtime.run_cycle("test")
            await self.runtime.shutdown()

            restored = AutonomousRuntime(state_path=path)
            try:
                state = await restored.snapshot()
                self.assertEqual(state["schema_version"], 2)
                self.assertGreaterEqual(state["cycle_number"], 1)
                self.assertIsNotNone(state["decision_brief"])
            finally:
                await restored.shutdown()
            self.runtime = None

    async def test_markdown_export_is_complete(self):
        self.runtime = AutonomousRuntime()
        await self.runtime.set_goal(
            "Conservar alimentos mediante enfriamiento pasivo sin electricidad"
        )
        state = await self.runtime.run_cycle("test")
        markdown = render_decision_markdown(state)
        self.assertIn("Memo de decisión", markdown)
        self.assertIn("Beneficio humano", markdown)
        self.assertIn("Precio hipotético", markdown)


if __name__ == "__main__":
    unittest.main()
