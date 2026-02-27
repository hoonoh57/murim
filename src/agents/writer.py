import os
import json
from typing import List
from src.core.models import Scenario, Scene, EpisodeRequest, Critique
from src.api.ai_clients import ScenarioEngine
from src.evolution.skill_tracker import DraftPractice
from src.agents.base_agent import BaseAgent

class WriterAgent(BaseAgent):
    def __init__(self, is_mock: bool = True):
        super().__init__(agent_type="writer", is_mock=is_mock)
        self.engine = ScenarioEngine(is_mock=is_mock)
        
    def write_scenario(self, request: EpisodeRequest) -> Scenario:
        print(f"[Writer] Writing scenario for topic: {request.topic}")
        raw_data = self.engine.generate_episode(request.topic, request.events)
        return self._parse_scenario(raw_data, request.topic, request.events)

    def revise_scenario(self, scenario: Scenario, critiques: List[Critique]) -> Scenario:
        """비평가의 의견을 반영하여 시나리오를 수정합니다."""
        print(f"[Writer] Revising scenario based on council feedback...")
        
        if self.is_mock:
            scenario.title += " (Revised)"
            scenario.script += "\n\n[Revision] 비평가들의 의견을 반영하여 묘사를 강화했습니다."
            return scenario
            
        feedback_summary = "\n".join([f"- {c.persona}: {c.comment} (추천: {', '.join(c.suggestions)})" for c in critiques])
        
        prompt = f"다음은 당신이 쓴 무협 시나리오에 대한 6인 비평위원회의 의견입니다.\n\n{feedback_summary}\n\n이 의견들을 적극 반영하여 시나리오를 수정하고 JSON 형식으로 다시 작성해주세요.\n원본 제목: {scenario.title}\n원본 대본: {scenario.script}"
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            system="당신은 비평을 겸허히 수용하여 작품을 완성하는 대가(大家) 작가입니다. 반드시 JSON으로만 답하세요.",
            messages=[{"role": "user", "content": prompt}]
        )
        
        try:
            content = response.content[0].text
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            raw_data = json.loads(content)
            return self._parse_scenario(raw_data, scenario.title, scenario.synopsis)
        except Exception as e:
            print(f"[Error] Revision failed: {e}")
            return scenario

    def self_practice(self, focus_point: str) -> str:
        """작가가 스스로 습작(習作)을 수행하고 비평-수정 루프를 거쳐 진화합니다."""
        print(f"\n[Writer Evolution] Focus Training: {focus_point}")
        
        # 1. 초안 작성
        req = EpisodeRequest(topic=f"습작: {focus_point}", events="자가 수련 중")
        scenario = self.write_scenario(req)
        
        # 2. 1차 비평
        print("\n[Evolution] 1st Round Critique...")
        scenario = self.council.evaluate(scenario)
        score_v1 = scenario.final_score
        
        # 3. 수정 집필
        scenario = self.revise_scenario(scenario, scenario.critiques)
        
        # 4. 2차 비평 (재평가)
        print("\n[Evolution] 2nd Round Critique (Final Assessment)...")
        scenario = self.council.evaluate(scenario)
        score_v2 = scenario.final_score
        
        # 5. 자기 성찰
        print("\n[Evolution] Self-Reflection...")
        reflection = self._generate_reflection(scenario, score_v1, score_v2)
        
        # 6. 진화 기록 저장
        practice = DraftPractice(
            topic=req.topic,
            focus_point=focus_point,
            scenario=scenario,
            self_reflection=reflection,
            evolution_step=self.log.current_level
        )
        self.add_experience(practice, score_v1, score_v2)
        
        improvement = score_v2 - score_v1
        return f"습작 및 진화 완료. 점수 변화: {score_v1:.1f} -> {score_v2:.1f} ({improvement:+.1f})"

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
