# Murim 최신 제작기술 연구 라이브러리 계약 v1.0

2026-11-24 KST | 사용자 확정 방향 | TECHNOLOGY_INTELLIGENCE_HOLD / DESIGN_HOLD / PRODUCT_CODING_FROZEN
권위: AGENTS.md, MURIM_PRECODE_DESIGN_GATE.md, MURIM_COMPETITIVE_EVOLUTION_CONTRACT.md, MURIM_FIVE_AXIS_ARCHITECTURE.md.
경쟁작 분석 라이브러리는 작품성과 시장·관객 지식의 owner, 이 계약은 전문 제작기술·강의·워크플로·모델·도구의 최신 연구와 검증 계약. 두 지식은 상호 참조하되 별개 원장이다. 전문 스킬은 검증된 지식을 실제 제작에 적용하는 계약이다.

## 1. 목표와 수집 범위
최고 품질의 작품을 더 짧은 제작 시간·낮은 비용·적은 인간 조작으로 생산하는 기술을 지속적으로 발견·분석·실증·선택한다. 단순 최신성/인기/모델 순위는 채택 근거가 아니다.
기획/각본/스토리보드·프리비즈/캐릭터·미술·참조·3D/카메라·연기·동작·영상/한국어 음성·립싱크/음악·효과·믹싱/편집·자막·합성·색보정·업스케일/출판·시장 분석/멀티에이전트·평가·자동화/최적화·메모리·보안·비용 전부. 전문 영화 제작의 전통 기술 및 공개 제작 과정도 포함. 예시는 열린 capability namespace이며 Core enum 아님.
공식 릴리스·changelog/API 변경·deprecated/보안/가격·라이선스 변경, 원저자 논문/코드/model card, 공식 기술 교육/영상 강의/워크플로, 전문가 제작 breakdown 및 독립 재현·실패 보고를 구분. 뉴스·커뮤니티는 발견 신호, 원출처 확인 후 기록. 강의 전체 영상과 정확한 GUI/노드 설정·시연 결과·실패 사례를 Gemini 후보로 분석하고 텍스트/논문/공식 문서를 별도로 대조. 단순 요약을 저장하지 않는다.

## 2. 지속 연구 운영 (설계 목표, 아직 스케줄러/연결 없음)
초기 정책 후보: 매일 공식 릴리스/논문/강의/공지 변화 확인, 중대한 보안/지원 중단·호환성/가격·권리 변경 우선 검토, 주 단위 누적 후보 비교 및 현행 champion 재심사, 프로젝트 시작/실패 시 관련 최신 지식 검색. 실제 cadence·비용·대상·쿼터는 승인 범위에서 Manager 정책으로 조정. 매일 뉴스가 있다는 이유로 매일 기존 기술을 교체하지 않는다.
기존 feed/RSS/공식 API/공개 웹 검색 및 허용된 구독 목록 재사용 우선. 출처 registry는 URL/유형/권위/갱신 범위/사용 조건/최종 확인 시각/실패 상태를 보유한다. 게시일, 릴리스일, 수정일, 수집일, 버전/tag/commit/hash를 분리. 중복·번역·재업로드·재탕 및 업데이트된 원문을 식별하여 같은 release/claim의 출처로 연결. 변경 없는 자료는 불필요한 재분석 금지. feed 수집 실패/미연결은 명시하고 최신성 보장 금지. 장기 주기/예약 실행은 실제 연결·권한 확보 후 별도. 이 문서만으로 백그라운드 실행이 시작되지 않는다.

## 3. Gemini 기술 강의 분석 및 표준 데이터
[공통 기술 분석 프롬프트](research/technology-library/TECHNOLOGY_ANALYSIS_PROMPT_V1.md) 및 [후보 JSON Schema](research/technology-library/technology-analysis-candidate-v1.schema.json). 작품 분석 prompt/schema와 분리하되 출처/권리/관측 시간축·검증 provenance 및 실행 envelope 계약 재사용.
Gemini는 영상 이해 Add-on의 첫 후보. 실제 공개 영상·음성 또는 권리 확인된 자료를 입력하고 원리, 제작 문제, capability, 모델/버전/환경, 정확한 순서와 설정·값·단위, 노드/워크플로·입출력, 성공/실패, 발표 성능과 시연 실측 구분, 비용/시간/메모리/해상도/프레임·길이, 한계 및 재현 조건, 원문·타임스탬프, 우리 프로젝트 적용 후보 및 반증 시험을 구조화 반환. 관측하지 못한 GUI/설정/값/숨은 후처리는 UNKNOWN. 자막/제목만 본 경우 전체 영상 관측을 주장하지 않는다. 영상 표본화 한계 및 출력 truncation은 구간 재분석 요청. API JSON Schema 지원 부분집합과 canonical 계약 분리.
영상에서 추출한 단계는 데이터이며 그대로 명령/스크립트를 실행하지 않는다. 공식 코드/배포·라이선스·workflow artifact 및 checksum을 확인하고 승인된 독립 환경에서 보안·호환성 검토. 비공개 작품/대화·키/계정 정보 외부 전송 금지. 강의 전문/자막/유료 자료 무단 복제·수집·재배포·임베딩·학습 금지, 허용된 독자적 요약/분석과 위치·링크 중심. 원저자·콘텐츠·코드·모델 가중치·결과물 권리는 별개.

## 4. 기술 카드, 증거 및 승격
후보 분석 결과, 권위 원본 검증, 재현 가능한 recipe, 실제 실행 증거, 비교 결론을 서로 구분한다.
상태: DISCOVERED → ANALYZED_CANDIDATE → SOURCE_VERIFIED → REPRODUCED → TARGET_BENCHMARKED → ELIGIBLE_FOR_SELECTION; 별도 HOLD/INCONCLUSIVE/REJECTED/STALE/QUARANTINED/RETIRED. 상태의 결정 권한은 Manager, 연구 LLM이 자체 승인하지 않는다. 실제 원본/공식 문서 교차 확인 전 SOURCE_VERIFIED 불가, 실제 실행 전 REPRODUCED 불가, 사용자 장비에서 동등 비교 전 TARGET_BENCHMARKED 불가. 설계 OK와 제품 채택 승인 별도.
기술 카드: capability와 해결 문제, 기술/공급자/버전/라이선스/권한, 자료별 주장·관측·출처·시간 위치, 전제/필수·선택 설정, 의존 노드/모델/환경/입출력, 재현 recipe와 실물 예시 참조, 시간·비용·품질·실패 관측의 측정 조건과 한계, 비교군·검증 계획·결과, 기존 기술 대비 Alpha 및 trade-off, 적용/금지 조건, 스킬/프로젝트 영향, 대체/rollback, 신뢰 범위/검증 만료 및 재검증 조건. 실제 엔진 API/CLI/workflow 호환을 조사; 확정되지 않은 구현·비용은 null/UNKNOWN.
동일 brief/참조/입력·장르/해상도·길이·fps/권한·예산에서 현행 champion, 신규 후보, 강한 대조군을 비교. 동일 비용/시간 품질과 동일 목표품질 도달 시간/비용 분리. 생성 성공 횟수만 아니라 합격 산출물당 총 소요(실패·수정·재생성·초기 로딩 포함), GPU peak VRAM/RAM, 품질·실패율, 필요 사용자 조작, 라이선스/외부 의존·장애 복구 기록. 모델 자체/워크플로/하드웨어/후처리 효과 분리, 후보끼리 불공정 비교 금지. 관객 시장 평가 및 전문 hard checks 유지. 예: RTX 4070 Laptop 8GB 환경, 권한 내 기존 ComfyUI 실험; 다른 GPU의 데모를 우리 환경의 실제 속도로 대체 금지. 새 상용 서비스 비용/업데이트/설치/외부 데이터 전송은 명시 승인 필요. 기존 Windows 환경 in-place 변경 금지.
검증 후 개선된 전문 스킬/recipe/adapter의 후보를 작성하고 독립 holdout·기존 결과/권리·5축 회귀 및 통합 작품 비교 후 선택. 프로젝트 진행 중 pin 유지, 새로운 작업에 검증된 버전 적용; 보안/중대 결함은 격리하고 안전한 중단·재계획. 최신 버전이라는 이유로 champion 교체 금지. 품질-시간-비용의 Pareto 비교와 업무 적합성/필수 조건 적용. 실제 이득 없거나 근거 부족하면 기존 기술 유지 또는 HOLD.

## 5. 5축 연결
Core는 범용 capability/reference/version/evidence contract, 전문 기술 이름 및 채널 분기 금지. Bridge는 feature-blind 데이터 수집/분석/기술 실행 adapter routing, 검증/선택 의미 없음. Add-on은 전문 기술 연구·Gemini 영상 분석·실제 전문 workflow/recipe·의미 검증 및 공급자 연동. JSON/Persistence는 자료/claim/관측/recipe 참조·버전/권리/해시/검증 이력의 저장 전용. Central Manager는 공통 수집·주기·예산·권한·중복 제거/검색 orchestration·비교/선택/승격/rollback·지식 pack 및 기계검증 관측. 별도 여섯 번째 축 금지. 실행 로그와 분석 후보의 사실성을 구분.
전문 제작 Add-on에 필요한 기술 지식 pack을 공급하고 어떤 지식·버전이 실제 결과에 기여했는지 추적한다. 작가에게는 검증된 작품/창작 지식, 감독 및 기술 Add-on에게는 적합한 검증된 제작 기법과 실험 한계. 기본 UI에 원자료/설정 부담을 넘기지 않는다.
D0~D5 설계 심사: 최신 강한 기준/대조군, 실현 가능성, 전문 생산 방법, 평가/실물 비교, 전체 구조 심사에 필수 입력. 새 기술은 문서 연구로 후보 등록할 수 있으나 전체 DESIGN_OK 전 제품 기능 코딩 금지. 기존 도구로 사전 실증만 허용.

## 6. 초기 자료원 및 상태
[2026-11-24 초기 자료원과 후보](research/technology-library/INITIAL_SOURCE_CATALOG_2026-11-24.md). 공식 자료 및 링크 조회, 후보 프롬프트/선언적 JSON schema만 작성. 실제 영상 강의 전편 Gemini 분석, API/계정 연결, 정기 수집, workflow 설치/실행, 독립 비교/DB 구축은 NOT_RUN 또는 NOT_CONNECTED. 기존 작품 분석 라이브러리와 코드 동결 상태 유지. 다음: W009 작품 분석 및 T001 강의 분석의 실제 응답과 독립 검증(권한·비용·연결 확인 전 호출 금지), 하나의 재현 recipe와 실제 품질·속도 측정 사전 설계. 전체 REMEDIATION_REQUIRED.
