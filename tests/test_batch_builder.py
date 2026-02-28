import unittest
import json
from src.relay.batch_builder import BatchBuilder, BatchRequest

class TestBatchBuilder(unittest.TestCase):
    def setUp(self):
        self.builder = BatchBuilder()

    def test_build_round1(self):
        requests = self.builder.build_round1("천마의 회귀", "1화: 회귀")
        self.assertEqual(len(requests), 1)
        req = requests[0]
        self.assertEqual(req.req_id, "REQ-001")
        self.assertEqual(req.owner, "WriterAgent")
        self.assertIn("천마의 회귀", req.user_msg)

    def test_build_round2(self):
        scenario = {"title": "천마강림", "script": "...", "scenes": [{"id": "S01"}]}
        requests = self.builder.build_round2(scenario)
        # REQ-002 (Council), REQ-003 (Art), REQ-004 (Camera)
        self.assertEqual(len(requests), 3)
        req_ids = [r.req_id for r in requests]
        self.assertIn("REQ-002", req_ids)
        self.assertIn("REQ-003", req_ids)
        self.assertIn("REQ-004", req_ids)

    def test_build_round3_go(self):
        scenario = {"title": "T", "script": "S", "scenes": [{"id": "S01"}]}
        council = {"average_score": 8.5, "verdict": "GO"}
        style = {"style": "Dark"}
        camera = {"camera_plans": []}
        
        requests = self.builder.build_round3(scenario, council, style, camera, needs_rework=False)
        # REQ-005 (Imaging), REQ-006 (Video), REQ-007 (Audio), REQ-008 (Marketing)
        self.assertEqual(len(requests), 4)
        req_ids = [r.req_id for r in requests]
        self.assertIn("REQ-005", req_ids)
        self.assertIn("REQ-008", req_ids)

    def test_build_round3_rework(self):
        scenario = {"title": "T", "script": "S", "scenes": []}
        council = {"average_score": 6.5, "verdict": "REWORK"}
        
        requests = self.builder.build_round3(scenario, council, {}, {}, needs_rework=True)
        self.assertEqual(len(requests), 1)
        self.assertEqual(requests[0].req_id, "REQ-005R")
        self.assertEqual(requests[0].owner, "WriterAgent")

    def test_format_batch(self):
        reqs = [BatchRequest("REQ-001", "Writer", "G1", "Sys", "User", "json")]
        formatted = self.builder.format_batch(reqs, 1)
        self.assertIn("Round 1", formatted)
        self.assertIn("---[RES-001 | WriterAgent]---", formatted) # Example section
        self.assertIn("---[RES-001 | Writer]---", formatted) # Guide section
        self.assertIn("---[REQ-001 | Writer | G1]---", formatted) # Actual request

if __name__ == "__main__":
    unittest.main()
