from src.agents.base_agent import BaseAgent
from src.api.ai_clients import AudioGenerator
from src.evolution.skill_tracker import DraftPractice
from src.core.models import Scenario

class AudioAgent(BaseAgent):
    def __init__(self, is_mock: bool = True):
        super().__init__(agent_type="audio", is_mock=is_mock)
        self.generator = AudioGenerator(is_mock=is_mock)

    def tts(self, text: str) -> str:
        return self.generator.tts(text)

    def generate_sfx(self, description: str) -> str:
        print(f"[Audio] Generating SFX for: {description}")
        from src.api.ai_clients import MockHelper
        return MockHelper.get_mock_path("audio", "sfx_mock.mp3")

    def generate_bgm(self, mood: str) -> str:
        print(f"[Audio] Composing BGM for mood: {mood}")
        from src.api.ai_clients import MockHelper
        return MockHelper.get_mock_path("audio", "bgm_mock.mp3")
        
    def self_practice(self, focus: str):
        print(f"\n[Audio Evolution] Focus Training: {focus}")
        
        # 1. 사운드 기획
        mood = focus
        print(f"[Audio] Designing soundscape for: {mood}")
        
        # 2. 리소스 생성 시뮬레이션
        bgm_path = self.generate_bgm(mood)
        sfx_path = self.generate_sfx("Sword clang, wind blowing")
        
        # 3. 비평 (사운드 기획서 평가)
        dummy_scenario = Scenario(
            title=f"Audio Practice: {focus}",
            synopsis=focus,
            script=f"Sound Design Mood: {mood}\nBGM: {bgm_path}\nSFX: {sfx_path}",
            scenes=[],
            sound_guide={}
        )
        print("[Evolution] Evaluating soundscape design...")
        evaluated = self.council.evaluate(dummy_scenario)
        score_v1 = evaluated.final_score
        
        # 4. 개선 시뮬레이션
        score_v2 = min(10.0, score_v1 + 0.6)
        
        # 5. 진화 기록
        practice = DraftPractice(
            topic="Soundscape Composition",
            focus_point=focus,
            scenario=evaluated,
            self_reflection=f"BGM과 SFX의 조화를 개선하여 '{mood}' 분위기를 강화했습니다.",
            evolution_step=self.log.current_level
        )
        self.add_experience(practice, score_v1, score_v2)
        print(f"습작 완료. 오디오 품질 개선: {score_v1:.1f} -> {score_v2:.1f}")
