from src.agents.base_agent import BaseAgent
from src.core.skills import build_full_system_prompt
from src.core.skill_prompt import (
    build_full_prompt, build_imaging_system_prompt,
    HERO_LCM, WORLD_NEGATIVE, NEGATIVE_UNIVERSAL, NEGATIVE_CHARACTER,
)
from src.api.ai_clients import ImageGenerator
from src.evolution.skill_tracker import DraftPractice
from src.core.models import Scenario


class ImagingAgent(BaseAgent):
    def __init__(self, is_mock: bool = True):
        super().__init__(agent_type="imaging", is_mock=is_mock)
        self.generator = ImageGenerator(is_mock=is_mock)
        self.system_prompt = build_full_system_prompt("imaging")

    def generate(self, prompt: str, style_guide: dict = None) -> str:
        """프롬프트에 캐릭터 앵커 + 세계관 네거티브 자동 보강"""
        # 캐릭터 앵커가 없으면 자동 삽입
        if HERO_LCM["face"][:20] not in prompt:
            prompt = (
                f"Realistic digital painting, wuxia martial arts style, 16:9, 4K. "
                f"A {HERO_LCM['age_default']}-year-old East Asian boy, "
                f"{HERO_LCM['face']}, {HERO_LCM['hair']}, {HERO_LCM['build']}, "
                f"{HERO_LCM['marks']}. {prompt}"
            )

        if style_guide:
            palette = style_guide.get("palette", [])
            style_name = style_guide.get("style", "")
            prompt = f"{prompt}, Style: {style_name}, Colors: {', '.join(palette)}"

        return self.generator.generate(prompt)

    def generate_from_matrix(
        self,
        action: str,
        location_code: str = "LOC_MOUNTAIN_PATH",
        costume_code: str = "A",
        time_key: str = "일출(06-07)",
        emotion_key: str = "냉정",
        shot: str = "WS",
        angle: str = "eye",
        lighting: str = "volumetric",
        age: int = 16,
    ) -> str:
        """동기화 매트릭스 기반 프롬프트 자동 생성 후 이미지 생성"""
        full_prompt = build_full_prompt(
            action=action,
            location_code=location_code,
            costume_code=costume_code,
            time_key=time_key,
            emotion_key=emotion_key,
            shot=shot,
            angle=angle,
            lighting=lighting,
            age=age,
        )
        print(f"[Imaging] Auto-built prompt ({len(full_prompt)} chars)")
        return self.generator.generate(full_prompt)

    def get_negative_prompt(self, scene_type: str = "outdoor") -> str:
        """장면 유형에 따른 네거티브 프롬프트 반환"""
        base = f"{NEGATIVE_UNIVERSAL}, {WORLD_NEGATIVE}, {NEGATIVE_CHARACTER}"
        extras = {
            "cave":    ", outdoor, sunlight, sky, clouds, trees, grass",
            "indoor":  ", outdoor, sunlight, sky, clouds",
            "outdoor": ", indoor, ceiling, floor tiles, furniture, walls",
            "day":     ", night, moon, stars, darkness, torchlight",
            "night":   ", bright sunlight, blue sky, daylight",
        }
        return base + extras.get(scene_type, "")

    def revise_prompt(self, original_prompt: str, critiques: list) -> str:
        if not critiques:
            return original_prompt

        if self.is_mock:
            return f"{original_prompt}, highly detailed, cinematic lighting, 8k masterpiece"

        if not self.client:
            return original_prompt

        print("[Imaging] AI is revising prompt based on critiques...")
        critique_text = "\n".join([f"- {c.comment}" for c in critiques])
        prompt = (
            f"{self.system_prompt}\n\n"
            f"기존 프롬프트: {original_prompt}\n"
            f"비평 내용:\n{critique_text}\n\n"
            f"비평을 수렴하여 개선된 영어 프롬프트를 작성하세요. "
            f"캐릭터 앵커 텍스트는 동의어 없이 동일하게 유지. "
            f"프롬프트 텍스트만 출력하세요."
        )
        response = self.client.messages.create(
            model=self.model,
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text.strip()

    def self_practice(self, focus: str):
        print(f"\n[Imaging Evolution] Focus Training: {focus}")

        prompt_v1 = build_full_prompt(
            action=f"{focus}, highly detailed",
            location_code="LOC_MOUNTAIN_PATH",
            emotion_key="각성",
            shot="MS",
            lighting="rim",
        )
        print(f"[Imaging] Generated initial prompt: {prompt_v1[:80]}...")

        dummy_scenario = Scenario(
            title=f"Imaging Practice: {focus}",
            synopsis=focus,
            script=f"Visual Concept: {prompt_v1}",
            scenes=[], sound_guide={}
        )

        print("\n[Evolution] 1st Round Critique...")
        evaluated_v1 = self.council.evaluate(dummy_scenario)
        score_v1 = evaluated_v1.final_score

        prompt_v2 = self.revise_prompt(prompt_v1, evaluated_v1.critiques)
        print(f"[Imaging] Revised prompt: {prompt_v2[:80]}...")

        dummy_scenario_v2 = Scenario(
            title=f"Imaging Practice: {focus} (Revised)",
            synopsis=focus,
            script=f"Visual Concept: {prompt_v2}",
            scenes=[], sound_guide={}
        )

        print("\n[Evolution] 2nd Round Critique (Final Assessment)...")
        evaluated_v2 = self.council.evaluate(dummy_scenario_v2)
        score_v2 = evaluated_v2.final_score

        reflection = self._generate_reflection(evaluated_v2, score_v1, score_v2)

        practice = DraftPractice(
            topic="Visual Style & Prompt Engineering",
            focus_point=focus,
            scenario=evaluated_v2,
            self_reflection=reflection,
            evolution_step=self.log.current_level
        )
        self.add_experience(practice, score_v1, score_v2)
        print(f"습작 완료. 시각 품질 개선: {score_v1:.1f} -> {score_v2:.1f}")
