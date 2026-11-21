"""Offline contract checks only; no download, Windows ffmpeg, or GPU render is implied."""
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
PS=(ROOT/'scripts/scail2/preview-scail-sword-candidates.ps1').read_text(encoding='utf-8')
CMD=(ROOT/'scripts/scail2/PREVIEW-SWORD-CANDIDATES.cmd').read_text(encoding='utf-8')
class CandidateReviewContract(unittest.TestCase):
    def test_preview_only_and_candidate_metadata(self):
        for v in ("https://www.pexels.com/download/video/6536346/",
                  "https://www.pexels.com/download/video/5973868/",
                  "CONTACT_SHEETS_READY_ASSETS_NOT_APPROVED",
                  "PENDING_VISUAL_REVIEW", "approved_for_scail = $false",
                  "tile=4x4:nb_frames=16","fps=1","source_sha256"):
            self.assertIn(v, PS)
    def test_strict_isolated_scope_and_no_unapproved_writes(self):
        self.assertIn("$ExpectedRoot = 'E:\\comfyui-scail'", PS)
        self.assertIn("samples\\sword-candidate-review", PS)
        for v in ("ComfyUI\\input\\", "ComfyUI_New", "Remove-Item", "git clean",
                  "reset --hard", "start-scail2.cmd"):
            self.assertNotIn(v, PS)
        self.assertIn("preview-scail-sword-candidates.ps1", CMD)
        self.assertIn("pause >nul", CMD)
if __name__ == '__main__':
    unittest.main()
