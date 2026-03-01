"""
src/core/skill_sync.py
IMAGE_NARRATION_SYNC_SKILL.md의 코드화
동기화 레이어: 이미지 ↔ 나레이션 정합성
"""

# ── 5법칙 ──
SYNC_LAWS = {
    "verb_lock": "나레이션 핵심 동사를 이미지 Peak Action으로 시각화",
    "emotional_temperature": {
        "냉": "cold blue-grey palette, hard directional lighting, high contrast",
        "온": "warm golden hour, soft diffused light, gentle bokeh",
        "열": "high contrast, rim light, dust particles, dynamic",
        "정": "low-key, monochrome tendency, static composition",
    },
    "gaze_direction": "나레이션 주목 대상 = 이미지 focal point (shallow DOF)",
    "temporal_sync": {
        "과거 회상":     "zoom_out — 멀어짐 = 기억에서 빠져나옴",
        "현재 긴장 고조": "zoom_in — 다가감 = 압박감",
        "환경 소개":     "pan_lr — 시선 이동 = 탐색",
        "감정 클라이맥스": "slow_zoom_in — 천천히, 감정 잠김",
        "결말/여운":     "static_or_slow_zoom_out",
    },
    "silence_law": "마지막 2-3초 나레이션 없음. 이미지만 호흡.",
}

# ── 나레이션 규칙 ──
NARRATION_RULES = {
    "perspective": "3인칭 전지적, 감정 절제",
    "sentence_length": "7-15자/문장, 20자 초과 금지",
    "rhythm": "짧-짧-길 패턴 반복. 세 번째 문장이 감정을 담는다.",
    "forbidden": ["감탄사(아!, 오!)", "설명적 형용사 남발", "독자 직접 호명"],
    "allowed": ["비유 1개/장면", "반복 모티프", "의도적 비문(단어만 던지기)"],
    "tts_speed": "-10%",
    "chars_per_sec": 3.5,
    "silence_tail_sec": 3,
    "motif_min_count": 3,
    "motif_rule": "매 변주마다 톤 변화: 무심 → 의미부여 → 감정 폭발. 마지막 변주는 무성.",
}

# ── 동기화 매트릭스 템플릿 ──
SYNC_MATRIX_TEMPLATE = {
    "scene_id": "",
    "narration_text": "",
    "core_verb": "",
    "emotional_temperature": "",   # 냉/온/열/정
    "gaze_focus": "",
    "peak_frame": "",
    "ken_burns": "",               # zoom_in / zoom_out / pan_lr / slow_zoom_in / static
    "silence_sec": 3,
    "camera": "",
    "lighting": "",
    "color_temperature": "",
}

# ── 모델 비교 설정 (ComfyUI) ──
MODEL_CONFIGS = {
    "M1_SDXL_Base": {
        "ckpt": "sd_xl_base_1.0.safetensors",
        "lora": "sdxl_lightning_4step_lora.safetensors",
        "lora_strength": 1.0,
        "steps": 4, "cfg": 1.0,
        "sampler": "euler", "scheduler": "sgm_uniform",
    },
    "M2_JuggernautXL": {
        "ckpt": "Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors",
        "lora": "sdxl_lightning_4step_lora.safetensors",
        "lora_strength": 1.0,
        "steps": 4, "cfg": 1.0,
        "sampler": "euler", "scheduler": "sgm_uniform",
    },
    "M3_RealVisXL_Lightning": {
        "ckpt": "RealVisXL_V4.0_Lightning.safetensors",
        "lora": None,
        "steps": 5, "cfg": 1.5,
        "sampler": "dpmpp_sde", "scheduler": "karras",
    },
    "M4_DreamShaperXL_Turbo": {
        "ckpt": "DreamShaperXL_Turbo_v2.safetensors",
        "lora": None,
        "steps": 4, "cfg": 2.0,
        "sampler": "dpmpp_sde", "scheduler": "karras",
    },
}


def build_narration_prompt(scene_duration_sec: float) -> str:
    """나레이션 생성용 가이드"""
    avail = scene_duration_sec - NARRATION_RULES["silence_tail_sec"]
    max_chars = int(avail * NARRATION_RULES["chars_per_sec"])
    return (
        f"[나레이션 규칙]\n"
        f"  - 시점: {NARRATION_RULES['perspective']}\n"
        f"  - 문장 길이: {NARRATION_RULES['sentence_length']}\n"
        f"  - 리듬: {NARRATION_RULES['rhythm']}\n"
        f"  - 이 장면 최대 글자수: {max_chars}자 ({avail:.1f}초 × 3.5자/초)\n"
        f"  - 마지막 {NARRATION_RULES['silence_tail_sec']}초는 침묵\n"
        f"  - 금지: {', '.join(NARRATION_RULES['forbidden'])}\n"
        f"  - 허용: {', '.join(NARRATION_RULES['allowed'])}\n"
        f"  - 모티프: {NARRATION_RULES['motif_rule']}"
    )


def get_emotional_lighting(temperature: str) -> str:
    """감정 온도 → 조명 키워드 자동 매핑"""
    return SYNC_LAWS["emotional_temperature"].get(temperature, "")


def get_ken_burns_direction(narrative_context: str) -> str:
    """나레이션 맥락 → Ken Burns 방향"""
    return SYNC_LAWS["temporal_sync"].get(narrative_context, "static")


def build_sync_matrix(
    scene_id: str,
    narration: str,
    core_verb: str,
    temperature: str,
    gaze: str,
    peak_frame: str,
    narrative_context: str,
    camera: str = "",
    color_temp: str = "",
) -> dict:
    """장면별 동기화 매트릭스 생성"""
    return {
        "scene_id": scene_id,
        "narration_text": narration,
        "core_verb": core_verb,
        "emotional_temperature": temperature,
        "emotional_lighting": get_emotional_lighting(temperature),
        "gaze_focus": gaze,
        "peak_frame": peak_frame,
        "ken_burns": get_ken_burns_direction(narrative_context),
        "silence_sec": NARRATION_RULES["silence_tail_sec"],
        "camera": camera,
        "lighting": get_emotional_lighting(temperature),
        "color_temperature": color_temp,
    }
