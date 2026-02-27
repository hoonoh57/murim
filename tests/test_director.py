import os
import unittest
from src.agents.director import DirectorAgent
from src.agents.writer import WriterAgent
from src.agents.imaging import ImagingAgent
from src.agents.video import VideoAgent
from src.agents.audio import AudioAgent
from src.core.models import ProductionResult

class TestDirectorAgent(unittest.TestCase):
    def setUp(self):
        self.is_mock = True
        self.director = DirectorAgent(is_mock=self.is_mock)
        self.agents = {
            "writer": WriterAgent(is_mock=self.is_mock),
            "imaging": ImagingAgent(is_mock=self.is_mock),
            "video": VideoAgent(is_mock=self.is_mock),
            "audio": AudioAgent(is_mock=self.is_mock)
        }

    def test_orchestrate_episode_success(self):
        topic = "Test Topic"
        events = "Test Events"
        result = self.director.orchestrate_episode(topic, events, self.agents)
        
        self.assertIsInstance(result, ProductionResult)
        self.assertEqual(result.status, "success")
        self.assertTrue(len(result.image_paths) > 0)
        self.assertIsNotNone(result.audio_path)
        self.assertIn("images", result.scenario.assets)

    def test_check_balance(self):
        report = self.director.check_balance(self.agents)
        self.assertIn("balanced", report)
        self.assertIn("levels", report)

if __name__ == "__main__":
    unittest.main()
