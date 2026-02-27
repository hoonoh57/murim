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
        self.agent.self_practice("visual focus")
        self.assertTrue(len(self.agent.log.practice_history) > 0)

if __name__ == "__main__":
    unittest.main()
