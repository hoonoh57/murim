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
        self.agent.self_practice("audio focus")
        self.assertTrue(len(self.agent.log.practice_history) > 0)

if __name__ == "__main__":
    unittest.main()
