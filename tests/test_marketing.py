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
        initial_xp = self.agent.log.total_xp
        self.agent.self_practice("marketing focus")
        
        self.assertTrue(len(self.agent.log.practice_history) > 0)
        practice = self.agent.log.practice_history[-1]
        
        self.assertGreater(self.agent.log.total_xp, initial_xp)
        self.assertTrue(len(practice.self_reflection) > 10)
        self.assertGreaterEqual(practice.scenario.final_score, 0)
        self.assertLessEqual(practice.scenario.final_score, 10)

    def tearDown(self):
        import os
        if os.path.exists(self.agent.log_file):
            os.remove(self.agent.log_file)

if __name__ == "__main__":
    unittest.main()
