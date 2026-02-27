from src.agents.base_agent import BaseAgent
from src.evolution.skill_tracker import DraftPractice
from src.core.models import Scenario

class ArtDirectionAgent(BaseAgent):
    def __init__(self, is_mock: bool = True):
        super().__init__(agent_type="art_direction", is_mock=is_mock)
        
    def design_style_guide(self, worldview: str) -> dict:
        print(f"[ArtDirection] Designing style guide for: {worldview}")
        return {"palette": ["#2D1B1B", "#DAA520"], "style": "Traditional Wuxia"}

    def revise_style_guide(self, original_concept: str, critiques: list) -> str:
        """비평을 바탕으로 스타일 가이드를 개선합니다."""
        if self.is_mock:
            return f"Enhanced Style: {original_concept} with deeper textures and refined color theory."
            
        critique_text = "\n".join([f"- {c.comment}" for c in critiques])
        prompt = f"""
        당신은 미술 감독입니다.
        기존 비주얼 컨셉: {original_concept}
        비평 내용:
        {critique_text}
        
        비평을 수렴하여 시각적 일관성과 예술성을 강화할 수 있는 개선된 스타일 정의(한글/영문 혼용)를 작성하세요.
        """
        response = self.client.messages.create(
            model=self.model,
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text.strip()

    def self_practice(self, focus: str):
        print(f"\n[ArtDirection Evolution] Focus Training: {focus}")
        
        # 1. 초안 스타일 기획
        dummy_scenario = Scenario(
            title=f"ArtDirection Practice: {focus}",
            synopsis=focus,
            script=f"Visual Identity focus: {focus}",
            scenes=[],
            sound_guide={}
        )
        
        # 2. 1차 비평
        print("\n[Evolution] 1st Round Critique...")
        evaluated_v1 = self.council.evaluate(dummy_scenario)
        score_v1 = evaluated_v1.final_score
        
        # 3. 스타일 가이드 수정
        revised_concept = self.revise_style_guide(focus, evaluated_v1.critiques)
        print(f"[ArtDirection] Revised concept: {revised_concept}")
        
        # 4. 2차 비평 (재평가)
        dummy_scenario_v2 = Scenario(
            title=f"ArtDirection Practice: {focus} (Revised)",
            synopsis=focus,
            script=f"Revised Visual Identity: {revised_concept}",
            scenes=[],
            sound_guide={}
        )
        print("\n[Evolution] 2nd Round Critique (Final Assessment)...")
        evaluated_v2 = self.council.evaluate(dummy_scenario_v2)
        score_v2 = evaluated_v2.final_score
        
        # 5. 자기 성찰
        reflection = self._generate_reflection(evaluated_v2, score_v1, score_v2)
        
        # 6. 진화 기록 저장
        practice = DraftPractice(
            topic="Visual World Building & Consistency",
            focus_point=focus,
            scenario=evaluated_v2,
            self_reflection=reflection,
            evolution_step=self.log.current_level
        )
        self.add_experience(practice, score_v1, score_v2)
        print(f"습작 완료. 미술 품질 개선: {score_v1:.1f} -> {score_v2:.1f}")
