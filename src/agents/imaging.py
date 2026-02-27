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

    def revise_prompt(self, original_prompt: str, critiques: list) -> str:
        """비평을 바탕으로 프롬프트를 개선합니다."""
        if self.is_mock:
            return f"{original_prompt}, highly detailed, cinematic lighting, 8k masterpiece"
            
        print("[Imaging] AI is revising prompt based on critiques...")
        critique_text = "\n".join([f"- {c.comment}" for c in critiques])
        prompt = f"""
        당신은 이미지 프롬프트 엔지니어입니다.
        기존 프롬프트: {original_prompt}
        비평 내용:
        {critique_text}
        
        비평을 수렴하여 더 고퀄리티의 이미지를 생성할 수 있는 개선된 영어 프롬프트를 작성하세요. 
        프롬프트 텍스트만 출력하세요.
        """
        response = self.client.messages.create(
            model=self.model,
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text.strip()

    def self_practice(self, focus: str):
        print(f"\n[Imaging Evolution] Focus Training: {focus}")
        
        # 1. 초안 프롬프트 생성
        prompt_v1 = f"Cinematic wuxia scene, {focus}, highly detailed, 8k"
        print(f"[Imaging] Generated initial prompt: {prompt_v1}")
        
        # 2. 1차 비평
        dummy_scenario = Scenario(
            title=f"Imaging Practice: {focus}",
            synopsis=focus,
            script=f"Visual Concept: {prompt_v1}",
            scenes=[],
            sound_guide={}
        )
        print("\n[Evolution] 1st Round Critique...")
        evaluated_v1 = self.council.evaluate(dummy_scenario)
        score_v1 = evaluated_v1.final_score
        
        # 3. 프롬프트 수정
        prompt_v2 = self.revise_prompt(prompt_v1, evaluated_v1.critiques)
        print(f"[Imaging] Revised prompt: {prompt_v2}")
        
        # 4. 2차 비평 (재평가)
        dummy_scenario_v2 = Scenario(
            title=f"Imaging Practice: {focus} (Revised)",
            synopsis=focus,
            script=f"Visual Concept: {prompt_v2}",
            scenes=[],
            sound_guide={}
        )
        print("\n[Evolution] 2nd Round Critique (Final Assessment)...")
        evaluated_v2 = self.council.evaluate(dummy_scenario_v2)
        score_v2 = evaluated_v2.final_score
        
        # 5. 자기 성찰
        reflection = self._generate_reflection(evaluated_v2, score_v1, score_v2)
        
        # 6. 진화 기록 저장
        practice = DraftPractice(
            topic="Visual Style & Prompt Engineering",
            focus_point=focus,
            scenario=evaluated_v2,
            self_reflection=reflection,
            evolution_step=self.log.current_level
        )
        self.add_experience(practice, score_v1, score_v2)
        print(f"습작 완료. 시각 품질 개선: {score_v1:.1f} -> {score_v2:.1f}")
