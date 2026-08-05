import asyncio
import unittest

from orpheus.autonomy import AutonomousRuntime, build_opportunity_plan
from orpheus.tools import run_reference_mission


class OpportunityPlanTests(unittest.TestCase):
    def test_verified_mission_produces_ranked_benefit_plan(self):
        plan = build_opportunity_plan(run_reference_mission())

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

    async def test_runtime_autostarts_cycle_and_returns_output(self):
        self.runtime = AutonomousRuntime()
        await self.runtime.start()
        await asyncio.sleep(0.1)
        state = await self.runtime.snapshot()

        self.assertTrue(state["enabled"])
        self.assertGreaterEqual(state["cycle_number"], 1)
        self.assertIsNotNone(state["mission_result"])
        self.assertIsNotNone(state["benefit_plan"])

    async def test_human_can_approve_gated_action(self):
        self.runtime = AutonomousRuntime()
        await self.runtime.run_cycle("test")
        state = await self.runtime.approve("contact-pilot-partners")

        action = next(
            item
            for item in state["benefit_plan"]["actions"]
            if item["id"] == "contact-pilot-partners"
        )
        self.assertEqual(action["status"], "approved")


if __name__ == "__main__":
    unittest.main()
