"""
src/core/skills.py
스킬 로더 — 4개 스킬 모듈의 진입점 + 공통 상수
에이전트들은 이 파일 또는 개별 skill_*.py를 직접 import
"""
import os
from typing import Dict

# ── 원본 마크다운 로더 (docs/skills/) ──
SKILLS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "skills")

SKILL_FILES = {
    "transcendent": "TRANSCENDENT_NARRATOR_SKILL.md",
    "story":        "STORY_SKILL_GUIDE.md",
    "prompt":       "PROMPT_SKILL_GUIDE.md",
    "sync":         "IMAGE_NARRATION_SYNC_SKILL.md",
}


def load_skill_raw(key: str) -> str:
    """마크다운 원본 전체를 문자열로 반환 (AI 프롬프트 주입용)"""
    path = os.path.join(SKILLS_DIR, SKILL_FILES[key])
    if not os.path.isfile(path):
        return f"[WARN] Skill file not found: {path}"
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def load_all_skills_raw() -> Dict[str, str]:
    return {k: load_skill_raw(k) for k in SKILL_FILES}


# ── 계층 구조 ──
SKILL_HIERARCHY = [
    "transcendent",   # 최상위: 의식의 깊이 (누가 보는가)
    "story",          # 중위: 서사의 구조 (어떻게 짜는가)
    "prompt",         # 하위: 시각의 일관성 (어떻게 보여주는가)
    "sync",           # 동기화 레이어 (이미지 ↔ 나레이션 정합)
]


# ── 통합 시스템 프롬프트 빌더 ──
def build_full_system_prompt(agent_role: str) -> str:
    """에이전트 역할에 따라 필요한 스킬을 계층적으로 조합"""
    from src.core.skill_narrator import NARRATOR_SYSTEM_PROMPT
    from src.core.skill_story import (
        build_writer_system_prompt,
        BEAT_STRUCTURE, CHARACTER_LAYERS, ANTI_CLICHE,
    )
    from src.core.skill_prompt import (
        build_imaging_system_prompt,
        HERO_LCM, WORLD_MURIM, WORLD_NEGATIVE,
    )
    from src.core.skill_sync import (
        build_narration_prompt, SYNC_LAWS,
    )

    if agent_role == "writer":
        return f"{NARRATOR_SYSTEM_PROMPT}\n\n{build_writer_system_prompt()}"

    elif agent_role == "imaging":
        return build_imaging_system_prompt()

    elif agent_role == "video":
        return (
            f"[동기화 법칙]\n"
            f"Verb Lock: {SYNC_LAWS['verb_lock']}\n"
            f"Gaze Direction: {SYNC_LAWS['gaze_direction']}\n"
            f"Silence Law: {SYNC_LAWS['silence_law']}\n"
            f"[세계관] {WORLD_MURIM}\n"
            f"[네거티브] {WORLD_NEGATIVE}"
        )

    elif agent_role == "audio":
        return build_narration_prompt(12.0)  # 기본 12초 장면

    elif agent_role == "art_direction":
        return (
            f"[세계관] {WORLD_MURIM}\n"
            f"[캐릭터 앵커] {HERO_LCM['face']}\n"
            f"[감정 온도 팔레트] 냉: cold blue-grey | 온: warm gold | "
            f"열: high contrast rim light | 정: low-key monochrome"
        )

    elif agent_role == "camera":
        temporal = "\n".join(
            f"  {k}: {v}" for k, v in SYNC_LAWS["temporal_sync"].items()
        )
        return f"[카메라-감정 동기화]\n{temporal}"

    elif agent_role == "director":
        return (
            f"{NARRATOR_SYSTEM_PROMPT}\n\n"
            f"[품질 기준] 15비트 구조 준수, Anti-Cliché 위반 시 재생성 명령.\n"
            f"[복선 관리] 매 에피소드 1개 배치, 1개 회수."
        )

    elif agent_role == "marketing":
        return (
            f"[작품 정체성] 천마의 귀환 — 무협 회귀물\n"
            f"[톤] 초월적 서술, 절제된 감정, 심연의 중저음\n"
            f"[키워드] 무협, 천마, 회귀, 강호, 성장"
        )

    return ""
