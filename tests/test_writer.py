import unittest
from src.agents.writer import WriterAgent
from src.core.models import Scenario

class TestWriterAgent(unittest.TestCase):
    def setUp(self):
        self.is_mock = True
        self.writer = WriterAgent(is_mock=self.is_mock)

    def test_self_practice_flow(self):
        # 5-step loop: Draft -> Critique 1 -> Revision -> Critique 2 -> Reflection
        result = self.writer.self_practice(focus_point="전투 씬의 긴장감 묘사")
        
        # Check if the result string contains score improvement info
        self.assertIn("습작 및 진화 완료", result)
        self.assertIn("점수 변화", result)
        
        # Verify evolution log has entries
        self.assertTrue(len(self.writer.log.practice_history) > 0)
        practice = self.writer.log.practice_history[-1]
        self.assertEqual(practice.focus_point, "전투 씬의 긴장감 묘사")
        self.assertIsNotNone(practice.self_reflection)
        self.assertIsInstance(practice.scenario, Scenario)

    def test_revise_scenario(self):
        scenario = Scenario(title="Title", synopsis="Syn", script="Script", scenes=[], sound_guide={})
        critiques = [] # Empty list for mock
        revised = self.writer.revise_scenario(scenario, critiques)
        self.assertIsInstance(revised, Scenario)
        self.assertTrue("Revised" in revised.title or "MOCK" in revised.title)

if __name__ == "__main__":
    unittest.main()
