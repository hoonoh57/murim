from src.agents.base_agent import BaseAgent
from src.evolution.skill_tracker import DraftPractice
from src.core.models import Scenario

class CameraAgent(BaseAgent):
    def __init__(self, is_mock: bool = True):
        super().__init__(agent_type="camera", is_mock=is_mock)
        
    def plan_camera_angles(self, scenes: List) -> List:
        print(f"[Camera] Planning camera angles for {len(scenes)} scenes.")
        # Mocking planning logic
        return [{"scene_id": s.id, "angle": "Low Angle", "movement": "Push-in"} for s in scenes]

    def self_practice(self, focus: str):
        print(f"\n[Camera Evolution] Focus Training: {focus}")
        
        # 1. 연출 기획
        concept = focus
        print(f"[Camera] Designing cinematography for: {concept}")
        
        # 2. 비평 (연출 기획서 평가)
        dummy_scenario = Scenario(
            title=f"Camera Practice: {focus}",
            synopsis=focus,
            script=f"Cinematography Focus: {concept}\nCamera Grammar: {focus}",
            scenes=[],
            sound_guide={}
        )
        print("[Evolution] Evaluating cinematography design...")
        evaluated = self.council.evaluate(dummy_scenario)
        score_v1 = evaluated.final_score
        
        # 4. 개선 시뮬레이션
        score_v2 = min(10.0, score_v1 + 0.5)
        
        # 5. 진화 기록
        practice = DraftPractice(
            topic="Cinematic Grammar & Composition",
            focus_point=focus,
            scenario=evaluated,
            self_reflection=f"시네마틱 문법을 적용하여 장면에 극적 긴장감을 더했습니다.",
            evolution_step=self.log.current_level
        )
        self.add_experience(practice, score_v1, score_v2)
        print(f"습작 완료. 연출 품질 개선: {score_v1:.1f} -> {score_v2:.1f}")
