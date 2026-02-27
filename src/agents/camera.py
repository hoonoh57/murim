from typing import List
from src.agents.base_agent import BaseAgent
from src.evolution.skill_tracker import DraftPractice
from src.core.models import Scenario

class CameraAgent(BaseAgent):
    def __init__(self, is_mock: bool = True):
        super().__init__(agent_type="camera", is_mock=is_mock)
        
    def plan_camera_angles(self, scenes: List) -> List:
        print(f"[Camera] Planning camera angles for {len(scenes)} scenes.")
        
        emotion_map = {
            "epic": {"angle": "Extreme Wide Shot", "movement": "Slow Zoom-in"},
            "비장함": {"angle": "Extreme Wide Shot", "movement": "Slow Zoom-in"},
            "action": {"angle": "Dutch Angle", "movement": "Handheld Shake"},
            "전투": {"angle": "Dutch Angle", "movement": "Handheld Shake"},
            "sad": {"angle": "Close-up", "movement": "Static"},
            "슬픔": {"angle": "Close-up", "movement": "Static"},
            "mystery": {"angle": "Low Angle", "movement": "Push-in"},
            "신비": {"angle": "Low Angle", "movement": "Push-in"}
        }
        
        plan = []
        for s in scenes:
            style = emotion_map.get(s.emotion.lower(), {"angle": "Eye Level", "movement": "Static"})
            plan.append({
                "scene_id": s.id,
                "angle": style["angle"],
                "movement": style["movement"]
            })
        return plan

    def revise_camera_plan(self, original_plan: str, critiques: list) -> str:
        """비평을 바탕으로 카메라 연출 계획을 개선합니다."""
        if not critiques:
            return original_plan

        if self.is_mock:
            return f"Enhanced Camera Strategy: {original_plan} with dynamic tracking and golden ratio framing."
            
        if not self.client:
            return original_plan

        critique_text = "\n".join([f"- {c.comment}" for c in critiques])
        prompt = f"""
        당신은 촬영 감독입니다.
        기존 연출 계획: {original_plan}
        비평 내용:
        {critique_text}
        
        비평을 수렴하여 시네마틱한 완성도를 높일 수 있는 개선된 카메라 연출 지시어(영문)를 작성하세요.
        """
        response = self.client.messages.create(
            model=self.model,
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text.strip()

    def self_practice(self, focus: str):
        print(f"\n[Camera Evolution] Focus Training: {focus}")
        
        # 1. 초안 카메라 기획
        dummy_scenario = Scenario(
            title=f"Camera Practice: {focus}",
            synopsis=focus,
            script=f"Camera strategy: {focus}",
            scenes=[],
            sound_guide={}
        )
        
        # 2. 1차 비평
        print("\n[Evolution] 1st Round Critique...")
        evaluated_v1 = self.council.evaluate(dummy_scenario)
        score_v1 = evaluated_v1.final_score
        
        # 3. 카메라 기획 수정
        revised_plan = self.revise_camera_plan(focus, evaluated_v1.critiques)
        print(f"[Camera] Revised strategy: {revised_plan}")
        
        # 4. 2차 비평 (재평가)
        dummy_scenario_v2 = Scenario(
            title=f"Camera Practice: {focus} (Revised)",
            synopsis=focus,
            script=f"Revised Camera Strategy: {revised_plan}",
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
            topic="Cinematic Grammar & Composition",
            focus_point=focus,
            scenario=evaluated_v2,
            self_reflection=reflection,
            evolution_step=self.log.current_level
        )
        self.add_experience(practice, score_v1, score_v2)
        print(f"습작 완료. 연출 품질 개선: {score_v1:.1f} -> {score_v2:.1f}")
