# IMAGE ↔ NARRATION 정합성 스킬 가이드
# Murim AI Content Factory — v1.0 (2026-03-01)
# 기존 스킬파일 위에 올라가는 "동기화 레이어"

---

## 제1장 — 핵심 원칙: 이미지는 나레이션의 "정지된 순간"이다

이미지와 나레이션이 따로 놀면 시청자는 3초 안에 이탈한다.
이미지는 나레이션이 묘사하는 장면의 **가장 극적인 1프레임**이어야 한다.

### 법칙 1: 동사 일치 (Verb Lock)
나레이션에 등장하는 **핵심 동사**가 이미지에 반드시 시각화되어야 한다.

| 나레이션 | 핵심 동사 | 이미지에 반드시 포함 |
|---------|---------|-------------------|
| "소년이 만두를 한 입 베어 문다" | 베어 물다 | 입에 만두가 닿은 순간 |
| "검끝이 목에 닿는다" | 닿다 | 금속이 피부를 누르는 접점 |
| "한 발 앞으로" | 걷다 | 한 발이 들린 자세 |

**규칙**: 프롬프트 작성 시, 나레이션의 핵심 동사를 추출 → 해당 동작의
정점(peak moment)을 이미지 프롬프트의 ACTION 슬롯에 삽입.

### 법칙 2: 감정 온도 일치 (Emotional Temperature Lock)
나레이션과 이미지의 감정 온도가 같아야 한다.

| 감정 온도 | 나레이션 톤 | 이미지 조명/색감 |
|----------|-----------|----------------|
| 냉(冷) | 건조, 짧은 문장, 사실 전달 | 차가운 블루/그레이, 하드 라이팅 |
| 온(溫) | 서정적, 감각 묘사 | 골든아워, 소프트 라이팅 |
| 열(熱) | 빠른 리듬, 단문 연속 | 하이콘트라스트, 림라이트, 먼지 |
| 정(靜) | 침묵, 최소 단어 | 로우키, 단색, 정적 구도 |

### 법칙 3: 시선 유도 일치 (Gaze Direction Lock)
나레이션이 주목하는 대상 = 이미지에서 시각적 초점(focal point).

나레이션: "약병이 깨진다" → 이미지 초점: 깨진 약병 (얕은 심도,
배경 인물은 흐리게).

나레이션: "소년의 눈이 달라졌다" → 이미지 초점: 눈 극단 클로즈업.

### 법칙 4: 시간 동기화 (Temporal Sync)
Ken Burns 효과의 방향이 나레이션의 시간 흐름과 일치해야 한다.

| 나레이션 내용 | Ken Burns 방향 |
|-------------|--------------|
| 과거 회상 | Zoom Out (멀어짐 = 기억에서 빠져나옴) |
| 현재 긴장 고조 | Zoom In (다가감 = 압박감) |
| 환경 소개 | Pan Left/Right (시선 이동 = 탐색) |
| 감정 클라이맥스 | Slow Zoom In (천천히, 감정 잠김) |
| 결말/여운 | 정지 또는 Very Slow Zoom Out |

### 법칙 5: 공백의 법칙 (Silence = Image Breathes)
나레이션이 멈추는 구간에서 이미지가 가장 강하게 작동한다.
모든 장면의 마지막 2~3초는 나레이션 없이 이미지만 보여준다.
이 침묵이 여운을 만든다.

---

## 제2장 — 장면별 동기화 매트릭스 작성법

모든 장면을 아래 형식으로 정의한 후 이미지/나레이션을 생성한다.
장면 ID: S05 나레이션 텍스트: "만두를 파는 할머니가 종이에 싼 만두 하나를 내민다. 말없이. 소년은 받지 않는다." 핵심 동사: 내민다 / 받지 않는다 감정 온도: 온(溫) → 정(靜) 전환 시선 초점: 할머니의 손 → 소년의 멈춘 손 정점 프레임: 만두가 소년의 손 위 5cm에 있는 순간 (닿기 직전) Ken Burns: Slow Zoom In (온기로 다가감) 침묵 구간: 마지막 3초 카메라: Medium two-shot, eye level 조명: 따뜻한 아침 측광, 만두에서 피어오르는 김에 후광 색온도: 따뜻한 골드 (3200K 느낌)


---

## 제3장 — 나레이션 작성 규칙

### 3.1 무협 내레이터의 목소리
- **문체**: 3인칭 전지적, 그러나 감정은 절제. 보고서도 시도 아닌 중간.
- **문장 길이**: 7~15자 / 문장. 20자 초과 금지.
- **리듬**: 짧-짧-길 패턴 반복. 세 번째 문장이 감정을 담는다.
  예: "검이 떨어진다. (짧) 한 번이었다. (짧) 진지하게 싸운 것이
  아니다, 한 번 쳐보고 수준을 확인한 것이다. (길)"
- **금지어**: 감탄사(아!, 오!), 설명적 형용사 남용(매우, 정말,
  엄청나게), 독자 직접 호명("여러분")
- **허용**: 비유 1개/장면, 반복 모티프, 의도적 비문(단어만 던지기)

### 3.2 나레이션-이미지 타이밍 설계
- TTS 속도: -10% (느리게) → 한국어 기준 약 3.5자/초
- 장면당 나레이션 길이 = (장면 시간 - 침묵 3초) × 3.5자
- 예: 12초 장면 → 나레이션 시간 9초 → 약 31자 이내

### 3.3 모티프 반복 규칙
- "밥 챙겨 먹어라" → 에피소드 내 최소 3회 변주
- 매 변주마다 톤이 변해야 한다: 무심 → 의미부여 → 감정 폭발
- 마지막 변주는 반드시 **무성(독자만 아는 독백)**

---

## 제4장 — 프롬프트 보강 규칙 (PROMPT_SKILL_GUIDE 확장)

### 4.1 ACTION 슬롯 강제
기존: [Style] + [Subject] + [Appearance] + [Costume] + [Environment] + [Camera]
보강: [Style] + [Subject] + **[Peak Action from Narration]** + [Appearance]
      + [Costume] + [Environment] + **[Emotional Lighting]** + [Camera]

### 4.2 장면 설명에서 나레이션 핵심 동사를 영어로 번역하여 삽입
나레이션: "검끝이 목에 닿는다"
→ 프롬프트에 추가: "gleaming steel sword blade pressing against
the boy's throat, metal dimpling skin"

### 4.3 조명 키워드를 감정 온도에서 자동 매핑
감정 온도 "냉" → "cold blue-grey palette, hard directional lighting,
high contrast"
감정 온도 "온" → "warm golden hour, soft diffused light, gentle
bokeh"

---

## 제5장 — 모델 비교 시스템

### 5.1 비교 대상 모델 (모두 SDXL 기반, Lightning 호환, 8GB VRAM OK)

| 코드 | 모델명 | 특성 | 파일 | 속도 방식 |
|-----|-------|-----|-----|---------|
| M1 | sd_xl_base_1.0 | 기본, 범용 | (이미 보유) | Lightning LoRA |
| M2 | JuggernautXL v9 | 사실적 피부/인물 최강 | 7.1GB | Lightning LoRA |
| M3 | RealVisXL V5.0 Lightning | 사실적 + Lightning 내장 | 6.5GB | 내장 (LoRA 불필요) |
| M4 | DreamShaperXL Turbo v2 | 예술적/환상적 + Turbo 내장 | 6.9GB | 내장 (LoRA 불필요) |

### 5.2 비교 테스트 프로토콜
- 동일 프롬프트(S07, S14)를 4개 모델로 생성
- 평가 기준: 인물 정확도, 의상 정확도, 분위기, 나레이션 정합성
- 최종 선택 후 14장 전체 재생성 (2분)

### 5.3 모델별 설정

**M1 (SDXL Base + Lightning LoRA)** — 현재 상태
- checkpoint: sd_xl_base_1.0.safetensors
- lora: sdxl_lightning_4step_lora.safetensors (strength 1.0)
- steps: 4, cfg: 1.0, sampler: euler, scheduler: sgm_uniform

**M2 (JuggernautXL v9 + Lightning LoRA)**
- checkpoint: Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors
- lora: sdxl_lightning_4step_lora.safetensors (strength 1.0)
- steps: 4, cfg: 1.0, sampler: euler, scheduler: sgm_uniform

**M3 (RealVisXL V5.0 Lightning)** — Lightning 내장
- checkpoint: RealVisXL_V5.0_Lightning.safetensors
- lora: 없음
- steps: 4, cfg: 1.5, sampler: euler, scheduler: sgm_uniform

**M4 (DreamShaperXL Turbo v2)** — Turbo 내장
- checkpoint: DreamShaperXL_Turbo_v2.safetensors
- lora: 없음
- steps: 4, cfg: 2.0, sampler: dpmpp_sde, scheduler: karras

---

## 제6장 — 통합 워크플로우

1. 나레이션 먼저 확정 (STORY_SKILL → TRANSCENDENT_NARRATOR)
2. 장면별 동기화 매트릭스 작성 (본 파일 제2장)
3. 매트릭스에서 이미지 프롬프트 자동 생성 (PROMPT_SKILL + 본 파일 제4장)
4. 모델 비교 테스트 (본 파일 제5장)
5. 최적 모델로 14장 일괄 생성
6. Ken Burns 방향 = 매트릭스의 감정 온도에서 자동 결정
7. TTS + FFmpeg 렌더링
8. 최종 검수: 나레이션 핵심 동사 ↔ 이미지 정점 프레임 일치 확인

---

## 부록 — 체크리스트

□ 핵심 동사가 이미지에 시각화되었는가?
□ 감정 온도와 조명/색감이 일치하는가?
□ 시선 초점 = 나레이션 주목 대상인가?
□ Ken Burns 방향이 나레이션 시간 흐름과 맞는가?
□ 마지막 2~3초 침묵 구간이 있는가?
□ 나레이션 길이 ≤ (장면시간-3초) × 3.5자인가?
□ 모티프가 올바른 변주 단계인가?
□ 프롬프트에 Peak Action이 영어로 삽입되었는가?