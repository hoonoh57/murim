# Murim 장기 경쟁우위 및 전문 스킬 진화 계약 v1.0

> 최신 최우선 계약 (2026-11-24): [제품 코딩 선행 설계 심사](MURIM_PRECODE_DESIGN_GATE.md). DESIGN_HOLD / PRODUCT_CODING_FROZEN. 기존 다음 코딩 계획은 전체 설계 OK까지 보류. 이 문서의 설계 방향은 보존하되 실제 비교·전문 생산·평가 설계 결함을 먼저 해소한다.

2026-11-24 | 사용자 확정 방향 | 설계 계약 및 최초 전문 스킬 후보, 경쟁우위 미실증
권위: AGENTS.md, MURIM_FIVE_AXIS_ARCHITECTURE.md, MURIM_CASCADING_QUALITY_CONTRACT.md.

## 1. 목적
수십 년간 변화할 모델·엔진·편집 기술을 동일 핵심 계약으로 흡수하면서, 경쟁 제품보다 우수한 실제 작품 및 낮은 사용자 부담을 지속적으로 입증할 수 있는 구조를 개발한다. 장기 수명·최고 품질·시장 성공은 설계 목표이지 보장하거나 기계 점수로 인증할 수 있는 사실이 아니다. 최신 제품이 나오면 재조사/동일조건 실증/채택으로 대응한다. 시나리오뿐 아니라 모든 제작 capability에 적용한다.

## 2. 이중 품질 캐스케이드
하위: 프로젝트 목표→스킬 선택→부모/자식 전문 제작→독립 검증→결함 원인에 한정된 수정→목표 초과 충족→통합 평가→기존 인간 감수 및 승인.
상위: 전문 기관/원저자/현업 교육/공개 표준/실제 경쟁작 조사→근거/출처/권리/적용범위 분류→현행 champion 대비 결함 가설→후보 스킬 설계→분리 데이터셋에 대한 실물 비교 및 회귀→권한 내 채택 또는 격리→실행 실패 증거의 재수집.
작품 개선과 스킬 개선을 분리한다. 작품별 실패는 학습 후보 데이터이지 자동으로 전역 규칙이 되지 않는다. 개인 작품·대화·피드백의 전역 이용은 별도 권한 및 비식별 조건 필요. 실행 중 스킬 버전 고정, 기존 승인 작품 자동 변경 금지. 자동 후보 수정은 sandbox에서만; 권한/안전/사료/라이선스/기존 4-GATE 계약 자체를 스킬이 재작성하지 못한다. 독립 시험 실패 시 현행 champion 유지. 운영 중 발견된 중대 안전 결함은 기존 champion도 격리할 수 있다.

## 3. 전문 지식 관리
모든 capability의 Add-on에 출처의 역할(공개 표준/공식 심사 기준/전문 교육/원저자 구현/연구/경험 가설), 적용 조건, 원문 링크와 확인일, 라이선스/인용 제한, 근거 수준, 기존 스킬과의 차이, 긍정 및 반례 fixture, 평가 루브릭, 후보/채택 상태를 관리한다. 제3자 문서를 무단 복제하지 않고 허용 범위에서 요약/독자적으로 재구성한다. 공식 심사 기준을 읽었다는 사실이 스킬의 기관 인증이나 실제 전문 심사 통과를 뜻하지 않는다.
공개 Agent Skills SKILL.md 형식은 상호운용 후보로 사용한다. skill별 instructions/references/assets는 Add-on 소유. 사용 전 검증된 manifest, 버전·digest, scope 및 의존 계약을 등록하고 필요한 문서만 로드. 외부 SKILL.md에 적힌 도구 호출·스크립트·지시가 시스템 권한을 확대하지 못한다. 출처에서 가져온 텍스트는 untrusted data로 처리한다.
상위 master skill은 공통 창작 방향·역할·필수 증거·질적 개선 프로세스만 조율하며, 장르/매체/길이/목표 관객별 전문 스킬을 합성한다. 단일 거대 프롬프트, 특정 장르 15비트, 고정 샷수, 고정 문장수 같은 획일 규칙을 전 장르에 강요하지 않는다.
전문 스킬 초기 사례: [시나리오 Master 후보](skills/screenplay-master/SKILL.md), [전문 출처 원장](skills/screenplay-master/references/professional-sources.md), [비교 실증 프로토콜](skills/screenplay-master/references/benchmark-protocol.md). 기존 역사/예술 EDITORIAL_MASTER_SKILL_V2, SOURCE_TRUTH_SKILL_V2, CINEMATIC_NARRATIVE_SKILL_V2, INTERNAL_RED_TEAM_SKILL_V2 및 시각 서사 스킬은 유지한다. 후보는 runtime 연결/채택 전이며 기존 권위 스킬을 대체하지 않는다.

## 4. 객관적 비교우위 검증
비교 대상: 현재 champion, 같은 모델의 일반 지시 baseline, 실사용 경쟁 제품(버전/날짜/설정/제약 기록), 가능한 경우 권리 확보 전문가 산출물. 문서/광고의 기능 비교와 실제 결과의 품질 비교 분리. 접근 불가/미시청/미실행이면 NOT_RUN/NOT_OBSERVED.
고정 brief와 입력 자산, 장르/길이/예산/인간개입·허용시간을 사전에 선언. 같은 모델의 skill A/B와 서로 다른 완성 제품 비교는 별도 실험. 동일 비용·시간 비교와 동일 목표품질 도달 비용 비교를 나누고 seed/샘플링/반복수/실패 포함 결과를 모두 보존. 독립 블라인드 pairwise(A/B 위치 교환, tie 허용), 필수 검증, 독립 평가자 불일치, 실제 사람의 보정 표본, 통계적 불확실성을 함께 기록한다. 비교 평가자에 생성자 자기점수, 공급자/스킬 이름, 기존 승패를 숨긴다. 개발 세트/선택용 검증 세트/보류 독립 시험을 분리하고 정답 누출/반복 선택 과적합을 막는다.
숫자나 고정 승률만으로 우위를 선언하지 않는다. 최소 품질 + 초과 목표, 핵심 품질 측면의 비열화 및 중대 결함 0, 별도로 사전 정의된 비교우위 효과크기/불확실성, 실제 사용자 노력·시간·비용 및 복구를 판정한다. 비교 실패 시 가설 수정. 소표본/불확실성 크면 INCONCLUSIVE, 근거 없이 우월하다고 표시 금지.
구조 경쟁우위 별도 시험: 0/100/300/500 등록, A/B 및 새로운 capability 장착 시 host 변경 0, worker crash/OOM/timeout/취소·재시작·권한 실패 격리, 원본/승인 이력 보존, 기존 저장소 schema/버전 migration 및 rollback, 장기 작업 resume, 독립 engine 교체와 UI 동일 계약 유지. 생존성 검증 없이 구조적 장수 보장 금지.
자동화 프레임워크/프롬프트 최적화 후보: Agent Skills, DSPy GEPA, 기존 평가 도구·워크플로 runtime. 채택 전 실제 동일 fixture, 비용, dependency, 보안, local Windows 호환 비교. 외부 telemetry/유료 요청은 사전 승인 없이 활성화 금지. 최적화기는 후보 생성자이지 최종 judge/승격 권한자가 아니다.

## 5. 5축
Core: generic immutable skill/capability/quality/evidence/version/dependency 계약 및 검증 primitive, 전문 스킬 텍스트나 경쟁 제품 목록 하드코딩 금지.
Bridge: feature-blind discovery/handshake/실행/격리; 외부 skill host/adapter 연결.
Add-on: 전문 스킬, 출처 분석·전문 생성/평가/개선, 실제 엔진 연동 및 고유 rubric. 다른 Add-on 직접 호출 금지.
JSON/Persistence: 출처/버전/해시/후보·실행·평가·승인·비교 증거를 불변 저장, 판단/실행 금지.
Central Manager: 공통 skill registry/선택/composition, 비교 실험 계획/권한/예산/작업 위임, 증거 확인/승격/rollback 및 targeted invalidation, 기계검증 관측. 도메인 의미/전문 작성 로직 구현 금지. 별도 여섯 번째 축이 아니다.
사용자는 자연어로 방향/감수/수정 요청을 제공하고 AI가 품질 향상된 실제 원고를 제시한다. 프로젝트 취향/확정 결정은 revision으로 관리, 사용자에게 모델/프롬프트/평가 점수 선택을 강요하지 않는다. 작품의 기존 승인 및 비용/권리 경계 유지.

### 5.1 실제 독자·시청자의 피드백

[실제 관객 검증 계약](MURIM_AUDIENCE_VALIDATION_CONTRACT.md) 적용. 저비용 원고/연재 및 독자 검증을 작품과 스킬 진화의 근거로 활용하되 노출/연독 proxy/댓글 편향, 권리, 매체 차이 통제. 독립 재검증 전 전역 스킬 승격 금지.

### 5.2 제작 기술의 시장 반응 기반 개선

[압축 실물 시장 검증 계약](MURIM_SHORT_FORM_MARKET_VALIDATION.md) 적용. 짧은 완성 작품과 단위 기술의 대표 난제, 실제 관객 반응/전문 관측/통제 비교를 함께 사용. 게시 revision과 생성·편집 타임라인·engine/skill pin 연결 및 독립 비교로 원인을 확인. 반복 실증 후 challenger 채택, 권한·동결 유지.

## 6. 현재 및 다음
M1-A 독립 품질 primitive 27 PASS, 전체 M0/Windows/구조 검증 미완료. 이 문서 및 시나리오 skill v1은 실제 실행이 아닌 신규 설계·출처 기반 후보. 전문 기관에 의한 Murim 검증 없음. 실물 경쟁 제품 비교 및 고객 검증 NOT_RUN. 다음 M1-B generic dependency/invalidation, skill version/reference 결속 및 이후 독립 Bridge/Manager/Persistence slice; 실물 screenplay benchmark는 해당 생성/독립 평가 capability와 승인된 실행 환경을 확보한 뒤 수행. 기존 제품 수정 없이 병행 준비 가능, 실제 비교 전 champion 교체 금지.
