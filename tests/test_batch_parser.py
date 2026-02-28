import unittest
import json
from src.relay.batch_parser import BatchParser, ParsedResponse

class TestBatchParser(unittest.TestCase):
    def setUp(self):
        self.parser = BatchParser()

    def test_parse_standard(self):
        raw = """
---[RES-001 | WriterAgent]---
{
  "title": "천마",
  "script": "본격 무협"
}
---[END RES-001]---
"""
        results = self.parser.parse(raw)
        self.assertEqual(len(results), 1)
        self.assertIn("RES-001", results)
        self.assertEqual(results["RES-001"].owner, "WriterAgent")
        self.assertTrue(results["RES-001"].is_json)
        self.assertEqual(results["RES-001"].parsed_json["title"], "천마")

    def test_parse_alphanumeric_id_005R(self):
        raw = """
---[RES-005R | WriterAgent]---
{
  "title": "천마 (수정)",
  "script": "수정된 대본"
}
---[END RES-005R]---
"""
        results = self.parser.parse(raw)
        self.assertEqual(len(results), 1)
        self.assertIn("RES-005R", results)
        self.assertEqual(results["RES-005R"].parsed_json["title"], "천마 (수정)")

    def test_parse_multiple(self):
        raw = """
---[RES-002 | CouncilAgent]---
{"verdict": "GO"}
---[END RES-002]---

---[RES-003 | ArtDirectionAgent]---
{"style": "Dark"}
---[END RES-003]---
"""
        results = self.parser.parse(raw)
        self.assertEqual(len(results), 2)
        self.assertEqual(results["RES-002"].parsed_json["verdict"], "GO")
        self.assertEqual(results["RES-003"].parsed_json["style"], "Dark")

    def test_extract_json_markdown(self):
        text = "여기 JSON이 있습니다: \n```json\n{\"id\": 123}\n```\n끝."
        data = self.parser.extract_json(text)
        self.assertEqual(data["id"], 123)

    def test_extract_json_raw(self):
        text = "평가 결과: {\"score\": 9.5} 입니다."
        data = self.parser.extract_json(text)
        self.assertEqual(data["score"], 9.5)

    def test_fallback_parse_loose(self):
        # 구분자가 불완전한 경우 (---[RES-001] 처럼)
        raw = """
[RES-001 | Writer]
{"title": "불완전"}
RES-002 | Council
{"verdict": "OK"}
"""
        results = self.parser.parse(raw)
        self.assertEqual(len(results), 2)
        self.assertIn("RES-001", results)
        self.assertIn("RES-002", results)
        self.assertEqual(results["RES-001"].owner, "Writer")

    def test_fallback_parse_alphanumeric(self):
        raw = "이것은 클로드의 답변입니다.\nRES-005R | WriterAgent\n{\"title\": \"Re-written\"}\n---[END RES-005R]---"
        results = self.parser.parse(raw)
        self.assertIn("RES-005R", results)
        resp = results["RES-005R"]
        self.assertEqual(resp.owner, "WriterAgent")
        self.assertEqual(resp.parsed_json["title"], "Re-written")

    def test_get_by_owner(self):
        results = {
            "RES-001": ParsedResponse("RES-001", "WriterAgent", "...", {"t": 1})
        }
        resp = self.parser.get_by_owner(results, "writer")
        self.assertIsNotNone(resp)
        self.assertEqual(resp.res_id, "RES-001")

    def test_parsed_response_serialization(self):
        resp = ParsedResponse("RES-001", "Owner", "Raw", {"k": "v"})
        data = resp.to_dict()
        new_resp = ParsedResponse.from_dict(data)
        self.assertEqual(new_resp.res_id, "RES-001")
        self.assertEqual(new_resp.owner, "Owner")
        self.assertEqual(new_resp.parsed_json["k"], "v")

if __name__ == "__main__":
    unittest.main()
