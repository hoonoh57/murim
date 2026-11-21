"""Offline contract for independent 2s licensed sword-motion SCAIL trial."""
import json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
FLOW=ROOT/'workflows/scail2/SCAIL-2-MURIM-SWORD-2S.json'
PS=ROOT/'scripts/scail2/prepare-scail2-sword.ps1'
CMD=ROOT/'scripts/scail2/PREPARE-SCAIL2-SWORD.cmd'
class SwordTrialTests(unittest.TestCase):
    def test_workflow(self):
        n=json.loads(FLOW.read_text(encoding='utf-8'))['nodes']
        def node(t):
            m=[x for x in n if x['type']==t]
            self.assertEqual(len(m),1,t)
            return m[0]
        self.assertEqual(node('UnetLoaderGGUF')['widgets_values'][0],'SCAIL-2-Q3_K_M.gguf')
        self.assertEqual(node('SCAIL2EasyConfig')['widgets_values'][0],2)
        self.assertEqual(node('SCAIL2EasyConfig')['widgets_values'][10],'murim_sword_driving_2s.mp4')
        self.assertEqual(node('VHS_LoadVideo')['widgets_values']['video'],'murim_sword_driving_2s.mp4')
        self.assertEqual(node('LoadImage')['widgets_values'][0],'murim_character_reference.png')
        self.assertEqual(node('VHS_VideoCombine')['widgets_values']['filename_prefix'],'SCAIL2_MURIM_SWORD')
    def test_script_safety(self):
        code=PS.read_text(encoding='utf-8')
        for required in ("E:\\comfyui-scail",'pexels.com/download/video/4734306/','anullsrc=r=48000:cl=stereo','fps=16','SWORD_INPUT_VERIFIED_NOT_RENDERED','[USER_INPUT_CONFLICT]','[RECEIPT_HASH_MISMATCH]'):
            self.assertIn(required,code)
        for forbidden in ('Remove-Item','git clean','git reset','Set-ExecutionPolicy'):
            self.assertNotIn(forbidden,code)
        self.assertIn('prepare-scail2-sword.ps1',CMD.read_text(encoding='utf-8'))
if __name__=='__main__':unittest.main()
