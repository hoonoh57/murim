from src.agents.base_agent import BaseAgent
from src.core.skills import build_full_system_prompt
from src.core.skill_sync import SYNC_LAWS
from src.core.skill_prompt import WORLD_MURIM
from src.evolution.skill_tracker import DraftPractice
from src.core.models import Scenario


class ArtDirectionAgent(BaseAgent):
    def __init__(self, is_mock: bool = True):
        super().__init__(agent_type="art_direction", is_mock=is_mock)
        self.system_prompt = build_full_system_prompt("art_direction")

    def design_style_guide(self, worldview: str) -> dict:
        """감정 온도 기반 스타일 가이드 — skills 연동"""
        print(f"[ArtDirection] Designing style guide for: {worldview}")

        temp_map = SYNC_LAWS["emotional_temperature"]

        if "어두운" in worldview or "피" in worldview or "냉" in worldview:
            return {
                "palette": ["#1A1A1A", "#8B0000", "#4B0082"],
                "style": "Dark/Grim Wuxia",
                "lighting": temp_map["냉"],
            }
        elif "화려한" in worldview or "황실" in worldview or "열" in worldview:
            return {
                "palette": ["#FFD700", "#DAA520", "#FFFFFF"],
                "style": "Imperial/Bright Wuxia",
                "lighting": temp_map["열"],
            }
        elif "신비로운" in worldview or "무당" in worldview or "정" in worldview:
            return {
                "palette": ["#E0FFFF", "#4682B4", "#F0F8FF"],
                "style": "Mystical/Taoist Wuxia",
                "lighting": temp_map["정"],
            }

        return {
            "palette": ["#2D1B1B", "#DAA520", "#3D3D3D"],
            "style": "Traditional Wuxia",
            "lighting": temp_map["온"],
        }

    def get_emotional_palette(self, temperature: str) -> dict:
        """감정 온도 코드로 직접 팔레트 조회"""
        palettes = {
            "냉": {"palette": ["#1A1A2E", "#16213E", "#0F3460"], "lighting": SYNC_LAWS["emotional_temperature"]["냉"]},
            "온": {"palette": ["#DAA520", "#CD853F", "#D2691E"], "lighting": SYNC_LAWS["emotional_temperature"]["온"]},
            "열": {"palette": ["#8B0000", "#FF4500", "#DC143C"], "lighting": SYNC_LAWS["emotional_temperature"]["열"]},
            "정": {"palette": ["#2F2F2F", "#4A4A4A", "#696969"], "lighting": SYNC_LAWS["emotional_temperature"]["정"]},
        }
        return palettes.get(temperature, palettes["온"])

    def revise_style_guide(self, original_concept: str, critiques: list) -> str:
        if not critiques:
            return original_concept

        if self.is_mock:
            return f"Enhanced Style: {original_concept} with deeper textures and refined color theory."

        if not self.client:
            return original_concept

        critique_text = "\n".join([f"- {c.comment}" for c in critiques])
        prompt = (
            f"{self.system_prompt}\n\n"
            f"기존 비주얼 컨셉: {original_concept}\n"
            f"비평 내용:\n{critique_text}\n\n"
            f"비평을 수렴하여 시각적 일관성과 예술성을 강화할 수 있는 개선된 스타일 정의를 작성하세요."
        )
        response = self.client.messages.create(
            model=self.model,
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text.strip()

    def self_practice(self, focus: str):
        print(f"\n[ArtDirection Evolution] Focus Training: {focus}")

        dummy_scenario = Scenario(
            title=f"ArtDirection Practice: {focus}",
            synopsis=focus,
            script=f"Visual Identity focus: {focus}",
            scenes=[], sound_guide={}
        )

        print("\n[Evolution] 1st Round Critique...")
        evaluated_v1 = self.council.evaluate(dummy_scenario)
        score_v1 = evaluated_v1.final_score

        revised_concept = self.revise_style_guide(focus, evaluated_v1.critiques)
        print(f"[ArtDirection] Revised concept: {revised_concept}")

        dummy_scenario_v2 = Scenario(
            title=f"ArtDirection Practice: {focus} (Revised)",
            synopsis=focus,
            script=f"Revised Visual Identity: {revised_concept}",
            scenes=[], sound_guide={}
        )

        print("\n[Evolution] 2nd Round Critique (Final Assessment)...")
        evaluated_v2 = self.council.evaluate(dummy_scenario_v2)
        score_v2 = evaluated_v2.final_score

        reflection = self._generate_reflection(evaluated_v2, score_v1, score_v2)

        practice = DraftPractice(
            topic="Visual World Building & Consistency",
            focus_point=focus,
            scenario=evaluated_v2,
            self_reflection=reflection,
            evolution_step=self.log.current_level
        )
        self.add_experience(practice, score_v1, score_v2)
        print(f"습작 완료. 미술 품질 개선: {score_v1:.1f} -> {score_v2:.1f}")
