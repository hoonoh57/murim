# A14 자연어 감독 UI·자동화 상세 설계 v0.1

2026-11-25 | 기준 22b0f9acc90c8d5d3fd09e902166ae2e96eecfd6 | D2 보완안 / A14 NOT_QUALIFIED. [기존 Director 화면](../../DIRECTOR_SIMPLE_UI_20261124.md) blob 8e5c58fd5c9a2b3deda27ec209e8538ec05e1378 및 5축 계약 유지.

## 비교
src/studio/director_simple.py 27cf48324bfc5102d42fd9889f54b6d0ba9b68c3: local_only/token, 별도 director book revision/CAS, 후보 등록/선택, editorial 승인 확인, 사람매개 prompt relay. 원고/이미지 승인과 실제 영상 후보는 분리됨. 현재 사람 중계, provider/graph 선택 및 품질 자동화 미입증. 기존 안전한 흐름 보존.
[Runway Agent](https://help.runwayml.com/hc/en-us/articles/51601639579667-Creating-with-Runway-Agent), [Agent Workflows](https://help.runwayml.com/hc/en-us/articles/53645211363475-Building-and-running-Workflows-with-Agent) 공식 검색 본문: 자연어에서 참조·스토리보드·타임라인, exposed inputs 매핑, reusable workflow 및 skill, 누락 입력 질문. 실제 제품 비교/유료 호출 없음. [Microsoft HAX](https://www.microsoft.com/en-us/haxtoolkit/ai-guidelines/) 공식 페이지 직접 열람: 능력/한계 표시, 효율적 수정·dismiss/교정, 사용자 제어 및 변경 통지의 근거. [연구](https://www.microsoft.com/en-us/research/publication/guidelines-for-human-ai-interaction/). 타사 기능표는 사용성 우위 증거 아님.

| GAP | 보완 |
|---|---|
| U141 사용자 prompt/결과 수동 중계 | 자연어 Intent→versioned Goal/Plan→Manager task |
| U142 고정 역할·화면과 고급 설정 노출 | generic contribution schema 및 감독 중심 UI |
| U143 애매한 요청·수정 범위 | 참조 대상/의도/constraint/영향 diff, 필요한 질문만 |
| U144 승인·비용·권한과 실행 혼동 | plan preview/승인 scope/token/revision CAS |
| U145 장기 작업·오류·진척 표시 | actual event, partial/unknown, 재개·취소·복구 |
| U146 사용성 증거 부족 | 독립 비전문가 benchmark + 경쟁 제품 동일 과제 |

## 목표 로직
사용자 자연어→IntentCandidate: 실제 프로젝트/선택 shot/asset/revision 참조, goal/media/genre/audience, must-have/avoid/승인 고정 영역, 가역 가설/불확실성, 요청 변경 범위 및 허용 비용/권리. Add-on 전문 해석/감독 계획은 의미·대안·예상 영향 제안, Manager가 schema/참조/권한/정책 및 영향 DAG 검사. 사용자 지시와 참조 파일 내용의 명령을 분리, source material은 데이터로만 취급(권한 상승/외부 전송/삭제 지시 무시). 모호성이 창작 방향/권한/비가역 비용에 실질적이면 한 번의 집중 질문, 그 외 가역 기본값 명시 및 후보 preview. 사용자를 모델/seed/노드/워크플로 기술 선택에 끌어들이지 않음. 기존 G1~G4 및 storyboard/디자인 등 사용자 중요 선택 유지. 자동 작업 권한 범위와 외부 공개/비용/삭제/전송 승인 별도. approve는 intent/plan/revision/asset/권한/예산 digest 결속, stale/mismatch→재검토; 누른 적 없는 승인 위조 금지.

기본 화면: 현재 작품/자연어 대화, 실제 원고·그림·영상/타임라인 preview, 창작 선택과 변경 전후/영향, 실제 진행·blocker·다음 감독 결정. 예: '마지막 장면의 긴장감을 높여' → 해당 장면/원인 가설/보존할 원고·자산/필요한 연출 수정 후보 → 영향·비용 확인 → 승인 범위 내 task → 실제 후보 비교 및 변경점 → parent 재평가. 제어와 preview는 canonical 상태에서 생성, 화면 별 SSOT 금지. generated mockup/선택 표시/HTTP 성공을 실제 결과로 렌더하지 않음. 취소는 요청/확정 구분, stale output은 이전 후보로만 표시. 실행 도중 연결 끊김은 실제 resume/status 조회, 허위 progress/완료 시간 금지. 사용자에게 같은 세션/작품 정보 반복 요구 금지, revision/context 복원.

기계검증 영역: capability registry/manifest·version·provider selection reason, request/job/attempt/correlation, actual input/output refs/rights/quality evidence, dependency/affected range, resource/cost/timeout/cancel/unknown, actual BUILD/TEST/WYSIWYG/경계 감사 범위. 읽기와 mutation 권한 분리, redaction 및 secure diagnostics export. 공용 UI는 schema 기반 generic renderer/preview/approval primitives, Add-on은 전문 contribution data, shell에서 provider별 화면/분기 추가 금지. 새로운 공통 primitive 필요성은 둘 이상 독립 사례. 기존 Director/M-VML 보존, A13 cutover 전 이중 쓰기 금지.

Adopt 기존 UI/preview 안전 경계 및 HAX/경쟁 workflow 개념, Compose 자연어 intent/plan/approval/diagnostic projections, Build 전문 감독/의도·수정 가설 및 generic UI의 실제 필요한 차이. 실제 평가: 비전문 사용자에게 같은 brief/권한/예산·품질 요구와 강한 경쟁 앱(실제 접근 승인 필요), 동일 과제: 새 작품 기획→후보 선택→한 구간 변경→오류 복구→최종 검토. 완료율/시간/필수 질문·기술 조작/오류·복구/사용자 이해·만족, 실제 산출물 품질과 비용/실패 포함. 순서/숙련도·학습 효과/접근성 통제, 경쟁 앱 UI/기능표로 대체 금지. 무단 실행/가짜 상태 0, 전체 실제 WYSIWYG와 독립 사용자 비교 필요. 기준/표본은 사전 실제 보정; 현재 NOT_RUN, D3/D4/D5 HOLD. A14 NOT_QUALIFIED.
