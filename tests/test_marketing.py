import unittest
from src.agents.marketing import MarketingAgent
from src.core.models import Scenario

class TestMarketingAgent(unittest.TestCase):
    def setUp(self):
        self.agent = MarketingAgent(is_mock=True)

    def test_generate_assets(self):
        scenario = Scenario(title="Title", synopsis="Syn", script="Script", scenes=[], sound_guide={})
        assets = self.agent.generate_assets(scenario)
        self.assertIn("title", assets)

    def test_self_practice(self):
        self.agent.self_practice("marketing focus")
        self.assertTrue(len(self.agent.log.practice_history) > 0)

if __name__ == "__main__":
    unittest.main()
