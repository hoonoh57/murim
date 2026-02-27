from src.agents.base_agent import BaseAgent
from src.evolution.skill_tracker import DraftPractice
from src.core.models import Scenario

class MarketingAgent(BaseAgent):
    def __init__(self, is_mock: bool = True):
        super().__init__(agent_type="marketing", is_mock=is_mock)
        
    def self_practice(self, focus: str):
        print(f"[MARKETING] Self-practice: {focus}")
        score_v1 = 7.0
        score_v2 = 7.5
        practice = DraftPractice(
            topic="Viral Strategy Training",
            focus_point=focus,
            scenario=Scenario(title="N/A", synopsis="N/A", script="N/A", scenes=[], sound_guide={}),
            self_reflection=f"marketing 분야 수련을 완료했습니다.",
            evolution_step=self.log.current_level
        )
        self.add_experience(practice, score_v1, score_v2)
