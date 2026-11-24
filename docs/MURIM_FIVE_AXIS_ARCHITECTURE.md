# Murim 5축 개방형 제작 플랫폼 — 아키텍처 및 Add-on 개발 시방서 v1.0

2026-11-24 KST | 사용자 확정 설계 방향 | **설계 계약, 구현/전체 준수 미검증**
권위: AGENTS.md 최신 5축 계약. 기존 제작 품질 4-GATE와 Adopt → Compose → Build 원칙 유지.
이 문서는 모든 신규 기술 조사·채택·개발·교체의 공통 기준이다. 구체적인 RPC/패키지/저장소 구현 선택은 비교 실증으로 확정한다.

## 1. 최상위 목표와 불변조건

Murim은 특정 LLM, 이미지/영상 모델, 편집기, 장르에 종속되지 않는 제작 플랫폼이다. 수백 개 Add-on이 등록되어도 Core와 공통 UI/관리 기능은 정상 시작하고, 일부가 중단되거나 제거되어도 관련 작업만 영향을 받는다. 필요한 능력이 사라진 작업은 명확히 HOLD되며, 다른 프로젝트와 기존 결과 조회·편집은 계속된다. 모든 모델이 동시에 GPU에 올라가는 것을 의미하지 않는다.
새 공급자/장르/모델/워크플로/전문 기술은 기존 공개 계약을 만족하는 한 Add-on과 등록 정보만 추가한다. Core/Bridge/Manager/shell에 특정 이름, import, switch, if/else, 전용 화면, 예외 목록을 추가해야 한다면 설계 결함이다. 공용 primitive의 실제 부족은 둘 이상의 독립 기술 사례로 입증한 뒤 별도 버전 계약·회귀 검증을 거쳐 확장한다. Core의 불변화는 기능 추가마다 수정하지 않는 안정 계약을 의미하며 보안/일반 결함 수정이나 승인된 호환 확장까지 금지하지 않는다.
외부 제작 앱도 전체 도입을 전제로 하지 않고 공개 API/CLI/SDK, 워크플로, 스킬 등 검증된 범위를 Add-on 뒤에 캡슐화한다. 공급자 미지원 기능을 갖춘 것처럼 표시하지 않는다.

## 2. 정확히 다섯 책임 축

| 축 | 단일 소유권 | 금지 |
|---|---|---|
| Core | 공급자 무관 프로젝트/장면/쇼트/트랙/미디어 참조/합리수 시간축, immutable revision 및 dependency graph의 범용 primitive, 상태 전이·계약·검증 primitive | 모델/API/장르/개별 툴 import, 이름 분기, 네트워크 호출, 공급자 설정, 자동 제작 판단 |
| Bridge/Runtime | 유일한 통합 경계: discovery, manifest 검증, version handshake, lifecycle, 등록/해제, RPC/event routing, job 실행·취소 전달, timeout/heartbeat, 프로세스 격리 및 전송 오류 전달 | 기능 의미·모델 선택·품질 평가·정책 결정, 별도 프로젝트 SSOT |
| Add-on | 고유 전문 기능/스킬, 공급자 SDK·노드·workflow/프롬프트 변환, 고유 파라미터·private state, 기능별 입력/출력 검증·품질 신호·선택 UI 선언 | Core/Bridge/Manager에 feature-specific 추가, 다른 Add-on 직접 import/호출, canonical 프로젝트 파일 직접 수정, 공통 큐·GPU 자원·비용/재시도 정책 복제 |
| JSON/Persistence | schema version이 있는 데이터 저장, atomic commit/CAS/이력·복구, 프로젝트/선택/승인·실행 증거와 content-addressed media 참조, namespace별 private data 영속화 | 실행 스크립트·eval·판단·타이머, 인증 토큰 원문 저장, 독립 도메인 권한 결정 |
| Central Manager | 공통 서비스 및 전 제작 총괄: registry/catalog, capability resolution, 선택/정책 CRUD, DAG 계획·스케줄·자원 lease, 비용/권한/승인·무효화 결정, retry/중복 제거·cache 정책, 통합 프로젝트 CRUD·자산/이력·감사·관측, 공용 UI 서비스 | 공급자 SDK/모델 조건문, 전문 장르 판단/영상 렌더 구현, Bridge 우회, 두 번째 저장 SSOT |

Studio shell은 Central Manager의 소비 화면이다. 공통 레이아웃·목록·CRUD·타임라인·상태·설정 UI는 공용 책임이며 기능별 UI는 Add-on의 선언형 contribution을 읽어 표시한다. 화면이 기능 로직을 재구현하지 않는다. 정책과 상태의 의미는 각 책임 축에 남는다. 다섯 축은 논리 소유권이며 물리 프로세스 수와 동일할 필요 없다.
기존 REA의 Chart/거래/TR 세부 규칙은 Murim에 이식하지 않는다. 사용자가 명시한 5축 경계 원칙만 영상 제작 도메인에 적용한다.

## 3. 유일한 호출·데이터 흐름

UI/Director 소비자 → Central Manager(요청/선택/정책/권한) → Bridge(검증된 route/실행) → Add-on(전문 작업 및 승인된 외부 엔진) → Bridge(결과/이벤트) → Central Manager(검증·결과 커밋·후속 스케줄) → JSON/Persistence.
Core는 공유 계약과 일반 primitive를 제공한다. Manager는 Core 공개 계약으로 도메인 상태를 검사하고 Persistence 공개 API로 커밋한다. Bridge는 Core 계약 타입만 공유한다. Add-on의 공용 서비스 요청은 공식 Bridge service request를 통해 Manager에 위임하며 다른 Add-on을 직접 호출하지 않는다. 외부 SDK는 오직 해당 연동 Add-on 내부에서 호출한다(네트워크/비용/권한 정책 준수). UI에서 외부 모델 직접 호출 금지.
Manager의 registry는 등록된 능력과 선택 정책의 SSOT, Bridge의 runtime handle은 실제 프로세스 연결 상태이다. Registry 등록과 실행 가능/승인 상태는 구별한다. Manager가 스케줄·재시도·취소 정책을 결정하고 Bridge가 물리 실행/취소/통신을 수행한다. 의미적 실패를 Bridge가 자동 성공으로 바꾸지 않는다.
Writer/Director/Council 등 창작 AI도 Add-on이며, Central Manager는 총괄 실행·제작 계획 조율의 owner이다. 고유 창작 판단은 전문 Add-on에 위임한다. 감독 AI의 계획은 제안이지 권한이 아니다. Manager만 게이트/예산/외부전송을 확인해 실행을 허가한다.

## 4. Capability 중심 열린 선택

작업은 공급자명이 아니라 capability + schema version + requirements로 요청한다. 예: text.script.generate, storyboard.plan, image.reference.generate, video.image_to_video, video.motion_transfer, audio.tts, timeline.compose, quality.continuity.inspect. 이는 초기 예시로 폐쇄 enum이 아니다. 신규 능력은 namespaced capability 및 versioned schema 등록으로 발견된다. 기존 계약으로 의미를 표현할 수 없는 경우에만 일반 계약 확장을 별도 심사한다.
한 Add-on은 복수 capability, 한 capability는 여러 Add-on을 지원한다. 호환성은 입력/출력 schema, modality, 참조 개수·종류, 시간·해상도, 언어, 권한, 비용, 품질 실측, GPU/RAM 및 모델 버전으로 판정. 이름을 근거로 능력을 추정하지 않는다.
선택 순서: 사용자 강제 지정 또는 프로젝트 정책 → 호환/설치/health/권한/게이트/예산/자원 hard filter → 검증된 성능과 품질에 기반한 ranking/선택 → 선택 근거 기록. 허용된 대체 정책 안에서만 failover. 미검증 후보는 실험 전용, 승인 없이 production fallback 금지. 지정 provider 없음/불일치이면 CAPABILITY_UNAVAILABLE 또는 POLICY_BLOCKED. 다른 모델로 조용히 변경 금지.
실행 revision에는 Add-on ID/버전/digest, 엔진·모델·workflow 버전/해시, 설정/seed, 입력과 정책/승인 버전을 pin한다. 새 작업은 새 선택 사용 가능, 실행 중 작업은 기존 pin 유지 또는 명시 취소·새 작업으로 분리한다. 호환 공급자 교체가 결과 동일성을 보장하지 않는다.

## 5. 신규 Add-on 개발 시방서

### 5.1 배포 단위 및 manifest (논리 계약; 구현 파일 배치는 추후)
독립 package/process 또는 외부 서비스 adapter. Add-on 개발자가 다음 항목을 제공해야 등록 후보가 된다.
- id(고유 namespaced ID), version, supported_core_api, bridge_protocol, entrypoint/transport, package digest와 출처/라이선스.
- provides[]: capability id/version, input_schema/output_schema 참조, 해당 능력의 제한·특성·품질 증거 참조.
- requires[]: 필요한 capability/version; requires는 Manager가 해석하며 직접 import 금지. 순환/충돌은 등록 또는 activation 시 차단.
- settings_schema/defaults, private_state_schema/version, migration 계약, UI contribution schema(설정/작업/프리뷰/결과).
- permissions: 파일/자산 범위, local process/GPU, network destinations, external upload, secret references, 비용 및 부작용 유형. 권한 선언은 승인 자체가 아니다.
- resource_profile, health/probe, cancellation/idempotency 지원 여부, timeout/recovery 특성, model/workflow/dependency version constraints.
- fixture input/output, contract tests, failure tests, real-environment benchmark evidence. mock 결과는 명시한다.

JSON manifest는 선언 데이터만 저장한다. 임의 코드를 넣어 실행시키는 DSL 금지. 설치 discovery는 신뢰된 패키지 메타데이터를 열거하며 unknown package를 자동 실행하지 않는다. Python entry points, isolated worker/RPC, MCP, HTTP/CLI adapter는 비교 후 채택한다.

### 5.2 기능별 공통 메시지 계약
Request envelope: protocol_version, request_id, job_id, attempt_id, idempotency_key, project_id, project_revision, capability_id/version, selected_addon_id/version, input_schema_id, inputs(artifact refs), settings_revision, policy_revision, approval_refs, resource_lease_ref, deadline.
Response/event: correlation IDs, sequence, status, progress(알 수 없으면 unknown), output_schema_id, artifact_refs/hash/media metadata, warnings, error_code/category, provider_job_ref, timings/cost/resource usage, provenance, evidence refs.
비동기 submit/status/events/cancel/reconcile를 기본으로 한다. 즉시 완료 작업도 동일 job envelope로 기록할 수 있다. 중복 전송, 취소 경쟁, stale result, 재시작을 처리한다. 공급자 고유 필드는 namespaced extension에 보존하고 필수 공통 필드를 숨기지 않는다. 비밀은 단기 scoped secret reference로 제공하고 원문을 응답·로그·GitHub에 기록하지 않는다.
상태 예: ACCEPTED → QUEUED → RUNNING → SUCCEEDED/FAILED/CANCELLED; UNCERTAIN는 외부 실행/취소 결과 미확정 상태. UNKNOWN 결과에서 중복 유료 호출 금지, 먼저 provider reconciliation. SUCCEEDED는 기술 실행 완료이지 품질 승인 아님. 기술 오류와 콘텐츠 평가 실패 분리.

### 5.3 착탈 수명주기
DISCOVERED → VALIDATED → REGISTERED_DISABLED → ACTIVATING → READY → DRAINING → DISABLED/DETACHED; QUARANTINED는 계약/보안/장애 격리 상태.
등록/설치/활성/프로젝트 선택/실행은 별도 CRUD. 설치되지 않은 모듈 import 때문에 호스트 부팅 실패 금지. 활성 전 protocol, 권한, dependency, schema, health 검증; 실패한 후보만 격리한다. CPU/GPU 작업자는 필요할 때 lazy load한다.
해제 시 새 작업 차단, 실행 중 작업 drain 또는 승인된 취소, provider 상태/lease 확인, 이벤트 구독·핸들 정리. in-flight 작업을 버려 성공으로 기록하지 않는다. 자산·과거 이력·private data·설정은 기본 보존. 해당 기능이 없는 프로젝트는 필요한 단계만 HOLD; 저장 데이터는 읽을 수 있어야 한다. 재장착 시 호환 schema 또는 사전검증된 migration으로 복구한다. rollback 가능한 버전과 원본 데이터 보존.
Python 모듈 unload만으로 native GPU 메모리/충돌 격리를 보장하지 않는다. 신뢰되지 않는 공급자, heavy model, native 라이브러리는 별도 process/venv 또는 서비스 격리 검토. 프로세스 격리는 그 자체로 권한 sandbox가 아니므로 파일/네트워크/비밀 접근 제어 별도 검증. 강제 종료 및 공유 GPU 서버 큐 취소는 허용 범위 내에서만.

## 6. 영속화 및 공통 제작 정보

Canonical project aggregate의 JSON revision이 프로젝트/씬/쇼트/트랙/자산 참조/승인/선택의 목표 SSOT. 이미지/영상/WAV/대형 원문은 파일로 보존하고 id, SHA-256, media type, 길이/시간축, 출처/권리, 생성 provenance를 기록한다. 파일 경로는 승인 workspace 내 관리 경로 또는 검증된 외부 asset ref. 프로젝트 수정은 Manager → persistence CAS·atomic revision commit, concurrent conflict는 명시 반환. 데이터 저장 계층은 기능 판단하지 않는다. audit/recovery/backup 및 schema migration은 원본 보존과 재현성을 만족해야 한다.
기존 M-VML XML, editorial 원장, director JSON, 원본 미디어는 즉시 변환/삭제하지 않는다. 전환 단계에는 기존 프로젝트 SSOT가 권위를 유지하며 새 JSON projection은 read-only 또는 별도 격리 후보. 양방향 이중 쓰기 금지. 승인/장면/트랙/해시/권리/이력 round-trip 입증과 명시적 cutover 후에만 JSON을 권위로 전환; migration 실패 시 기존 원본 유지. 외부 앱의 SQLite/프로젝트 파일은 해당 Add-on 내부/외부 시스템 데이터이며 Murim canonical project의 병렬 권위가 아니다.
입력/원고/스토리보드/선택 자산 변경 시 dependency graph에서 영향을 받은 downstream 결과·승인만 계약에 따라 stale/HOLD 처리. 이전 결과는 삭제하지 않는다. 불변 revision/승인 해시를 유지하고 단순 UI 열기·Add-on 비활성화가 승인 내용을 변경하지 않는다.

## 7. 사용자 작업 흐름 / 품질 게이트 / 공용 관리 UI

프로젝트 CRUD → 장르·기획·시나리오·텍스트 스토리보드 자동 작성/CRUD → 인간 감수 및 기존 독립 G1/G2 → 단계별 자동 제작 준비/CRUD(캐스팅, 참조, 쇼트, 영상·음성·편집 계획 및 승인된 후보 생성) → 인간 감수/주요 선택 → 자동 제작/조립 및 G3/G4 실제 품질 승인.
단계별 필수 capability·입력/출력·의존성 및 gate는 versioned composition/profile로 구성하며 데이터는 선언적. Manager가 실행·승인·정책을 해석한다. 프로필과 UI 조합은 변경 가능하나 기존 hard gates를 삭제하거나 우회할 수 없다. 사람이 검토할 실제 원문/스토리보드가 없는 상태는 작성 단계이지 감수 완료 단계가 아니다. 실제 생성 후보나 최종 렌더는 해당 기존 승인 조건을 만족해야 한다. 독립 심사 및 인간 승인 증거를 synthetic score로 대체 금지. 최종 게시 별도 승인.
공용 관리 화면: Add-on 카탈로그(발견/설치/활성/격리/해제/버전/권한/health/실측), capability별 provider 선택(전체 기본값/프로젝트/장면 override), profile CRUD, 예산/GPU/queue/retry/timeout 정책 CRUD, generic schema 기반 설정·폼·미디어 preview·타임라인·로그·상태·승인. 사용자에게 schema/JSON 수동 편집을 요구하지 않는다. 설정은 단위/범위/영향/재시작 여부를 표시하고 preview → 검증 → CAS commit → 실제 적용 확인. 비밀 원문 노출 금지. 추가 UI 표현 primitive가 필요하면 범용 contribution 확장으로 별도 검증한다.

### 7.1 기본 화면과 기계검증 화면의 분리 (사용자 확정)

기본 화면은 작품 목록/새 작품, 자연어 대화, 실제 작품 원고·스토리보드·후보·영상 및 중요한 감수/선택으로 제한한다. "60초 무협 작품 만들어 줘", "두 번째 장면을 더 긴장감 있게", "이 인물로 확정"처럼 자연어만으로 진행 가능하게 한다. AI는 장르 스킬·조사·원고·제작 계획·품질 개선을 자동 수행하고 비용/권리/외부 전송 및 중요한 감독 선택만 쉬운 말로 요청한다. 음성 입력은 선택적 Add-on이며 현재 연결 주장 금지. 기술 설정은 기본 화면에서 숨기되 실제 사용자 위험/결정은 숨기지 않는다.
기계검증 탭은 Central Manager 관측 서비스의 소비 화면으로, 등록된 Add-on/capability/contract/schema/version, 선택 근거, dependency graph, job/attempt/correlation ID, events, 상태/실패 분류, 품질 근거/승인, 입력/출력 hash 및 provenance, GPU/RAM/시간/비용/queue, 로그/재현 bundle, 경계 검사 및 BUILD/TEST/실제 실행 결과를 일관된 형식으로 조회한다. Bridge는 lifecycle/실행 이벤트, Add-on은 고유 진단·evidence, Persistence는 불변 이력을 제공한다. 동적 schema 기반 필터/검색/상세·JSON export 및 read-only diagnostics API로 개발 LLM이 직접 확인할 수 있도록 한다. 운영 설정 변경/재시도/실행은 조회 권한과 분리하고 별도 정책 검증·승인·CAS를 거친다. secret/PII redaction, 권한 범위, 로그 용량·보존/rotation, 무단 외부 전송 금지, unknown 측정치 명시. 실제 개발 LLM 연결 실증 전 NOT_CONNECTED.
자연어 요청→의도/변경 제안→검증/필요 승인→실행→증거 readback→쉬운 말 결과, 모든 단계에 동일 correlation ID. 품질 실패는 제한된 재작업/대안 검증 또는 HOLD; 승인/비용/권한을 무한 반복으로 우회하지 않는다. 원고 없는 감수와 사용자에게 JSON/프롬프트/모델 선택 강제 금지. UX 인수시험: 처음 접한 비전문가가 기술 설정 없이 실제 원고 생성·수정·감수·결과 재생; 개발 LLM이 사용자 개입 없이 승인된 진단 범위 내 실패 원인을 추적; 기본 UI/기계검증 탭 동일 작업 상태 증거 일치, 신규 Add-on에 shell 수정 없음. 최고 품질은 검증 목표이며 보장 아님.

### 7.2 다층 품질 캐스케이드 및 자율 개발

[캐스케이딩 품질 계약](MURIM_CASCADING_QUALITY_CONTRACT.md)이 부모-자식 업무 분해, 독립 평가, 목표 초과 승격, 원인 자식 targeted rework, bounded HOLD, 개발 자율 진행과 기계검증의 세부 권위다. 5축 소유권 및 기존 품질·권한 계약 유지. 구현 완료로 오인 금지.

### 7.3 전문 지식 및 장기 비교우위

[장기 경쟁우위 시방서](MURIM_COMPETITIVE_EVOLUTION_CONTRACT.md)의 이중 품질 캐스케이드, 전문 스킬 version pin, 독립 비교/회귀, evidence 기반 채택 및 rollback을 전 capability에 적용한다. 전문 지식은 Add-on, 비교·선택·관측은 Manager, 실행 Bridge, 일반 검증 Core, 이력 JSON. 신규 책임 축 또는 특정 산업 기준을 Core에 고정하지 않는다.

## 8. 기술 재사용 조사 및 표준 후보 (참고, 채택 확정 아님)

- Python Packaging Entry Points: 표준 discovery metadata. https://packaging.python.org/en/latest/specifications/entry-points/ ; https://packaging.python.org/en/latest/guides/creating-and-discovering-plugins/
- JSON Schema 2020-12: versioned manifest/settings/message/schema 검증 후보. https://json-schema.org/draft/2020-12/
- MCP: 외부 에이전트 tool/capability 연동 후보. 2026-07-28 공식 개정 https://blog.modelcontextprotocol.io/posts/2026-07-28/ ; 외부 프로토콜을 Murim 전체 내부 계약으로 강제하지 않고 adapter에 격리.
- OpenTimelineIO: 편집 교환 형식 및 adapter plugin 후보. https://opentimelineio.readthedocs.io/en/latest/tutorials/adapters.html ; 실제 편집 효과/트랙/시간축 round-trip 검증 필요, 렌더 엔진이 아님.
- Calliope, ComfyAgent 및 기존 모델/엔진: AGENTIC_FILMMAKING_BENCHMARK_2026-11-24.md. 실제 기능·라이선스·GPU·권한 비교 후 필요한 능력만 독립 Add-on으로 수용. 한 후보의 DB/API/런타임 구조가 Core를 지배하지 않도록 한다.
표준과 라이브러리의 존재만으로 보안·호환·성능 PASS를 주장하지 않는다.

## 9. 개발자 인수 기준 (자동검증 필수)

신규 Add-on PR은 (a) 공개 계약만 사용, (b) manifest/schema/라이선스/권한/환경 검증, (c) 독립 fixture·실패 테스트, (d) 실제 결과/재현 기록을 제공. 동일 capability 다른 공급자 교체 시험 및 아래 경계 검증. 실제 필요한 권한과 approved policy 범위 내 실행만 허용한다.
- Zero-add-on: 호스트 boot, CRUD/read, 미디어/이력 열람, 빈 카탈로그, 명시 unavailable. provider SDK 미설치에도 부팅.
- A/B 동일 capability: 동일 Core/Bridge/Manager/shell source hash, manifest와 독립 Add-on만 추가/교체, 계약 결과/상태/정책 일관성. 제3의 신규 능력 등록 및 generic UI 표시.
- 100/300/500 synthetic manifests: 등록/검색/필터/선택·지연 초기화, 반복 착탈, bounded memory/queue/handles. 실제 500개 GPU 동시 실행을 뜻하지 않는다. 성능 목표 수치는 baseline 실측 후 정책으로 확정.
- 장애 격리: missing dependency, incompatible version, invalid manifest/schema, permission denied, crash/hang/timeout/OOM, failed cancel, stale callback, event duplicate, restart/unknown job. 다른 작업·프로젝트 및 Core의 생존 검증.
- 보존/안전: 동시 CAS, 원본 byte/hash, detach/re-attach, immutable approval, stale downstream, no unauthorized external upload or billing, no secret leakage, no automatic failed clip promotion.
- Repo-wide boundary audit: import graph, feature-name branches 및 direct provider calls, duplicated common services, direct storage writes, JSON executable payload, lifecycle cleanup. 후보별 allowlist/legacy fallback/source surgery/약한 assertion 금지. 신규 기능의 Core/Bridge/Manager/shell 변경 0을 diff/hash로 입증.
- 제품 수용: 동일 30~60초 시나리오를 독립 후보 엔진으로 실제 제작/재생, 필요한 Windows/GPU/브라우저 검증, 비용/시간/인간 개입/복구/일관성/작품성 비교. 전 기술 성공을 영상 품질이나 최종 사용자 승인으로 승격 금지.
변경분 감사, repo-wide 자동경계검사, 전체 구조 준수, Windows 실행, GPU, 콘텐츠 품질을 별도 판정한다. 설계 문서 작성만으로 5축 PASS 선언 금지.

## 10. 단계적 이행 (현행 코드는 변경하지 않음)

현재 Git tree에는 src/core, src/agents, src/api/ai_clients.py, src/pipeline/comfyui_client.py, src/studio/{editorial,workspace,web,director_simple,comfy,voice,render}.py 등이 존재한다. 폴더 이름은 책임 준수 증거가 아니다.
다음 한 작업: 현재 호출/import/상태·파일 쓰기/공용 서비스의 소유권 전수 조사와 외부 기술 adapter 후보 비교. 기존 4-GATE/실제 프로젝트 데이터·출력 경로 보호. 중복·직접 호출·이중 SSOT 등 결함을 분류하고 5축 목표 ownership map 및 migration plan 작성. 이후 승인 범위 내 독립 Core 계약/Bridge/Manager의 최소 vertical slice를 개발해 zero-add-on/A-B 교체/실패 격리 테스트하고, 검증된 실제 엔진 하나씩 연결한다. 기존 원본 동작과 승인 이력을 보존하는 단계적 전환; 기존 UI를 무조건 확장하거나 외부 앱 전체 포크로 대체하지 않는다.
상태: ARCHITECTURE_CONTRACT_DEFINED / IMPLEMENTATION_NOT_VERIFIED / REPO_WIDE_AUDIT_NOT_RUN / ADOPTION_NOT_DECIDED / QUALITY_HOLD. 전체 준수 미확인, 기존 UI PRODUCT_DEFECT 미해결.
