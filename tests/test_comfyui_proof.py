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

    def test_quality_preset_preserves_source_and_uses_real_reference_settings(self):
        original = proof.load_workflow()
        before = copy.deepcopy(original)
        result = proof.build_workflow(
            original, "real.png", steps=24, frames=33, width=576, height=768,
            prompt=proof.QUALITY_PROMPT, label="quality")
        self.assertEqual(original, before)
        self.assertEqual(result["55"]["inputs"]["width"], 576)
        self.assertEqual(result["55"]["inputs"]["height"], 768)
        self.assertEqual(result["55"]["inputs"]["length"], 33)
        self.assertEqual(result["3"]["inputs"]["steps"], 24)
        self.assertIn("reference image", result["6"]["inputs"]["text"])
        self.assertTrue(result["58"]["inputs"]["filename_prefix"].startswith("murim_p1/quality_"))

    def test_quality_png_is_real_and_orientation_sensitive(self):
        import struct
        with tempfile.TemporaryDirectory() as tmp:
            photo = Path(tmp) / "ref.png"
            # Header-only fixture: metadata inspection never decodes or rewrites pixels.
            photo.write_bytes(b"\x89PNG\r\n\x1a\n" + struct.pack(">I", 13)
                              + b"IHDR" + struct.pack(">II", 896, 1152))
            self.assertEqual(proof.quality_resolution(photo), (576, 768))
            photo.write_bytes(b"\x89PNG\r\n\x1a\n" + struct.pack(">I", 13)
                              + b"IHDR" + struct.pack(">II", 1536, 864))
            self.assertEqual(proof.quality_resolution(photo), (832, 480))
            photo.write_bytes(b"\xff\xd8\xff\xe0" + b"JPEG-content")
            with self.assertRaisesRegex(proof.ProofError, "genuine PNG"):
                proof.quality_resolution(photo)

    def test_quality_requires_reference_and_resolution_validation(self):
        with patch.object(proof, "LocalAPI", side_effect=AssertionError("No network expected")):
            with self.assertRaisesRegex(proof.ProofError, "QUALITY_REFERENCE_REQUIRED"):
                proof.main(["--quality"])
        with self.assertRaisesRegex(proof.ProofError, "RESOLUTION"):
            proof.build_workflow(proof.load_workflow(), "real.png",
                                 width=513, height=768)

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
