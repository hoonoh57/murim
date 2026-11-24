"""GPT-style Director facade regression checks; no GPU, remote LLM or external services."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch as mock_patch

from flask import Flask

from src.studio import director_simple as director
from src.studio.editorial import Editorial, AXES, FIELDS
from src.studio.workspace import Store, assets, get_scene, register_asset, track


class DirectorSimpleTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = Store(self.temp.name)
        self.pid = self.store.create("청명 연구")
        self.patcher = mock_patch.object(director, "store", self.store)
        self.patcher.start()
        self.app = Flask(__name__, template_folder="../../templates")
        self.app.register_blueprint(director.BP)
        self.client = self.app.test_client()
        self.headers = {"X-Murim-Studio": director.TOKEN}
        self.editorial = Editorial(self.store, self.pid)

    def tearDown(self):
        self.patcher.stop()
        self.temp.cleanup()

    def post(self, suffix, **values):
        return self.client.post("/studio/simple/api/project/" + self.pid + suffix,
                                json=values, headers=self.headers)

    def view(self):
        response = self.client.get("/studio/simple/api/project/" + self.pid)
        self.assertEqual(response.status_code, 200, response.get_json())
        return response.get_json()

    def approve_scenario(self):
        original = self.editorial.view()
        p = copy.deepcopy(original["latest"]["plan"])
        for key in FIELDS:
            p[key] = "청명 독립 장면 설계 " + key
        for scene in p["scenes"]:
            scene.update(title="매화만개", narration="서사적 선택의 순간", subtitle="서사적 선택의 순간",
                         visual="검을 쥔 청명과 배경", sound="검기와 바람",
                         facts="창작 무협, 역사적 사실 아님")
        self.editorial.mutate(original["token"], "plan", {"plan": p, "note": "실제 시나리오 초안"})
        current = self.editorial.view()
        review = {"revision": current["latest"]["revision"], "scores": {key: 10 for key in AXES},
                  "evidence": "독립 검토 fixture", "issues": [], "resolutions": [], "verdict": "PASS"}
        self.editorial.mutate(current["token"], "review",
                              {"raw": json.dumps(review), "reviewer": "fixture independent"})
        current = self.editorial.view()
        self.editorial.mutate(current["token"], "approval",
                              {"confirmed": True, "approver": "fixture human",
                               "mvml_revision": current["mvml_revision"]})
        return p

    def fake_asset(self, kind="image"):
        base = self.store.folder(self.pid) / "imports" / kind
        base.mkdir(parents=True, exist_ok=True)
        suffix = ".png" if kind == "image" else ".mp4"
        path = base / ("sample" + suffix)
        path.write_bytes(b"real-test-file-bytes-" + kind.encode())
        doc, rev = self.store.load(self.pid)
        aid = register_asset(doc, self.store.root, path, kind,
                             kind + " test", "test fixture", "test rights")
        self.store.save(self.pid, doc, rev)
        return aid

    def add_and_select(self, role, aid, scene=None):
        info = self.view()
        created = self.post("/candidate", director_token=info["director_token"],
                            asset=aid, role=role, scene=scene, label="검증 후보")
        self.assertEqual(created.status_code, 200, created.get_json())
        chosen = self.post("/select", director_token=created.get_json()["director_token"],
                           candidate=created.get_json()["candidate"]["id"])
        self.assertEqual(chosen.status_code, 200, chosen.get_json())

    def test_preproduction_gate_blocks_storyboard(self):
        aid = self.fake_asset()
        info = self.view()
        response = self.post("/candidate", director_token=info["director_token"],
                             role="character", asset=aid)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(info["editorial"]["approved"])
        self.assertFalse(info["storyboard_ready"])

    def test_mutation_requires_local_token(self):
        response = self.client.post("/studio/simple/api/projects", json={"title": "unauthorized"})
        self.assertEqual(response.status_code, 403)

    def test_project_crud_is_reversible_and_keeps_original(self):
        info = self.view()
        changed = self.post("/project-action", action="rename", title="청명 검술",
                            revision=info["project"]["revision"],
                            director_token=info["director_token"])
        self.assertEqual(changed.status_code, 200, changed.get_json())
        info = self.view()
        self.assertEqual(info["project"]["title"], "청명 검술")
        archive = self.post("/project-action", action="archive",
                            director_token=info["director_token"])
        self.assertEqual(archive.status_code, 200)
        self.assertTrue(self.view()["director"]["archived"])
        token = self.view()["director_token"]
        restore = self.post("/project-action", action="restore", director_token=token)
        self.assertEqual(restore.status_code, 200)
        self.assertFalse(self.view()["director"]["archived"])
        self.assertGreaterEqual(len(self.store.revisions(self.pid)), 2)

    def test_selected_images_become_actual_vml_tracks(self):
        plan = self.approve_scenario()
        aid = self.fake_asset()
        self.add_and_select("character", aid)
        self.add_and_select("style", aid)
        for scene in plan["scenes"]:
            self.add_and_select("scene", aid, scene["id"])
        info = self.view()
        confirmed = self.post("/confirm", director_token=info["director_token"],
                              revision=info["project"]["revision"],
                              confirmed=True, approver="fixture user")
        self.assertEqual(confirmed.status_code, 200, confirmed.get_json())
        after = self.view()
        self.assertTrue(after["storyboard_ready"])
        doc, _ = self.store.load(self.pid)
        for scene in plan["scenes"]:
            self.assertEqual(track(get_scene(doc, scene["id"]), "image").get("asset"), aid)
        production = self.client.get("/studio/simple/api/project/" + self.pid + "/production")
        self.assertEqual(production.status_code, 200)
        self.assertEqual(production.get_json()["state"], "HUMAN_RELAY_UNTIL_WORKFLOW_VALIDATED")
        self.assertEqual(production.get_json()["shots"][0]["status"], "HUMAN_RELAY_REQUIRED")

    def test_stale_revision_and_unapproved_video_rejected(self):
        self.approve_scenario()
        aid = self.fake_asset("video")
        bad = self.post("/attach-video", revision=self.view()["project"]["revision"],
                        scene=self.view()["editorial"]["scenes"][0]["id"], asset=aid)
        self.assertEqual(bad.status_code, 400)
        self.assertFalse(self.view()["storyboard_ready"])
        stale = self.post("/project-action", action="archive", director_token="stale")
        self.assertEqual(stale.status_code, 400)


if __name__ == "__main__":
    unittest.main()
