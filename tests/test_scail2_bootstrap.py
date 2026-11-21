"""Offline checks of the version-pinned, isolated SCAIL-2 bootstrap contract.

These do not purport to run PowerShell, install ComfyUI, or validate GPU output.
"""
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parent
PS1 = (ROOT / 'install-scail2.ps1').read_text(encoding='utf-8')
CMD = (ROOT / 'INSTALL-SCAIL2.cmd').read_text(encoding='utf-8')

class InstallerContractTests(unittest.TestCase):
    def test_isolated_root_and_legacy_preservation(self):
        self.assertIn("$ExpectedRoot = 'E:\\comfyui-scail'", PS1)
        self.assertIn("$Old = 'E:\\ComfyUI_New\\ComfyUI'", PS1)
        self.assertNotIn('mklink', PS1.lower())
        self.assertNotIn('reset --hard', PS1.lower())
        self.assertNotIn('Remove-Item', PS1)
        self.assertIn('extra_model_paths.yaml', PS1)

    def test_pins_and_cuda_versions(self):
        for tag in ('v0.33.1', 'torch==2.8.0', 'torchvision==0.23.0',
                    'torchaudio==2.8.0', 'cu126', 'python-3.12.10-amd64.exe',
                    'SCAIL-2-Q3_K_M.gguf', 'sam3.1_multiplex_fp16.safetensors',
                    'Wan21_I2V_14B_lightx2v_cfg_step_distill_lora_rank64.safetensors'):
            self.assertIn(tag if tag != 'v0.33.1' else "version='0.33.1'", PS1)
        self.assertIn('2a0d3c0d613e206b4222d61462cf214304488ffd', PS1)
        self.assertIn('72865f4f27eaf5396f8f36370e0a2be3a9a090ee', PS1)

    def test_quiet_console_and_one_click(self):
        self.assertIn('powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass', CMD)
        self.assertIn('install-scail2.ps1', CMD)
        self.assertIn('setup-report.json', PS1)
        self.assertIn('logs', PS1)
        self.assertIn('SCAIL2AutoVideo', PS1)
        self.assertIn("$controlNode[0].widgets_values[0] = 2", PS1)
        self.assertIn('your_driving_video.mp4', PS1)
        self.assertIn('The installer never queues a GPU render', (ROOT / 'README-SCAIL2.txt').read_text(encoding='utf-8'))
        self.assertIn('8189', PS1)

    def test_local_files_no_uncontrolled_broad_permission(self):
        forbidden = ('git clean', 'git reset', 'force-push', 'setx', 'Set-ExecutionPolicy',
                     'winget ', 'pip install --user')
        for text in forbidden:
            self.assertNotIn(text.lower(), PS1.lower())
        self.assertTrue(PS1.count("throw '[") >= 6)

if __name__ == '__main__':
    unittest.main()
