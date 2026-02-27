from src.agents.base_agent import BaseAgent
from src.evolution.skill_tracker import DraftPractice
from src.core.models import Scenario

class MarketingAgent(BaseAgent):
    def __init__(self, is_mock: bool = True):
        super().__init__(agent_type="marketing", is_mock=is_mock)
        
    def generate_assets(self, scenario: Scenario) -> dict:
        print(f"[Marketing] Generating assets for: {scenario.title}")
        return {"title": f"🔥 {scenario.title} 🔥", "description": scenario.synopsis, "tags": ["무협", "천마", "회귀"]}

    def revise_strategy(self, original_strategy: str, critiques: list) -> str:
        """비평을 바탕으로 마케팅 전략을 개선합니다."""
        if not critiques:
            return original_strategy

        if self.is_mock:
            return f"Enhanced Strategy: {original_strategy} with better CTR optimization and emotional hooks."
            
        if not self.client:
            return original_strategy

        critique_text = "\n".join([f"- {c.comment}" for c in critiques])
        prompt = f"""
        당신은 마케팅 전문가입니다.
        기존 전략: {original_strategy}
        비평 내용:
        {critique_text}
        
        비평을 수렴하여 시청률과 도달 범위를 높일 수 있는 개선된 마케팅 지시어(한글/영문 혼용)를 작성하세요.
        """
        response = self.client.messages.create(
            model=self.model,
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text.strip()

    def self_practice(self, focus: str):
        print(f"\n[Marketing Evolution] Focus Training: {focus}")
        
        # 1. 초안 마케팅 기획
        dummy_scenario = Scenario(
            title=f"Marketing Practice: {focus}",
            synopsis=focus,
            script=f"Marketing strategy: {focus}",
            scenes=[],
            sound_guide={}
        )
        
        # 2. 1차 비평
        print("\n[Evolution] 1st Round Critique...")
        evaluated_v1 = self.council.evaluate(dummy_scenario)
        score_v1 = evaluated_v1.final_score
        
        # 3. 마케팅 전략 수정
        revised_strategy = self.revise_strategy(focus, evaluated_v1.critiques)
        print(f"[Marketing] Revised strategy: {revised_strategy}")
        
        # 4. 2차 비평 (재평가)
        dummy_scenario_v2 = Scenario(
            title=f"Marketing Practice: {focus} (Revised)",
            synopsis=focus,
            script=f"Revised Marketing Strategy: {revised_strategy}",
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
            topic="Viral Marketing & SEO",
            focus_point=focus,
            scenario=evaluated_v2,
            self_reflection=reflection,
            evolution_step=self.log.current_level
        )
        self.add_experience(practice, score_v1, score_v2)
        print(f"습작 완료. 마케팅 품질 개선: {score_v1:.1f} -> {score_v2:.1f}")
