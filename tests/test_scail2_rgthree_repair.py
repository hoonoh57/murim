"""Offline contract assertions for the isolated rgthree missing-node repair.

No PowerShell execution, GPU process, or ComfyUI render is implied by these tests.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1] / 'scripts' / 'scail2'
REPAIR = (ROOT / 'repair-rgthree.ps1').read_text(encoding='utf-8')
CMD = (ROOT / 'REPAIR-RGTHREE.cmd').read_text(encoding='utf-8')
INSTALL = (ROOT / 'install-scail2.ps1').read_text(encoding='utf-8')
PIN = 'bc48c6aaeca87bedbc14245d89f9bc6be37a630e'


class MissingNodeRecoveryTests(unittest.TestCase):
    def test_pinned_rgthree_on_first_setup_and_repair(self):
        for script in (INSTALL, REPAIR):
            self.assertIn('rgthree-comfy', script)
            self.assertIn(PIN, script)
        self.assertIn('RgthreeDisplayInt.NAME', REPAIR)
        self.assertIn('Display Int (rgthree)', REPAIR)

    def test_isolation_and_fail_closed_prechecks(self):
        self.assertIn("$ExpectedRoot = 'E:\\comfyui-scail'", REPAIR)
        self.assertIn('PORT_8189_IN_USE', REPAIR)
        self.assertIn('EXISTING_EXTENSION_CONFLICT', REPAIR)
        self.assertIn('RGTHREE_LOCAL_CHANGES', REPAIR)
        for forbidden in ('Remove-Item', 'reset --hard', 'git clean', 'force-push'):
            self.assertNotIn(forbidden, REPAIR)

    def test_startup_and_node_registry_not_render(self):
        self.assertIn('start-scail2.cmd', REPAIR)
        self.assertIn('STARTUP_NODE_VERIFIED_NOT_RENDERED', REPAIR)
        for node in ('Display Int (rgthree)', 'WanSCAILToVideo', 'SCAIL2EasyConfig'):
            self.assertIn(node, REPAIR)
        self.assertIn('/object_info', REPAIR)
        self.assertIn('powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass', CMD)


if __name__ == '__main__':
    unittest.main()
