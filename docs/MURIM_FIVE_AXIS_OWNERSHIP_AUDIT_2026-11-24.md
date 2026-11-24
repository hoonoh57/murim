# Murim 5축 책임 경계 감사 및 단계적 이행안 — 2026-11-24

기준 Git HEAD: 4ec63cf40506b01403e42ee895d232a8e06d4a7e. 권위: MURIM_FIVE_AXIS_ARCHITECTURE.md, AGENTS.md.
판정: REMEDIATION_REQUIRED. 주요 제품 경로 소스 정적 조사(38개 Python 파일, static/director_simple.js; 추가 git tree inventory). 전체 repo 자동 경계 검사 아님. scripts/experiments/workflows, 나머지 static/template 및 tests 전수 분석과 Windows 상태는 미실행. 기존 코드/자산 무변경. 파일/행 근거는 기준 HEAD에 고정.

## A. 구조 결함 및 보존할 기능

| ID / 분류 | 기준 HEAD 근거 | 목표 소유권 / 조치 |
|---|---|---|
| A01 AUTHORITY_DRIFT | src/core/skills.py:65–89 장르 분기 및 역할 prompt 조립; src/core/skill_prompt.py:19–197 HERO/WORLD/소품/촬영; skill_story.py:8–136 15비트/무협; skill_sync.py:57 MODEL_CONFIGS; constants.py, prompts.py, skill_narrator.py | 전문 장르/역할/모델 Add-on의 선언적 스킬로 분리. 공용 시간/미디어/의존성 primitive만 Core. historical_art 고유 금지 및 품질 계약 유지. |
| A02 AUTHORITY_DRIFT | main.py:5–12 고정 전문 agent import; agents/director.py:63–98,104–119 고정 agent 이름/직접 호출/승인 확인. 121–176은 unconditional return 뒤 도달 불가 legacy 제작 코드 | Central Manager 총괄/게이트/스케줄, Bridge route, Director/Writer/Council 등 전문 Add-on. 기존 HOLD를 제거하지 않음. |
| A03 AUTHORITY_DRIFT | agents/base_agent.py:3–19 Anthropic 및 Council 직접 생성, 27–36 로그 직접 저장; writer.py:16–19 council 설정 직접 변경, 53 SDK, 77/83 직접 심사; art_direction/audio/camera/imaging/marketing/video의 client.messages.create 또는 council.evaluate; critics/council.py:4,15,42,82–97 | 공급자 SDK Add-on, 역할별 capability 호출을 Bridge로. 공용 로그/비평 원장 Manager→Persistence; 전문 계산 보존. |
| A04 AUTHORITY_DRIFT | api/ai_clients.py:20–79 Gemini 고정 기본 모델·키 전환/재시도; 88–172 ScenarioEngine/Anthropic/MockHelper/미디어 generator | 공급자별 adapter 및 private 전송 처리. 전체 retry, budget, credential ref, mock 차단 중앙 정책. mock placeholder를 실제 생성으로 승격 금지. |
| A05 AUTHORITY_DRIFT | pipeline/comfyui_client.py:25–79 upload/queue/history/poll, 84/117 WAN/LTX 전용; studio/comfy.py:22–65 별도 upload/queue/poll/fetch, 121–188 binding/asset 등록; pipeline/video_comparator.py:11–18 직접 client 연결 | 검증된 단일 ComfyUI transport/adapter owner 재사용. workflow/model별 의미는 해당 Add-on; Manager job lease/retry, Bridge transport, 공용 media 서비스 위임. 기존 Studio의 local-only/NoRedirect/graph/권리 검증 보존. |
| A06 AUTHORITY_DRIFT | studio/web.py:12–23 고정 render/voice/comfy/editorial import와 JOB_LOCK; 112–143 patch/import 저장; 154–170 voice/render 직접 호출; 229–245 workflow 및 comfy | UI/HTTP shell → Manager→Bridge. token/local-only/CAS/gate 유지. 고정 단일 lock을 무턱대고 해제하지 않고 GPU lease 및 project transaction 계약 증명 후 전환. |
| A07 AUTHORITY_DRIFT | studio/workspace.py:25–59 digest/path, 80–128 domain XML/asset, 169–255 voice/patch/state, 267–342 Store; editorial.py:123–148 자체 원장 쓰기, 200–310 승인·원장·M-VML commit; director_simple.py:51–99 독립 revision 파일, 183–200 project-action, 287–325 확정 | Core 일반 모델/검증, Manager CRUD/approval/stale policy, persistence immutable CAS. 독립 원장 존재 자체가 이중 SSOT라는 판정 아님. 실제 전환은 read-only projection + round-trip + cutover; 원본 XML/원장/미디어 유지. |
| A08 AUTHORITY_DRIFT | studio/voice.py:8–9 render import, 18–29 engine/모델/worker/asset 직접 등록, 30–31 lip-bound 제거; studio/comfy.py:14–15 render/workspace import, 175–187 request/receipt/asset; studio/render.py:17–49 executable/probe, 105–178 fingerprint/cache/FFmpeg | TTS/Comfy/FFmpeg 전문 Add-on + Manager 공용 asset/receipt/cache/invalidation/lease, Core media/time primitive. FFmpeg 실 렌더 및 voice hash 의존성 보존. |
| A09 PRODUCT_DEFECT / AUTHORITY_DRIFT | relay/relay_client.py:130–180 7.5/6.0 평가, force_go; relay/relay_automator.py:47–56 max_reworks 후 강제 GO; web_ui.py:208–223 /api/force_go, 226–257 /api/auto_run의 Gemini 직접 실행/완료 표시 | 즉시 우선 안전 보완 경계. G1/G2 권위에 결속되지 않은 리소스 제작 프롬프트 및 자동 진행 fail-closed; 사람 매개 초안 작성과 승인된 제작 분리. 실제 GPU 실행/게이트 우회 실험은 하지 않음. 기존 Relay 경로가 최종 영상 생성한다는 주장 아님. |
| A10 AUTHORITY_DRIFT | relay/batch_builder.py:31/62/136 고정 round/role; relay_client.py:230–277 파일 쓰기; web_ui.py:29–53 세션 저장/복원, 430–466 자산 직접 관리; pipeline/image_manager.py:38–45,119–151 manifest/선택/점수; prompt_combiner.py:128–188 tool별 포맷 | legacy session/asset import는 검증된 read adapter; canonical Manager CRUD, persistence, 역할별 prompt Add-on. 기존 결과 삭제/자동 전환 금지. |
| A11 PRODUCT_DEFECT / AUTHORITY_DRIFT | static/director_simple.js:91/128–134 fixed stage, 167 iframe /studio/, 177–194 asset/candidate/confirm 직접 orchestration; director_simple.py:209–244 고정 scenario/storyboard/motion prompt | 원고·텍스트 스토리보드 작성이 감수보다 먼저. 공용 UI/동적 contribution, capability 요청. 이미지 후보/실제 영상 분리 및 기존 gate 유지. |
| A12 AUTHORITY_DRIFT / 조사 후보 | render_episode.py:17 고정 voice, 61–72 edge_tts, 116–149 FFmpeg 직접 호출 및 무음 트랙; compare_videos.py:8 고정 episode; preview_s01_prompt.py; make_render.py; evolution/skill_tracker.py의 XP 모델; core/visual_dramaturgy.py:12/36 장면 감사 | 독립 실험/레거시 스크립트와 제품 진입점 구별. 실제 배포 경로 확인 후 전문 Add-on/공용 서비스에 이관하거나 archival tool로 격리. 장르 의미가 있는 평가는 Add-on, 일반 해시/시간 primitive만 Core. |

## B. 외부 기술의 공개 연결 경계 비교 (소스 조사, 설치/실행 미검증)

- Calliope MIT. 조회 git tree 32bcd92f3826bd8c10219aebf4cebefbff116eaf. https://github.com/benjiyaya/Calliope : calliope-backend/src/calliope/routers/jobs.py:38–58 list/queue status/pause/resume, 64–142 generate-videos/preview-prompt/export, 180–214 create/get/retry/cancel; routers/workflows.py:27–38 analyze/reanalyze, 67–208 CRUD; routers/agent.py:172–374 session CRUD/review confirm/messages, 447 cancel. HTTP 서비스 adapter 후보; 외부 project ID, job ID, review card를 Murim revision/approval/correlation ID에 매핑하고 readback/reconcile 확인. 외부 SQLite를 Murim의 canonical 상태로 삼지 않는다. queue pause/resume 등 global 동작은 공유 사용자 job 침해 금지. 내부 runtime/capabilities를 통째로 Core에 이식하지 않는다. 외부 API auth/버전 안정성/동일 idempotency/결과 자산 전달/실제 독립 승인 검증 필요.
- ComfyAgent MIT. 조회 git tree 43ff2497c83fe62cb322d6940e449e66ca0c5800. https://github.com/IvenKooLab/comfy-agent : mcp_server.py:29–54 query_status, submit_generation, list_workflows, search_gallery; 68–100 HTTP bridge. MCP 또는 공개 HTTP adapter 후보. 관측된 4개 MCP tool만으로 Murim의 job별 cancel/reconcile/approval/권한·정확한 asset correlation을 만족한다고 볼 수 없음. server.py 해당 계약 추가 검증 후 능력별 채택. global queue/force-submit 및 자동 모델 설치는 중앙 승인 없이 금지.
- 기존 studio/comfy.py는 role binding/graph 검증/local-only 기반 보존 후보이며 기존 설치에서 실제 LTX 다중 키프레임 미검증. 현재 코드를 전면 폐기할 근거 없음. 외부 기술은 독립 비교 대상, 어느 것도 기본 엔진으로 확정하지 않음.
- 기존 FFmpeg/GPT-SoVITS 및 승인 원장은 기술 자산. 전면 재작성 대신 좁은 공개 contract 뒤의 재사용을 먼저 검증한다.

## C. 단계적 migration 순서 및 검증

M0: 권위 충돌(A09) 우선 차단, 초안/편집 기능은 보존. 레거시 버튼/API/자동 재작업 한계를 시험하고 미승인 상태에서 리소스 제작 요청이 생성/전송되지 않는지 확인. 기존 G1/G2 심사/승인 회귀를 약화하지 않는다. 그 전 기존 자동 제작 사용 보류.
M1: 독립 fixture에서 Core contract, Manager registry/선택, Bridge 격리 lifecycle, JSON persistence 최소 vertical slice. Python entry points/JSON Schema 등 기존 표준 검토 후 선택. 기존 프로젝트와 분리, 0개 boot/A-B 동일 capability 교체/제3 능력 등록/실패 격리/100-300-500 manifest 테스트. 실제 provider가 없으면 명시 unavailable. 호스트 코드 해시 고정 증거.
M2: 기존 Studio immutable source/asset/approval을 read-only projection으로 연결, round-trip/원본 보호. 기존 승인 원장의 권위를 유지; 이중 쓰기 금지. 공용 asset/probe/job/receipt 서비스를 한 소유권으로 이관. 실제 Windows 이전과 rollback 검증 전 cutover 금지.
M3: 동일 30~60초 기획의 실제 외부 엔진 비교: Calliope/ComfyAgent/기존 ComfyUI 중 호환 경계와 권한 검증된 후보부터 좁게 연결. 작업 status/cancel/unknown reconciliation, GPU 시간, 비용, 영상/음성, 인간 개입 횟수, 품질 기록. 실제 provider 2개 이상 교체 시험 후 확대.
M4: 장르·writer·storyboard·casting·motion·audio·edit·review Add-on 전환과 동적 UI. 사전 제작 작성→감수→단계별 CRUD→감수→자동 제작. 기존 품질 게이트 유지. 호환 layer나 legacy bypass를 영구 예외로 두지 않는다.
M5: 실제 제품 전체/Windows/GPU/영상 품질/전체 5축 repo-wide 검증. 개별 checkpoint PASS와 전체 준수 분리. 미검증 기능을 제품 완료로 표시 금지.

다음 한 경계: M0 안전 차단(A09) 및 focused regression. M1 설계/구현은 그 뒤 진행. 이번 감사로 코드 변경/테스트 실행/실제 Windows 검증/후보 기술 실행은 하지 않았다. 전체 자동 경계 검사는 아직 NOT_RUN.
