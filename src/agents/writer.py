import os
import json
from typing import List
from src.core.models import Scenario, Scene, EpisodeRequest, Critique
from src.core.skills import build_full_system_prompt
from src.core.skill_story import BEAT_STRUCTURE, FORESHADOWING_RULES
from src.api.ai_clients import ScenarioEngine
from src.evolution.skill_tracker import DraftPractice
from src.agents.base_agent import BaseAgent


class WriterAgent(BaseAgent):
    def __init__(self, is_mock: bool = True):
        super().__init__(agent_type="writer", is_mock=is_mock)
        self.engine = ScenarioEngine(is_mock=is_mock)
        # 스킬 기반 시스템 프롬프트 (초월적 서술자 + 15비트 + 금지패턴)
        self.system_prompt = build_full_system_prompt("writer")

    def write_scenario(self, request: EpisodeRequest) -> Scenario:
        print(f"[Writer] Writing scenario for topic: {request.topic}")
        print(f"[Writer] System prompt loaded: {len(self.system_prompt)} chars")
        raw_data = self.engine.generate_episode(
            request.topic, request.events,
            system_prompt_override=self.system_prompt
        )
        return self._parse_scenario(raw_data, request.topic, request.events)

    def revise_scenario(self, scenario: Scenario, critiques: List[Critique]) -> Scenario:
        print(f"[Writer] Revising scenario based on council feedback...")

        if self.is_mock:
            scenario.title += " (Revised)"
            scenario.script += "\n\n[Revision] 비평가들의 의견을 반영하여 묘사를 강화했습니다."
            return scenario

        feedback_summary = "\n".join(
            [f"- {c.persona}: {c.comment} (추천: {', '.join(c.suggestions)})"
             for c in critiques]
        )

        prompt = (
            f"다음은 당신이 쓴 무협 시나리오에 대한 6인 비평위원회의 의견입니다.\n\n"
            f"{feedback_summary}\n\n"
            f"이 의견들을 적극 반영하여 시나리오를 수정하고 JSON 형식으로 다시 작성해주세요.\n"
            f"15비트 구조를 반드시 준수하세요. 총 {len(BEAT_STRUCTURE)}개 비트.\n"
            f"원본 제목: {scenario.title}\n원본 대본: {scenario.script}"
        )

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            system=self.system_prompt,
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
        print(f"\n[Writer Evolution] Focus Training: {focus_point}")

        req = EpisodeRequest(topic=f"습작: {focus_point}", events="자가 수련 중")
        scenario = self.write_scenario(req)

        print("\n[Evolution] 1st Round Critique...")
        scenario = self.council.evaluate(scenario)
        score_v1 = scenario.final_score

        scenario = self.revise_scenario(scenario, scenario.critiques)

        print("\n[Evolution] 2nd Round Critique (Final Assessment)...")
        scenario = self.council.evaluate(scenario)
        score_v2 = scenario.final_score

        print("\n[Evolution] Self-Reflection...")
        reflection = self._generate_reflection(scenario, score_v1, score_v2)

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
