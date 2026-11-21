"""Dependency-free, non-network unit checks for the one-shot WAN 2.2 probe."""
import copy
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from scripts import prove_comfyui as proof


class TestComfyUIProof(unittest.TestCase):
    def test_only_local_http_allowed(self):
        self.assertEqual(proof.loopback_url("http://127.0.0.1:8188/"),
                         "http://127.0.0.1:8188")
        for url in ("https://127.0.0.1:8188", "http://example.com:8188",
                    "http://127.0.0.1:8188/path", "http://127.0.0.1:8188@evil.test"):
            with self.subTest(url=url), self.assertRaises(proof.ProofError):
                proof.loopback_url(url)

    def test_load_and_build_unchanged_original(self):
        template = proof.load_workflow()
        original = copy.deepcopy(template)
        result = proof.build_workflow(template, "test.png", frames=17, steps=8)
        self.assertEqual(template, original)
        self.assertEqual(result["56"]["inputs"]["image"], "test.png")
        self.assertEqual(result["55"]["inputs"]["length"], 17)
        self.assertEqual(result["3"]["inputs"]["steps"], 8)
        self.assertEqual(result["6"]["inputs"]["text"], proof.PROMPT)
        self.assertTrue(result["58"]["inputs"]["filename_prefix"].startswith("murim_p1/"))

    def test_invalid_frames_are_rejected(self):
        template = proof.load_workflow()
        with self.assertRaises(proof.ProofError):
            proof.build_workflow(template, "x.png", frames=16)

    def test_preflight_reports_missing_models_before_queue(self):
        template = proof.load_workflow()

        class MockAPI:
            def json(self, path):
                if path == "/system_stats":
                    return {"devices": []}
                if path == "/object_info":
                    return {
                        node["class_type"]: {"input": {"required": {
                            field: [["missing_model.safetensors"]]
                            for field in ("unet_name", "clip_name", "vae_name")
                        }}}
                        for node in template.values()
                    }
                raise AssertionError("Unexpected API call " + path)

        with self.assertRaisesRegex(proof.ProofError, r"\[MODEL_MISSING\]"):
            proof.preflight(MockAPI(), template)

    def test_locates_savevideo_under_images(self):
        report = {"outputs": {
            "58": {"images": [{"filename": "clip.mp4", "subfolder": "murim_p1", "type": "output"}]},
            "1": {"images": [{"filename": "image.png"}]},
        }}
        self.assertEqual(proof.locate_video(report)["filename"], "clip.mp4")
        self.assertIsNone(proof.locate_video({"outputs": {"58": {"images": [
            {"filename": "still.png"}]}}}))

    def test_render_fail_is_not_a_success(self):
        class MockAPI:
            def json(self, path):
                return {"abc": {"status": {"status_str": "error", "completed": False,
                                            "messages": ["model load failed"]}}}
        with self.assertRaisesRegex(proof.ProofError, "RENDER_FAIL"):
            proof.await_video(MockAPI(), "abc", 10)

    def test_download_never_deletes_existing_file_on_collision(self):
        class NoNetworkAPI:
            def request(self, *args, **kwargs):
                raise AssertionError("Must not fetch when destination already exists")

        with tempfile.TemporaryDirectory() as tmp:
            from types import SimpleNamespace
            path = Path(tmp) / "p1_aaaaaaaaaaaa_clip.mp4"
            path.write_bytes(b"KEEP_ORIGINAL")
            with patch.object(proof.uuid, "uuid4", return_value=SimpleNamespace(hex="aaaaaaaaaaaa")):
                with self.assertRaises(FileExistsError):
                    proof.save_video(NoNetworkAPI(), {
                        "filename": "clip.mp4", "subfolder": "", "type": "output"
                    }, tmp)
            self.assertEqual(path.read_bytes(), b"KEEP_ORIGINAL")

    def test_png_is_real_and_only_new_file_created(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ref.png"
            proof.make_test_png(path)
            self.assertTrue(path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"))
            with self.assertRaises(FileExistsError):
                proof.make_test_png(path)


if __name__ == "__main__":
    unittest.main()
