"""
src/core/skill_prompt.py
PROMPT_SKILL_GUIDE.md의 코드화
하위 레이어: "어떻게 보여주는가" — 시각의 일관성
"""

# ── 7단계 프롬프트 공식 ──
PROMPT_FORMULA = [
    "스타일 프리픽스 (Style Prefix)",
    "주체 (Subject)",
    "행동/포즈 — Peak Action from Narration",
    "외모 상세 (Appearance)",
    "의상 상세 (Costume)",
    "환경/배경 + 감정 조명 (Emotional Lighting)",
    "촬영 기법 (Camera)",
]

# ── 캐릭터 ID 앵커 ──
HERO_LCM = {
    "name": "이천명 (Lee Cheon-myeong)",
    "code": "HERO_LCM",
    "age_default": 16,
    "face": (
        "Sharp angular face with high cheekbones, cold piercing black eyes "
        "with slight upward tilt, thick straight eyebrows, thin lips usually pressed together"
    ),
    "hair": (
        "Long straight black hair reaching mid-back, loosely tied at the nape "
        "with a worn dark leather cord, two loose strands framing his face"
    ),
    "build": "Lean but densely muscular, 173cm, broad shoulders relative to narrow waist",
    "marks": "Thin pale scar across left cheekbone (3cm), calloused hands",
    "expression": "Stoic, emotionless, with an underlying intensity",
}

# ── 연령별 외모 변화 ──
HERO_AGE_VARIANTS = {
    13: {
        "build": "Thin, bony, underdeveloped, 155cm",
        "face": "Rounder, still childlike, eyes look too large for face",
        "hair": "Shorter, messy, unkempt, reaching shoulders",
        "scar": "Fresh, slightly reddish",
        "extra": "young teenage boy, adolescent, thin frame, boyish face",
    },
    16: {
        "build": HERO_LCM["build"],
        "face": "Angular, sharp jawline emerged, high cheekbones prominent",
        "hair": "Long, mid-back length, tied loosely",
        "scar": "Faded to pale white",
        "extra": "teenage boy, lean muscular build, sharp angular face",
    },
    20: {
        "build": "Fully muscular, 180cm, powerful presence",
        "face": "Mature, harder edges, slight stubble possible",
        "hair": "Longer, more deliberately styled, tighter tie",
        "scar": "Almost invisible, only visible in close-up",
        "extra": "young man, athletic muscular build, commanding presence, mature face",
    },
    30: {
        "build": "Peak physical condition, 182cm, imposing stature",
        "face": "Fully mature, deepened features, slight lines around eyes",
        "hair": "Long, jet black with single streak of white at temple",
        "scar": "Blended into skin, character mark",
        "extra": "adult man in prime, imposing powerful build, weathered handsome face",
    },
}

# ── 의상 시트 ──
COSTUMES = {
    "A": {
        "code": "COSTUME_A", "name": "하산복",
        "desc": (
            "Tattered black martial arts robe of coarse hemp fabric, "
            "dark crimson inner lining visible at torn edges and collar, "
            "loose black pants frayed at the ankles, worn straw sandals"
        ),
    },
    "B": {
        "code": "COSTUME_B", "name": "전투복",
        "desc": (
            "Dark crimson and black layered robe, reinforced with leather chest piece, "
            "black combat pants with leather shin guards, black leather boots, "
            "dark metal wrist guards"
        ),
    },
}

# ── 세계관 앵커 ──
WORLD_MURIM = (
    "Ancient East Asian period, similar to Joseon/Ming dynasty era. "
    "No modern technology, no electricity. Traditional wooden architecture, "
    "paper doors, stone foundations. Candles, oil lamps, torches, natural light only. "
    "Muted desaturated earth tones — black, dark crimson, grey, brown, forest green."
)

WORLD_NEGATIVE = (
    "modern clothing, t-shirt, jeans, sneakers, glasses, watch, plastic, zipper, "
    "neon lights, electricity, cars, roads, concrete buildings, phone, laptop, "
    "western medieval armor, plate armor, European castle"
)

# ── 네거티브 프롬프트 ──
NEGATIVE_UNIVERSAL = (
    "ugly, deformed, disfigured, blurry, low quality, low resolution, watermark, "
    "text, logo, signature, cropped, out of frame, worst quality, jpeg artifacts, "
    "duplicate, morbid, mutilated, extra fingers, extra limbs, fused fingers, "
    "too many fingers, long neck, poorly drawn hands, poorly drawn face"
)

NEGATIVE_CHARACTER = (
    "different person, changed face, wrong ethnicity, western features, "
    "blonde hair, blue eyes, red hair, curly hair, beard, old man, child, female"
)

# ── 장소 프리셋 ──
LOCATIONS = {
    "LOC_MANMADONG": {
        "name": "만마동",
        "desc": "Vast underground cave, hundreds of red candles, ancient Chinese characters carved on walls, "
                "stalactites, dripping water, oppressive atmosphere",
        "lighting": "Warm candlelight only, deep shadows, volumetric fog",
        "color": "Orange-red candle glow against pitch black darkness",
    },
    "LOC_MOUNTAIN_PATH": {
        "name": "산길",
        "desc": "Narrow winding stone steps on steep mountainside, ancient pine trees, morning mist, distant green peaks",
        "lighting": "Dawn/golden hour, god rays through mist",
        "color": "Cool blue-green with warm golden accents",
    },
    "LOC_VILLAGE": {
        "name": "마을",
        "desc": "Small rural village, thatched/tiled roofs, single dirt road, market with fabric canopies, ox carts",
        "lighting": "Warm midday sunlight",
        "color": "Warm earth tones, golden sunlight",
    },
    "LOC_VILLAGE_SQUARE": {
        "name": "마을 광장",
        "desc": "Open dirt square in village center, wooden buildings, stone well, wooden market stalls",
        "lighting": "Harsh midday sun creating strong shadows",
        "color": "Dusty warm tones with high contrast shadows",
    },
}

# ── 시간-조명 매핑 ──
TIME_LIGHTING = {
    "새벽(04-06)":  {"en": "pre-dawn, first light",           "color": "Cool blue, 4000K"},
    "일출(06-07)":  {"en": "dawn, golden hour, sunrise",      "color": "Warm gold, 3500K"},
    "오전(08-11)":  {"en": "morning, soft daylight",          "color": "Neutral warm, 5500K"},
    "정오(11-13)":  {"en": "midday, harsh overhead sun",      "color": "Bright white, 6500K"},
    "오후(14-17)":  {"en": "afternoon, warm sunlight",        "color": "Warm, 5000K"},
    "석양(17-19)":  {"en": "golden hour, sunset, dusk",       "color": "Deep warm, 3000K"},
    "밤(20-04)":    {"en": "night, moonlight, darkness",      "color": "Cool blue 4500K / warm fire 2500K"},
}

# ── 소품 사전 ──
PROPS = {
    "PROP_MASTER_STAFF": "Gnarled dark wooden staff, 170cm, coiled serpent head carving, polished smooth from decades",
    "PROP_CANDLES_RED": "Hundreds of thick red wax candles, varying heights, concentric circles on stone floor, flickering warm orange",
    "PROP_SWORD_CRANE": "Straight double-edged jian, 90cm silver-white blade with blue sheen, crane-shaped pommel, blue tassel",
    "PROP_MERCHANT_CART": "Wooden two-wheeled hand cart, dried herbs in cloth bundles, faded red cloth canopy, one wobbly wheel",
}

# ── 감정 표현 사전 ──
EMOTION_VISUALS = {
    "냉정":    {"en": "stoic, expressionless, cold gaze", "body": "jaw clenched, rigid posture"},
    "내면의 분노": {"en": "suppressed rage, burning eyes", "body": "fists clenched, veins visible, slight trembling"},
    "살기":    {"en": "killing intent, murderous aura", "body": "dark energy distortion, predatory stance"},
    "경멸":    {"en": "contempt, disdainful", "body": "chin raised, eyes half-lidded"},
    "각성":    {"en": "determination, resolved, awakened", "body": "eyes wide and focused, stepping forward"},
    "고독":    {"en": "loneliness, solitude, melancholy", "body": "shoulders dropped, looking at horizon"},
    "경계":    {"en": "alert, vigilant, tense", "body": "weight on balls of feet, eyes scanning"},
    "위압감":   {"en": "overwhelming presence, dominating", "body": "standing tall, dark energy radiating"},
    "고통":    {"en": "pain, suffering, enduring", "body": "gritted teeth, sweat on brow"},
    "초월":    {"en": "serene, transcendent, inner peace", "body": "eyes closed, slight smile, perfect stillness"},
}

# ── 촬영 기법 사전 ──
SHOT_SIZES = {
    "ECU":  "extreme close-up — 눈, 손, 상처 디테일",
    "CU":   "close-up, face portrait — 감정 표현",
    "MCU":  "medium close-up, bust shot — 상반신, 대화",
    "MS":   "medium shot, waist-up — 인물+환경 균형",
    "FS":   "full body shot — 전신, 의상, 포즈",
    "WS":   "wide shot, establishing — 환경 소개",
    "EWS":  "extreme wide shot, aerial — 풍경, 스케일, 고독",
}

CAMERA_ANGLES = {
    "low":   "low angle, looking up — 위압감, 영웅적",
    "eye":   "eye level, neutral — 자연스러움",
    "high":  "high angle, looking down — 나약함, 관조",
    "bird":  "bird's eye view, top-down — 전체 상황",
    "dutch": "dutch angle, tilted — 불안감, 긴장",
    "ots":   "over-the-shoulder — 대화, 대치",
}

LIGHTING_PATTERNS = {
    "rembrandt":    "Rembrandt lighting — 극적 초상화",
    "split":        "split lighting, half shadow — 내면 갈등",
    "rim":          "rim light, backlit silhouette — 신비감",
    "silhouette":   "silhouette, strong backlight — 정체 은닉",
    "chiaroscuro":  "chiaroscuro, dramatic contrast — 강한 명암",
    "volumetric":   "volumetric lighting, god rays — 안개 속 빛줄기",
    "candle":       "candlelight, warm single source — 밀실, 동굴",
}


def build_imaging_system_prompt() -> str:
    """Imaging 에이전트용 시스템 프롬프트"""
    formula = " → ".join(PROMPT_FORMULA)
    return (
        f"[프롬프트 7단계 공식] {formula}\n\n"
        f"[캐릭터 앵커 — HERO_LCM]\n"
        f"  얼굴: {HERO_LCM['face']}\n"
        f"  머리: {HERO_LCM['hair']}\n"
        f"  체격: {HERO_LCM['build']}\n"
        f"  특징: {HERO_LCM['marks']}\n"
        f"  표정: {HERO_LCM['expression']}\n\n"
        f"[의상 A] {COSTUMES['A']['desc']}\n"
        f"[의상 B] {COSTUMES['B']['desc']}\n\n"
        f"[세계관] {WORLD_MURIM}\n"
        f"[네거티브] {WORLD_NEGATIVE}\n"
        f"[인물 네거티브] {NEGATIVE_CHARACTER}\n\n"
        f"[핵심 규칙]\n"
        f"  1. 동의어 금지 — 매번 동일한 캐릭터 앵커 텍스트 사용\n"
        f"  2. Peak Action 슬롯에 나레이션 핵심 동사를 영어로 삽입\n"
        f"  3. 감정 온도 → 조명 키워드 자동 매핑\n"
        f"  4. 화면비 16:9, 최대 200단어"
    )


def build_full_prompt(
    action: str,
    location_code: str = "LOC_MOUNTAIN_PATH",
    costume_code: str = "A",
    time_key: str = "일출(06-07)",
    emotion_key: str = "냉정",
    shot: str = "WS",
    angle: str = "eye",
    lighting: str = "volumetric",
    age: int = 16,
) -> str:
    """장면 파라미터로 완성된 프롬프트 자동 생성"""
    style = "Realistic digital painting, wuxia martial arts style, 16:9, 4K"

    # 연령별 외모
    av = HERO_AGE_VARIANTS.get(age, HERO_AGE_VARIANTS[16])
    subject = (
        f"A {age}-year-old East Asian boy named Lee Cheon-myeong, "
        f"{HERO_LCM['face']}, {HERO_LCM['hair']}, {av['build']}, "
        f"{HERO_LCM['marks']}, {av.get('extra', '')}"
    )

    costume = COSTUMES.get(costume_code, COSTUMES["A"])["desc"]
    loc = LOCATIONS.get(location_code, LOCATIONS["LOC_MOUNTAIN_PATH"])
    env = f"{loc['desc']}, {loc['lighting']}, {loc['color']}"
    time_l = TIME_LIGHTING.get(time_key, TIME_LIGHTING["일출(06-07)"])
    emo = EMOTION_VISUALS.get(emotion_key, EMOTION_VISUALS["냉정"])
    cam = f"{SHOT_SIZES[shot]}, {CAMERA_ANGLES[angle]}, {LIGHTING_PATTERNS[lighting]}"

    return (
        f"{style}. {subject}. {action}, {emo['en']}, {emo['body']}. "
        f"Wearing {costume}. {env}, {time_l['en']}, {time_l['color']}. "
        f"{cam}."
    )
