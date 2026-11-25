# A11 통합 작품·관객 평가 기반기술 및 생산 설계 v0.1

2026-11-25 KST | 기준 a2fdb166d2e0ae92499ebe433e0095860b21ed1b | D2 상세 설계 보완안 / A11 NOT_QUALIFIED / DESIGN_HOLD.
권위: [통합 심사](../../MURIM_ASSURANCE_AND_COMMITTED_EXECUTION_CONTRACT.md), [캐스케이드](../../MURIM_CASCADING_QUALITY_CONTRACT.md), [관객 검증](../../MURIM_AUDIENCE_VALIDATION_CONTRACT.md), [압축 실물 계약](../../MURIM_SHORT_FORM_MARKET_VALIDATION.md), [5축](../../MURIM_FIVE_AXIS_ARCHITECTURE.md), [공정 원장](STAGE_ACCEPTANCE_REGISTER.md). G1~G4, D0~D5, MARKET-M0~M6 및 기존 독립 평가/권리/인간 승인 불변. 본 연구는 코딩 전 비교 및 개선이지 관객 실험/작품 제작/게시/승격 아님.

## 2026-11-25 — 실제 제작 증거의 범위·결함 위치·수정 책임 연결

기준 0b4f0f46a84d680f48732a017338587af0b847bb. A07~A10에서 확인한 기존 실제 Deno recipe, 공개 입력 계약 및 격리 FFmpeg 반례를 평가 설계에 결속한다. 기존 Q4의 고정 24개/5 control 및 실제 Core 모듈 실험은 재실행하지 않았다. 현재 quality_contract.py 6b88cb3ef1465025e085ea6a4056b56f9def81c9 전체와 web.py c3f6002887235c9661f84f024a012cc12daa7c49 review 경로 재확인: 전자는 선언 evidence 정합, 후자는 render SHA 일치 후 human-relayed UNADJUDICATED raw review 저장이다. 어느 쪽도 독립 영상 평가기/승격 엔진이 아니다. 이 차이는 정상 책임 경계이며 Core에 콘텐츠 검사나 도메인 예외를 추가하지 않는다.

### 실제 근거를 잘못 승격하는 반례와 다음 검사

아래는 이미 확보한 원장에 대한 작성자 설계 검토다. 새 semantic evaluator 실행/독립 adjudication 또는 새 품질 시험 결과 아님. CURRENT_STATE 및 A06~A10의 원본 관측을 그대로 참조한다.

| 직접 확보한 근거 | 인정 가능한 범위 | 금지된 확대 해석 / 필요한 다음 증거 |
|---|---|---|
| Deno native PNG prompt CRC/JSON 46 nodes/79 links | 해당 저장 API graph 구조 | 전체 영상 품질/현재 GPU 성공 아님. actual attempt, output decode, 전편 감상 필요 |
| 설치 Deno num_images max50, LF 입력, per-slot strength | 공개 소스 입력 규격 | 50장 품질/VRAM·실효 guide index 아님. 실제 batch/order/guide range 및 장면 검수 |
| Deno loader skip/black fallback | 실패 처리 소스 관측 | 기존 실제 영상에 해당 오류가 발생했다고 단정 금지. 실행별 input/loader/output evidence 필요 |
| GPT-SoVITS WAV header 4개 | 선언 PCM rate/size/duration | 원문·발음·감정·동일 모델 비교 아님. full decode/ASR/정렬/독립 청취 및 weight binding |
| FFmpeg impulse/mapping 실험 | 격리 버전의 sample peak·delay·합산 반례 | Windows 최종 음질·true peak·AV drift 아님. 실제 납품 profile 및 decoded master 측정 |
| A05 도식 animatic | 배치/계획상의 시간·공간 진단 | 실제 인물 연기·검술 물리·음향 작품성 아님 |
| A06 이미지에 생성된 평가 문구 | 이미지에 포함된 텍스트 | 독립 QA 아님. 원본 픽셀 및 별도 evaluator 필요 |
| Q4 24/24 structural empty | 선언 구조 정합 | 14 known-invalid 의미 통과 아님. 독립 사실·semantic 검증 필요 |

### 실제 관측 계약과 평가 순서

1. 각 요구별 EvidenceRequirement에 artifact/revision, 필요한 modality, 시간 범위/coverage, 평가 방법/qualifier, criticality, 기준/target/comparator를 사전 고정. 원본 영상과 proxy의 frame/PTS 대응, 오디오 decode, 자막/원고/asset digest를 실제 입력으로 기록. 해시 확인은 내용 검증이나 출처 인증과 별개. 사전 정의된 관측 범위 미충족은 NOT_EVALUATED/HOLD, 근거와 모순된 주장은 REJECT. 미지의 결과를 0점 또는 PASS로 대체 금지.
2. 기술 probe에서 file/stream/frame/sample/PTS/권리/요구 누락·중복 검증. A07 guide/asset order, A08 실제 대사·화자·alignment, A09 source routing 및 loudness, A10 edit range/transition/자막을 각 전문 Add-on의 실제 artifact 검사로 담당. generic Manager는 요구 및 인증 여부/실제 평가 완료/승격 조건만 처리. 영상 metadata나 정지 프레임만 관측한 평가기는 시간적 동작·lip-sync·대사 평가 자격 없음; 오디오만 관측한 평가기는 입모양과 시각 품질 평가 금지.
3. 전문 의미 평가: 정상 재생 속도 전체 감상으로 먼저 작품의 인과·인물 목표/감정·리듬/흥미·전편 AV 조화 평가. 그 후 구간 진단에서 actual frame/sample evidence를 통해 identity/의상/소품 상태, 접촉·동작·카메라 연속성, 원문 발화/화자/입모양, 대사 마스킹/무음·중복, 자막과 편집 연결을 조사한다. 샘플 프레임 검사는 후보 탐지에 활용할 수 있으나 관측하지 않은 구간의 결함 부재를 보장하지 않는다. 자동 객관 지표는 검증된 적용범위에서만 사용하고, 서로 다른 모델이 동일 입력을 평가한다는 사실만으로 독립성을 확정하지 않는다.
4. 관객 및 시장의 실제 관측은 기존 A11 protocol을 유지. 기술 불량이 없어도 작품의 재미/몰입/수익성을 보장하지 않으며, 실험이나 공개 없이 이를 합격 처리하지 않는다. 기존 non-compensatory gate 및 인간 승인·권리·비용 승인 불변.

### 결함에서 국소 개선까지의 실행 계약 (설계, 미구현)

Finding은 observed symptom, requirement ref, artifact/revision, observation interval, modality/coverage, 실제 frame/sample/source evidence refs, severity, evaluator qualification, uncertainty를 포함한다. 원인 가설은 Finding과 분리한다. CandidateCause에는 담당 capability ref, upstream dependency, 근거/반증, 예상 영향, test plan, 비용을 저장한다. 한 결함에 여러 원인이 가능하면 경쟁 가설을 유지하며 확인 전 책임 Add-on을 실패로 단정하지 않는다.

| 증상 | 첫 확인과 원인 구분 | 수정 및 재검증 범위 후보 |
|---|---|---|
| 얼굴/의상 변화 | 승인 reference와 실제 연속 frame, 입력 순서/구도/guide 강도 | A06 asset 또는 A07 guide/shot만; 인접 shot continuity 및 전편 재평가 |
| 손/소품의 접촉 불량 | 원고상 요구, 가시 keyframe, 접촉 전후 실제 motion | A05 blocking/A06 ref/A07 plan 중 원인 확인된 항목만; Deno 내부 수정 기본 제외 |
| 대사 누락/중복 | 원문, decoded source, ASR/청취, actual mix routing | source 자체 누락이면 A07 joint AV 또는 A08 take, source 정상·최종 누락이면 A09/A10 routing; 동일 대사 ownership 재검증 |
| 입모양 불일치 | 동일 화자/실제 발화·video PTS, audio transform, cut/retime | A08/A07 sync 또는 A10 time mapping 원인 검증; 승인 WAV 무단 교체 금지 |
| 대사 불명료 | clean take와 master 비교, 음악·효과 마스킹 및 발음 판단 | take 정상이라면 A09 envelope/mix만; 음질/원문/전편 loudness 재계측 |
| 감정/서사 몰입 저하 | 독립 전편 감상 및 대상 관객, 원고/연기/편집 경쟁 가설 | 고정 baseline 대비 한 요소 대조, 창작 의도 변경은 승인; 단일 점수/이탈로 원인 확정 금지 |

위 표는 조건부 repair 정책이며 실제 해당 영상의 결함 판정이 아니다. RepairProposal에 immutable baseline, 최소 변경 revision, 목표·고정 검증 계약, dependency closure, expected effect, attempt/budget cap, rollback, approval refs 명시. 실행 오류 retry와 의미 개선 attempt 분리. 새 결과는 동일한 사전 고정 조건에서 필요한 기술/독립 의미/인접 경계 및 상위 전편을 재평가한다. 독립 증거를 갖춘 목표 달성 및 강점 비열화가 없으면 baseline 교체 금지. 정체 시 대안 또는 HOLD, 무한 자동 재생성 금지. 변경되지 않은 artifact 보존; 해당 효과 범위가 바뀐 기존 evaluation evidence는 stale. 전편 재검수·최종 mux와 모든 장면 재생성은 구분.

### 인수 범위 및 다음 작업

현재는 실제 기존 코드·실물 원장·격리 기술 반례를 요구와 연결한 설계 검토만 수행. 새로운 전문가/독립 모델/관객/전편 실제 평가/repair uplift NOT_RUN. A15의 평가기별 qualification 및 D3 gate가 없으면 전문 자동 승격 금지. A11/A15 NOT_QUALIFIED, 전체 설계/코딩 동결 유지. 다음은 A12~A14 및 D0~D5 통합 원장에 이번 실제 설치·native API·음향 근거 및 여전히 열린 독립 평가/시장/실행 조건을 대조해 우선순위를 재설정. 기존 Deno/FFmpeg 엔진 반복 조사와 동일 예시 작품 제작은 제외.

## 1. 실제 현재 구현 및 기존 설계
- src/core/quality_contract.py blob 6b88cb3ef1465025e085ea6a4056b56f9def81c9: immutable MetricTarget/QualityContract/EvidenceBinding/QualityEvidence 및 evidence_issues. 선언된 정수 metric/check, 계약과 artifact/revision SHA 결속, 선언 producer/evaluator ID 구분. 함수 docstring이 명시하듯 빈 tuple은 승격/독립 심사/콘텐츠 PASS 아님.
- src/studio/web.py blob c3f6002887235c9661f84f024a012cc12daa7c49 L214~221: 실제 render receipt와 media digest를 확인한 후 사용자 전달 raw review를 reviewer=human-relayed/status=UNADJUDICATED로 저장. 리뷰 작성자의 독립성, 관측 coverage, 전문 판단, 비교 조건/실험/통계 검증 구현으로 오인 금지. 기존 실제 원장과 보존 계약 재사용.
- [Q4 실증](Q4_A15_EVALUATOR_BOUNDARY_EVIDENCE_2026-11-24.md) blob d0efb0d5c76d008606b43ace9c071de2219281d6: 고정 24개 선언 evidence에 구조 오류 없음(14 REJECT/6 SUPPORTED/4 HOLD), 5 control mutation 감지. 실제 의미 평가자 오판률/독립 평가/승격 시험 아님. 새 Core 점수 검사를 강화하는 것만으로 작품성 평가 해결 불가.
- 통합 심사 blob f844c9ece7abfa0a1e9724f86a303e2b352a97d0, 관객 계약 9b60e874fd415c35bd3b0401be6dd3a065f9584e, 캐스케이드 d762ae7c6fdcf2d9069a0e3f6c7582ce64c59523, 압축 실물 fd7a03ecc7c5101a528c87da9c4711e49a53b49b: non-compensatory READY, 독립/보정/holdout, 관객 cohort, 기술·노출 원인 분리, 동일 조건 비교 이미 정의. 아래는 이를 실행 가능한 전문 평가 논리로 구체화하는 설계이며 중복 게이트나 현재 제품 구현 완료가 아님. repo-wide audit 아님.

## 2. 공식/원저자 기반과 관측 범위
1. [ITU-T P.910 2023 공식 요약](https://www.itu.int/dms_pubrec/itu-t/rec/p/T-REC-P.910-202310-I%21%21SUM-HTM-E.htm): 단방향 영상/음성/시청각 주관 품질 평가. 2026-07 판본 [공식 레코드](https://www.itu.int/rec/T-REC-P.910-202607-P)는 TIES 제한. 2023 판의 stimulus 순서 무작위화 검색 본문만 확인, PDF 직접 분석 없음. 시험 환경·제시 순서·평가 척도 통제 원리 후보. 최신 원문/적용 범위 확보 후 protocol 고정; 영화 서사/흥행 전체를 P.910 인증으로 판단하지 않음.
2. Busselle & Bilandzic (2009) [Measuring Narrative Engagement](https://doi.org/10.1080/15213260903287259): 공개 초록에서 narrative understanding, attentional focus, emotional engagement, narrative presence의 네 차원과 영화/TV 표본 기반 구성 타당성 연구 확인. 원문 직접 요청 403. 2026 [후속 메타분석](https://doi.org/10.1080/15213269.2026.2705870) 검색 초록도 차원별 관계를 연구. 설문 문항의 원문 이용권/한국어 번안·측정 불변성/무협·숏폼 표본 재보정 전 validated scale 또는 보편 기준이라고 주장 금지. 네 차원은 독립 작품 평가 설계의 개념 기반, 사용자 재미/선호·지불의사와 별개.
3. Microsoft Research [Pre-Experiment](https://www.microsoft.com/en-us/research/articles/patterns-of-trustworthy-experimentation-pre-experiment-stage/) 2020-07-31 및 [During-Experiment](https://www.microsoft.com/en-us/research/articles/patterns-of-trustworthy-experimentation-during-experiment-stage/) 2021-01-25 직접 HTML 열람: 반증 가능한 가설, randomization unit, power, data quality/overall objective/diagnostic/guardrail 구분, sample ratio mismatch(SRM), 사전 종료 조건·중간 관측 다중검정, 세그먼트·novelty effect. 제품 A/B 원칙을 관객 비교에 적용하되 회사 수치/기간/정책 그대로 강제하지 않음.
4. [YouTube Analytics metrics](https://developers.google.com/youtube/analytics/metrics?hl=ko) 직접 열람: audienceWatchRatio는 구간 시청 횟수/전체 조회수, 반복 시청으로 1 초과 가능. elapsedVideoTimeRatio는 영상 상대 시간. [dimensions](https://developers.google.com/youtube/analytics/dimensions), [content owner reports](https://developers.google.com/youtube/analytics/content_owner_reports) 검색 확인. 비슷한 길이 영상과의 relativeRetentionPerformance는 동일 장르·노출·예산을 통제한 경쟁군 아님. 한국어 metrics 페이지의 0/1 설명 문구 중 0 쪽이 1과 동일하게 표시된 이상 관측; 해당 endpoint 의미/locale/version은 실제 사용 전 영어 원문·스키마 대조, 이번 설계에서 그 문구로 우열 확정하지 않음.
5. 위 원저자 기술은 개별 비교 방법의 근거이지 모든 창작의 최고 품질 보증 아님. 전문 감독/편집자와 목표 독자/시청자, 강한 전문 제작 baseline 및 현재 승인된 champion의 실제 실물 비교가 필수. 독립 접근/권리/비용/실제 관객 표본 현재 미확보.

## 3. GAP 및 도입 결정
| ID | 기존 구현/계약의 미구현 상세 | 개선 선택 |
|---|---|---|
| I111 | 구조 검사 및 raw review, 실제 관측·인증 분리 미실증 | Compose revision/coverage/독립 증거/판정 레이어, Q4 반례 유지 |
| I112 | 개별 전문 성공과 전체 작품 품질의 연결 상세 부족 | Compose 전편 1차 감상 및 2차 장면 진단, A04~A10 evidence graph; Adopt P.910/NES 방법 후보 |
| I113 | 동일 조건 관객 비교 원칙, 할당/표본/지표/결측 처리 미정 | Adopt 통제 실험·무작위화·통계 방법; Compose AudienceStudyPlan |
| I114 | 공개 retention와 실제 작품성/인과 구분 계약, 지표별 분석 상세 부족 | Adopt 공식 허용 analytics, Compose definition/denominator/cohort/time binding, 관측 vs 인과 분리 |
| I115 | 결함 위치와 책임 capability 연결은 있으나 원인 검증 절차 미실증 | Compose competing hypotheses, 한 요소 대조/경계 영향, 독립 재검증 후 targeted repair |
| I116 | 작품 개선과 스킬 진화 원칙, 다작품 일반화/실패 비용 검증 미실증 | Compose separate project/skill experiments, sealed holdout 및 비열화·비용 margin |

Build는 전문 통합 평가 계획/원인 분석 및 도구 adapter·증거 결속의 남은 차이만. 검증된 통계·영상 측정 library를 재사용하고 새 범용 통계 엔진·평가 플랫폼·마케팅 크롤러 자체 구현 근거 없음. 신규 모델·평가기 채택 확정 아님.

## 4. 목표 통합 평가 로직
### 4.1 평가 입력 및 증거 계약
IntegratedReviewPlan: 승인된 brief/관객/장르/매체/분량/채널, 비교 목적, 전편 artifact SHA-256, script/edit/audio/subtitle/asset/timeline revision 및 child evidence, applicable requirement refs, risk/rights, evaluator qualification, primary endpoint/guardrails, comparison budget, 판정 기준·허용 불확실성. A07~A10 결과 계약을 pin. 독립 근거 없는 PASS 금지.
관측 record: artifact/contract digest, source role, 실제 관측 modality(영상/음성/텍스트), coverage/time ranges/결측, evaluator identity & verified qualification/relationship, model/prompt/version/실제 입력 및 raw response, timestamp & provenance, method/metric/unit/denominator/uncertainty, evidence digest, finding severity. 모델이 전체 영상을 보지 않았으면 전편 감상 검증으로 분류 금지. hash 존재와 진실성/권리/서명 확인은 별개. A15 평가기 보정과 독립 검증 필요.

### 4.2 전편 심사 4개 증거 계층
T: 객관 필수 검사. 권리·원고/승인·asset/track/시간·영상/음성 decode·기술 납품·중대한 정합 오류. 모든 적용 요구와 현재 child 증거 valid; 알려진 필수 중대 오류 0, 미평가 필수 항목은 HOLD. 관객 반응/점수로 상쇄 불가.
E: 전문 독립 감상. 최초에는 최종 작품을 정상 관람 속도로 전체 감상(중간 검사 정보·다른 평가·제작사 라벨 차단 가능한 범위). 서사 인과/인물 목표와 변화/장르·감정/시각·음향의 역할/리듬·전환/연속성/결말, 모순/공감·가독성. 2차는 shot/track/구간별 진단 및 A04~A10 child와 교차 검증. 한 기술의 미학적 우수성/높은 점수 평균은 통합 성공 증거 아님. 심사 불일치 및 전문성 부족은 독립 adjudication/HOLD, 제작자 자체 평가는 진단용.
A: 목표 관객 반응. 서사 이해(실제 질문의 정답·자유회상), 집중, 감정 및 존재감, 선호/재시청·다음 회차 자발적 선택. 네 몰입 차원과 실제 행동 분리, 강제 완주 환경에서 시장 완주율 추정 금지. 설문 문항/응답척도/표본 적합성 보정 전 점수 합격선 발명 금지. 매체에 따라 소설/영상/무대 등 별도 scale; 공통 개념을 같은 수치로 합산하지 않는다.
M: 공개 관측 및 사업 평가. 권리·정책·별도 게시 승인 시에만 A12/시장 계약에 연결. 노출, 진입, 실제 시청/완주·재시청, 반응, 후속 선택, 수익·완전 원가 분리. 공개 관측은 통제 실험과 다름. 시청시간 최적화가 서사·인권·정책·사용자 의도·비용을 훼손하지 않도록 guardrails.
필수 적용 계층과 기존 G1~G4를 충족해야 해당 작품 범위 승인. D0~D5 코딩 승인은 별도. T/E/A/M을 모두 단일 숫자로 평균내지 않음. 필수 M이 요구되지 않는 비공개 연구 등은 적용성 계약에 명시, 미실측 시장 수익을 통과 처리하지 않음.

### 4.3 비교 실험 계약
- 연구 질문별 단위: 기술 원인 시험(동일 작품에서 한 요소 교체), 전체 제작 파이프라인 비교(동일 brief/장르/분량/예산·자원/권리, 여러 독립 작품), 실제 시장 공개 관측(노출/추천/채널 confounding). 같은 감독·모델 출력만 반복하면 독립 작품 수로 세지 않음.
- AudienceStudyPlan: 대상 모집단, inclusion/exclusion 기준 및 동의/AI 고지/이용권, 최소 표본 계산(기존 실제 분산·효과 크기·검정력·허용 오차), unit=참가자 또는 적합한 cluster, assignment seed/variant hashes/대조군 및 stratification, 검정 계획/중도 종료 규칙/기간·예산 사전 pin. baseline 없는 경우 pilot로 분산/척도 보정; pilot를 확증 holdout으로 재사용 금지. 실제 평가 없는 고정 n/합격 확률 임의 선언 금지.
- 최초 감상은 동일 환경/화면·음량·재생 조건 및 가능하면 조건 라벨을 가린 between-subject randomization. paired 비교가 필요한 경우 AB/BA counterbalance, 순서·학습/스포일러/피로 기록, 동일 원고 재감상으로 자연 첫 시청 효과 단정 금지. 동일 참가자/작품의 상관 고려. 모집/AI 고지 의무 우선, blind 불가능한 부분 기록.
- 주 지표(primary)와 필수 비열화 guardrail, 진단 지표, 데이터 품질 지표 분리. 실제 할당·노출/제시 성공·중도 이탈/응답 누락/중복/순서, SRM/집계 오류 확인. 할당 기준 분석(ITT 가능한 범위), 완주자만 사후 선택 금지, 결측 및 비응답 sensitivity. 의미 차이의 추정치/불확실성(적절한 confidence interval 및 clustered/paired 분석) 보고. 다중 비교/반복 중간 관측 사전 처리, p값 단독/유의하지 않음=동등함 금지. 보수적 효과 경계와 사전 margin/비열화 충족 시에만 우위 판정. 별도 신규 표본과 실제 작품에서 재현.
- 비용·시간·실패·사람 조작은 모든 attempt 포함. equal-budget quality와 equal-quality cost를 별도 비교, 실패한 후보를 빼고 최고 결과만 비교 금지. 사용자의 사업 기준 및 실제 승인 예산 내에서만 실행. 데이터 최소 수집·가명화·보존 기간/권한, 무단 추적·모집·공개·외부 전송 금지.

### 4.4 관객 반응 → 원인 진단 → 개선
PublicObservation에는 channel/report/video ID, 게시 당시 artifact digest/timeline revision, 관측 기간 및 data version, metric 정의·분모/집계·privacy/권한, traffic/cohort/노출·포맷/길이, missing/suppressed 상태. 시간 bucket을 영상 실제 길이→rational time range→shot/track 후보에 연결하며 단일 정확 frame 사건을 관측한 듯 표현 금지. audienceWatchRatio=1.2 같은 값은 재시청 포함 횟수 비율이지 120% 사람이 완주한 결과 아님. 소표본/노출 부족은 INSUFFICIENT_EXPOSURE; 플랫폼 변동/썸네일/노출 효과 및 제목·내용 불일치 구분.
Finding: 현상, 구간, 직접 근거, severity, 관객 또는 전문가 scope, competing causes(원고·연출·자산·동작·음성·음향·편집·유통/기기), 대안과 반증 방법, 예상 영향·비용·불확실성. 예: 대화 구간 이탈은 발음/배경음 masking/긴 대사/서사 이해/버퍼링·외부 추천 등 여러 가능성. 먼저 독립 청취·원문·재생 증거 확인, 같은 영상·대사에서 믹스만 변경한 비교 등 단일 변수 대조로 가설 검증; 다른 요소까지 변경됐다면 인과 확정 금지. 단순 댓글/retention dip만으로 A08/A09 실패 판정 금지.
RepairProposal은 affected capability 및 revision/time span/의존 closure, 기존 좋은 baseline 보호, 구체 수정 가설 및 고정 재검증 계약, attempt/budget cap, rollback. 원고/편집 시간 변경 시 관련 음성·자막/음악·연속성 등 A07~A10 invalidation. 같은 구간과 전편 통합 재평가, unrelated sibling 보존. 효과 불명은 INCONCLUSIVE/UNKNOWN, 무한 재시도 금지. 성공 작품의 특정 수정과 전역 skill promotion은 별개, 독립 작품/관객 holdout 및 회귀/비용·비열화 입증 전 전역 적용 금지.

## 5. 5축 및 검증 경계
Core: generic time/revision/metric/evidence/dependency 및 구조 검사 primitive, 영화 서사/통계 공급자/YouTube 의미 구현 금지. Bridge: feature-blind 실행/관측 전달. Add-on: 전문 감상·관객 실험·통계/채널 해석·결함 원인 분석/repair proposal, private state. 다른 Add-on 직접 호출 및 자기 결과 최종 승인 금지. JSON: 증거·protocol·assignments·권한·집계/원본 허용 범위·revision/판정 이력 persistence-only. Central Manager: capability/승인/권한/예산/lease, evidence authentication 및 scope/freshness/독립성 정책, generic experiment orchestration·gate/promotion·dependency invalidation. 분야별 취향이나 채널-specific 분기 없음. 기존 M-VML/리뷰 원본 및 Core 구조 검사 보존.
반증 후보: 다른 문자열 reviewer ID를 독립성 증거로 인정; 고점수 평균으로 필수 음성 결함 상쇄; 4차원 설문을 한국어 검증 척도라고 주장; 무음 animatic로 음향 평가; 완주자 응답만 분석; SRM 무시; 중간 p값이 낮아질 때 종료; 한 작품 반복을 독립 n으로 계산; retention>1을 완주율; 이탈 지점을 특정 원인 확정; 공개 조회수와 controlled uplift 혼용; 성공 수정 1건으로 스킬 자동 변경. 기존 Q4 고정 집합은 변경하지 않고 A11/A15 추가 후보로 유지.
판정: I111~I116 설계 개선 및 작성자 논리 검토만. 실제 전편 완성품/독립 전문가·관객/통제 실험/공개 관측·수익/평가 보정 및 D1/D3/D4/D5 NOT_RUN 또는 HOLD. A11 NOT_QUALIFIED, 기존 게이트 불변. 다음 A12 공개·확장·수익 로직과 정책/정산·원가·scale/stop 비교 및 설계. 게시/모집/지출/실행 권한 부여 아님. 전체 코드 동결 유지.
