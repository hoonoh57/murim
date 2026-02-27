import unittest
from src.agents.video import VideoAgent

class TestVideoAgent(unittest.TestCase):
    def setUp(self):
        self.agent = VideoAgent(is_mock=True)

    def test_generate_from_image(self):
        path = self.agent.generate_from_image("img.png", "test prompt")
        self.assertIn("mock_video.mp4", path)

    def test_self_practice(self):
        initial_xp = self.agent.log.total_xp
        self.agent.self_practice("motion focus")
        
        self.assertTrue(len(self.agent.log.practice_history) > 0)
        practice = self.agent.log.practice_history[-1]
        
        self.assertGreater(self.agent.log.total_xp, initial_xp)
        self.assertTrue(len(practice.self_reflection) > 10)
        self.assertGreaterEqual(practice.scenario.final_score, 0)
        self.assertLessEqual(practice.scenario.final_score, 10)

if __name__ == "__main__":
    unittest.main()
