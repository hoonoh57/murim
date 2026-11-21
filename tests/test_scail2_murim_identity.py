"""Offline invariants for the Q3 2-second Murim reference-image transfer trial.

This verifies the workflow file only, not a Windows GPU render.
"""
import json
import pathlib
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
FLOW=ROOT/'workflows/scail2/SCAIL-2-MURIM-IDENTITY-2S.json'

class ScailMurimIdentityTrial(unittest.TestCase):
    def test_baseline_settings_and_inputs(self):
        graph=json.loads(FLOW.read_text(encoding='utf-8'))
        nodes=graph['nodes']
        self.assertEqual(len(set(n['id'] for n in nodes)), len(nodes))
        def single(node_type):
            matches=[n for n in nodes if n['type']==node_type]
            self.assertEqual(len(matches),1,node_type)
            return matches[0]
        self.assertEqual(single('UnetLoaderGGUF')['widgets_values'][0],'SCAIL-2-Q3_K_M.gguf')
        self.assertEqual(single('SCAIL2EasyConfig')['widgets_values'][0],2)
        self.assertEqual(single('SCAIL2EasyConfig')['widgets_values'][1],16)
        self.assertEqual(single('SCAIL2EasyConfig')['widgets_values'][2],480)
        self.assertEqual(single('SCAIL2EasyConfig')['widgets_values'][4],6)
        self.assertEqual(single('VHS_LoadVideo')['widgets_values']['video'],'your_driving_video.mp4')
        self.assertEqual(single('LoadImage')['widgets_values'][0],'murim_character_reference.png')
        self.assertEqual(single('VHS_VideoCombine')['widgets_values']['filename_prefix'],'SCAIL2_MURIM_IDENTITY')
        self.assertTrue(any(n['type']=='Display Int (rgthree)' for n in nodes))

if __name__=='__main__':
    unittest.main()
