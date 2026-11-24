import unittest
from unittest.mock import MagicMock
from src.relay.relay_client import RelaySession
from src.relay.relay_automator import RelayAutomator

class TestRelayAutomator(unittest.TestCase):
    def setUp(self):
        self.session = RelaySession("Topic", "Events")
        self.mock_ai = MagicMock()

    def test_run_all_go_requires_studio_approval(self):
        # Mock responses for Round 1, 2, 3
        self.mock_ai.generate_response.side_effect = [
            '---[RES-001 | WriterAgent]---\n{"title": "T1", "script": "S1", "scenes": []}\n---[END RES-001]---',
            '---[RES-002 | CouncilAgent]---\n{"average_score": 9.8, "verdict": "GO"}\n---[END RES-002]---\n---[RES-003 | ArtDirectionAgent]---\n{}\n---[END RES-003]---\n---[RES-004 | CameraAgent]---\n{}\n---[END RES-004]---',
            '---[RES-005 | ImagingAgent]---\n{}\n---[END RES-005]---'
        ]
        
        automator = RelayAutomator(self.session, self.mock_ai)
        summary = automator.run_all()
        
        self.assertEqual(summary["status"], "hold")
        self.assertEqual(self.mock_ai.generate_response.call_count, 2)
        self.assertIsNone(summary["imaging"])
        self.assertEqual(summary["scenario"]["title"], "T1")

    def test_run_all_with_rework(self):
        # Round 1, Round 2 (Rework), Round 3 (Rework Scenario), Round 2 (GO), Round 3 (Final)
        self.mock_ai.generate_response.side_effect = [
            '---[RES-001 | WriterAgent]---\n{"title": "Initial", "scenes": []}\n---[END RES-001]---',
            '---[RES-002 | CouncilAgent]---\n{"average_score": 6.0, "verdict": "REWORK"}\n---[END RES-002]---',
            '---[RES-005R | WriterAgent]---\n{"title": "Improved", "scenes": []}\n---[END RES-005R]---',
            '---[RES-002 | CouncilAgent]---\n{"average_score": 9.0, "verdict": "GO"}\n---[END RES-002]---',
            '---[RES-005 | ImagingAgent]---\n{}\n---[END RES-005]---'
        ]
        
        automator = RelayAutomator(self.session, self.mock_ai)
        summary = automator.run_all(max_reworks=1)
        
        self.assertEqual(summary["rework_count"], 1)
        self.assertEqual(summary["scenario"]["title"], "Improved")
        self.assertEqual(summary["status"], "hold")
        self.assertEqual(self.mock_ai.generate_response.call_count, 4)
        self.assertIsNone(summary["imaging"])

    def test_missing_evaluation_stops_before_resource_request(self):
        self.mock_ai.generate_response.side_effect = [
            '---[RES-001 | WriterAgent]---\n{"title":"T","script":"S","scenes":[]}\n---[END RES-001]---',
            "invalid evaluation",
        ]
        summary = RelayAutomator(self.session, self.mock_ai).run_all()
        self.assertEqual(summary["status"], "hold")
        self.assertEqual(self.mock_ai.generate_response.call_count, 2)

    def test_run_all_killed(self):
        # Round 1 (OK), Round 2 (KILL)
        self.mock_ai.generate_response.side_effect = [
            '---[RES-001 | WriterAgent]---\n{"title": "Initial", "scenes": []}\n---[END RES-001]---',
            '---[RES-002 | CouncilAgent]---\n{"average_score": 5.0, "verdict": "KILL"}\n---[END RES-002]---'
        ]
        
        automator = RelayAutomator(self.session, self.mock_ai)
        summary = automator.run_all()
        
        self.assertEqual(summary["status"], "killed")
        self.assertEqual(self.mock_ai.generate_response.call_count, 2)

if __name__ == "__main__":
    unittest.main()
