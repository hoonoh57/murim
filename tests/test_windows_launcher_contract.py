"""Regression guard for the Windows CMD-to-PS5.1 launcher path contract."""
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class WindowsLauncherContractTest(unittest.TestCase):
    def test_root_is_resolved_by_powershell_without_quoted_trailing_backslash(self):
        cmd = (ROOT / "windows-test.cmd").read_text(encoding="utf-8")
        ps = (ROOT / "scripts" / "windows-sync-test.ps1").read_text(encoding="utf-8-sig")
        self.assertIn('"%~dp0scripts\\windows-sync-test.ps1"', cmd)
        self.assertNotIn('-Workspace "%REPO_DIR%"', cmd)
        self.assertIn('Split-Path -Parent $PSScriptRoot', ps)
        self.assertIn('merge", "--ff-only"', ps)
        self.assertIn('--untracked-files=all', ps)


if __name__ == "__main__":
    unittest.main()
