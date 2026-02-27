import statistics
from typing import List, Dict
from src.agents.base_agent import BaseAgent
from src.core.models import EpisodeRequest, Scenario

class DirectorAgent(BaseAgent):
    def __init__(self, is_mock: bool = True):
        super().__init__(agent_type="director", is_mock=is_mock)
        
    def check_balance(self, agents: Dict[str, BaseAgent]) -> dict:
        """전 에이전트 레벨 조회 -> 편차 분석 -> 훈련 명령 생성"""
        print("[Director] Checking ecosystem balance...")
        levels = {name: agent.get_level() for name, agent in agents.items()}
        
        max_lv = max(levels.values())
        min_lv = min(levels.values())
        gap = max_lv - min_lv
        avg = sum(levels.values()) / len(levels)
        
        training_targets = []
        for name, lv in levels.items():
            if lv < avg - 0.5:
                training_targets.append({
                    "agent": name,
                    "current_level": lv,
                    "priority": "HIGH" if lv == min_lv else "MEDIUM"
                })
        
        report = {
            "levels": levels,
            "gap": gap,
            "balanced": (gap <= 1),
            "training_targets": training_targets
        }
        return report

    def orchestrate_episode(self, topic: str, events: str, agents: Dict[str, BaseAgent]):
        """전체 파이프라인 조율"""
        print(f"\n[Director] Starting orchestration for: {topic}")
        
        # 1. 시나리오 생성 (Writer)
        writer = agents.get("writer")
        if not writer: return
        
        print("\n[GATE 1] Scenario Generation")
        scenario = writer.write_scenario(EpisodeRequest(topic=topic, events=events))
        
        # 2. 비평 및 승인
        scenario = writer.council.evaluate(scenario)
        if scenario.final_score < 7.0:
            print("[Director] Scenario quality below threshold. Re-writing recommended.")
            # 실제로는 여기서 루프를 돌거나 중단 가능
        
        print(f"[Director] Episode '{scenario.title}' is ready for production assets.")
        return scenario

    def self_practice(self, focus: str):
        print(f"[Director] Self-practice: Optimizing orchestration rules for {focus}")
        # 감독은 직접 산출물을 만들지 않으므로 규칙 최적화 시뮬레이션으로 대체
        score_v1 = 7.0
        score_v2 = 8.5 # Simulated improvement
        
        practice = DraftPractice(
            topic="Orchestration Optimization",
            focus_point=focus,
            scenario=Scenario(title="N/A", synopsis="N/A", script="N/A", scenes=[], sound_guide={}),
            self_reflection="감독 로직을 최적화했습니다.",
            evolution_step=self.log.current_level
        )
        self.add_experience(practice, score_v1, score_v2)
        return "Director self-optimization complete."
