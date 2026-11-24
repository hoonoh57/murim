# Murim 다층 부모-자식 캐스케이딩 품질 계약 v1.0

2026-11-24 KST | 사용자 확정 방향 | 설계 계약, 실행 엔진 미구현
권위: AGENTS.md 및 MURIM_FIVE_AXIS_ARCHITECTURE.md. 기존 4-GATE 및 사료/권리/인간 승인·권한·원본 보호 유지.
## 1. 두 가지 독립 실행 루프
**개발 LLM 루프**: 권위/HEAD/원본 복구 → 최신 업계 기술·기존 구현 조사 → 검증 목표 설정 → 경계별 코드/테스트/실행 → 실패 원인 분류 및 수정 → 국소 재검증 → 상위 통합·회귀·경계감사 → 실제 제품 수용. 기술 선택, 설계, 코드, 테스트, 자동 오류 분석 및 복구는 개발 LLM이 맡고 사용자에게 매 단계 계속할지, 모델/라이브러리를 고를지, 테스트를 해석할지 질문하지 않는다. 권한 내 도구로 가능한 모든 일을 현재 작업에서 연속 처리한다. 실제 로컬 UI/영상 확인이 필요한 수용 경계에서만 사용자 관측을 요청하는 것이 정상 운영 목표. 미연결 로컬 실행/진단은 NOT_CONNECTED, 권한/환경 장애는 별도 기록하며 승인되지 않은 지출·외부 전송·설치·원본 변경을 강행하지 않는다. 도구/세션 종료 후 백그라운드 개발이 진행된다고 주장 금지. 이전 검증이 실패하면 원인을 해결하고 다음 경계를 통과시키며 assertion 약화 금지.
**제품 제작 루프**: 사용자 자연어 목표 → 전문 제작팀 자동 분해/계획/제작/평가/보완 → 품질 초과 달성된 자식 산출물 승격 → 부모 통합 평가 → 상위 전달. 사용자에게 제작 기술이나 중간 실패 처리를 맡기지 않는다. 기존 작품 G1/G2/G3/G4의 인간 감수·승인과 게시/권리/비용 등 별도 권한 계약은 개발 중간 승인과 구분하며 유지한다. 인간에게 제시하는 것은 검증된 실제 원고/후보/영상 및 중요한 감독 결정뿐이다.

## 2. 다층 부모-자식 모델 (업무 계층 + 의존 DAG)
부모는 목적, 입력 revision, 산출물 schema, 품질 rubric, 필수 검증, 최소 기준과 그 이상의 목표 품질, 예산·기간·자원·권한 범위를 선언한다. 자식은 스스로 세부 작업 부모가 될 수 있다. 계층의 깊이와 종류는 데이터/등록 capability로 확장하고 이름/장르/공급자를 Core에 고정하지 않는다. 동일 자산을 여러 부모가 사용할 수 있으므로 hierarchy와 cross-stage dependency DAG를 분리한다. 의존성 순환은 거부하고 개선 반복은 새 attempt/revision으로 기록한다.
예시: 작품→시퀀스→씬→쇼트→참조 이미지/동작/영상/음성/자막. 전문 업무 계층은 조사→시나리오/스토리보드→캐스팅→제작→편집으로 별도 composition 가능. 이는 예시이며 폐쇄 enum이나 고정된 부모 수 아님. 부모는 자식 Add-on을 직접 호출하지 않고 Manager에 capability 작업을 요청한다.
계약 필드(논리 예시, 스키마 확정은 M1): root_run_id, task_id, parent_task_id, dependency_ids, project_revision, input_artifact_refs+hashes, capability/schema/profile/version, required_checks, min_thresholds, target_thresholds/comparator, budget/deadline/depth/attempt limits, policy_revision, approval_refs, evaluator_capabilities, evidence requirements. 자식에게 부모보다 넓은 권한/예산을 위임하지 못한다. parent input snapshot에 선택된 하위 contract/evaluator/engine 및 rubric 버전 pin.

## 3. 공통 품질 루프
PLAN → EXECUTE → TECHNICAL_VERIFY → INDEPENDENT_EVALUATE → IMPROVE/REPLAN → PROMOTE 또는 HOLD. 모든 상태/전이/attempt는 불변 이력으로 기록. 기술 오류와 의미 품질 불합격은 별개. 작업 생성기와 최종 평가의 독립성/관측 증거가 확인되지 않으면 NOT_EVALUATED. 부모에는 통과한 산출물+증거 묶음만 전달한다.
승격 조건: 필수 자식 모두 현재 입력/contract 버전에서 승격, 모든 hard checks PASS, 미평가/미해결 결함 0, 차원별 minimum 및 사전에 정한 target(초과 margin/comparator 포함) 충족, 실제 산출물/권리/승인 검증, 부모 자신의 통합 rubric PASS. 평균 점수가 높아도 필수 검증 FAIL을 상쇄하지 않는다. 기존 95/100·각 9/10 등 G1/G2 기준은 하한으로 유지하며 장르/작업별 독립 검증 목표와 초과 margin을 사전에 수립한다. 목표 수치를 임의로 발명하거나 실패 후 기준을 낮추지 않는다. 최대값이 있는 점수에서 불가능한 threshold를 설정하지 않는다. 콘텐츠의 최고 품질 자체는 수학적으로 보장할 수 없으며 검증 증거가 있는 비교 후보 중 목표 충족을 증명한다.
생성→평가→결함 분류→원인 위치와 수정 가설→해당 자식만 새 revision으로 재실행→재평가. 재시도는 동일 작업의 일시 장애 복구, 개선은 새로운 입력/전략/후보를 가진 의미 있는 새 attempt. 동일 실패 무작정 반복, 점수만 높이기, critique 원문/증거 덮어쓰기 금지. 이전 우수 후보는 보존하고 비교 검증 없이 교체하지 않는다.
부모 통합 평가에서 캐릭터/연속성/서사/음향 시간 정합 실패가 드러나면 실제 원인 자식으로 결함을 반환한다. 의존 DAG로 영향 받은 조상/후속 결과만 STALE/HOLD, 무관한 성공 작업 재제작 금지. 부모의 이전 승인/기존 결과물과 증거 보존. 승인된 원고의 구조 변경은 새 사전 승인 필요. 새 revision에 대한 평가가 구 revision 승인으로 대체될 수 없음.
품질 목표까지 지속 개선하되 한 실행에서 무한 루프/무제한 비용 금지. 진척 없는 동일 결함, 품질 악화, 최대 깊이/기간/attempt/예산/자원 한계, unavailable/권리/승인 제약에 도달하면 원인 분석→승인된 대체 capability/전략 탐색→가능한 경우 재계획. 범위 내 대안이 없으면 HOLD+재현/원인/최선 후보 기록, 영향 없는 다른 작업 진행. 미달 결과 강제 GO/부모 승격 금지. 부모의 합산 예산에 모든 하위 attempt와 동시 실행 lease가 포함되어야 한다.

## 4. 5축 소유권
- Core: generic Task/Dependency/Revision/Evidence/QualityContract 및 순수 검증·전이 primitive. 도메인·모델·실행기 import 없음. 품질판정 권한은 Core가 자체 행사하지 않음.
- Bridge: 동일 작업 envelope 및 결과/이벤트, 실행 격리/취소/재연결. 품질/재시도/자식 선택 판단 없음.
- Add-on: 전문 계획, 생성, 평가, 결함 분석/수정 제안, 고유 품질 근거. 다른 Add-on 직접 호출 금지. 자신의 결과를 최종 승인할 수 없음.
- JSON/Persistence: pinned contract, task graph, attempt, immutable artifact refs/hash, verdict/evidence, provenance, checkpoint/event/승인, CAS. 실행/판단 없음.
- Central Manager: 부모-자식 orchestration, 의존 DAG, capability/평가기 선택, 공용 retry/replan/promotion/invalidation, budget/lease, authority/gate, aggregate evidence/diagnostic. 전문 품질 검사 직접 구현 금지. UI는 동일 상태의 소비자. 외부 workflow runtime을 채택해도 Murim canonical 상태 및 승인 권위를 대체하지 않으며 해당 실행 Adapter/Manager 공용 서비스 뒤로 격리한다.

### 4.1 작품과 전문 스킬의 이중 개선

작품 캐스케이드에서 축적된 결함은 [장기 경쟁우위 시방서](MURIM_COMPETITIVE_EVOLUTION_CONTRACT.md)에 따른 별도 스킬 후보 개선 근거가 된다. 프로젝트 승인과 전역 스킬 채택을 분리하고, 격리 비교/holdout/회귀를 통과한 버전만 적용한다. 실행 중 계약 및 스킬 버전 고정, 기존 결과물 보존. 실패 시 champion 유지 또는 중대 결함 격리. 전문 최적화·평가 Add-on과 공통 Manager orchestration 분리.

## 5. 재사용할 기존 실행 기술 조사
- Temporal Child Workflows: 다층 실행, 독립 history/lifecycle, 부모 종료/취소 정책. https://docs.temporal.io/child-workflows
- Temporal durable execution 및 retry pattern: 재시작/실패 후 복구, 제한된 retry, 일시/비재시도 오류 분리. https://docs.temporal.io/durable-execution ; https://docs.temporal.io/design-patterns
- LangGraph: node/state/conditional transitions 및 subgraphs, 수정 루프와 checkpoint/interrupt 후보. https://docs.langchain.com/oss/javascript/langgraph/thinking-in-langgraph ; https://docs.langchain.com/oss/python/learn
- LangSmith 평가 방식: offline regression, online evaluation, composite metrics 참고. https://docs.langchain.com/langsmith/evaluation-types ; 외부 telemetry 전송을 기본 활성화하지 않는다.
문서 조사 완료, 라이선스/Windows 로컬 의존성·실제 실행/비용/격리/재현성 비교는 미실행. Temporal/LangGraph 도입 확정 아님. 기존 엔진을 채택/조합하고 Murim 고유 품질 계약만 별도 구현하는 방향. 일반 스케줄러/큐/재시도 시스템을 불필요하게 재발명하지 않는다.

## 6. 검증 인수 조건 (개발과 제품)
- 3단 이상 임의 깊이·동적 capability: 자식 FAIL/미평가/미해결 결함/증거 위조·누락/입력 해시 불일치 시 부모 승격 불가. 부모 통합 FAIL이면 대상 자식만 새 revision, 무관 자식 캐시 보존.
- 실패 후 실제 개선→목표 초과→독립 증거 검증→상위 자동 승격. 실패 후 목표 하향/동일 결과 반복/리밋 도달→HOLD, 무단 fallback 없음. 임의 깊이/순환/공유 DAG, stale result, 재시작·중복 callback, cancel/unknown, 총 예산/자원 소진 시험.
- 동일 capability A/B 교체 및 새로운 전문 평가 Add-on 등록 시 Core/Bridge/Manager/shell 소스 hash 불변. 0/100/300/500 등록 및 장애 격리 시방서 유지.
- 기본 UI는 자연어 목표, 실제 미리보기, 의미 있는 결과/감수 및 쉬운 HOLD 원인만. 기계검증 탭은 root/parent/child/job/attempt correlation, 기준/목표/실측/증거/결함/재작업/승격 근거/무효화 graph, 비용/GPU/실행 로그를 공통 형식으로 보여주고 승인된 read-only 개발 LLM 진단으로 직접 조회. 연결되지 않으면 NOT_CONNECTED.
- 개발 자체도 변경분 감사·국소 테스트·repo-wide 자동 검사·전체 준수·Windows 실행·실제 WYSIWYG·콘텐츠 품질을 독립 검증. 사용자에게 기술 결정을 넘기지 않으며 실제 UI 검토가 필요한 경계에서 구체적 관측 요청. mock/합성 fixture로 실제 작품 품질 PASS 선언 금지.

## 7. 현재 위치 및 다음 경계
M0 승인 우회 방지 코드 27f1b7df75f1 반영, focused regression 실제 실행 미확인. 현 세션 컨테이너 GitHub DNS 연결 불가, GitHub connector는 원격 CRUD만 제공; Windows 실행/진단 연결 미확인. 이 환경 제약은 제품 실패가 아니며, 사용자에게 지금 루틴 테스트 명령 실행을 요구하지 않는다. 가능한 검증 경로 우선 복구. 다음 M0 집중 회귀 및 잔여 경계 확인 후 M1의 generic cascade contract와 최소 착탈 slice를 함께 검증한다. 기존 제품 코드/원장/ComfyUI 변경 없음. 자동 개발/품질 엔진 구현 완료 아님. REMEDIATION_REQUIRED.
