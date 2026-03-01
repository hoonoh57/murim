from src.agents.base_agent import BaseAgent
from src.core.skills import build_full_system_prompt
from src.core.skill_sync import SYNC_LAWS, get_ken_burns_direction
from src.api.ai_clients import VideoGenerator
from src.evolution.skill_tracker import DraftPractice
from src.core.models import Scenario


class VideoAgent(BaseAgent):
    def __init__(self, is_mock: bool = True):
        super().__init__(agent_type="video", is_mock=is_mock)
        self.generator = VideoGenerator(is_mock=is_mock)
        self.system_prompt = build_full_system_prompt("video")

    def generate_from_image(self, image_path: str, prompt: str, camera_plan: dict = None) -> str:
        full_prompt = prompt
        if camera_plan:
            angle = camera_plan.get("angle", "")
            movement = camera_plan.get("movement", "")
            full_prompt = f"{prompt}, Camera: {angle}, Motion: {movement}"
        return self.generator.generate_from_image(image_path, full_prompt)

    def generate_with_sync(
        self,
        image_path: str,
        prompt: str,
        narrative_context: str = "현재 긴장 고조",
        camera_plan: dict = None,
    ) -> str:
        """동기화 법칙 기반 영상 생성 — Ken Burns 방향 자동 결정"""
        ken_burns = get_ken_burns_direction(narrative_context)
        motion = f"Ken Burns {ken_burns}"

        if camera_plan:
            angle = camera_plan.get("angle", "eye level")
            motion = f"{motion}, Camera: {angle}"

        full_prompt = f"{prompt}, {motion}"
        print(f"[Video] Sync: {narrative_context} → {ken_burns}")
        return self.generator.generate_from_image(image_path, full_prompt)

    def revise_plan(self, original_focus: str, critiques: list) -> str:
        if not critiques:
            return original_focus

        if self.is_mock:
            return f"Enhanced motion: {original_focus} with better temporal stability and fluid transitions."

        if not self.client:
            return original_focus

        critique_text = "\n".join([f"- {c.comment}" for c in critiques])
        prompt = (
            f"{self.system_prompt}\n\n"
            f"기존 연출 초점: {original_focus}\n"
            f"비평 내용:\n{critique_text}\n\n"
            f"비평을 수렴하여 영상의 자연스러움과 연출적 완성도를 높일 수 있는 "
            f"개선된 연출 지시어(영문)를 작성하세요."
        )
        response = self.client.messages.create(
            model=self.model,
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text.strip()

    def self_practice(self, focus: str):
        print(f"\n[Video Evolution] Focus Training: {focus}")

        dummy_scenario = Scenario(
            title=f"Video Practice: {focus}",
            synopsis=focus,
            script=f"Motion Focus: {focus}",
            scenes=[], sound_guide={}
        )

        print("\n[Evolution] 1st Round Critique...")
        evaluated_v1 = self.council.evaluate(dummy_scenario)
        score_v1 = evaluated_v1.final_score

        revised_focus = self.revise_plan(focus, evaluated_v1.critiques)
        print(f"[Video] Revised motion focus: {revised_focus}")

        dummy_scenario_v2 = Scenario(
            title=f"Video Practice: {focus} (Revised)",
            synopsis=focus,
            script=f"Revised Motion Focus: {revised_focus}",
            scenes=[], sound_guide={}
        )

        print("\n[Evolution] 2nd Round Critique (Final Assessment)...")
        evaluated_v2 = self.council.evaluate(dummy_scenario_v2)
        score_v2 = evaluated_v2.final_score

        reflection = self._generate_reflection(evaluated_v2, score_v1, score_v2)

        practice = DraftPractice(
            topic="Motion Naturalness & Temporal Consistency",
            focus_point=focus,
            scenario=evaluated_v2,
            self_reflection=reflection,
            evolution_step=self.log.current_level
        )
        self.add_experience(practice, score_v1, score_v2)
        print(f"습작 완료. 영상 품질 개선: {score_v1:.1f} -> {score_v2:.1f}")
