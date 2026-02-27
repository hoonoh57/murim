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
        
    def revise_soundscape(self, original_mood: str, critiques: list) -> str:
        """비평을 바탕으로 사운드스케이프 기획을 개선합니다."""
        if not critiques:
            return original_mood

        if self.is_mock:
            return f"Enhanced {original_mood}: Better BGM/SFX layering and emotional resonance."
            
        if not self.client:
            return original_mood

        critique_text = "\n".join([f"- {c.comment}" for c in critiques])
        prompt = f"""
        당신은 사운드 디자이너입니다.
        기존 분위기: {original_mood}
        비평 내용:
        {critique_text}
        
        비평을 수렴하여 BGM과 SFX의 조화를 높일 수 있는 개선된 사운드 기획(한글/영문 혼용)을 작성하세요.
        """
        response = self.client.messages.create(
            model=self.model,
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text.strip()

    def self_practice(self, focus: str):
        print(f"\n[Audio Evolution] Focus Training: {focus}")
        
        # 1. 초안 사운드 기획
        dummy_scenario = Scenario(
            title=f"Audio Practice: {focus}",
            synopsis=focus,
            script=f"Sound Mood: {focus}",
            scenes=[],
            sound_guide={}
        )
        
        # 2. 1차 비평
        print("\n[Evolution] 1st Round Critique...")
        evaluated_v1 = self.council.evaluate(dummy_scenario)
        score_v1 = evaluated_v1.final_score
        
        # 3. 사운드 기획 수정
        revised_mood = self.revise_soundscape(focus, evaluated_v1.critiques)
        print(f"[Audio] Revised soundscape: {revised_mood}")
        
        # 4. 2차 비평 (재평가)
        dummy_scenario_v2 = Scenario(
            title=f"Audio Practice: {focus} (Revised)",
            synopsis=focus,
            script=f"Revised Sound Mood: {revised_mood}",
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
            topic="Soundscape Composition",
            focus_point=focus,
            scenario=evaluated_v2,
            self_reflection=reflection,
            evolution_step=self.log.current_level
        )
        self.add_experience(practice, score_v1, score_v2)
        print(f"습작 완료. 오디오 품질 개선: {score_v1:.1f} -> {score_v2:.1f}")
