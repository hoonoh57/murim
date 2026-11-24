import unittest
import json
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

    def test_force_go_is_denied(self):
        self.session.scenario_json = {"title": "T", "script": "S"}
        self.session.start_round2()
        self.session.council_json = {"average_score": 10, "verdict": "GO"}
        self.assertIsNone(self.session.start_round3(force_go=True))
        self.assertEqual(self.session.status, "hold")

    def test_old_round3_cannot_register_resource_response(self):
        self.session.current_round = 3
        self.session.status = "round3"
        result = self.session.process_round3_response('---[RES-005 | ImagingAgent]---\n{"enhanced_prompts":[]}\n---[END RES-005]---')
        self.assertFalse(result["success"])
        self.assertEqual(self.session.status, "hold")
        self.assertIsNone(self.session.imaging_json)

    def test_malformed_review_fails_closed(self):
        def block(number, owner, payload):
            return f"---[RES-{number} | {owner}]---\n```json\n{json.dumps(payload)}\n```\n---[END RES-{number}]---"
        valid = block("002", "CouncilAgent", {"average_score": 8, "verdict": "REWORK"})
        cases = [
            "",
            block("002", "CouncilAgent", [1]),
            block("002", "CouncilAgent", {"average_score": 10**400, "verdict": "GO"}),
            block("002", "CouncilAgent", {"average_score": float("nan"), "verdict": "GO"}),
            valid + "\n" + block("003", "CameraAgent", {"camera_plans": None}),
            valid + "\n" + block("004", "ArtDirectionAgent", [1]),
        ]
        for raw in cases:
            with self.subTest(raw=raw[:80]):
                session = RelaySession("T", "E")
                session.scenario_json = {"title": "T", "script": "S", "scenes": []}
                session.start_round2()
                self.assertFalse(session.process_round2_response(raw)["success"])
                self.assertEqual(session.status, "hold")
                self.assertIsNone(session.council_json)
                self.assertIsNone(session.start_round3())

    def test_restored_invalid_evaluation_cannot_start_round3(self):
        for council in ([1], {"average_score": 10**400, "verdict": "GO"}):
            with self.subTest(council=council):
                session = RelaySession("T", "E")
                session.scenario_json = {"title": "T", "script": "S", "scenes": []}
                session.start_round2()
                data = session.to_dict()
                data["council"] = council
                restored = RelaySession.from_dict(data)
                self.assertIsNone(restored.start_round3())
                self.assertEqual(restored.status, "hold")

    def test_stale_review_response_cannot_reopen_hold(self):
        self.session.scenario_json = {"title": "T", "script": "S", "scenes": []}
        self.session.start_round2()
        self.session.hold("test hold")
        raw = '---[RES-002 | CouncilAgent]---\n{"average_score":7,"verdict":"REWORK"}\n---[END RES-002]---'
        self.assertFalse(self.session.process_round2_response(raw)["success"])
        self.assertIsNone(self.session.start_round3())

    def test_serialization(self):
        self.session.start_round1()
        data = self.session.to_dict()
        self.assertEqual(data["topic"], "Topic")
        self.assertEqual(data["status"], "round1")
        
        new_session = RelaySession.from_dict(data)
        self.assertEqual(new_session.topic, "Topic")
        self.assertEqual(new_session.status, "round1")
        self.assertEqual(new_session.current_round, 1)

if __name__ == "__main__":
    unittest.main()
