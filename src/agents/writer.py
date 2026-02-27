import os
import json
from typing import List
from src.core.models import Scenario, EpisodeRequest
from src.api.ai_clients import ScenarioEngine

class WriterAgent:
    def __init__(self, is_mock: bool = True):
        self.engine = ScenarioEngine(is_mock=is_mock)
        
    def write_scenario(self, request: EpisodeRequest) -> Scenario:
        print(f"[Writer] Writing scenario for topic: {request.topic}")
        # 실제 환경에서는 AI API로부터 JSON을 받아 Scenario 모델로 파싱합니다.
        raw_data = self.engine.generate_episode(request.topic, request.events)
        
        # Mock 데이터를 Scenario 모델 형식으로 변환 (실제로는 AI 응답 파싱)
        if isinstance(raw_data, dict) and "scenes" in raw_data:
            return Scenario(
                title=raw_data.get("title", request.topic),
                synopsis=request.events,
                script=raw_data.get("script", ""),
                scenes=raw_data.get("scenes", []),
                sound_guide={"bgm": "Epic Wuxia", "fx": "Sword Clashing"}
            )
        return Scenario(title="Error", synopsis="", script="", scenes=[], sound_guide={})

class CouncilAgent:
    def __init__(self):
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
            # 실제로는 각 페르소나별 프롬프트로 AI 호출
            score = 8 # Mock score
            critique = {
                "persona": persona,
                "score": score,
                "comment": f"{persona} 입장에서 본 의견입니다. (Mock)",
                "suggestions": ["내공 묘사를 더 비장하게", "첫 장면 훅을 더 강하게"]
            }
            critiques.append(critique)
            total_score += score
            
        scenario.critiques = critiques
        scenario.final_score = total_score / len(self.personas)
        print(f"[Council] Final Average Score: {scenario.final_score}")
        return scenario
