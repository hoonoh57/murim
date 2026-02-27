from src.agents.base_agent import BaseAgent
from src.evolution.skill_tracker import DraftPractice
from src.core.models import Scenario

class MarketingAgent(BaseAgent):
    def __init__(self, is_mock: bool = True):
        super().__init__(agent_type="marketing", is_mock=is_mock)
        
    def generate_assets(self, scenario: Scenario) -> dict:
        print(f"[Marketing] Generating assets for: {scenario.title}")
        return {"title": f"🔥 {scenario.title} 🔥", "description": scenario.synopsis, "tags": ["무협", "천마", "회귀"]}

    def self_practice(self, focus: str):
        print(f"\n[Marketing Evolution] Focus Training: {focus}")
        
        # 1. 마케팅 전략 수립
        strategy = focus
        print(f"[Marketing] Developing viral strategy for: {strategy}")
        
        # 2. 비평 (마케팅 기획 평가)
        dummy_scenario = Scenario(
            title=f"Marketing Practice: {focus}",
            synopsis=focus,
            script=f"Marketing Strategy: {strategy}\nTarget Audience: Wuxia Fans",
            scenes=[],
            sound_guide={}
        )
        print("[Evolution] Evaluating marketing strategy...")
        evaluated = self.council.evaluate(dummy_scenario)
        score_v1 = evaluated.final_score
        
        # 4. 개선 시뮬레이션
        score_v2 = min(10.0, score_v1 + 0.4)
        
        # 5. 진화 기록
        practice = DraftPractice(
            topic="Viral Marketing & SEO",
            focus_point=focus,
            scenario=evaluated,
            self_reflection=f"시청자의 클릭을 유도하는 후킹 포인트와 키워드를 최적화했습니다.",
            evolution_step=self.log.current_level
        )
        self.add_experience(practice, score_v1, score_v2)
        print(f"습작 완료. 마케팅 품질 개선: {score_v1:.1f} -> {score_v2:.1f}")
