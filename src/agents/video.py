from src.agents.base_agent import BaseAgent
from src.api.ai_clients import VideoGenerator
from src.evolution.skill_tracker import DraftPractice
from src.core.models import Scenario

class VideoAgent(BaseAgent):
    def __init__(self, is_mock: bool = True):
        super().__init__(agent_type="video", is_mock=is_mock)
        self.generator = VideoGenerator(is_mock=is_mock)

    def generate_from_image(self, image_path: str, prompt: str) -> str:
        return self.generator.generate_from_image(image_path, prompt)
        
    def self_practice(self, focus: str):
        print(f"[VIDEO] Self-practice: {focus}")
        score_v1 = 7.0
        score_v2 = 7.7
        
        self.generate_from_image("mock_img.png", f"Practice: {focus}")
        
        practice = DraftPractice(
            topic="Core Skill Training",
            focus_point=focus,
            scenario=Scenario(title="N/A", synopsis="N/A", script="N/A", scenes=[], sound_guide={}),
            self_reflection=f"video 분야 수련을 완료했습니다. 모션 자연스러움 강화.",
            evolution_step=self.log.current_level
        )
        self.add_experience(practice, score_v1, score_v2)
