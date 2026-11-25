# Murim 전 공정 통합 설계 수렴 및 D0~D5 반대심사 v0.1

2026-11-25 | 기준 22b0f9acc90c8d5d3fd09e902166ae2e96eecfd6. 사용자 요청: 남은 설계 한 번에 개선. 중앙 agent 권위 5개 문서(AGENTS 37a5f9998781dfef746d92b13d8c70dea6e31378, portability 7562db6dd81958e3aa656e6b301d196c3cd2d149, runbook 3145a55042708efb6b589cb4f2e2c04319bbba1d, state edeed0966ece795d1adee368981e08082334174e, handoff 2e91cef449f7276fb03bf5e2fd867baa420740b4)의 적용 경로/활성 상태 확인. Murim GitHub 원본/Windows 소비 계약 우선. 역사상 중앙 Windows Murim read PASS가 있으나 현재 실제 연결/로컬 HEAD/사용자 변경 확인 안 됨. 이번 변경은 remote 문서만. 독립 평가자나 repo-wide 자동 검사 아님.

## 1. 전 공정 설계 연결
A01~A06/A15: [역대조 및 구체 설계](A01_A06_A15_DESIGN_RECONCILIATION_2026-11-25.md). A07~A11 기존 상세 원장 및 [A12](A12_RELEASE_AND_ECONOMICS_DESIGN_2026-11-25.md), [A13](A13_FIVE_AXIS_EXECUTION_DESIGN_2026-11-25.md), [A14](A14_NATURAL_LANGUAGE_DIRECTOR_DESIGN_2026-11-25.md). 15개 초기 공정 모두 설계 입력·비교 후보·실패/검증 경계에 연결. 전 기능 inventory의 완전성/전체 구현/합격 아님.

| 생산 경계 | 입력 → 산출물/권위 | 핵심 gate |
|---|---|---|
| A01 시장 | evidence → candidate/market decision | MARKET-M0~M6, 투자 0 유지 |
| A02 지식 | observed source → candidate KnowledgePack | 실제 coverage·권리·효과 |
| A03 기술 | source recipe → technology/capability evidence | 실제 target 비교·권리 |
| A04 집필 | 승인 brief/pack → story/outline/script/state | G1/G2 및 실제 독립 평가 |
| A05 프리비즈 | script/beat → shot plan/timeline | scene coverage·actual timing·공간 |
| A06 자산 | shot/identity requirements → asset refs/revisions | 정체성·권리·실제 검증 |
| A07 영상 | shot/asset/voice constraints → video takes | actual frame/continuity/condition |
| A08 음성 | script/speaker/performance → voice take/alignment | 권리·발음·실제 sync |
| A09 음향 | voice/video events → cues/stems/master | 대사·sync·delivery profile |
| A10 편집 | approved media/ranges/cues → EditPlan/final candidate | time/round-trip/전체 QC |
| A11 통합 | final artifact+evidence → integrated review | 기술·전문·관객/시장 분리 |
| A12 공개 | 승인 final/권리 → release/settlement | 별도 업로드/게시/비용 승인 |
| A13 공통 | intent/contracts → canonical job/revision/events | 5축/권한/restore/lease |
| A14 UI | 자연어/선택 → proposal/approved intent | 실제 상태·권한·사용성 |
| A15 평가 | 실제 evidence/calibration → adjudicated review | 독립성·holdout·선별 효과 |

A07/A08은 단순 선형 순서가 아님: 대사 시간·화자 필요한 A2V shot은 voice take를 먼저 pin, 영상 후보의 실제 timing 검토 후 A05/A10 승인 edit 변경. A09는 실제 video event/voice timing, A10은 picture edit와 sound spotting의 교차 의존. 반복은 새 revision DAG로만; cycle/무한 feedback 금지. A15 평가기와 A13/A14는 전 공정 선행/공통이며 마지막 순서의 실행으로 미루지 않는다. A01 시장 gate가 없는 연구용 fixture는 미승인으로 격리, 투자/공개 경로와 결속 금지.

## 2. 교차 경계 반대심사(작성자 논리 검토)
| 반례/충돌 | 설계 보완 | 남은 실제 검증 |
|---|---|---|
| 같은 프로젝트 두 저장소가 권위 | 현 M-VML 유지, isolated projection, explicit CAS cutover/restore | actual round-trip/approval equivalence |
| 외부 durable engine이 Manager를 대체 | 단일 Manager 정책/승격, Bridge 실행·adapter, provider ref | replay/restart/cancel/race |
| 생성 job timeout 이후 중복 지출/게시 | durable intent, UNCERTAIN, reconcile, no blind resubmit | 실제 provider semantics |
| A07 프레임수 vs A08 sample vs A10 timeline | rational half-open, actual PTS/sample mapping, trim/retime evidence | VFR/29.97/latency/round-trip |
| A05/A06/A07 정체성/소품과 정확 문자가 충돌 | approved refs, state map, A10 deterministic composite 후보 | 독립 view/shot/contact/문자 QC |
| A08 영상 내 음성/A09 별도 voice 중복 | explicit source routing, D/M/E, source audio preserve | 실제 믹스/동기/명료도 |
| shot 수정으로 global 믹스/편집 영향 누락 | dependency closure 및 master 재계측, 정상 source 보존 | dirty range 및 decoded compare |
| 가짜 PASS/점수/동일 reviewer ID | A15 인증/객관/독립 판정·HOLD, Core 구조검사만 | 독립 holdout/selection lift |
| retention/조회로 원인·수익 확정 | A11 비교·A12 정산 및 원가 | 실제 관객/정산 |
| AI가 자연어를 외부 공개 승인으로 해석 | A14 intent/diff/CAS, 별도 권한/비용 | 실제 권한/UX |
| 최신 기술/단일 성공으로 무조건 교체 | A03/A15 champion/challenger·권리/비열화·고정 version | target environment/비용/효과 |
| 새 Add-on이 공용 host를 수정 | A13 generic manifest/route/schema/ownership | 0/100/300/500 및 repo-wide 검사 |

추가 기능 inventory 후보: 권리/사료 provenance, 보안·비밀·복구·관측, 현지화/자막 accessibility, 배포/결제 승인, 외부 tool integration, multi-user/프로젝트 동시성, 장편·연재 및 현지화 자산 이력. 기존 15분류에 연결하되 모든 미래 기능 완전성은 미입증. 신규 기능이 공통 코드 feature-specific 수정을 요구하면 구조 결함. 외부 engine 후보의 실제 가용성/비용/권리 미확인 상태를 솔루션 채택으로 변경하지 않음.

## 3. D0~D5 판정(기존 요구 불변)
| Gate | 이번 설계 성과 | 판정 및 blocker |
|---|---|---|
| D0 문제·시장·비교 | A01/A11/A12 요구 및 후보 비교 연결 | HOLD: 실제 동종 수익/비용·시장·직접 경쟁 앱 사용성 비교 부족, qualified pool 0 |
| D1 기술 실현성 | A03/A07~A10 공식 source 기술 후보/환경·복구/권리 조건 | HOLD: 실제 target GPU/설치·모델/권리·비용·난제 비교 미확보 |
| D2 전문 생산 | 15공정 상세 설계 연결, A12~A14 및 선행 7공정 보완, 교차 계약 점검 | DESIGN_DRAFT_CONVERGED (설계안 작성 범위); D2 HOLD: 전수 구현 가능 계약 검증·독립 설계 반증 미완료 |
| D3 평가 | A11/A15 독립/불확실성/holdout 및 증거 층 | HOLD: 실제 평가기/전문가·관객 보정/사전 기준 미검증 |
| D4 사전 실물 | 기존 원고/무음 animatic/참조 이미지 및 실패 보존 | HOLD: 대표 최종 실제 영상/음성/독립 경쟁 비교·실제 비용/실환경 미확보 |
| D5 통합 | 위 의존/시간/권한/상태/SSOT/복구 위험 및 완화책 | HOLD: 독립 반대심사·D0~D4 근거·전체 repo 경계/누락 감사 미완료 |

A01~A15 전부 NOT_QUALIFIED, DESIGN_HOLD / PRODUCT_CODING_FROZEN / COMPETITIVE_ALPHA_NOT_PROVEN / REMEDIATION_REQUIRED. 문서 일관성과 실제 제품 성공/5축 준수/시장 성공/모든 기반기술 완전성 구분. 기존 코드/테스트 변경 0; 신규 실제 검증 실행 없음. 기존 27/16 PASS 범위 유지. 소스 부분 비교와 문서 정합 검토는 repo-wide 자동 감사 아님.

## 4. 다음 단일 작업: 최우선 blocker 해소
연구/설계 문서 추가를 목적화하지 않는다. 먼저 기존 Windows 실행 경로의 read-only inventory 및 기존 승인된 툴/가용 모델/권리·비용·자원·실행 가능 범위를 실제 확인(현재 연결 미확보, 무단 설치/전송/지출 금지). 목표 장비의 대표 고위험 A07 손·소품 접촉/정체성 및 A08 한국어 발화·sync의 기존 엔진 기반 동등 비교 조건과 평가자 접근을 확정. 가능하면 기존 도구만으로 가장 작은 실물 비교를 수행; 동등 비용/실패/독립 증거 미확보는 HOLD, Q1/Q2/Q3/Q4 재개 조건 미충족이면 반복 검색 금지. 병행 가능 범위의 D0 시장 코호트/실제 경쟁 앱 및 A15 독립 holdout 보정; 실물 확보 권한 필요 시 구체 blocker만 보고. 최종 D5 독립 반대심사에서 실제 증거, 잔여 위험, 전체 inventory 및 검증 계약 확인 후에만 DESIGN_OK 및 코드 착수 여부 결정. 사용자에게 기술 선택이나 파일 수동 rewrite 위양 금지. 원본 보존 및 모든 기존 gate 유지.
