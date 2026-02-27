import unittest
from src.agents.imaging import ImagingAgent
from src.core.models import Scenario

class TestImagingAgent(unittest.TestCase):
    def setUp(self):
        self.agent = ImagingAgent(is_mock=True)

    def test_generate(self):
        prompt = "test prompt"
        path = self.agent.generate(prompt)
        self.assertIn("mock_image.png", path)

    def test_self_practice(self):
        initial_xp = self.agent.log.total_xp
        self.agent.self_practice("visual focus")
        
        self.assertTrue(len(self.agent.log.practice_history) > 0)
        practice = self.agent.log.practice_history[-1]
        
        self.assertGreater(self.agent.log.total_xp, initial_xp)
        self.assertTrue(len(practice.self_reflection) > 10)
        self.assertGreaterEqual(practice.scenario.final_score, 0)
        self.assertLessEqual(practice.scenario.final_score, 10)

if __name__ == "__main__":
    unittest.main()
