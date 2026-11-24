import unittest
import os
import tempfile
from src.agents.video import VideoAgent

class TestVideoAgent(unittest.TestCase):
    def setUp(self):
        # Mock Council writes critique and evolution logs; never touch user outputs.
        self._sandbox = tempfile.TemporaryDirectory()
        self.addCleanup(self._sandbox.cleanup)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self._sandbox.name)
        self.agent = VideoAgent(is_mock=True)

    def test_generate_from_image(self):
        path = self.agent.generate_from_image("img.png", "test prompt")
        self.assertIn("mock_video.mp4", path)

    def test_self_practice(self):
        initial_xp = self.agent.log.total_xp
        self.agent.self_practice("motion focus")
        
        self.assertTrue(len(self.agent.log.practice_history) > 0)
        practice = self.agent.log.practice_history[-1]
        
        # Mock Council must remain NOT_EVALUATED; no fabricated reward.
        self.assertEqual(self.agent.log.total_xp, initial_xp)
        self.assertEqual(self.agent.log.current_level, 1)
        self.assertEqual(self.agent.log.total_practices, 1)
        self.assertEqual(len(self.agent.log.practice_history), 1)
        self.assertEqual(practice.scenario.final_score, 0.0)
        self.assertEqual(len(practice.scenario.critiques), len(self.agent.council.personas))
        for critique in practice.scenario.critiques:
            self.assertEqual(critique.score, 0.0)
            self.assertTrue(critique.comment.startswith("NOT_EVALUATED"))
        self.assertTrue(os.path.isfile(self.agent.log_file))
        self.assertTrue(len(practice.self_reflection) > 10)
        self.assertGreaterEqual(practice.scenario.final_score, 0)
        self.assertLessEqual(practice.scenario.final_score, 10)

if __name__ == "__main__":
    unittest.main()
