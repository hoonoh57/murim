import unittest
from pathlib import Path

from src.core.visual_dramaturgy import audit_shot_plan, reference_intro_audit


class VisualMeaningGateTests(unittest.TestCase):
    def test_existing_sehando_intro_flags_repeated_uninformative_image(self):
        p = Path(__file__).resolve().parents[1] / "experiments/mvml_intro_lab/review_v02/intro.mvml.xml"
        v = reference_intro_audit(p)
        self.assertEqual(v["total_seconds"], 60)
        self.assertEqual(v["asset_seconds"]["ART:DETAIL@1"], 32)
        self.assertEqual(v["asset_seconds"]["ART:OBJECT@1"], 18)
        self.assertEqual(v["status"], "REWORK_REQUIRED")
        self.assertIn("UNCHANGED_IMAGE_REEXPOSED", {i["code"] for i in v["issues"]})
        self.assertIn("NO_VERIFIABLE_VIEWER_DISCOVERY", {i["code"] for i in v["issues"]})
        self.assertEqual(v["actual_render_review"], "NOT_RUN")

    def test_new_heading_does_not_cure_same_image(self):
        one = dict(id="a",asset="original",framing="whole",seconds=12,
                   visual_focus="whole painting",new_visual_information="four trees",
                   observed_change="first introduction")
        two = dict(one,id="b",heading="1944",seconds=8,observed_change="")
        self.assertEqual(audit_shot_plan([one,two])["status"],"REWORK_REQUIRED")

    def test_repeat_only_provisional_with_distinct_observed_visual_evidence(self):
        first = dict(id="a",asset="original",framing="whole",seconds=9,
                     visual_focus="house and four trees",
                     new_visual_information="viewer identifies painting composition",
                     observed_change="original displayed")
        second = dict(first,id="b",seconds=9,visual_focus="unnoticed seal near text",
                      new_visual_information="viewer can now identify the seal",
                      observed_change="documented precise reframing on genuine detail")
        result = audit_shot_plan([first,second])
        self.assertEqual(result["status"],"READY_FOR_REAL_VIEWING")
        self.assertEqual(result["actual_render_review"],"NOT_RUN")

    def test_missing_meaning_is_rework_not_a_permitted_long_pause(self):
        result = audit_shot_plan([dict(id="long",asset="painting",framing="whole",
                                       seconds=30,visual_focus="",new_visual_information="")])
        self.assertEqual(result["status"],"REWORK_REQUIRED")

if __name__ == "__main__":
    unittest.main()
