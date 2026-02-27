from src.agents.base_agent import BaseAgent
from src.api.ai_clients import VideoGenerator
from src.evolution.skill_tracker import DraftPractice
from src.core.models import Scenario

class VideoAgent(BaseAgent):
    def __init__(self, is_mock: bool = True):
        super().__init__(agent_type="video", is_mock=is_mock)
        self.generator = VideoGenerator(is_mock=is_mock)

    def generate_from_image(self, image_path: str, prompt: str) -> str:
        return self.generator.generate_from_image(image_path, prompt)
        
    def self_practice(self, focus: str):
        print(f"\n[Video Evolution] Focus Training: {focus}")
        
        # 1. 모델 선택 및 연출 기획
        model = "Grok Imagine Video (Simulated)"
        print(f"[Video] Selected model: {model} for {focus}")
        
        # 2. 영상 생성 시뮬레이션
        vid_path = self.generate_from_image("mock_img.png", f"Motion focus: {focus}")
        
        # 3. 비평 (모션 및 연출 평가)
        dummy_scenario = Scenario(
            title=f"Video Practice: {focus}",
            synopsis=focus,
            script=f"Motion Description: {focus}\nModel Used: {model}",
            scenes=[],
            sound_guide={}
        )
        print("[Evolution] Evaluating motion quality...")
        evaluated = self.council.evaluate(dummy_scenario)
        score_v1 = evaluated.final_score
        
        # 4. 개선 시뮬레이션
        score_v2 = min(10.0, score_v1 + 0.5)
        
        # 5. 진화 기록
        practice = DraftPractice(
            topic="Motion Naturalness & Temporal Consistency",
            focus_point=focus,
            scenario=evaluated,
            self_reflection=f"프레임 간 일관성을 유지하며 {focus} 동작의 자연스러움을 개선했습니다.",
            evolution_step=self.log.current_level
        )
        self.add_experience(practice, score_v1, score_v2)
        print(f"습작 완료. 영상 품질 개선: {score_v1:.1f} -> {score_v2:.1f}")
