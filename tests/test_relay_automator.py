import unittest
from unittest.mock import MagicMock
from src.relay.relay_client import RelaySession
from src.relay.relay_automator import RelayAutomator

class TestRelayAutomator(unittest.TestCase):
    def setUp(self):
        self.session = RelaySession("Topic", "Events")
        self.mock_ai = MagicMock()

    def test_run_all_success_go(self):
        # Mock responses for Round 1, 2, 3
        self.mock_ai.generate_response.side_effect = [
            '---[RES-001 | WriterAgent]---\n{"title": "T1", "script": "S1", "scenes": []}\n---[END RES-001]---',
            '---[RES-002 | CouncilAgent]---\n{"average_score": 8.5, "verdict": "GO"}\n---[END RES-002]---\n---[RES-003 | ArtDirectionAgent]---\n{}\n---[END RES-003]---\n---[RES-004 | CameraAgent]---\n{}\n---[END RES-004]---',
            '---[RES-005 | ImagingAgent]---\n{}\n---[END RES-005]---'
        ]
        
        automator = RelayAutomator(self.session, self.mock_ai)
        summary = automator.run_all()
        
        self.assertEqual(summary["status"], "completed")
        self.assertEqual(self.mock_ai.generate_response.call_count, 3)
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
        self.assertEqual(summary["status"], "completed")

if __name__ == "__main__":
    unittest.main()
