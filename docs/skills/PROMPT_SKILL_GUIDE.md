# 무림 AI 콘텐츠 팩토리 — 이미지 프롬프트 스킬 가이드
# PROMPT_SKILL_GUIDE.md
# 최종 업데이트: 2026-03-01

---

## 1. 프롬프트 기본 공식

모든 이미지 프롬프트는 아래 7단계 구조를 따릅니다.
순서가 중요합니다 — AI는 앞에 나온 단어에 더 높은 가중치를 부여합니다.

[스타일 프리픽스] + [주체] + [행동/포즈] + [외모 상세] + [의상 상세] + [환경/배경] + [촬영 기법]


### 각 단계 설명

| 순서 | 항목 | 설명 | 예시 |
|------|------|------|------|
| 1 | 스타일 프리픽스 | 전체 화풍/매체 결정 | `Realistic digital painting, wuxia martial arts style` |
| 2 | 주체(Subject) | 누구인지, 나이, 성별 | `A 16-year-old East Asian boy named Lee Cheon-myeong` |
| 3 | 행동/포즈(Action) | 뭘 하고 있는지 | `walks slowly forward on a mountain path` |
| 4 | 외모 상세(Appearance) | 얼굴, 머리, 체격, 특징 | `sharp cold black eyes, long black hair tied with leather cord, thin scar on left cheekbone` |
| 5 | 의상 상세(Costume) | 옷, 무기, 소품 | `tattered black martial arts robe with dark crimson inner lining, worn straw sandals` |
| 6 | 환경/배경(Environment) | 장소, 시간, 날씨 | `misty mountain path at dawn, ancient pine trees, volumetric fog` |
| 7 | 촬영 기법(Camera) | 구도, 렌즈, 조명 | `cinematic wide shot, golden hour lighting, 50mm lens, shallow depth of field` |


---

## 2. 캐릭터 일관성 시스템 (Character Consistency)

### 2-1. 캐릭터 ID 카드

각 캐릭터마다 **절대 변하지 않는 고정 설명문(Identity Anchor)**을 만들어 모든 장면에 동일하게 삽입합니다.

캐릭터 ID: 이천명 (Lee Cheon-myeong)
코드명: HERO_LCM
나이: 16세 (에피소드 1 기준)
인종: East Asian (Korean)
얼굴: Sharp, angular face with high cheekbones, cold piercing black eyes with slight upward tilt, thick straight eyebrows, thin lips usually pressed together
머리: Long straight black hair reaching mid-back, loosely tied at the nape with a worn dark leather cord, two loose strands framing his face
체격: Lean but densely muscular, 173cm, broad shoulders relative to narrow waist
특징: Thin pale scar across left cheekbone (3cm), calloused hands
기본 표정: Stoic, emotionless, with an underlying intensity

### 2-2. 의상 시트 (Costume Sheet)

의상도 장면별로 변할 수 있으므로 **의상 코드**를 분리합니다.

의상 코드: COSTUME_A (하산복)
상의: Tattered black martial arts robe (도복), coarse hemp fabric, dark crimson inner lining visible at torn edges and collar
하의: Loose black pants of same fabric, frayed at the ankles
신발: Worn straw sandals (짚신) with bare toes visible
악세서리: None
무기: None (맨손)
상태: Heavily worn, multiple tears and patches, faded from years of training
의상 코드: COSTUME_B (전투복)
상의: Dark crimson and black layered robe, reinforced with leather chest piece
하의: Black combat pants with leather shin guards
신발: Black leather boots
악세서리: Dark metal wrist guards
무기: None visible (내공 위주)
상태: Clean but battle-scarred

### 2-3. 조합 방법

장면 프롬프트를 작성할 때 아래와 같이 조합합니다:

[스타일] + [HERO_LCM 전체 텍스트] + [COSTUME_A 전체 텍스트] + [행동] + [환경] + [촬영]


**핵심 규칙: 동의어 금지**
- ❌ "black robe" → "dark clothes" → "dark outfit" (매번 다른 표현)
- ✅ "tattered black martial arts robe with dark crimson inner lining" (매번 동일)


---

## 3. 일관된 시대상/세계관 (World Consistency)

### 3-1. 세계관 앵커 (World Anchor)

모든 장면에 삽입하는 시대/분위기 고정 문구:

세계관 코드: WORLD_MURIM
시대: Ancient East Asian period, similar to Joseon/Ming dynasty era
기술수준: No modern technology, no electricity, no glass windows
건축: Traditional wooden architecture with tiled or thatched roofs, paper doors (한지), stone foundations
이동수단: On foot, horseback, ox carts
조명: Candles, oil lamps, torches, natural sunlight/moonlight only
무기: Swords (검/도), spears (창), hidden weapons (암기), bare fists
의복: Traditional martial arts robes (도복), hanbok-influenced, natural fabrics only (hemp, silk, cotton)
색감: Muted, desaturated earth tones — black, dark crimson, grey, brown, forest green, faded white
금지요소: NO modern items, NO plastic, NO metal buttons, NO zippers, NO glasses, NO watches

### 3-2. 장소별 환경 프리셋

자주 등장하는 장소를 미리 정의합니다:

장소 코드: LOC_MANMADONG (만마동)
Vast underground cave, hundreds of red candles, ancient Chinese characters carved on walls
Stalactites, dripping water, oppressive atmosphere
Lighting: Warm candlelight only, deep shadows, volumetric fog
Color: Orange-red candle glow against pitch black darkness
장소 코드: LOC_MOUNTAIN_PATH (산길)
Narrow winding stone steps on steep mountainside
Ancient pine trees, morning mist, distant green peaks
Lighting: Dawn/golden hour, god rays through mist
Color: Cool blue-green with warm golden accents
장소 코드: LOC_VILLAGE (마을)
Small rural village, thatched/tiled roofs, single dirt road
Market with fabric canopies, ox carts, chickens
Lighting: Warm midday sunlight
Color: Warm earth tones, golden sunlight
장소 코드: LOC_VILLAGE_SQUARE (마을 광장)
Open dirt square in village center, surrounded by wooden buildings
Stone well in corner, wooden market stalls
Lighting: Harsh midday sun creating strong shadows
Color: Dusty warm tones with high contrast shadows


---

## 4. 시간 경과와 조명 시스템 (Time & Lighting)

장면의 시간대가 바뀌면 조명도 자동으로 따라가야 합니다:

| 시간대 | 영문 키워드 | 조명 특성 | 색온도 |
|--------|-------------|-----------|--------|
| 새벽 (04-06시) | `pre-dawn, first light` | 차가운 파란빛, 희미한 수평선 | Cool blue, 4000K |
| 일출 (06-07시) | `dawn, golden hour, sunrise` | 강한 측면광, 신의 빛줄기 | Warm gold, 3500K |
| 오전 (08-11시) | `morning, soft daylight` | 부드러운 자연광, 그림자 중간 | Neutral warm, 5500K |
| 정오 (11-13시) | `midday, harsh overhead sun` | 강한 하향광, 짧은 그림자 | Bright white, 6500K |
| 오후 (14-17시) | `afternoon, warm sunlight` | 따뜻한 측면광, 긴 그림자 | Warm, 5000K |
| 석양 (17-19시) | `golden hour, sunset, dusk` | 극적 오렌지/붉은 빛, 긴 그림자 | Deep warm, 3000K |
| 밤 (20-04시) | `night, moonlight, darkness` | 차가운 청백색 달빛 또는 횃불빛 | Cool blue 4500K or warm fire 2500K |

### 시간 경과 프롬프트 예시

에피소드 내에서 시간이 흐르는 것을 표현할 때:

S01 (새벽): "...pre-dawn blue light inside the cave, single candle flame..." S02 (일출): "...first golden rays of sunrise breaking through mountain peaks, god rays..."
S03 (오전): "...soft morning light filtering through mist, cool blue-green atmosphere..." S04 (정오): "...bright midday sunlight bathes the village, warm golden tones..." S05 (오후): "...afternoon sun casting long shadows across the dirt road..." S06 (석양): "...golden hour backlighting, dramatic orange silhouette..."



---

## 5. 인물 연령 변화 시스템 (Age Progression)

장기 시리즈에서 주인공이 성장하는 것을 표현할 때:

HERO_LCM 연령별 외모 변화
13세 (수련기 회상)
Build: Thin, bony, underdeveloped, 155cm
Face: Rounder, still childlike, eyes look too large for face
Hair: Shorter, messy, unkempt, reaching shoulders
Scar: Fresh, slightly reddish
Expression: Mix of fear and determination
추가 키워드: "young teenage boy, adolescent, thin frame, boyish face"
16세 (에피소드 1 기준 - 현재)
Build: Lean but densely muscular, 173cm, broad shoulders
Face: Angular, sharp jawline emerged, high cheekbones prominent
Hair: Long, mid-back length, tied loosely
Scar: Faded to pale white
Expression: Stoic, cold, controlled
추가 키워드: "teenage boy, lean muscular build, sharp angular face"
20세 (미래 에피소드)
Build: Fully muscular, 180cm, powerful presence
Face: Mature, harder edges, slight stubble possible
Hair: Longer, more deliberately styled, tighter tie
Scar: Almost invisible, only visible in close-up
Expression: Commanding, piercing, intimidating
추가 키워드: "young man, athletic muscular build, commanding presence, mature face"
30세 (절정기)
Build: Peak physical condition, 182cm, imposing stature
Face: Fully mature, deepened features, slight lines around eyes
Hair: Long, jet black with single streak of white at temple
Scar: Blended into skin, character mark
Expression: Absolute calm, terrifying stillness
추가 키워드: "adult man in prime, imposing powerful build, weathered handsome face"


---

## 6. 촬영 기법 사전 (Camera & Composition Dictionary)

### 6-1. 샷 사이즈 (Shot Size)

| 한글 | 영문 키워드 | 용도 |
|------|-------------|------|
| 익스트림 클로즈업 | `extreme close-up, ECU` | 눈, 손, 상처 등 디테일 강조 |
| 클로즈업 | `close-up, face portrait` | 감정 표현, 내면 갈등 |
| 미디엄 클로즈업 | `medium close-up, bust shot` | 상반신, 대화 장면 |
| 미디엄 샷 | `medium shot, waist-up` | 인물+환경 균형 |
| 풀 샷 | `full body shot, full-length` | 전신, 의상, 포즈 전체 |
| 와이드 샷 | `wide shot, establishing shot` | 환경 소개, 공간감 |
| 익스트림 와이드 | `extreme wide shot, aerial view` | 풍경, 스케일감, 고독함 |

### 6-2. 카메라 앵글 (Camera Angle)

| 한글 | 영문 키워드 | 효과 |
|------|-------------|------|
| 로우 앵글 | `low angle, looking up` | 위압감, 권위, 영웅적 |
| 아이 레벨 | `eye level, neutral angle` | 자연스러움, 관객 시점 |
| 하이 앵글 | `high angle, looking down` | 나약함, 위기, 관조 |
| 버드아이 | `bird's eye view, top-down` | 전체 상황 파악 |
| 더치 앵글 | `dutch angle, tilted` | 불안감, 긴장 |
| 오버 더 숄더 | `over-the-shoulder, OTS` | 대화, 대치 상황 |

### 6-3. 조명 패턴 (Lighting Patterns)

| 한글 | 영문 키워드 | 효과 |
|------|-------------|------|
| 렘브란트 조명 | `Rembrandt lighting` | 극적 초상화, 한쪽 눈 아래 삼각형 빛 |
| 스플릿 조명 | `split lighting, half shadow` | 내면 갈등, 선악 이중성 |
| 림 라이트 | `rim light, backlit silhouette` | 신비감, 영웅 등장 |
| 실루엣 | `silhouette, strong backlight` | 정체 은닉, 극적 등장 |
| 체리아로스쿠로 | `chiaroscuro, dramatic contrast` | 강한 명암, 르네상스 느낌 |
| 볼류메트릭 | `volumetric lighting, god rays` | 안개 속 빛줄기, 신성함 |
| 캔들라이트 | `candlelight, warm single source` | 밀실, 동굴, 친밀한 대화 |


---

## 7. 프롬프트 조합 실전 예시

### 예시: S03 — 첫 하산, 산길을 걷다

**조합 과정:**

스타일: "Realistic digital painting, wuxia martial arts style, 16:9, 4K" 주체: [HERO_LCM 16세 전문]
의상: [COSTUME_A 전문] 행동: "walks alone down a narrow winding mountain stone path, seen from behind" 환경: [LOC_MOUNTAIN_PATH 전문] 시간: "dawn, golden hour, first rays of sunlight" 촬영: "extreme wide shot, aerial perspective, cinematic composition" 세계관: [WORLD_MURIM — 자동 적용: no modern items]


**최종 프롬프트:**

Realistic digital painting, wuxia martial arts style, 16:9 aspect ratio, 4K quality. A 16-year-old East Asian boy with a sharp angular face, cold piercing black eyes, long straight black hair reaching mid-back tied loosely with a worn dark leather cord, two loose strands framing his face, thin pale scar across left cheekbone, lean but densely muscular build. He wears a tattered black martial arts robe of coarse hemp fabric with dark crimson inner lining visible at torn edges, loose black pants frayed at the ankles, worn straw sandals. He walks alone down a narrow winding mountain stone path, seen from behind, descending through layers of misty clouds. Ancient pine trees cling to steep cliff faces on both sides, the path made of rough-cut stone steps weathered by centuries. Morning d

계속
Copyew glistens on leaves. A vast landscape of green mountains stretches endlessly into
the foggy distance below. Dawn golden hour, first rays of golden sunlight breaking
through distant peaks, god rays through mist. Extreme wide shot, aerial perspective,
cinematic composition, cool blue-green tones with warm golden accents.
8. 네거티브 프롬프트 표준 (Negative Prompt Standard)
모든 이미지에 공통으로 적용하는 금지 키워드:

8-1. 범용 네거티브
ugly, deformed, disfigured, blurry, low quality, low resolution, watermark,
text, logo, signature, cropped, out of frame, worst quality, jpeg artifacts,
duplicate, morbid, mutilated, extra fingers, extra limbs, fused fingers,
too many fingers, long neck, poorly drawn hands, poorly drawn face
8-2. 무협 전용 네거티브 (시대 오류 방지)
modern clothing, t-shirt, jeans, sneakers, glasses, sunglasses, watch,
wristwatch, plastic, zipper, buttons, neon lights, electricity, power lines,
cars, roads, asphalt, concrete buildings, skyscrapers, phone, laptop,
western medieval armor, plate armor, chainmail, European castle
8-3. 인물 일관성 네거티브
different person, changed face, wrong ethnicity, western features,
blonde hair, blue eyes, red hair, curly hair, beard (16세 기준),
old man (16세 기준), child (16세 기준), female
8-4. 장면별 추가 네거티브 예시
# 동굴 장면: 실외 요소 배제
outdoor, sunlight, sky, clouds, trees, grass

# 실외 장면: 실내 요소 배제  
indoor, ceiling, floor tiles, furniture, walls

# 낮 장면: 밤 요소 배제
night, moon, stars, darkness, torchlight

# 밤 장면: 낮 요소 배제
bright sunlight, blue sky, daylight
9. 소품/사물 일관성 사전 (Props Dictionary)
반복 등장하는 소품은 고정 설명을 만들어 둡니다:

## PROP_MASTER_STAFF (스승의 지팡이)
- Gnarled dark wooden staff, 170cm tall, twisted natural wood grain
- Top is carved into a coiled serpent head
- Surface is polished smooth from decades of use
- Dark brown almost black color

## PROP_CANDLES_RED (만마동 붉은 촛불)
- Hundreds of thick red wax candles, varying heights (10-40cm)
- Arranged in concentric circles on stone floor
- Melted wax pooling at bases, flickering warm orange flames
- Some candles extinguished with smoke trails

## PROP_SWORD_CRANE (학파 직검)
- Straight double-edged Chinese sword (직검/jian), 90cm blade
- Silver-white blade with faint blue sheen
- White wrapped hilt with crane-shaped pommel
- Light blue tassel hanging from guard

## PROP_MERCHANT_CART (약재상 수레)
- Wooden two-wheeled hand cart, weathered oak
- Loaded with dried herbs in cloth bundles, medicine bottles
- Faded red cloth canopy for shade
- One wheel slightly wobbly
10. 감정 표현 사전 (Emotion Dictionary)
캐릭터의 감정을 정확히 전달하는 키워드:

감정	영문 키워드	신체 언어 추가
냉정/무표정	stoic, expressionless, cold gaze	jaw clenched, arms at sides, rigid posture
내면의 분노	suppressed rage, burning eyes, controlled fury	fists clenched, veins visible on forearms, slight trembling
살기	killing intent, murderous aura, ice-cold eyes	dark energy distortion around body, predatory stance
경멸	contempt, looking down, disdainful	chin slightly raised, eyes half-lidded, one eyebrow raised
각성/결의	determination, resolved, awakened	eyes wide and focused, stepping forward, wind stirring robes
고독/쓸쓸함	loneliness, solitude, melancholy	shoulders slightly dropped, looking at distant horizon, isolated figure
경계/긴장	alert, vigilant, tense	weight on balls of feet, eyes scanning, one hand slightly raised
위압감	overwhelming presence, oppressive aura, dominating	standing tall, dark energy radiating, others shrinking back
고통	pain, suffering, enduring	gritted teeth, sweat on brow, one knee partially bent
평온/초월	serene, transcendent, inner peace	eyes closed, slight smile, perfect stillness, wind gently moving hair
11. 다중 인물 장면 가이드 (Multi-Character Scenes)
2명 이상 등장할 때는 위치 지정이 필수입니다:

11-1. 위치 키워드
# 2인 장면
"[Character A] on the left side, [Character B] on the right side"
"[Character A] in the foreground, [Character B] in the background"
"[Character A] facing [Character B]"

# 3인 이상
"[Character A] in the center, [Character B] on the left, [Character C] on the right"
"[Characters B and C] standing behind [Character A]"
11-2. 인물 구분 강화
각 인물의 가장 눈에 띄는 차별점을 반드시 명시:

❌ "Three men in robes stand in the square"
✅ "Three martial artists: the LEADER in white robes with blue crane sash and straight sword,
    the LARGE man in grey robes with a broadsword on his back,
    the THIN man in green robes holding a folding fan"
11-3. 크기/원근 관계
# 주인공 강조
"[Hero] in sharp focus in the foreground, [enemies] slightly blurred in the background"

# 대치 구도
"[Hero] on the left facing right, [Villain] on the right facing left, 
 tension between them, 3 meters apart"
12. 도구별 프롬프트 최적화 팁
12-1. ChatGPT (DALL-E 3) / GPT Image
자연어 문장형 프롬프트 선호
네거티브 프롬프트 지원 안 함 → 원하지 않는 것은 "without ~" 또는 "no ~"로 표현
캐릭터 일관성: 같은 대화 내에서 이전 이미지를 참조 가능
최대 강점: 복잡한 지시 이해력
12-2. Midjourney
--cref [이미지URL] 로 캐릭터 참조 (가장 강력한 일관성)
--cw 100 얼굴+의상 모두 유지, --cw 0 얼굴만 유지
--sref [이미지URL] 스타일 참조
--ar 16:9 화면비 지정
쉼표로 구분된 키워드 나열형 선호
12-3. Flux (fal.ai / ComfyUI)
상세한 자연어 설명 선호
LoRA 학습으로 캐릭터 고정 가능 (15-30장 학습)
ControlNet(Pose/LineArt) 활용 시 포즈 고정
GGUF 양자화 모델은 품질 저하 주의
12-4. Stable Diffusion XL
쉼표 구분 태그형 + 가중치 (keyword:1.3) 지원
네거티브 프롬프트 별도 입력 지원
LoRA + ControlNet 조합이 최강
시드(seed) 고정으로 변형 최소화
12-5. Wan 2.2 (I2V 프롬프트)
이미지가 이미 주체/환경/스타일을 확립하므로 동작과 카메라만 기술
공식: Motion Description + Camera Movement
예시: "The boy walks slowly forward, his robes swaying in the wind. Slow cinematic tracking shot, dolly in."
"static shot" 또는 "fixed camera" 명시하면 카메라 고정
13. 자주 하는 실수와 해결법
실수	증상	해결법
동의어 사용	인물 외모가 매번 달라짐	고정 ID 텍스트 복사-붙여넣기
시대 혼용	현대 물건이 등장	WORLD_MURIM 네거티브 항상 적용
조명 미지정	분위기가 들쑥날쑥	시간대별 조명 키워드 필수
얼굴 미상세	다른 사람으로 바뀜	눈색/눈모양/눈썹/코/입 각각 기술
포즈 미지정	어색한 자세	행동+자세+손위치 명시
배경 미지정	엉뚱한 장소 생성	LOC_ 코드 전문 삽입
인종 미지정	서양인으로 생성됨	"East Asian" 반드시 명시
화면비 미지정	정사각형으로 나옴	"16:9 aspect ratio" 또는 도구 파라미터 설정
프롬프트 과다	AI가 혼란, 품질 저하	핵심 200단어 이내, 중요도순 배치
복수 인물 미구분	인물이 합쳐지거나 섞임	위치(left/right) + 외모 차별점 명시
14. 에피소드 제작 체크리스트
새 에피소드 이미지를 생성할 때 매번 확인:

□ 1. 캐릭터 ID 카드 확인 (HERO_LCM 등)
□ 2. 의상 코드 확인 (이번 에피소드에서 어떤 의상?)
□ 3. 세계관 앵커 적용 (WORLD_MURIM)
□ 4. 장면별 시간대 → 조명 매핑 완료
□ 5. 장소 코드 적용 (LOC_xxx)
□ 6. 네거티브 프롬프트 적용 (범용 + 무협 전용)
□ 7. 촬영 기법 결정 (샷 사이즈 + 앵글 + 조명 패턴)
□ 8. 다중 인물 시 위치/구분 명시
□ 9. 소품 등장 시 PROP_ 코드 적용
□ 10. 감정 키워드 + 신체 언어 추가
□ 11. 화면비 16:9 확인
□ 12. 최종 프롬프트 200단어 이내 확인
15. 퀵 레퍼런스: 한 줄 프롬프트 공식
급할 때 이것만 기억하세요:

"[Style], [Who] [Doing what], [Wearing what], [Where], [When/Light], [Camera shot]"
예시:

"Realistic wuxia painting, a 16-year-old East Asian boy with long black hair and tattered black robe walks down misty mountain steps at dawn, golden hour god rays, extreme wide shot from behind"
부록: 자주 쓰는 무협 키워드 모음
분위기
dark wuxia atmosphere, martial arts drama, ancient Chinese/Korean aesthetic,
ink wash painting influence, jianghu (강호) world, historical fantasy
무공 표현
inner energy (내공/qi) visible as dark smoke/aura, shockwave from palm strike,
sword energy (검기) as glowing slash, pressure wave cracking ground,
afterimage from speed, floating/levitating with qi
자연 표현
misty mountains (운무), bamboo forest, cherry blossoms falling,
waterfall cliff, ancient temple ruins, moonlit lake reflection,
snow-covered pine trees, autumn red maple forest
건축물
traditional wooden martial arts training hall (무관/도장),
mountain temple with stone steps, wine house/tavern (주루) with
red lanterns, underground secret chamber, cliff-side cave dwelling

---

저장 후 확인:

```bash
