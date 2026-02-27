from src.agents.base_agent import BaseAgent
from src.evolution.skill_tracker import DraftPractice
from src.core.models import Scenario

class ArtDirectionAgent(BaseAgent):
    def __init__(self, is_mock: bool = True):
        super().__init__(agent_type="art_direction", is_mock=is_mock)
        
    def self_practice(self, focus: str):
        print(f"[ART_DIRECTION] Self-practice: {focus}")
        score_v1 = 7.0
        score_v2 = 7.5
        practice = DraftPractice(
            topic="Visual Style Guide Training",
            focus_point=focus,
            scenario=Scenario(title="N/A", synopsis="N/A", script="N/A", scenes=[], sound_guide={}),
            self_reflection=f"art_direction 분야 수련을 완료했습니다.",
            evolution_step=self.log.current_level
        )
        self.add_experience(practice, score_v1, score_v2)
