import unittest
import os
import tempfile
from src.agents.camera import CameraAgent
from src.core.models import Scene
from src.core.skill_prompt import CAMERA_ANGLES, SHOT_SIZES, LIGHTING_PATTERNS

class TestCameraAgent(unittest.TestCase):
    def setUp(self):
        # Mock Council writes critique and evolution logs; never touch user outputs.
        self._sandbox = tempfile.TemporaryDirectory()
        self.addCleanup(self._sandbox.cleanup)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self._sandbox.name)
        self.agent = CameraAgent(is_mock=True)

    def test_plan_camera_angles(self):
        scenes = [Scene(
            id="S01", 
            time_range="00:00-00:05", 
            description="desc", 
            emotion="epic",
            camera="Low Angle",
            image_prompt="prompt",
            video_prompt="prompt"
        )]
        plan = self.agent.plan_camera_angles(scenes)
        self.assertEqual(len(plan), 1)
        # Since skill integration, angle and shot size are separate fields.
        # Epic -> low angle + EWS, slow zoom, volumetric lighting.
        self.assertEqual(plan[0], {
            "scene_id": "S01",
            "angle": CAMERA_ANGLES["low"],
            "shot": SHOT_SIZES["EWS"],
            "movement": "slow_zoom_in",
            "lighting": LIGHTING_PATTERNS["volumetric"],
        })

    def test_plan_camera_angles_korean(self):
        scenes = [
            Scene(id="S01", time_range="00:00", description="desc", emotion="비장함", camera="ca", image_prompt="p", video_prompt="p"),
            Scene(id="S02", time_range="00:05", description="desc", emotion="전투", camera="ca", image_prompt="p", video_prompt="p")
        ]
        plan = self.agent.plan_camera_angles(scenes)
        self.assertEqual(plan, [
            {
                "scene_id": "S01",
                "angle": CAMERA_ANGLES["low"],
                "shot": SHOT_SIZES["EWS"],
                "movement": "slow_zoom_in",
                "lighting": LIGHTING_PATTERNS["volumetric"],
            },
            {
                "scene_id": "S02",
                "angle": CAMERA_ANGLES["dutch"],
                "shot": SHOT_SIZES["MS"],
                "movement": "zoom_in",
                "lighting": LIGHTING_PATTERNS["rim"],
            },
        ])

    def test_plan_camera_angles_unknown_emotion(self):
        scenes = [
            Scene(id="S03", time_range="00:10", description="desc",
                  emotion="unknown", camera="ca",
                  image_prompt="p", video_prompt="p")
        ]
        self.assertEqual(self.agent.plan_camera_angles(scenes), [
            {
                "scene_id": "S03",
                "angle": CAMERA_ANGLES["eye"],
                "shot": SHOT_SIZES["MS"],
                "movement": "static",
                "lighting": LIGHTING_PATTERNS["volumetric"],
            }
        ])

    def test_self_practice(self):
        initial_xp = self.agent.log.total_xp
        self.agent.self_practice("camera focus")
        
        self.assertTrue(len(self.agent.log.practice_history) > 0)
        practice = self.agent.log.practice_history[-1]
        
        # Strengthened assertions
        # Mock Council must remain NOT_EVALUATED; no fabricated reward.
        self.assertEqual(self.agent.log.total_xp, initial_xp)
        self.assertEqual(self.agent.log.current_level, 1)
        self.assertEqual(self.agent.log.total_practices, 1)
        self.assertEqual(len(self.agent.log.practice_history), 1)
        self.assertEqual(practice.scenario.final_score, 0.0)
        self.assertEqual(len(practice.scenario.critiques), len(self.agent.council.personas))
        for critique in practice.scenario.critiques:
            self.assertEqual(critique.score, 0.0)
            self.assertTrue(critique.comment.startswith("NOT_EVALUATED"))
        self.assertTrue(os.path.isfile(self.agent.log_file))
        self.assertIsNotNone(practice.self_reflection)
        self.assertTrue(len(practice.self_reflection) > 10)
        self.assertGreaterEqual(practice.scenario.final_score, 0)
        self.assertLessEqual(practice.scenario.final_score, 10)

if __name__ == "__main__":
    unittest.main()
