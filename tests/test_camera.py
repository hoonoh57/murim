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
            script="script", 
            emotion="epic",
            camera="Low Angle",
            image_prompt="prompt",
            video_prompt="prompt"
        )]
        plan = self.agent.plan_camera_angles(scenes)
        self.assertEqual(len(plan), 1)

    def test_self_practice(self):
        self.agent.self_practice("camera focus")
        self.assertTrue(len(self.agent.log.practice_history) > 0)

if __name__ == "__main__":
    unittest.main()
