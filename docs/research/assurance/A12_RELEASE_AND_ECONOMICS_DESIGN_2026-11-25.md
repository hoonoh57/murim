# A12 공개·확장·수익화 상세 설계 v0.1

2026-11-25 | 기준 22b0f9acc90c8d5d3fd09e902166ae2e96eecfd6 | D2 보완안 / A12 NOT_QUALIFIED. [시장 선행 게이트](../../MURIM_PREPRODUCTION_MARKET_GATE.md) blob 8535de100b6a8ad6aaadf7563801b9359f2e5ada, [Q1](../market-library/Q1_A01_ACTUAL_EVIDENCE_2026-11-24.md) 79fd8a726c78dc714c73096d21a4cb577e3764ba, [A11](A11_INTEGRATED_WORK_AUDIENCE_EVALUATION_DESIGN_2026-11-25.md) 우선. 기존 MARKET-M0~M6 투자 선별과 사후 정산·운영 확대는 별도. 실제 게시/계정 연결/투자/정산 없음.

## 비교 근거와 GAP
- 현행 Studio render.py는 완성 파일 및 DRAFT_RENDERED_QUALITY_NOT_APPROVED receipt, web.py는 UNADJUDICATED 리뷰를 생성. 해당 확인 범위에 자동 게시/정산/확장 기능 없음; repo 전체 부재 증명은 아님. 기존 시장 계약은 정책·완전원가·손실하한을 정의했으나 실제 실행 상태/정산 연결 미실증.
- [YouTube videos.insert](https://developers.google.com/youtube/data/reference/rest/v3/videos/insert), [revision history](https://developers.google.com/youtube/data/revision_history?hl=en): 공식 검색 본문상 2026-11-03 변경으로 미검증 API 프로젝트 업로드의 강제 private 제한 해제, privacyStatus 생략 시 public 기본값(계정별 예외). revision history 직접 열람 cache miss; API 버전·실제 계정 검증 필요. 기본값/과거 제한을 안전장치로 사용 금지. containsSyntheticMedia, notifySubscribers, 권한·실제 상태 검증.
- [resumable upload](https://developers.google.com/youtube/data/guides/using_resumable_upload_protocol?hl=en): 세션 URL, 중단 시 빈 PUT 상태 조회 및 수신된 마지막 byte 이후 재개. 세션 URL은 민감정보, 로그 금지. 새 upload 반복 호출로 중복 게시하지 않음.
- [monetization policies](https://support.google.com/youtube/answer/1311392?hl=en), [partner earnings](https://support.google.com/youtube/answer/72902?hl=en-EN): 공식 검색 본문상 독창성/진정성·반복적 대량생산 기준, 추정 수입은 무효 트래픽/Content ID 등 조정 후 확정. 자막 API [captions](https://developers.google.com/youtube/data/reference/rest/v3/captions) 및 [localizations](https://developers.google.com/youtube/data/reference/rest/v3/videos) 지원; 자동 sync 옵션 deprecated(2024-03-13 발표), A08/A10 확정 timing 사용.
- Q1 무산 모집금은 매출 아님, 모집 성공도 순익 아님. 기존 다섯 투자 후보 제외 유지. 새 동등 정산 코호트 미확보. 현 정책/과거 사례 소급 적용 금지.

| GAP | 설계 선택 |
|---|---|
| R121 게시 전 작품/권리/채널 상태 결속 | Compose ReleasePlan/approval pin, Adopt 공식 API |
| R122 중단 업로드·중복·실제 공개 상태 불확실 | Adopt resumable/status, Compose attempt/reconcile |
| R123 예상·확정·실수취 혼용 위험 | Compose SettlementLedger와 비용·현금흐름 |
| R124 확대 시 지역·언어·정책/품질 편차 | Compose locale branch와 단계별 승인 |
| R125 조회수·추정 수익으로 규모 확대 | Compose stop/scale, 실제 cohort·완전 원가·불확실성 |
| R126 권리 철회/정책 변경/claim | Compose release hold/containment/회수 이력 |

## 실행 계약
ReleasePlan은 승인 artifact/hash·timeline·G1~G4 증거·A11 비교, channel/account/region/locale/format, 제목/소개/표지/자막/음성, AI 표시/대상 연령/라이선스·권리 만료, 배포 방식·명시 privacy/notify, 비용/일정/승인/정책 snapshot을 pin. 채널 정책 및 account eligibility 재확인, 실제 업로드/공개/지출/개인정보 사용은 서로 별도 승인. 게시 직전 승인 artifact/metadata revision과 권리 일치 검사. 원고·자막·음성 현지화는 source 의미/캐릭터/시간/문화·규정 검토, A08~A11 관련 재평가; 다른 국가 성과로 기존 시장 자동 승격 금지.

상태: DRAFT→RELEASE_REVIEW→APPROVED_FOR_UPLOAD→UPLOADING→PROCESSING→PRIVATE_VERIFIED→APPROVED_FOR_PUBLICATION→PUBLISHED_VERIFIED, 별도 HOLD/UNKNOWN/REJECTED/RESTRICTED. 이 전이는 예시이며 실제 API 지원 범위와 명시 권한으로 매핑. private도 외부 전송이므로 승인 필요. API 요청에 privacyStatus 명시; 최초 upload 승인과 공개 승인 분리, notifySubscribers false 등 필요 조건을 명시하고 실제 동작 지원 여부 검사. provider 결과가 예상과 다르면 공개 작업 중단, 미승인 공개 감지 시 추가 확산 차단 및 승인된 containment 정책; 자동 삭제/무단 수정 금지. session ID/received bytes/remote video ID/receipt와 attempt를 보존, response lost→UNKNOWN, 실제 상태 조회 후 재개. 중복 위험 확인 전 새 upload 금지. 실제 processing/upload/privacy/status/claim 증거, 원격 artifact와 제공 가능한 identity 확인; 원격 인코딩 hash 동일 가정 금지. 공개 성공과 수익 자격·수익 발생 구분.

SettlementLedger: source record/period/currency/locale, gross sales/estimated revenue/finalized payable/settled cash, 수수료 차감 상태, refunds/chargebacks/withholding, platform statement ID 및 허용 실제 입금 evidence, FX 날짜/출처, 프로젝트별 allocation rule 및 reconciliation 차이. 매출 차감 수수료 중복 차감 금지. 직접 제작/재시도/실패/인간 노동·기회비용·GPU/전력/감가·외주·저장·현지화·마케팅·유통·리워드 이행·세무/고정비의 근거와 actual/estimate 구분. cash flow(실입금-실지출)와 economic profit(인식 수익-완전원가) 별개; 전망은 Q1/M5의 비교 코호트와 joint scenario 기반, 미확인 null. 손실 후보를 분모에서 제외하지 않는다. 광고 RPM과 Shorts/유료전환/판권의 분모/통화/시점 혼용 금지. 세법/회계 판단은 실제 관할 전문가 확인.

ScaleDecision: 기존 승인 사업 한도, 실제 합격 품질·수취/완전원가/현금흐름 및 노출, A11 비교 우위/비열화·채널 정책과 제작 처리량, 하방·잔여 위험. 신규 시장/언어/포맷별 작은 승인 pilot→정산/비용 확인→다음 범위 확대. 숫자 손실 한도/수익률/표본 기준은 사용자 사업 목표와 실제 데이터로 사전 확정, 현재 미확정. 기준 미달/현금 또는 권리 위험 발생→추가 투자/공개 HOLD; 이미 게시본의 수정·회수는 별도 승인. 예측 시점 snapshot과 실제 실패 포함 결과 비교로 시장 선택 스킬 검증, 과거를 결과로 재작성 금지. 사업 성공과 앱 경쟁력은 별개.

5축: Core generic artifact/time/evidence/state; Bridge lifecycle/approved execution; Add-on channel API/정책·현지화·경제성 의미/settlement mapping; JSON 원장·정책·상태 저장; Manager 승인/권한·budget/lease/attempt/reconcile/DAG/승격. 외부 account/token 비밀 저장소, JSON 원문 금지. Build는 전문 release planner·비용/정산/정책 결속 차이만. 신규 채널 전용 host 분기 금지. 반례: private 기본값 가정, upload timeout 후 중복, 추정 수익=현금, 무산 pledge=매출, 비용 누락, 조회수로 scale, 번역/권리 철회에도 이전 승인 사용. 실제 계정/정산/수익/권리/비용 검증 NOT_RUN; D0/D1/D3/D4/D5 HOLD, A12 NOT_QUALIFIED.
