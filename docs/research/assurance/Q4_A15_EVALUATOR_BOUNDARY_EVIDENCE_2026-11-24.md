# Q4 / A15 평가기 타당성 — 기존 구조 검사기의 의미 검증 경계 실증

2026-11-24 KST | 기준 main 4790a84fba88787ed91752db3333d579f1bf85c4 | PARTIAL_EVALUATOR_BOUNDARY_EVIDENCE / A15 NOT_QUALIFIED

상위 [심사 계약](../../MURIM_ASSURANCE_AND_COMMITTED_EXECUTION_CONTRACT.md) 및 [A15](STAGE_ACCEPTANCE_REGISTER.md) 유지. 기존 Q1/Q2/Q3 근거 원장과 실제 module을 사용. 새 제품 코드/테스트 파일 없이 격리 환경에서 기존 함수 호출 및 원본 JSON 정적 검사. 독립 전문가·관객·다른 LLM의 실제 평가가 아님.

## 1. 시험 전 참조 집합 고정

참조 출처: [Q1](../market-library/Q1_A01_ACTUAL_EVIDENCE_2026-11-24.md) blob 79fd8a726c78dc714c73096d21a4cb577e3764ba; [Q2](../works-library/Q2_W009_SPRING_SOURCE_EVIDENCE_2026-11-24.md) blob 9f54791a662330a2591aa9fd0113fe127707fb63; [Q3](../technology-library/Q3_LTX25_OFFICIAL_GRAPH_EVIDENCE_2026-11-24.md) blob e8c0660b7c07fa6ad89b07d885c995456db37943. R01~R14는 기존 반례를 재표현, S01~S06 및 H01~H04는 연구자가 추가한 양성/경계 사례. REJECT=근거와 모순되거나 근거 범위를 넘어선 확정 주장; SUPPORTED=명시된 출처 범위에서 개별 진술 지지(생산 승인 아님); HOLD=질문에 답할 필수 자료 미확보. 기존 요구의 알려진 중대 반례 false accept 0 유지. 아래 데이터는 사전 고정된 진단 집합이며 독립 전문가 adjudication 및 봉인 holdout 아님. 동일 작성자/기존 공개 반례라는 누출 한계 때문에 일반화 성능 추정 금지.

실제 실행 전 /tmp 격리 디렉터리에 UTF-8 LF JSON 저장, SHA-256 7dc417cb7c394c176bb9fda2885ce0b7cae3eecb12ee8833ef63d1935ae3ef1d, 24 unique IDs, REJECT 14 / SUPPORTED 6 / HOLD 4 확인. 아래는 해당 파일의 정확한 JSON 데이터(종료 LF 포함). 출처 ID는 각 원장 내부 ID. 숫자/관측 진술은 해당 원장의 증거 범위를 따름.

```json
[
["R01","REJECT","E04","무산 펀딩의 표시 112000원을 실제 수취 매출로 인정"],
["R02","REJECT","E06","펀딩 135% 달성으로 순이익을 확정"],
["R03","REJECT","E02","2009~2020 모집 성공률 37.7%를 Murim 수익 성공확률로 적용"],
["R04","REJECT","E03","노동 기회비용 미포함과 1달러 불일치를 무시하고 완전 경제성을 확정"],
["R05","REJECT","B01/B02","삭제된 기상 장면이 최종 영상에 있다고 확인 주장"],
["R06","REJECT","B05","선정 쇼트 파일 20개를 편집 수정 20회로 해석"],
["R07","REJECT","B03","2분 편집 단축이 관객 만족도를 높였다고 실증 확정"],
["R08","REJECT","Q2 coverage","미수신 영상의 특정 장면 음향을 직접 관측했다고 주장"],
["R09","REJECT","G02","nested widget만으로 2차 sampler euler_ancestral 확정"],
["R10","REJECT","G03","README만으로 Union Control 단일 실행 단계 확정"],
["R11","REJECT","G01","공식 graph 24fps 5초 frame expression이 120을 산출한다고 주장"],
["R12","REJECT","G02","원본 음성 보존이 한국어 립싱크 정확성을 보장"],
["R13","REJECT","Q3 requirements","8GB 커뮤니티 주장으로 대상 장비 생산성 입증"],
["R14","REJECT","T002","코드 Apache-2.0이 모델 가중치에 자동 적용"],
["S01","SUPPORTED","E04","표시 모집액 112000원, 무산; 수취 미확인"],
["S02","SUPPORTED","E06","표시 달성률 135%, 펀딩 성공; 순이익 미확인"],
["S03","SUPPORTED","B02","원저자 기록상 기상 도입부 제작 전 삭제; 영상 직접 관측 아님"],
["S04","SUPPORTED","B05","제작 기록 검색 본문상 선별 쇼트 20개; 파일 직접 열람 아님"],
["S05","SUPPORTED","G02","상위 sampler_name euler가 내부 노드에 연결; 실제 렌더 미확인"],
["S06","SUPPORTED","G01","frame expression 계산 121; 실제 출력 probe 미실행"],
["H01","HOLD","E06","실제 수취 및 완전원가 기준 순이익은 얼마인가"],
["H02","HOLD","B03","편집 단축의 관객 만족도 효과는 얼마인가"],
["H03","HOLD","G02","한국어 대사 립싱크 실측 정확도는 얼마인가"],
["H04","HOLD","Q3 requirements","대상 8GB 환경에서 합격 영상당 전체 비용은 얼마인가"]
]
```

## 2. 기존 M1-A 모듈 실제 실행 (구조/의미 경계 시험)

원본 src/core/quality_contract.py blob 6b88cb3ef1465025e085ea6a4056b56f9def81c9를 원격 조회 후 격리 Linux Python 3.13.5 환경에 그대로 복사. git hash-object 결과 동일. fixture digest 재확인 후 기존 evidence_issues() 호출. 연구용 ephemeral fixture/harness만 사용, repo 제품 및 테스트 구현 변경 없음. 기존 tests/test_quality_contract.py blob bfc3e688b799be68d7ef993902995942b3c9a278 열람, 기존 27개 전체 회귀 재실행 안 함.

실험 목적: 거짓/미검증 보고서라도 올바른 구조·digest·서로 다른 선언 ID 및 좋은 자체 점수를 갖출 수 있음을 실제 기존 함수로 검증. 실험용 QualityContract version q4-research-only, MetricTarget declared_score (90,96,100), check declared_evidence_valid. 이 숫자는 구조 fixture이며 A15 실물 합격선 아님. 각 case claim UTF-8 bytes의 실제 SHA-256을 artifact에, claim/declared_score=100/declared_evidence_valid=true의 JSON bytes SHA-256을 report에 사용; task ID=case ID, revision r1, producer=producer, evaluator=declared_reviewer, contract.digest 결속. metrics=100, checks=True, unresolved_defects/unassessed 빈 tuple. 선언된 reviewer는 실제 독립 평가자가 아님. 고정 참조 label은 함수 입력 아님. 기존 함수에 필요한 형식은 충족; 평가자의 사실성을 검증하지 않음.

| 참조 의미 분류 | 표본 수 | 실제 구조 오류 없음 반환 |
|---|---:|---:|
| REJECT | 14 | 14 |
| SUPPORTED | 6 | 6 |
| HOLD | 4 | 4 |

실제 출력: STRUCTURAL_EMPTY_BY_REFERENCE {'REJECT': 14, 'SUPPORTED': 6, 'HOLD': 4}; 24개 모두 빈 tuple. 의미적 결함 검출 0/14. 빈 tuple을 자동 합격으로 오용한다는 반사실 조건에서는 14/14 known-invalid와 4/4 미확인 질문을 잘못 승격할 위험. 이는 실제 promotion 발생 또는 전문 평가자의 false accept 측정이 아니다. 함수 계약은 빈 결과가 승격/독립 평가/콘텐츠 PASS가 아니라고 명시하므로 PRODUCT_DEFECT로 분류하지 않는다. 의미 평가자로 오용하는 설계 가정은 AUTHORITY_DRIFT. 구조 검사 소유권 유지.

같은 마지막 fixture에서 단일 필드만 변형한 구조 대조군 5개 실제 결과:
- C01 binding.revision r2 → STALE_OR_MISMATCHED_BINDING
- C02 evaluator_id=producer → SELF_EVALUATION
- C03 declared_evidence_valid=False → CHECK_NOT_PASSED:declared_evidence_valid
- C04 unassessed=(actual_cost,) → UNASSESSED
- C05 declared_score=95 → BELOW_TARGET:declared_score
예상 오류 포함 5/5 실제 확인. 선언된 서로 다른 ID가 진정한 독립성이라는 증거는 아님. 전체 Core 회귀/통합/실제 Windows 미실행.

## 3. 원본 객관 검증 4건 실제 실행

GitHub 원본 3개 JSON blob 및 CHANGELOG blob을 Q3와 대조 후 JSON.parse 및 read-only link/node inspection을 수행. 원본 동일성 확인, 사용자 환경/ComfyUI 실행은 아님.

| 검증 | 실행 관측 | 참조 연결 |
|---|---|---|
| V01 | G01 node 5561 expression 1 + floor(a*b/8)*8, top fps 24 duration 5 → 121 | R11 / S06 |
| V02 | G02 top 5517 sampler euler, inner 4976 euler_ancestral, 연결 13690 origin -10 → target 4976 | R09 / S05 |
| V03 | G03 top 5517 mode 0, samples link 13755, subgraph LTXVLatentUpsampler 및 SamplerCustomAdvanced 존재 | R10; graph 존재가 실제 runtime 성공은 아님 |
| V04 | T002 1.6.0 changelog 코드 Apache 2.0 및 LTX-2.5 모델 LTX-2.x Community License 별개 표기 | R14; 실제 권리 자격 판정 아님 |

4/4 원본 관측 재확인. 동일 연구 세션의 객관적 사실 검사이며 독립 평가자/holdout/전문 판정 성능 아님. 나머지 사례는 기존 Q1/Q2/Q3 원장 기반 참조이며 이번에 모든 외부 페이지 재열람/독립 검증했다고 주장하지 않음.

## 4. 설계 반증 및 실제 다음 조치

1. 구조 검사(Core)와 출처/관측/권리 검증 및 분야 전문 평가(Add-on), 승격/인증/정책(Central Manager), routing(Bridge), 증거 저장(JSON)을 분리. 구조 정상은 평가 시작의 조건일 뿐. 공개 원본의 객관적 확인 가능한 사실부터 별도 검증; 누락/미관측은 HOLD, 근거 위조는 REJECT. 모델 판단으로 사실을 덮지 않음. 공통 축에 도메인별 조건 추가 금지.
2. 평가기의 다음 시험은 실제 독립 모델 또는 전문가, 별도 adjudicator가 확보되면 현재 24건 진단 집합을 개발용으로만 사용. 미공개 독립 참조/경계/위조 사례와 holdout, 출처의 판본/근거 위치 검증, 동일 입력·비용 조건의 강한 단일 평가 기준 대비 비교. 응답 모델/버전/프롬프트/원문/시간/비용/독립성 기록. 참조 답안은 독립 시험 입력에서 제거; 실제 전문가 보정 및 허용 오차/표본/최소 효과를 평가 전 확정. 알려진 중요 결함 false accept 관측 0 유지. 과잉 탈락/HOLD의 비용, 실제 선별·개선 우위 및 재현성 별도. 24개 표본으로 통계 일반화/미탐률 추정 금지.
3. 독립 LLM/전문가 접근 미확보: 현재 도구 목록에 evaluator/독립 model inference 직접 실행 수단 없음; Q2 plugin 검색에서 Gemini 호출 기능 미발견. ENVIRONMENT_ISSUE. 외부 모델 실제 호출·전문 인간/관객 평가·실제 선별 효과/불확실성 시험 NOT_RUN. 반복 연결 시도 대신 다음 A04 전문 집필의 상세 생산 설계와 기존 도구로 가능한 실제 독창적 비교 원고 사전 실험(강한 baseline/기준 선고정, 지식 pack은 미검증 후보, 독립 평가 미확보 시 HOLD)을 진행한다. A15 재개 조건은 독립 평가·참조/실물 접근 및 별도 보정 증거. Q1~Q3 미달도 유지.

결론: 구조 검사기 오용 반증 및 객관적 원본 검사 경계 완료. A15 NOT_QUALIFIED; D3/D4 미통과, 전체 15개 공정 NOT_QUALIFIED 유지. 제품 소스/테스트/UI/DB/Windows 변경 없음, 유료/게시/외부 전송 없음. DESIGN_HOLD / PRODUCT_CODING_FROZEN / REMEDIATION_REQUIRED.
