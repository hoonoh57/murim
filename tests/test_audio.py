import unittest
from src.agents.audio import AudioAgent

class TestAudioAgent(unittest.TestCase):
    def setUp(self):
        self.agent = AudioAgent(is_mock=True)

    def test_tts(self):
        path = self.agent.tts("hello")
        self.assertIn(".mp3", path)

    def test_generate_bgm(self):
        path = self.agent.generate_bgm("epic")
        self.assertIn("bgm_mock.mp3", path)

    def test_self_practice(self):
        initial_xp = self.agent.log.total_xp
        self.agent.self_practice("audio focus")
        
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
