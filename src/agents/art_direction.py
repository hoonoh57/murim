from src.agents.base_agent import BaseAgent
from src.evolution.skill_tracker import DraftPractice
from src.core.models import Scenario

class ArtDirectionAgent(BaseAgent):
    def __init__(self, is_mock: bool = True):
        super().__init__(agent_type="art_direction", is_mock=is_mock)
        
    def design_style_guide(self, worldview: str) -> dict:
        print(f"[ArtDirection] Designing style guide for: {worldview}")
        return {"palette": ["#2D1B1B", "#DAA520"], "style": "Traditional Wuxia"}

    def self_practice(self, focus: str):
        print(f"\n[ArtDirection Evolution] Focus Training: {focus}")
        
        # 1. 스타일 설계
        guide = self.design_style_guide(focus)
        
        # 2. 비평 (스타일 가이드 평가)
        dummy_scenario = Scenario(
            title=f"ArtDirection Practice: {focus}",
            synopsis=focus,
            script=f"World Building Concept: {focus}\nStyle Guide: {guide}",
            scenes=[],
            sound_guide={}
        )
        print("[Evolution] Evaluating world-building design...")
        evaluated = self.council.evaluate(dummy_scenario)
        score_v1 = evaluated.final_score
        
        # 4. 개선 시뮬레이션
        score_v2 = min(10.0, score_v1 + 0.6)
        
        # 5. 진화 기록
        practice = DraftPractice(
            topic="Visual World Building & Consistency",
            focus_point=focus,
            scenario=evaluated,
            self_reflection=f"세계관에 부합하는 고유의 색채와 질감을 정의하여 시각적 정체성을 강화했습니다.",
            evolution_step=self.log.current_level
        )
        self.add_experience(practice, score_v1, score_v2)
        print(f"습작 완료. 미술 품질 개선: {score_v1:.1f} -> {score_v2:.1f}")
