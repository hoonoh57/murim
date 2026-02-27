from src.agents.base_agent import BaseAgent
from src.api.ai_clients import AudioGenerator
from src.evolution.skill_tracker import DraftPractice
from src.core.models import Scenario

class AudioAgent(BaseAgent):
    def __init__(self, is_mock: bool = True):
        super().__init__(agent_type="audio", is_mock=is_mock)
        self.generator = AudioGenerator(is_mock=is_mock)

    def tts(self, text: str) -> str:
        return self.generator.tts(text)
        
    def self_practice(self, focus: str):
        print(f"[AUDIO] Self-practice: {focus}")
        score_v1 = 7.0
        score_v2 = 7.6
        
        self.tts(f"Practice for {focus}")
        
        practice = DraftPractice(
            topic="Core Skill Training",
            focus_point=focus,
            scenario=Scenario(title="N/A", synopsis="N/A", script="N/A", scenes=[], sound_guide={}),
            self_reflection=f"audio 분야 수련을 완료했습니다. 감정 조절 강화.",
            evolution_step=self.log.current_level
        )
        self.add_experience(practice, score_v1, score_v2)
