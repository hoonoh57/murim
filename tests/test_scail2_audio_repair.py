"""Offline contract checks: SCAIL-2 demo video contains no audio and must be remuxed safely.

These tests do not claim to run Windows, ComfyUI, or a GPU render.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1] / "scripts" / "scail2"
PS = (ROOT / "repair-scail-audio.ps1").read_text(encoding="utf-8")
CMD = (ROOT / "REPAIR-SCAIL-AUDIO.cmd").read_text(encoding="utf-8")

class ScailAudioRepairTests(unittest.TestCase):
    def test_video_copy_silent_audio_and_verify(self):
        for term in ("anullsrc=r=48000:cl=stereo", "'-c:v','copy'", "'-c:a','aac'",
                     "'-shortest'", "FFPROBE_BINARY_MISSING", "POSTREPAIR_PROBE_FAILED"):
            self.assertIn(term, PS)
        self.assertIn("INPUT_AUDIO_VERIFIED_NOT_RENDERED", PS)
        self.assertIn("STARTUP_AND_INPUT_AUDIO_VERIFIED_NOT_RENDERED", PS)

    def test_restore_and_user_data_protection(self):
        for term in ("[USER_INPUT_CHANGED]", "[BACKUP_CONFLICT]", "Get-FileHash",
                     "[IO.File]::Replace", "your_driving_video.before_silent_audio.mp4"):
            self.assertIn(term, PS)
        for banned in ("Remove-Item", "git clean", "git reset", "Set-ExecutionPolicy"):
            self.assertNotIn(banned, PS)

    def test_scope_and_easy_restart(self):
        self.assertIn("$ExpectedRoot = 'E:\\comfyui-scail'", PS)
        self.assertIn("[PORT_8189_IN_USE]", PS)
        self.assertIn("start-scail2.cmd", PS)
        self.assertIn("'VHS_LoadVideo'", PS)
        self.assertIn("'SCAIL2EasyConfig'", PS)
        self.assertIn("'Display Int (rgthree)'", PS)
        self.assertIn("powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass", CMD)

if __name__ == "__main__":
    unittest.main()
