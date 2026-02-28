import unittest
from unittest.mock import MagicMock
from src.relay.relay_client import RelaySession

class TestRelaySession(unittest.TestCase):
    def setUp(self):
        self.session = RelaySession("Topic", "Events")

    def test_initialization(self):
        self.assertEqual(self.session.status, "initialized")
        self.assertEqual(self.session.topic, "Topic")

    def test_start_round1(self):
        prompt = self.session.start_round1()
        self.assertEqual(self.session.status, "round1")
        self.assertEqual(self.session.current_round, 1)
        self.assertIn("Round 1", prompt)

    def test_process_round1_response_success(self):
        self.session.start_round1()
        # Mock Round 1 response
        raw_response = """
---[RES-001 | WriterAgent]---
{
  "title": "천마강림",
  "script": "대본 내용",
  "scenes": [{"id": "S01", "description": "D"}]
}
---[END RES-001]---
"""
        result = self.session.process_round1_response(raw_response)
        self.assertTrue(result["success"])
        # Note: RelaySession doesn't automatically transition status to round2 after process_round1_response,
        # it stays at the current round until the next start_roundX call.
        self.assertEqual(self.session.scenario_json["title"], "천마강림")

    def test_process_round2_and_rework_logic(self):
        self.session.scenario_json = {"title": "T", "scenes": []}
        self.session.start_round2()
        
        # Scenario with low score
        raw_response = """
---[RES-002 | CouncilAgent]---
{"average_score": 6.5, "verdict": "REWORK"}
---[END RES-002]---
"""
        result = self.session.process_round2_response(raw_response)
        self.assertTrue(result["success"])
        self.assertTrue(result["needs_rework"])
        
        # Start round 3 (rework path)
        prompt = self.session.start_round3()
        self.assertEqual(self.session.rework_count, 1)
        self.assertIn("REQ-005R", prompt)

    def test_get_summary(self):
        summary = self.session.get_summary()
        self.assertEqual(summary["topic"], "Topic")
        self.assertIn("status", summary)

if __name__ == "__main__":
    unittest.main()
