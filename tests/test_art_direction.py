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
        self.agent.self_practice("art focus")
        self.assertTrue(len(self.agent.log.practice_history) > 0)

if __name__ == "__main__":
    unittest.main()
