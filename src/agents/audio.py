from src.agents.base_agent import BaseAgent
from src.core.skills import build_full_system_prompt
from src.core.skill_sync import NARRATION_RULES, build_narration_prompt
from src.api.ai_clients import AudioGenerator, MockHelper
from src.evolution.skill_tracker import DraftPractice
from src.core.models import Scenario


class AudioAgent(BaseAgent):
    def __init__(self, is_mock: bool = True, content_mode: str = "wuxia"):
        super().__init__(agent_type="audio", is_mock=is_mock)
        self.generator = AudioGenerator(is_mock=is_mock)
        self.content_mode = content_mode
        self.system_prompt = build_full_system_prompt("audio", content_mode=content_mode)

    def tts(self, text: str) -> str:
        if self.content_mode == "historical_art":
            raise ValueError("검증된 실제 낭독 원고·음성 품질 G3 전 자동 TTS는 금지합니다.")
        return self.generator.tts(text)

    def generate_sfx(self, description: str) -> str:
        if self.content_mode == "historical_art":
            raise ValueError("역사서사 음향은 장면 의미/권리 확인 이전 임의 생성 금지")
        print(f"[Audio] Generating SFX for: {description}")
        return MockHelper.get_mock_path("audio", "sfx_mock.mp3")

    def generate_bgm(self, mood: str) -> str:
        if self.content_mode == "historical_art":
            raise ValueError("문화·예술 BGM은 승인된 음향 설계와 청취 검증 필요")
        print(f"[Audio] Composing BGM for mood: {mood}")
        return MockHelper.get_mock_path("audio", "bgm_mock.mp3")

    def validate_narration_length(self, text: str, scene_duration_sec: float) -> dict:
        """나레이션 텍스트가 장면 시간에 맞는지 검증"""
        if self.content_mode == "historical_art":
            raise ValueError("무협 3초 무음/초당 문자수 기준은 역사서사에 적용 불가")
        available = scene_duration_sec - NARRATION_RULES["silence_tail_sec"]
        max_chars = int(available * NARRATION_RULES["chars_per_sec"])
        actual = len(text)
        ok = actual <= max_chars
        return {
            "valid": ok,
            "actual_chars": actual,
            "max_chars": max_chars,
            "available_sec": available,
            "silence_tail_sec": NARRATION_RULES["silence_tail_sec"],
            "overflow": max(0, actual - max_chars),
        }

    def get_narration_guide(self, scene_duration_sec: float) -> str:
        """장면 시간에 맞는 나레이션 가이드 반환"""
        if self.content_mode == "historical_art":
            raise ValueError("문화·예술 음성은 실제 낭독으로 시간 측정해야 합니다")
        return build_narration_prompt(scene_duration_sec)

    def revise_soundscape(self, original_mood: str, critiques: list) -> str:
        if self.content_mode == "historical_art":
            raise ValueError("문화·예술 음향은 무협형 자동 감정 포장으로 고칠 수 없습니다")
        if not critiques:
            return original_mood

        if self.is_mock:
            return f"Enhanced {original_mood}: Better BGM/SFX layering and emotional resonance."

        if not self.client:
            return original_mood

        critique_text = "\n".join([f"- {c.comment}" for c in critiques])
        prompt = (
            f"{self.system_prompt}\n\n"
            f"기존 분위기: {original_mood}\n"
            f"비평 내용:\n{critique_text}\n\n"
            f"비평을 수렴하여 BGM과 SFX의 조화를 높일 수 있는 개선된 사운드 기획을 작성하세요."
        )
        response = self.client.messages.create(
            model=self.model,
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text.strip()

    def self_practice(self, focus: str):
        print(f"\n[Audio Evolution] Focus Training: {focus}")

        dummy_scenario = Scenario(
            title=f"Audio Practice: {focus}",
            synopsis=focus,
            script=f"Sound Mood: {focus}",
            scenes=[], sound_guide={}
        )

        print("\n[Evolution] 1st Round Critique...")
        evaluated_v1 = self.council.evaluate(dummy_scenario)
        score_v1 = evaluated_v1.final_score

        revised_mood = self.revise_soundscape(focus, evaluated_v1.critiques)
        print(f"[Audio] Revised soundscape: {revised_mood}")

        dummy_scenario_v2 = Scenario(
            title=f"Audio Practice: {focus} (Revised)",
            synopsis=focus,
            script=f"Revised Sound Mood: {revised_mood}",
            scenes=[], sound_guide={}
        )

        print("\n[Evolution] 2nd Round Critique (Final Assessment)...")
        evaluated_v2 = self.council.evaluate(dummy_scenario_v2)
        score_v2 = evaluated_v2.final_score

        reflection = self._generate_reflection(evaluated_v2, score_v1, score_v2)

        practice = DraftPractice(
            topic="Soundscape Composition",
            focus_point=focus,
            scenario=evaluated_v2,
            self_reflection=reflection,
            evolution_step=self.log.current_level
        )
        self.add_experience(practice, score_v1, score_v2)
        print(f"습작 완료. 오디오 품질 개선: {score_v1:.1f} -> {score_v2:.1f}")
