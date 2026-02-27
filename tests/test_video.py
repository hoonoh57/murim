import unittest
from src.agents.video import VideoAgent

class TestVideoAgent(unittest.TestCase):
    def setUp(self):
        self.agent = VideoAgent(is_mock=True)

    def test_generate_from_image(self):
        path = self.agent.generate_from_image("img.png", "test prompt")
        self.assertIn("mock_video.mp4", path)

    def test_self_practice(self):
        self.agent.self_practice("motion focus")
        self.assertTrue(len(self.agent.log.practice_history) > 0)

if __name__ == "__main__":
    unittest.main()
