import importlib.util
import unittest


@unittest.skipUnless(importlib.util.find_spec("google.adk"), "google-adk not installed")
class AgentContractTests(unittest.TestCase):
    def test_adk_agent_exports_app_and_tools(self):
        from agent_app.agent import app, root_agent

        self.assertEqual("orpheus_omega", root_agent.name)
        self.assertEqual("agent_app", app.name)
        self.assertGreaterEqual(len(root_agent.tools), 5)


if __name__ == "__main__":
    unittest.main()
