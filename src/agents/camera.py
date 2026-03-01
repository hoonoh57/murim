from typing import List
from src.agents.base_agent import BaseAgent
from src.core.skills import build_full_system_prompt
from src.core.skill_sync import SYNC_LAWS
from src.core.skill_prompt import SHOT_SIZES, CAMERA_ANGLES, LIGHTING_PATTERNS
from src.evolution.skill_tracker import DraftPractice
from src.core.models import Scenario


class CameraAgent(BaseAgent):
    def __init__(self, is_mock: bool = True):
        super().__init__(agent_type="camera", is_mock=is_mock)
        self.system_prompt = build_full_system_prompt("camera")

    def plan_camera_angles(self, scenes: List) -> List:
        """감정 → 카메라 매핑: skills 기반"""
        print(f"[Camera] Planning camera angles for {len(scenes)} scenes.")

        emotion_map = {
            "epic":   {"angle": "low",   "shot": "EWS", "movement": "slow_zoom_in", "lighting": "volumetric"},
            "비장함":  {"angle": "low",   "shot": "EWS", "movement": "slow_zoom_in", "lighting": "volumetric"},
            "action": {"angle": "dutch", "shot": "MS",  "movement": "zoom_in",      "lighting": "rim"},
            "전투":   {"angle": "dutch", "shot": "MS",  "movement": "zoom_in",      "lighting": "rim"},
            "sad":    {"angle": "high",  "shot": "CU",  "movement": "static",       "lighting": "candle"},
            "슬픔":   {"angle": "high",  "shot": "CU",  "movement": "static",       "lighting": "candle"},
            "mystery":{"angle": "low",   "shot": "WS",  "movement": "pan_lr",       "lighting": "chiaroscuro"},
            "신비":   {"angle": "low",   "shot": "WS",  "movement": "pan_lr",       "lighting": "chiaroscuro"},
            "온기":   {"angle": "eye",   "shot": "MCU", "movement": "slow_zoom_in", "lighting": "rembrandt"},
            "긴장":   {"angle": "dutch", "shot": "CU",  "movement": "zoom_in",      "lighting": "split"},
            "고독":   {"angle": "high",  "shot": "EWS", "movement": "zoom_out",     "lighting": "silhouette"},
            "초월":   {"angle": "low",   "shot": "FS",  "movement": "static",       "lighting": "volumetric"},
        }

        default = {"angle": "eye", "shot": "MS", "movement": "static", "lighting": "volumetric"}

        plan = []
        for s in scenes:
            style = emotion_map.get(s.emotion.lower(), default)
            plan.append({
                "scene_id": s.id,
                "angle": CAMERA_ANGLES.get(style["angle"], CAMERA_ANGLES["eye"]),
                "shot": SHOT_SIZES.get(style["shot"], SHOT_SIZES["MS"]),
                "movement": style["movement"],
                "lighting": LIGHTING_PATTERNS.get(style["lighting"], LIGHTING_PATTERNS["volumetric"]),
            })
        return plan

    def revise_camera_plan(self, original_plan: str, critiques: list) -> str:
        if not critiques:
            return original_plan

        if self.is_mock:
            return f"Enhanced Camera Strategy: {original_plan} with dynamic tracking and golden ratio framing."

        if not self.client:
            return original_plan

        critique_text = "\n".join([f"- {c.comment}" for c in critiques])
        prompt = (
            f"{self.system_prompt}\n\n"
            f"기존 연출 계획: {original_plan}\n"
            f"비평 내용:\n{critique_text}\n\n"
            f"비평을 수렴하여 시네마틱한 완성도를 높일 수 있는 개선된 카메라 연출 지시어(영문)를 작성하세요."
        )
        response = self.client.messages.create(
            model=self.model,
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text.strip()

    def self_practice(self, focus: str):
        print(f"\n[Camera Evolution] Focus Training: {focus}")

        dummy_scenario = Scenario(
            title=f"Camera Practice: {focus}",
            synopsis=focus,
            script=f"Camera strategy: {focus}",
            scenes=[], sound_guide={}
        )

        print("\n[Evolution] 1st Round Critique...")
        evaluated_v1 = self.council.evaluate(dummy_scenario)
        score_v1 = evaluated_v1.final_score

        revised_plan = self.revise_camera_plan(focus, evaluated_v1.critiques)
        print(f"[Camera] Revised strategy: {revised_plan}")

        dummy_scenario_v2 = Scenario(
            title=f"Camera Practice: {focus} (Revised)",
            synopsis=focus,
            script=f"Revised Camera Strategy: {revised_plan}",
            scenes=[], sound_guide={}
        )

        print("\n[Evolution] 2nd Round Critique (Final Assessment)...")
        evaluated_v2 = self.council.evaluate(dummy_scenario_v2)
        score_v2 = evaluated_v2.final_score

        reflection = self._generate_reflection(evaluated_v2, score_v1, score_v2)

        practice = DraftPractice(
            topic="Cinematic Grammar & Composition",
            focus_point=focus,
            scenario=evaluated_v2,
            self_reflection=reflection,
            evolution_step=self.log.current_level
        )
        self.add_experience(practice, score_v1, score_v2)
        print(f"습작 완료. 연출 품질 개선: {score_v1:.1f} -> {score_v2:.1f}")
