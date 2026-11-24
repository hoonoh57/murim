# Agentic Filmmaking — 기술 우선 비교 및 도입 검증 (2026-11-24 KST)

## 판정
사용자 실제 /studio/simple/ 화면에서 원고가 없는 신규 작품에 시나리오 감수를 요구하고 프롬프트 수동 복사/등록을 중심으로 한 결함 확인: PRODUCT_DEFECT (UX / automation architecture). 기능 버튼 추가를 중단한다. 목표는 인간의 제작 대행이 아니라 AI 제작팀의 자동 실행, 인간은 중요한 창작 결정과 품질 감수만 담당. 기존 G1/G2/G3/G4 안전·품질 계약 및 원본은 유지한다.

## 상용 기술 기준 (공식 공개 기능; 실제 사용/영상 독립 비교는 미실행)
- InVideo Agent Two: 프로젝트 공유 맥락, 전문 제작 에이전트, Slate 편집(2026-08-04), Workflows(2026-08-08). https://invideo.io/news/introducing-slate-invideo-agent-two/ ; https://invideo.io/news/introducing-workflows-invideo-agent-two/ ; https://invideo.io/news/introducing-expert-agents-invideo-agent-two/
- Runway Agent: 자연어 다중 쇼트 제작, 자동 영상/음성 조립 Final Cut, reusable skills. https://help.runwayml.com/hc/en-us/articles/51601639579667-Creating-with-Runway-Agent ; https://help.runwayml.com/hc/en-us/articles/53907039424915-Using-Agent-Skills ; API 개발자 안내 2026-11-02 갱신 https://dev.runwayml.com/learn/build-with-your-coding-agent
- Higgsfield Cinema Studio 4.0: 장르·카메라·조명·캐스팅·장소·모델 통합. https://higgsfield.ai/cinematic-video-generator
- LTX Studio: 아이디어/대본→동적 스토리보드→캐릭터 참조→제작 및 편집. https://ltx.io/studio ; https://ltx.io/blog/how-to-build-a-complete-pre-visualization-pipeline
- Google Flow: 자연어 에이전트·맞춤 도구; 2026-11-12 신규 시각 서사 도구 발표. https://blog.google/innovation-and-ai/models-and-research/google-labs/new-google-flow-tools/

## 재사용 후보 (GitHub 메타데이터/README 확인, 설치/실행/완성 영상 미검증)
1. **Calliope — 우선 통합 후보**, MIT, 313 stars, pushed 2026-11-15 UTC (조회 당시). https://github.com/benjiyaya/Calliope — FastAPI/SvelteKit/SQLite, 역할별 LLM, 프로젝트 도구, story/assets/script/video, ComfyUI API JSON role tags 기반 바인딩, 큐·재시도, FFmpeg 연결. Python 3.11+, Node 18+, comfy-api-proxy, LLM endpoint 필요. README 실제 사용 흐름에서 자산/영상은 review card에서 Generate 클릭, 일부 카메라 작업 수동; 무인 전체 완성 검증 아님. 데모 https://youtu.be/JcGqt3DYn6c (시청 미실행).
2. **ComfyAgent — ComfyUI 운용 후보**, MIT, 34 stars, pushed 2026-11-16 UTC. https://github.com/IvenKooLab/comfy-agent — Windows/stdlib Python/JS, 캐릭터 LoRA, 에피소드 큐, 첫/끝 프레임, 상태/재시도, MCP, 로컬 그래프. README는 force-submit 가능; Murim 승인 우회 금지. 기존 모델/노드 업데이트 자동 실행 금지.
3. **NodeTool — agent-first 플랫폼 비교 후보**, AGPL-3.0, 655 stars, pushed 2026-11-24 UTC. https://github.com/nodetool-ai/nodetool — agent-accessible editors, DAG workflow, supervised retry/repair, budget, multi-track, MCP. 코드 재사용 및 배포는 라이선스 검토 후.
4. **AI Video Production Editor — 전문 제작 UX 기준**, GPL-3.0-or-later (README), 195 stars, pushed 2026-11-20 UTC. https://github.com/LudwigKienle/ai-video-production-editor — director treatment, story bible, continuity review/re-film queue, scene wall, timeline 및 OTIO/FCPXML handoff. 일부 API/hosted 기능 별도 구성. 코드 재사용/배포 전 라이선스 검토.
5. **AI-Director-Skills — 영화 제작 스킬/그래프 후보**, MIT, 3 stars, pushed 2026-07-09 UTC. https://github.com/hzw1199/AI-Director-Skills — 서사 진단/재작성, shot planning, Z-Image 캐릭터시트, Qwen reference edit, LTX-2.3 I2V, FFmpeg. 외부 submodule/스킬 필요, README GPU 권장 16GB 이상. 8GB 실증 아님.
6. **OpenMontage — 승인 및 제작 관측 UX 참고**, AGPL-3.0, 2 stars, pushed 2026-07-11 UTC (조회한 저장소 기준). https://github.com/tjebastin/openmontage — reference analysis, Backlot storyboard, 비용/승인. 원저자·최신 upstream과 기능/라이선스 추가 확인 필요. 우선 도입 대상으로 확정하지 않음.

Stars와 최근 push는 개발활동 지표일 뿐 작품 품질 증거가 아니다. README/공식 발표와 실제 실행/비교 영상의 증거 등급을 분리한다.

## 로컬 모델 전략
기존 설치 기준/검술 물리 문제는 WUXIA_VIDEO_4070_BEST_PRACTICE_2026-11-21.md 참조. 사용자 RTX 4070 Laptop 8GB/32GB RAM, 기존 ComfyUI 0.20.1은 당시 관측이며 최신 인벤토리 재확인 필요. LTX-2.5 공식 예제: https://github.com/Lightricks/ComfyUI-LTXVideo/tree/master/example_workflows/2.5 ; 커뮤니티 8GB baseline https://github.com/reventadirecta/LTX-2.5-I2V-8GB-VRAM — RTX4060 Laptop 8GB/16GB RAM, ComfyUI 0.34.3, 73frames/24fps, 실제 512x256, 84.58s, audio decode/mux OFF; 작성자 보고, 정확한 peak VRAM 미측정. 사용자 PC 호환/품질 보장 아님. 기존 ComfyUI inplace 업데이트·모델 설치 금지. 저VRAM quant/offload, short-shot preview, first/last frame, character references, motion transfer/prop constraints, 필요 시 승인된 외부 GPU/API의 비교를 진행한다. 모델·노드·코드·출력 이용권은 각각 검토.

## 목표 제작 흐름 / Murim 고유 Alpha
프로젝트 CRUD → 장르 및 기획/시나리오/텍스트 스토리보드 자동 작성·CRUD → 인간 감수(기존 독립 G1/G2 포함) → 단계별 자동 생성·CRUD(캐릭터/장소/소품/이미지/키프레임/영상/음성/편집) → 인간 감수 및 주요 선택 → 승인된 그래프 자동 제작 및 G3/G4 검증. 계획용 텍스트 스토리보드와 실제 생성 이미지 후보를 분리한다. 사용자가 JSON/프롬프트/파일 전달 담당자가 되지 않도록 한다. 기존 승인 계약 변경 없음.
특화: 장르별 전문 스킬/사료 사실성 및 권리, 한국어 연기·운율, 무협 인물/검/손/동작 일관성, 시각적 새 발견, 장편·연속 에피소드 세계관 유지, shot별 모델 라우팅 및 자동 재시도, 실패 컷만 재생성, 감독이 고칠 부분만 제시하는 한국어 UX. M-VML 및 승인 이력은 실제 호환 검증 후 연결. 범용 편집기/큐/워크플로/자산 저장 중복 개발 지양. 자동 비평은 보조 증거이며 독립 인간 승인 또는 작품성 PASS를 가장하지 않는다.

## 다음 단일 작업: 공통 실물 벤치마크
Calliope 및 ComfyAgent 소스/라이선스/의존성/외부 전송·설치 권한을 점검하고, 기존 설치와 격리한 별도 후보 실증 환경에서 30~60초 동일 기획을 비교할 시험안을 준비. 가능하면 하나의 사료 기반 한국어 문화 서사와 별도 짧은 검술 동작 fixture로 구분. 원고→쇼트/참조/생성→편집/음성→실제 MP4. 실제 사람 개입 횟수·소요시간·GPU/비용·실패 재시도·원고 보존·인물/소품 일관성·편집·한국어·시청 가치와 재실행 가능성을 측정하고 상용 기준과 비교. 설치/유료 API/외부 파일 전송은 사전 승인 범위 내에서만. 실행과 영상 확인 전 우승 제품 선정·전면 교체 금지. 기존 Murim 코드는 현재 그대로 유지하고 별도 후보 실증 후 adopt/compose/build 결정.

상태: RESEARCH_INITIAL_COMPLETE / BENCHMARK_NOT_RUN / ADOPTION_NOT_DECIDED / WINDOWS_FULL_TEST_NOT_VERIFIED / QUALITY_HOLD.
