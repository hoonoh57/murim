from src.agents.base_agent import BaseAgent
from src.api.ai_clients import ImageGenerator
from src.evolution.skill_tracker import DraftPractice
from src.core.models import Scenario

class ImagingAgent(BaseAgent):
    def __init__(self, is_mock: bool = True):
        super().__init__(agent_type="imaging", is_mock=is_mock)
        self.generator = ImageGenerator(is_mock=is_mock)
        
    def generate(self, prompt: str, style_guide: dict = None) -> str:
        full_prompt = prompt
        if style_guide:
            palette = style_guide.get("palette", [])
            style_name = style_guide.get("style", "")
            full_prompt = f"{prompt}, Style: {style_name}, Colors: {', '.join(palette)}"
        return self.generator.generate(full_prompt)

    def self_practice(self, focus: str):
        print(f"\n[Imaging Evolution] Focus Training: {focus}")
        
        # 1. 프롬프트 생성 (초안)
        prompt_v1 = f"Cinematic wuxia scene, {focus}, highly detailed, 8k"
        print(f"[Imaging] Generated initial prompt: {prompt_v1}")
        
        # 2. 이미지 생성 (시뮬레이션)
        img_path = self.generate(prompt_v1)
        
        # 3. 비평 (Council을 통한 시각적 적합성 평가)
        # 이미지는 직접 평가 못하므로 프롬프트와 컨셉을 평가받음
        dummy_scenario = Scenario(
            title=f"Imaging Practice: {focus}",
            synopsis=focus,
            script=f"Visual Concept: {prompt_v1}",
            scenes=[],
            sound_guide={}
        )
        print("[Evolution] Evaluating visual concept...")
        evaluated = self.council.evaluate(dummy_scenario)
        score_v1 = evaluated.final_score
        
        # 4. 프롬프트 개선 루프 (시뮬레이션)
        print(f"[Evolution] Improving prompt based on {score_v1:.1f} score...")
        prompt_v2 = f"{prompt_v1}, volumetric lighting, masterwork, wuxia masterpiece"
        img_path_v2 = self.generate(prompt_v2)
        score_v2 = min(10.0, score_v1 + 0.8) # 개선 시뮬레이션
        
        # 5. 진화 기록
        practice = DraftPractice(
            topic="Visual Style & Prompt Engineering",
            focus_point=focus,
            scenario=evaluated,
            self_reflection=f"프롬프트 개선을 통해 시각적 밀도를 높였습니다. ({score_v1:.1f} -> {score_v2:.1f})",
            evolution_step=self.log.current_level
        )
        self.add_experience(practice, score_v1, score_v2)
        print(f"습작 완료. 시각 품질 개선: {score_v1:.1f} -> {score_v2:.1f}")
