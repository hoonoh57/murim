import os
import json
from typing import List
from src.core.models import Scenario, Scene, EpisodeRequest
from src.api.ai_clients import ScenarioEngine

class WriterAgent:
    def __init__(self, is_mock: bool = True):
        self.engine = ScenarioEngine(is_mock=is_mock)
        self.evolution_log_path = "outputs/evolution/writer_evolution.json"
        os.makedirs(os.path.dirname(self.evolution_log_path), exist_ok=True)
        
    def write_scenario(self, request: EpisodeRequest) -> Scenario:
        print(f"[Writer] Writing scenario for topic: {request.topic}")
        raw_data = self.engine.generate_episode(request.topic, request.events)
        return self._parse_scenario(raw_data, request.topic, request.events)

    def self_practice(self, focus_point: str) -> str:
        """작가가 스스로 습작(習作)을 수행하고 기록을 남깁니다."""
        print(f"[Writer] Starting self-practice focusing on: {focus_point}")
        
        # 1. 습작 주제 선정 및 생성
        practice_topic = f"습작: {focus_point} 강화 훈련"
        practice_events = "기존 스타일에서 벗어나 더 깊은 정통 무협의 정수를 담는 연습"
        
        scenario = self.write_scenario(EpisodeRequest(topic=practice_topic, events=practice_events))
        
        # 2. 스스로 회고 (Self-Reflection)
        reflection = f"이번 습작에서는 {focus_point}를 중점적으로 다루었습니다. 이전보다 표현의 깊이가 좋아졌으나, 여전히 감정 묘사에서 보완이 필요합니다."
        
        # 3. 진화 로그 스토리지 업데이트
        self._save_evolution_record(practice_topic, focus_point, scenario, reflection)
        
        return f"습작 완료: {practice_topic}. 기록이 저장되었습니다."

    def _save_evolution_record(self, topic, focus, scenario, reflection):
        import json
        from datetime import datetime
        
        record = {
            "timestamp": datetime.now().isoformat(),
            "topic": topic,
            "focus_point": focus,
            "reflection": reflection,
            "scenario_title": scenario.title,
            "skill_level_up": True
        }
        
        # 간단한 JSON 로그 관리 (실제로는 EvolutionLog 모델 사용 권장)
        history = []
        if os.path.exists(self.evolution_log_path):
            with open(self.evolution_log_path, "r", encoding="utf-8") as f:
                history = json.load(f)
        
        history.append(record)
        
        with open(self.evolution_log_path, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=4, ensure_ascii=False)
        print(f"[Evolution] Practice record saved to {self.evolution_log_path}")

    def _parse_scenario(self, raw_data, topic, events) -> Scenario:
        if "error" in raw_data:
            return Scenario(title="Error", synopsis="", script="", scenes=[], sound_guide={})
        
        scenes_data = raw_data.get("scenes", [])
        parsed_scenes = [Scene(**s) for s in scenes_data]
        
        return Scenario(
            title=raw_data.get("title", topic),
            synopsis=events,
            script=raw_data.get("script", ""),
            scenes=parsed_scenes,
            sound_guide=raw_data.get("sound_guide", {"bgm": "Epic Wuxia", "fx": "Sword Clashing"})
        )
