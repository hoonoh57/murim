from src.agents.base_agent import BaseAgent
from src.api.ai_clients import ImageGenerator
from src.evolution.skill_tracker import DraftPractice
from src.core.models import Scenario

class ImagingAgent(BaseAgent):
    def __init__(self, is_mock: bool = True):
        super().__init__(agent_type="imaging", is_mock=is_mock)
        self.generator = ImageGenerator(is_mock=is_mock)
        
    def generate(self, prompt: str) -> str:
        return self.generator.generate(prompt)

    def self_practice(self, focus: str):
        print(f"[Imaging] Self-practice: {focus}")
        score_v1 = 7.0
        score_v2 = 7.8 # Improving
        
        # 실제 생성 시뮬레이션
        self.generate(f"Practice: {focus}")
        
        practice = DraftPractice(
            topic="Style Consistency Training",
            focus_point=focus,
            scenario=Scenario(title="N/A", synopsis="N/A", script="N/A", scenes=[], sound_guide={}),
            self_reflection=f"이미지 일관성 및 '{focus}' 표현 수련을 완료했습니다.",
            evolution_step=self.log.current_level
        )
        self.add_experience(practice, score_v1, score_v2)
