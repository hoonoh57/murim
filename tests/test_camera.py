import unittest
from src.agents.camera import CameraAgent
from src.core.models import Scene

class TestCameraAgent(unittest.TestCase):
    def setUp(self):
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
        self.assertEqual(plan[0]["angle"], "Extreme Wide Shot")

    def test_self_practice(self):
        initial_xp = self.agent.log.total_xp
        self.agent.self_practice("camera focus")
        
        self.assertTrue(len(self.agent.log.practice_history) > 0)
        practice = self.agent.log.practice_history[-1]
        
        # Strengthened assertions
        self.assertGreater(self.agent.log.total_xp, initial_xp)
        self.assertIsNotNone(practice.self_reflection)
        self.assertTrue(len(practice.self_reflection) > 10)
        self.assertGreaterEqual(practice.scenario.final_score, 0)
        self.assertLessEqual(practice.scenario.final_score, 10)

if __name__ == "__main__":
    unittest.main()
