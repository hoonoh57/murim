import unittest
import os
import json
import shutil
import tempfile
from src.pipeline.image_manager import ImageManager


class TestImageManager(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix='murim_test_ep_')
        self.images_dir = os.path.join(self.test_dir, 'images')
        self.prompts_dir = os.path.join(self.test_dir, 'prompts')
        os.makedirs(self.images_dir, exist_ok=True)
        os.makedirs(self.prompts_dir, exist_ok=True)
        prompts_data = {
            'enhanced_prompts': [
                {'scene_id': 'S01', 'prompt': 'Dark cliff scene'},
                {'scene_id': 'S02', 'prompt': 'Battle in rain'},
                {'scene_id': 'S03', 'prompt': 'Temple interior'}
            ]
        }
        with open(os.path.join(self.prompts_dir, 'image_prompts.json'), 'w') as f:
            json.dump(prompts_data, f)
        self.mgr = ImageManager(self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_load_prompts(self):
        prompts = self.mgr.load_prompts()
        self.assertEqual(len(prompts), 3)
        self.assertEqual(prompts[0]['scene_id'], 'S01')

    def test_generate_skeleton(self):
        manifest = self.mgr.load_manifest()
        self.assertEqual(len(manifest['scenes']), 3)
        self.assertIsNone(manifest['scenes'][0]['selected'])

    def test_scan_single_source(self):
        for i in range(1, 4):
            with open(os.path.join(self.images_dir, f'S0{i}_nanobanana.png'), 'w') as f:
                f.write(f'fake image {i}')
        manifest = self.mgr.scan_images()
        self.assertEqual(len(manifest['scenes']), 3)
        for scene in manifest['scenes']:
            self.assertEqual(len(scene['candidates']), 1)
            self.assertIsNotNone(scene['selected'])

    def test_scan_multi_source(self):
        for src in ['nanobanana', 'dalle3', 'midjourney']:
            with open(os.path.join(self.images_dir, f'S01_{src}.png'), 'w') as f:
                f.write(src)
        manifest = self.mgr.scan_images()
        s01 = next(s for s in manifest['scenes'] if s['scene_id'] == 'S01')
        self.assertEqual(len(s01['candidates']), 3)

    def test_select_image(self):
        for name in ['S01_a.png', 'S01_b.png']:
            with open(os.path.join(self.images_dir, name), 'w') as f:
                f.write('x')
        self.mgr.scan_images()
        self.assertTrue(self.mgr.select_image('S01', 'S01_b.png'))
        manifest = self.mgr.load_manifest()
        s01 = next(s for s in manifest['scenes'] if s['scene_id'] == 'S01')
        self.assertEqual(s01['selected'], 'S01_b.png')

    def test_select_invalid(self):
        with open(os.path.join(self.images_dir, 'S01_a.png'), 'w') as f:
            f.write('x')
        self.mgr.scan_images()
        self.assertFalse(self.mgr.select_image('S01', 'nonexistent.png'))

    def test_quality_score(self):
        with open(os.path.join(self.images_dir, 'S01_a.png'), 'w') as f:
            f.write('x')
        self.mgr.scan_images()
        self.assertTrue(self.mgr.set_quality_score('S01', 'S01_a.png', 8.5, 'good'))
        manifest = self.mgr.load_manifest()
        s01 = next(s for s in manifest['scenes'] if s['scene_id'] == 'S01')
        self.assertEqual(s01['candidates'][0]['quality_score'], 8.5)

    def test_quality_score_clamp(self):
        with open(os.path.join(self.images_dir, 'S01_a.png'), 'w') as f:
            f.write('x')
        self.mgr.scan_images()
        self.mgr.set_quality_score('S01', 'S01_a.png', 15.0)
        manifest = self.mgr.load_manifest()
        s01 = next(s for s in manifest['scenes'] if s['scene_id'] == 'S01')
        self.assertEqual(s01['candidates'][0]['quality_score'], 10.0)

    def test_auto_select_best(self):
        for name in ['S01_a.png', 'S01_b.png']:
            with open(os.path.join(self.images_dir, name), 'w') as f:
                f.write('x')
        self.mgr.scan_images()
        self.mgr.set_quality_score('S01', 'S01_a.png', 6.0)
        self.mgr.set_quality_score('S01', 'S01_b.png', 9.0)
        selections = self.mgr.auto_select_best()
        self.assertEqual(selections['S01'], 'S01_b.png')

    def test_coverage_partial(self):
        for i in [1, 2]:
            with open(os.path.join(self.images_dir, f'S0{i}_test.png'), 'w') as f:
                f.write(str(i))
        self.mgr.scan_images()
        report = self.mgr.get_coverage_report()
        self.assertEqual(report['total_scenes'], 3)
        self.assertEqual(report['images_selected'], 2)
        self.assertIn('S03', report['missing_scenes'])
        self.assertFalse(report['ready_for_video'])

    def test_coverage_full(self):
        for i in range(1, 4):
            with open(os.path.join(self.images_dir, f'S0{i}_test.png'), 'w') as f:
                f.write(str(i))
        self.mgr.scan_images()
        report = self.mgr.get_coverage_report()
        self.assertEqual(report['coverage_pct'], 100.0)
        self.assertTrue(report['ready_for_video'])

    def test_selected_paths(self):
        with open(os.path.join(self.images_dir, 'S01_test.png'), 'w') as f:
            f.write('1')
        self.mgr.scan_images()
        selected = self.mgr.get_selected_images()
        self.assertIn('S01', selected)
        self.assertTrue(os.path.isfile(selected['S01']))

    def test_rescan_idempotent(self):
        with open(os.path.join(self.images_dir, 'S01_test.png'), 'w') as f:
            f.write('data')
        self.mgr.scan_images()
        self.mgr.scan_images()
        self.mgr.scan_images()
        manifest = self.mgr.load_manifest()
        s01 = next(s for s in manifest['scenes'] if s['scene_id'] == 'S01')
        self.assertEqual(len(s01['candidates']), 1)

    def test_no_prompts_file(self):
        pf = os.path.join(self.prompts_dir, 'image_prompts.json')
        if os.path.exists(pf):
            os.remove(pf)
        with open(os.path.join(self.images_dir, 'S01_test.png'), 'w') as f:
            f.write('data')
        manifest = self.mgr.scan_images()
        self.assertEqual(len(manifest['scenes']), 1)


if __name__ == '__main__':
    unittest.main()