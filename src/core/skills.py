"""
src/core/skills.py
스킬 로더 — legacy wuxia 스킬과 사료 기반 역사서사 v2 스킬 분리
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

# Historical modes never share the legacy "load_all_skills_raw" aggregate.
HISTORICAL_SKILL_FILES = {
    "editorial_master": "EDITORIAL_MASTER_SKILL_V2.md",
    "source_truth": "SOURCE_TRUTH_SKILL_V2.md",
    "cinematic_story": "CINEMATIC_NARRATIVE_SKILL_V2.md",
    "internal_red_team": "INTERNAL_RED_TEAM_SKILL_V2.md",
    "cultural_visual": "CULTURAL_VISUAL_DRAMATURGY_SKILL_V1.md",
}


def load_skill_raw(key: str) -> str:
    """마크다운 원본 전체를 문자열로 반환 (AI 프롬프트 주입용)"""
    registry = HISTORICAL_SKILL_FILES if key in HISTORICAL_SKILL_FILES else SKILL_FILES
    path = os.path.join(SKILLS_DIR, registry[key])
    if not os.path.isfile(path):
        return f"[WARN] Skill file not found: {path}"
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def load_all_skills_raw() -> Dict[str, str]:
    return {k: load_skill_raw(k) for k in SKILL_FILES}


# ── 기존 무협 전용 계층 구조 (역사서사에는 적용하지 않음) ──
SKILL_HIERARCHY = [
    "transcendent",   # 최상위: 의식의 깊이 (누가 보는가)
    "story",          # 중위: 서사의 구조 (어떻게 짜는가)
    "prompt",         # 하위: 시각의 일관성 (어떻게 보여주는가)
    "sync",           # 동기화 레이어 (이미지 ↔ 나레이션 정합)
]


# ── 사실 기반 장르 별도 SSOT (기존 무협 템플릿과 완전히 격리) ──
HISTORICAL_ART_SKILLS = {
    "director": ("editorial_master","source_truth","cinematic_story","cultural_visual","internal_red_team"),
    "writer": ("editorial_master","source_truth","cinematic_story"),
    "council": ("editorial_master","source_truth","cultural_visual","internal_red_team"),
    "art_direction": ("editorial_master","source_truth","cultural_visual"),
    "camera": ("editorial_master","cinematic_story","cultural_visual"),
    "audio": ("editorial_master","cinematic_story"),
    "imaging": ("editorial_master","source_truth","cultural_visual"),
    "video": ("editorial_master","source_truth","cultural_visual"),
    "marketing": ("editorial_master","cinematic_story"),
}

def build_historical_art_system_prompt(agent_role: str) -> str:
    if agent_role not in HISTORICAL_ART_SKILLS:
        raise ValueError("Historical art production role is not registered")
    texts = [load_skill_raw(name) for name in HISTORICAL_ART_SKILLS[agent_role]]
    if any(t.startswith("[WARN]") for t in texts):
        raise FileNotFoundError("Historical production skill is missing; work held")
    return "\n\n".join(texts)

# ── 통합 시스템 프롬프트 빌더 ──
def build_full_system_prompt(agent_role: str, content_mode: str = "wuxia") -> str:
    """Only the explicitly selected genre's skills may reach an agent."""
    if content_mode == "historical_art":
        return build_historical_art_system_prompt(agent_role)
    if content_mode != "wuxia":
        raise ValueError("Unregistered content mode")
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
