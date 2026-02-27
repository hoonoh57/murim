import unittest
from src.agents.art_direction import ArtDirectionAgent

class TestArtDirectionAgent(unittest.TestCase):
    def setUp(self):
        self.agent = ArtDirectionAgent(is_mock=True)

    def test_design_style_guide(self):
        guide = self.agent.design_style_guide("worldview")
        self.assertIn("palette", guide)
        self.assertIn("style", guide)

    def test_self_practice(self):
        initial_xp = self.agent.log.total_xp
        self.agent.self_practice("art focus")
        
        self.assertTrue(len(self.agent.log.practice_history) > 0)
        practice = self.agent.log.practice_history[-1]
        
        self.assertGreater(self.agent.log.total_xp, initial_xp)
        self.assertTrue(len(practice.self_reflection) > 5)
        self.assertGreaterEqual(practice.scenario.final_score, 0)
        self.assertLessEqual(practice.scenario.final_score, 10)

if __name__ == "__main__":
    unittest.main()
