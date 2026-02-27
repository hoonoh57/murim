from typing import List
from src.core.models import Scenario, Critique

class CouncilAgent:
    def __init__(self, is_mock: bool = True):
        self.is_mock = is_mock
        self.personas = [
            "정통무협 마니아 (고증 중시)",
            "영상 연출가 (비주얼 중시)",
            "대본 작가 (서사 구조 중시)",
            "속도형 시청자 (도파민/자극 중시)",
            "글로벌 팬 (보편적 정서 중시)",
            "전략 마케터 (조회수/바이럴 중시)"
        ]

    def evaluate(self, scenario: Scenario) -> Scenario:
        print(f"[Council] Evaluating scenario: {scenario.title}")
        critiques = []
        total_score = 0
        
        for persona in self.personas:
            if self.is_mock:
                score = 8 # Mock score
                critique = Critique(
                    persona=persona,
                    score=score,
                    comment=f"{persona} 입장에서 본 의견입니다. (Mock)",
                    suggestions=["내공 묘사를 더 비장하게", "첫 장면 훅을 더 강하게"]
                )
            else:
                # Actual AI critique logic would go here
                score = 7 
                critique = Critique(persona=persona, score=score, comment="Good progress", suggestions=[])
            
            critiques.append(critique)
            total_score += score
            
        scenario.critiques = critiques
        scenario.final_score = total_score / len(self.personas)
        
        # Verdict Logic
        verdict = "REWORK"
        if scenario.final_score >= 7.5:
            verdict = "GO"
        elif scenario.final_score < 6.0:
            verdict = "KILL"
        
        print(f"[Council] Final Average Score: {scenario.final_score:.1f} -> Verdict: {verdict}")
        return scenario
