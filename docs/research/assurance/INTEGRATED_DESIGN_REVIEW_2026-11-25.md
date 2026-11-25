# Murim 전 공정 통합 설계 수렴 및 D0~D5 반대심사 v0.1

2026-11-25 | 기준 22b0f9acc90c8d5d3fd09e902166ae2e96eecfd6. 사용자 요청: 남은 설계 한 번에 개선. 중앙 agent 권위 5개 문서(AGENTS 37a5f9998781dfef746d92b13d8c70dea6e31378, portability 7562db6dd81958e3aa656e6b301d196c3cd2d149, runbook 3145a55042708efb6b589cb4f2e2c04319bbba1d, state edeed0966ece795d1adee368981e08082334174e, handoff 2e91cef449f7276fb03bf5e2fd867baa420740b4)의 적용 경로/활성 상태 확인. Murim GitHub 원본/Windows 소비 계약 우선. 역사상 중앙 Windows Murim read PASS가 있으나 현재 실제 연결/로컬 HEAD/사용자 변경 확인 안 됨. 이번 변경은 remote 문서만. 독립 평가자나 repo-wide 자동 검사 아님.

## 2026-11-25 후속 통합 재심사 — 실제 근거 및 실행 우선순위 (최우선)

기준 HEAD dc2bf1fcd1bfecf935cd70fa775acdfca7fff5a8. 이전 통합 checkpoint 5e3a5c6adff9b7047e50335c9347cd24c242437a 대비 실제 GitHub compare ahead 12 commits, docs 8 modified, 삭제0, 제품/테스트 변경0. 작성자 재심사이며 독립 심사/전체 repo 경계 검사 아님. Drive queue 80 entries, unmatched req0. 마지막 승인 root E:/ComfyUI_New, 현재 worker/server/GPU 및 Murim local HEAD/status 신규 미실측.

| 공정 | 실제 근거/개선 수준 | 잔여 필수 조건 |
|---|---|---|
| A01 | Q1 실제 공개 펀딩 성공·실패/원가 반증, 5개 후보 제외 | 동종 신규 제작자 실제 정산+완전원가/노출/실패 포함 cohort, concept 검증. 투자 pool0 |
| A02 | W009 원저자 제작 기록 일부 직접 관측 | 권리 확보 실제 AV coverage, 독립 pack 효과 |
| A03 | 원저자 graph/Windows 설치 파일 및 recipe 확인 | live schema/loader/실행/권리/비용·동등 품질 비교 |
| A04 | 실제 A/B 원고 및 B r2, 동일 작성자 비독립 | 독립 전문 원고·관객 비교 |
| A05 | 실제 83초 도식 animatic 및 국소 수정 | 실제 영상 연속성/동작/전달력 |
| A06 | 일부 참조 이미지, 생성된 가짜 QA 격리 | 다양한 각도·조명·손/소품·정체성 독립 검증/권리 |
| A07 | 사용자 Deno 원형 Adopt, UI graph 5개 및 PNG native API 46 nodes/79 links, 실제 LF/slot/frame/strength 계약 | 기존 실제 output decode, multi-guide runtime/실효 index/8GB 품질·비용 |
| A08 | WAV header 4개, v3/v4 config discrepancy, 사용자 v2 평가 | 실제 inference binding/권리/독립 원어민 청취/정렬/외부 음성 A2V |
| A09 | 실제 renderer mapping GAP 및 격리 FFmpeg delay/level/합산 반례 | Windows actual AV/mix/true peak/명료도/권리 |
| A10 | 실제 renderer/cache 및 rational timeline/picture/audio 분리 설계 | 실제 전편 decode·편집·자막·roundtrip/독립 비교 |
| A11 | 실제 근거 8종 관측 범위 및 원인별 repair | 전체 감상/관객/독립 비교/repair uplift |
| A12 | ReleasePlan/settlement/별도 공개 승인 | 승인 계정/정책/권리/정산/원가. 2026-11-03 privacy 변경 원문 미확인, 해당 주장에 의존 금지. 명시 private 및 actual status 검증 유지 |
| A13 | 기존 Core/Studio/CRUD 증거, manifest/DAG/lease/CAS/UNKNOWN/single cutover 계약 | 기존 기술로 위험 가정 검증, 실제 migration 원본·계약 및 독립 심사, 구현 후 runtime/host/registry/restore |
| A14 | 기존 human relay/CAS/raw review 및 자연어 proposal 설계 | 실제 강한 경쟁 앱/비전문가 비교 및 구현 후 WYSIWYG |
| A15 | Q4 실제 구조 반례, 관측 범위/qualification/repair 평가 계약 | 독립 참조/평가자/봉인 holdout/실제 선택·개선 효과 |

D0 HOLD: 동종 시장 및 직접 경쟁 제품 비교 부족. D1 HOLD(부분 근거): 실제 설치/native prompt/공개 입력/WAV header/격리 DSP 확보, target runtime/품질/권리/비용 미검증. D2 HOLD(DESIGN_DRAFT_CONVERGED): 15공정 생산 및 교차 계약 보완, 독립 구현 가능성/반증 심사 미완료. D3 HOLD: 독립 평가자/실제 사람 보정/봉인 holdout 없음. D4 HOLD(부분 실물 근거): 실제 기존 원고/animatic/media 및 반례는 있으나 동일 조건의 독립 평가·강한 비교군·실환경·완전원가 결합 부족. D5 HOLD: D0~D4 및 독립 반대심사 부족. 기존 D5 원계약대로 구현 이후에만 측정 가능한 실제 신규 host hash/0·100·300·500 registry 규모/최종 UI/WYSIWYG/신규 runtime 복구는 구현 인수 조건으로 분리. 미구현 제품 실행을 사전 코드 허가의 전제로 요구하는 순환 금지. 선행 설계·기존 기술 위험 실증/권리/시장/독립 검증 요구는 유지. 전체 15공정 NOT_QUALIFIED. 사용자 Deno Adopt 결정은 원형 채택 정책이지 전체 실측 PASS 아님.

### 실제 blocker 해결 순서

1. P0 기존 실물 관측 경로: 기존 승인 ComfyUI root saved PNG/MP4/audio 쌍 1개에 대해 실제 size/stream/PTS/decode 가능성 확인. read-only CRUD 크기/전송 한도 내에서만 기존 파일 조회, 전체 2222개 출력 전송 금지. 큰 파일/실행 제약이면 기존 Windows ffprobe/기존 실행 기능의 승인 범위 및 필요한 사용자 수용 관측만 확인. 새 고정 runner·제품 코드·원본 변경·무단 외부 분석 API 금지. 실제 digest/관측 범위 또는 구체 blocker 기록. 이번 MP4 decode 미실행.
2. P0 병행 독립 평가 및 시장: 현재 연결 도구 목록에서 독립 AV 의미 평가 실행/Windows shell 직접 실행 수단 미확인(조회 범위의 ENVIRONMENT_ISSUE). Q4 공개 진단 집합 반복 대신 독립 reference/adjudicator/실제 관측/봉인 holdout 접근·비용·권리 및 사전 protocol 필요. Q1 재개는 실제 정산+완전원가 동종 성공/실패 cohort 또는 검증 계약/원가 대안 확보 시. 동일 공개 검색 반복/자기 평가를 독립 평가로 대체 금지. 외부 전송/모집/비용/게시 별도 승인.
3. P1 최소 위험 실증: P0 이후 필요한 대표 난제만 동일 brief/강한 기준으로 기존 도구 사용. Deno 원형 불변, multi-guide와 실제 시간·음성 routing 검증. 로컬 CRUD는 shell/GPU 실행 권한 아님. 실제 실행/권리/예산/독립 근거 미확보 HOLD.
4. P1 A13/A14 공통 구조 및 사용성: 실제 기존 XML/history/approval 의미 보존과 기존 runtime 후보의 replay/reconcile/permission 위험 검증, 독립 설계 반대심사. 실제 미구현 host/registry/UI는 구현 인수 계획. A12는 별도 승인 전 simulation/계약 범위만.
5. 새 실제 증거 또는 구체 HOLD로만 갱신. 문서 양·동일 Deno 조사·예시 제작 반복은 종료. 독립 평가 및 시장 증거 없이 DESIGN_OK 기록 금지. D0~D5 충족 및 독립 반대심사 뒤 착수 판단. 다음 단일 작업은 1번 기존 실물 관측 가능 경로 확인.

DESIGN_HOLD / PRODUCT_CODING_FROZEN / COMPETITIVE_ALPHA_NOT_PROVEN / REMEDIATION_REQUIRED. 신규 실물 실행/코드/비용/게시/원본 변경 없음.

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
