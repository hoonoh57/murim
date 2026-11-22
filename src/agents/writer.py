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
    def __init__(self, is_mock: bool = True, content_mode: str = "wuxia"):
        super().__init__(agent_type="writer", is_mock=is_mock)
        self.content_mode = content_mode
        self.council.content_mode = content_mode
        if content_mode == "historical_art":
            from src.core.constants import HISTORICAL_ART_PERSONAS
            self.council.personas = HISTORICAL_ART_PERSONAS
        self.engine = ScenarioEngine(is_mock=is_mock)
        # 장르 명시적 분기: 역사서사에는 무협 전용 15비트·천마 설정을 주입하지 않음
        self.system_prompt = build_full_system_prompt("writer", content_mode=self.content_mode)

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
            # Rehearsal is not a revised manuscript. Never manufacture quality improvement.
            return scenario

        feedback_summary = "\n".join(
            [f"- {c.persona}: {c.comment} (추천: {', '.join(c.suggestions)})"
             for c in critiques]
        )

        prompt = (
            f"다음은 당신이 쓴 {'사료 기반 역사서사' if self.content_mode == 'historical_art' else '무협'} 시나리오에 대한 6인 비평위원회의 의견입니다.\n\n"
            f"{feedback_summary}\n\n"
            f"실제 근거가 있는 결함만 해당 범위의 원문을 수정하고 JSON 형식으로 다시 제출하세요.\n"
            + (f"15비트 구조를 반드시 준수하세요. 총 {len(BEAT_STRUCTURE)}개 비트.\n" if self.content_mode == "wuxia" else "사료 기반 장편의 기존 관점·사건·결말은 감독의 변경 승인 없이 재설계하지 마세요.\n")
            + f"원본 제목: {scenario.title}\n원본 대본: {scenario.script}"
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
        return (f"모의 실습 기록 (작품 품질 검증 아님): {score_v1:.1f} -> {score_v2:.1f}" if self.is_mock else f"실제 비평 연습 결과: {score_v1:.1f} -> {score_v2:.1f} ({improvement:+.1f})")

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
            sound_guide=raw_data.get("sound_guide", {})
        )
