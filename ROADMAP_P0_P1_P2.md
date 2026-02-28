# 무림 에셋 대시보드 구현 로드맵

## ✅ Phase 4 완료: 에셋 관리 대시보드 구현
- ✓ `src/pipeline/prompt_combiner.py` - 프롬프트 결합 및 도구별 포맷
- ✓ `templates/assets.html` - 에셋 관리 UI 대시보드
- ✓ `web_ui.py` - 7개 에셋 관리 API 엔드포인트
- ✓ `tests/test_prompt_combiner.py` - 자동 검증 테스트

---

## 📋 P0: 즉시 실행 (오늘)

### 목표
에셋 대시보드의 실제 동작과 프롬프트 생성 검증

### 단계

#### 1️⃣ 웹 서버 시작
```bash
cd e:\2026\murim
python web_ui.py
```
- 리스닝 주소: `http://localhost:8080`

#### 2️⃣ 에셋 대시보드 접근
```
http://localhost:8080/assets
```

#### 3️⃣ 에피소드 로드 & 프롬프트 확인
```
- 에피소드 선택: ep002_천마의_첫_하산__피로_물든_강호_첫걸음_20260228_114846
- 이미지 갤러리: S01~S06 이미지 표시 (이미 생성되어 있음)
- 비디오 프롬프트 탭 전환:
  - Kling AI (기본)
  - Runway Gen-3
  - Pika
  - Google Veo
  - Haiper
```

#### 4️⃣ S01 Kling 프롬프트 복사 & 실제 도구 테스트
```
장면: S01
도구: Kling AI
```

**생성되는 프롬프트 예시:**
```
{motion_prompt}. Style: cinematic wuxia, dark atmosphere, volumetric lighting. Duration: 6s.
```

(실제 motion_prompt는 outputs/ep002_천마의_첫_하산__피로_물든_강호_첫걸음_20260228_114846/prompts/video_prompts.json에서 로드)

#### 5️⃣ 결과 기록
- 품질 점수: ⭐⭐⭐⭐ (1-10 / 5 도구)
- 속도: 생성 시간 측정
- 비용: 무료 크레딧 사용량
- 테스트 결과표에 기록

---

## 📦 P1: 정리 & 테스트 (이번 주)

### 1️⃣ Outputs 중복 정리

**목표**: 불필요한 에피소드 및 임시 파일 정리

```
outputs/
├── ep002_천마의_첫_하산__피로_물든_강호_첫걸음_20260228_114846/ ✅ (유지)
├── critiques/                  (30+ 파일 - 분석 후 보관)
├── episodes/                   (진행 중 에피소드)
├── evolution/                  (에이전트 진화 로그)
└── sessions/                   (이전 세션 - 정리 대상)
```

**작업**:
- [ ] 테스트 에피소드 1개 유지, 나머지는 `archives/` 이동
- [ ] 상태별로 분류:
  - `완성`: main 디렉토리 유지
  - `진행중`: `episodes/` 폴더
  - `보관`: `archives/` 폴더

### 2️⃣ 테스트 코드 실행

```bash
# test_prompt_combiner.py 실행
pytest tests/test_prompt_combiner.py -v

# 검증 항목:
# - 6개 장면 모두 프롬프트 로드
# - 5개 도구 모두 포맷 테스트
# - 테스트 시트 생성 (30 tests = 6 scenes x 5 tools)
# - JSON 직렬화 검증
# - 성능 테스트 (로드 < 1초, 포맷 < 100ms)
```

### 3️⃣ 테스트 커버리지 확인

```bash
pytest tests/test_prompt_combiner.py --cov=src/pipeline/prompt_combiner --cov-report=html
```

**목표 커버리지**: > 85%

---

## 🎬 P2: 수동 테스트 & 도구 선택 (이번 주 후반)

### 목표
5개 무료 도구에서 S01 장면을 생성하고 품질/속도/비용 비교

### 테스트 매트릭스

| 도구 | URL | 최대 지속 | 포맷 | 무료 크레딧 | 예상 결과 |
|------|-----|---------|------|-----------|---------|
| **Kling AI** | https://klingai.com | 10초 | img→vid | 10/일 | 🎬 |
| **Runway Gen-3** | https://runwayml.com | 10초 | img→vid | 125초 | 🎬 |
| **Pika** | https://pika.art | 4초 | img→vid | 일일 | 🎬 |
| **Google Veo** | https://aistudio.google.com | 8초 | txt→vid | 무제한 | 🎬 |
| **Haiper** | https://haiper.ai | 6초 | img→vid | 일일 | 🎬 |

### 단계

#### 1️⃣ 이미지 업로드
```
S01 이미지 (이미 생성됨):
e:\2026\murim\outputs\ep002_천마의_첫_하산__피로_물든_강호_첫걸음_20260228_114846\images\S01_nanobanana.png
```

#### 2️⃣ 각 도구에서 프롬프트 입력 & 생성
- 대시보드의 "📋 복사" 버튼으로 프롬프트 복사
- 각 도구 웹사이트에서 생성 시작
- 예상 소요 시간: 도구당 5-10분 (처리 시간 포함)

#### 3️⃣ 결과 평가
**평가 항목 (각 5점)**:
- 품질 (해상도, 디테일, 일관성)
- 움직임 (자연스러움, 모션 퀄리티)
- 음향 효과 (적용 가능성)
- 렌더링 속도 (시간 효율)
- 비용 효율 (무료 크레딧 소진)

**평가 기준**: 
```
점수 입력: /5 점
결과: ⭐⭐⭐⭐⭐ (5단계)
```

#### 4️⃣ 결과 기록 & 분석

```
결과 저장 위치:
outputs/tool_comparison_results_20260228.json
```

**구조**:
```json
{
  "scene_id": "S01",
  "test_date": "2026-02-28",
  "results": [
    {
      "tool": "kling",
      "status": "✅ 완료",
      "generation_time": "45초",
      "quality_score": 4.5,
      "motion_score": 4.0,
      "cost_score": 5.0,
      "total": 13.5,
      "video_url": "https://klingai.com/...",
      "notes": "매우 부드러운 동작, 약간의 인물 흔들림"
    },
    // ... 나머지 4개 도구
  ],
  "recommendation": "Runway Gen-3 (최고 품질 + 충분한 크레딧)"
}
```

#### 5️⃣ 최적 도구 선택 & 결정
```
의사결정 트리:
1. 품질 > 85점 필터링
2. 남은 도구 중 무료 크레딧 최대값 선택
3. 동점 시 속도 기준
```

---

## 🎯 각 단계별 체크리스트

### P0 (오늘)
- [ ] 웹 서버 시작 (`python web_ui.py`)
- [ ] `http://localhost:8080/assets` 접근 확인
- [ ] 에피소드 로드 & 이미지 갤러리 표시
- [ ] S01 Kling 프롬프트 복사
- [ ] Kling AI 웹사이트에서 프롬프트 입력 & 테스트
- [ ] 결과 스크린샷 저장

### P1 (이번 주)
- [ ] `outputs/` 디렉토리 정리 및 구조화
- [ ] `archives/` 폴더 생성 및 파일 이동
- [ ] `pytest tests/test_prompt_combiner.py -v` 실행
- [ ] 모든 테스트 통과
- [ ] 커버리지 리포트 생성 (> 85%)
- [ ] GitHub에 푸시

### P2 (이번 주 후반)
- [ ] 5개 도구 모두에서 S01 생성 테스트
- [ ] 각 결과 품질 평가 (1-5점)
- [ ] 비교 분석표 작성
- [ ] 최적 도구 선택 결정
- [ ] 결과 저장 (`tool_comparison_results_20260228.json`)
- [ ] Phase 5 계획 수립 (선정 도구로 4-6장면 원샷 생성)

---

## 📌 주요 파일 위치

```
현재 에피소드:
e:\2026\murim\outputs\ep002_천마의_첫_하산__피로_물든_강호_첫걸음_20260228_114846\

프롬프트:
├── prompts/
│   ├── image_prompts.json      (6개 장면 이미지 프롬프트)
│   ├── video_prompts.json      (6개 장면 비디오 모션 플랜)
│   └── audio_guide.json        (BGM, SFX, TTS 가이드)
├── images/
│   ├── S01_nanobanana.png      (이미 생성됨)
│   ├── S02_nanobanana.png
│   ├── ... S06_nanobanana.png
│   └── manifest.json           (이미지 선택 상태)

테스트 코드:
e:\2026\murim\tests\test_prompt_combiner.py

대시보드:
e:\2026\murim\templates\assets.html
```

---

## 🚀 Phase 5 (다음): 

대형 도구 통합 (선정된 도구로 4-6장면 원샷 생성)

```
예상 시간: 1-2일 (도구 API 통합)
```
