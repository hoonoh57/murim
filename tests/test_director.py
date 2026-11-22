import os
import unittest
from src.agents.director import DirectorAgent
from src.agents.writer import WriterAgent
from src.agents.imaging import ImagingAgent
from src.agents.video import VideoAgent
from src.agents.audio import AudioAgent
from src.agents.camera import CameraAgent
from src.agents.art_direction import ArtDirectionAgent
from src.agents.marketing import MarketingAgent
from src.core.models import ProductionResult

import random

class TestDirectorAgent(unittest.TestCase):
    def setUp(self):
        random.seed(42)
        self.is_mock = True
        self.director = DirectorAgent(is_mock=self.is_mock)
        self.agents = {
            "writer": WriterAgent(is_mock=self.is_mock),
            "imaging": ImagingAgent(is_mock=self.is_mock),
            "video": VideoAgent(is_mock=self.is_mock),
            "audio": AudioAgent(is_mock=self.is_mock),
            "camera": CameraAgent(is_mock=self.is_mock),
            "art_direction": ArtDirectionAgent(is_mock=self.is_mock),
            "marketing": MarketingAgent(is_mock=self.is_mock)
        }

    def tearDown(self):
        # Clean up any potential logs if practice was somehow called
        import os
        for agent in self.agents.values():
            if os.path.exists(agent.log_file):
                os.remove(agent.log_file)

    def test_unapproved_mock_cannot_produce_any_assets(self):
        # A false-positive production result would violate the actual G1/G2 gates.
        self.agents["imaging"].generate = lambda *a, **k: self.fail("image generation crossed HOLD")
        self.agents["video"].generate_from_image = lambda *a, **k: self.fail("video generation crossed HOLD")
        self.agents["audio"].tts = lambda *a, **k: self.fail("audio generation crossed HOLD")
        result = self.director.orchestrate_episode("Test Topic","Test Events",self.agents)
        self.assertIsNone(result)


    def test_check_balance(self):
        report = self.director.check_balance(self.agents)
        self.assertIn("balanced", report)
        self.assertIn("levels", report)

if __name__ == "__main__":
    unittest.main()
