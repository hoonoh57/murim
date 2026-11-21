# CURRENT_STATE — Murim AI Content Factory

**기준일:** 2026-11-21  
**소스 원본:** https://github.com/hoonoh57/murim (`main`)  
**검토 시작 HEAD:** `93cde6ee399a9e45911374a665c440855c79beea`  
**현재 HEAD:** 변경 시 GitHub `main`을 직접 조회해 확정한다. 문서의 예전 SHA를 실제 HEAD로 오인하지 않는다.  
**Windows 소비 경로:** `E:\gpt\projects\comfyui\murim`

## 확인한 저장소 기존 구현

- `main.py`: Director/Writer/Council 등 멀티 에이전트 실행기.
- `web_ui.py`: Human-Relay 웹 UI/에셋 관리의 서버 코드.
- `render_episode.py`: 에피소드 기반 TTS/FFmpeg 조합 렌더러.
- `workflows/wan22_5b_api.json`, `workflows/ltx2_i2v_api.json`: ComfyUI API 워크플로 JSON.
- `tests/`: 기존 테스트 모음. `ROADMAP_P0_P1_P2.md`에는 에셋 대시보드 개발 이력과 구형 Windows 경로(`e:\2026\murim`)가 기록되어 있다. **현재 경로는 위 소비 경로**로 취급하며 과거 경로를 자동 덮어쓰지 않는다.

## 이번 범위와 판정

| 구분 | 판정 | 증거 / 보류 |
|---|---|---|
| 기존 저장소 발견 및 파일 읽기 | VERIFIED | GitHub `main` 원본·구조 확인 |
| 원격 단일 변경 체크포인트 | 커밋 성공 여부로 확인 | README, AGENTS, 상태·인계, Windows 진입 스크립트 |
| 기존 제품 Python 테스트 | NOT_RUN | 이번 경계는 소스 제품 변경이 아닌 운영 문서/실행 계약 |
| Windows 목표 경로의 Git remote/HEAD/status | NOT_VERIFIED | 연결된 Windows 실행 테스트 결과 없음 |
| 자동 동기화 예약/runner 연결 | NOT_INSTALLED/NOT_VERIFIED | 저장소의 스크립트만으로 Windows에 자동 설치되지는 않음 |
| 실제 ComfyUI GPU 생성/영상 품질 | NOT_RUN | 실제 Windows 장면 API 실행과 WYSIWYG 필요 |
| 10편 연속 제작/배포 | NOT_STARTED | 단계 P5/P6 목표 |

## 운영 불변식

- GitHub 소스 CRUD / Windows fast-forward 동기화 및 테스트만 담당.
- 파일별 GitHub Actions·반복 승인 금지; 필요한 최종 Windows 실행만.
- Windows 사용자 파일·비밀·산출물 보호, force reset/clean 금지.
- 과거 문서의 단계 완료 표시와 현재 실제품 실행 PASS 혼동 금지.

## 다음 한 단계

기존 Windows 실행기에서 `E:\gpt\projects\comfyui\murim`이 정확한 `hoonoh57/murim` 클론인지와 local dirty/ignored 충돌을 확인하고, `windows-test.cmd`로 **최초 안전 동기화 + pytest + 선택 ComfyUI 확인**을 수행한다. 그 후 P1 실제 한 장면 API 생성으로 진행한다.

## 2026-11-21 — Windows pytest 최초 전체 실행의 3개 회귀 실패 분석

- **사용자가 제공한 실제 Windows 실행 증거:** `E:\gpt\projects\comfyui\murim`에서 `55 passed / 3 failed / 12 skipped` (Python pytest, 6.01s). Windows 예약 작업은 등록되었고 자동 동기화/테스트는 실제 가동하였으나 **전체 pytest FAIL**.
- 실패 원인: `tests/test_camera.py`는 이전 단일 `angle="Extreme Wide Shot"` 규격 및 `Handheld Shake`를 기대했으나, 최신 Camera는 `angle`(실제 촬영각)과 `shot`(화면 크기)을 분리한다. `epic/비장함` → low/EWS/slow_zoom_in/volumetric; `전투` → dutch/MS/zoom_in/rim. `tests/test_prompt_combiner.py`는 5개 외부 서비스만 기대했으나 제품은 ComfyUI 로컬 2개를 포함한 **7개 템플릿**을 지원한다.
- **분류:** `TEST_DEFECT` (기존 구현의 명시적 스킬·도구 계약과 테스트의 예전 기대가 불일치). 테스트 수치만 느슨하게 만들지 않고, 카메라의 각도·샷·움직임·조명 매핑 전체와 7개 템플릿/2장면×7도구 출력, 6장면×7도구(실제 fixture 존재 시)를 구체 검증하도록 강화한다. 제품 소스는 수정하지 않는다.
- **변경 검증:** 원격 파일 내용·결함 분석 VERIFIED; Windows 재실행/실제 출력 PASS는 **NOT_RUN**. 다음 자동 동기화 테스트에서 결과 확인 후 새 SHA의 검증 상태를 기록한다.
- **다음 한 단계:** 새 GitHub main HEAD가 Windows 예약 작업으로 fast-forward 반영되어 pytest 완료되는지 확인. 통과 후 ComfyUI `/system_stats` 연결 및 한 장면 실제 생성 P1 검증.

## 2026-11-21 — Windows 최신 테스트 성공 및 후속 예약 실패 구분

- 사용자 제공 실행 증거: `E:\gpt\projects\comfyui\murim` Windows HEAD = `3e697b3e13a8`. `%LOCALAPPDATA%\Murim\last-verified-pytest.txt`에 정확한 SHA `3e697b3e13a850b8a80eb8ad872311011cd614d8` 기록, 기록 시각 **11:16:52 KST**. 기존 스크립트는 pytest 종료 코드 0 이후에만 이 마커를 저장하므로 **그 시점 해당 HEAD의 pytest 성공 증거**로 인정한다.
- 별도 예약 실행 **11:18:34 KST**, 종료 코드 **1**. 실패 진단 **11:18:38 KST**: `[LOCAL_CHANGES_PRESENT]`. 이후 사용자가 직접 확인한 `git status --short --untracked-files=all`은 비어 있었다. **일시적 로컬 변경인지, PowerShell이 합친 Git stderr인지 UNKNOWN**. 재현 당시 status 기록 없이 환경 문제로 확정하지 않는다.
- 대응: `windows-sync-test.ps1`의 fail-closed local changes 검사를 유지하면서, 실패 순간 `git status --porcelain` 출력의 처음 20개 상태/경로를 **로컬 `last-task-failure.txt`에만** 함께 남기도록 변경. 파일 내용 수집이나 소스 덮어쓰기/무조건 허용/allowlist는 하지 않는다.
- 판정: 해당 HEAD pytest **VERIFIED_ONCE**, 자동 예약 작업 지속 정상 동작 **NOT_VERIFIED**, ComfyUI/GPU 실영상 **NOT_RUN**.
- 다음 한 단계: 기존 예약 작업의 다음 실행 결과, 실행 시 HEAD, 실패 시의 새로운 `last-task-failure.txt`를 확인해 정확한 transient 원인을 분류한다.

## 2026-11-21 — pytest 캐시 접근 거부와 Git porcelain/stderr 혼입 원인 확정

- 사용자 증거: Windows 예약 실행 `2026-11-21 12:24:40 KST`, `LastTaskResult=1`. `last-task-failure.txt` (`2026-11-21 12:24:44 KST`)에 `[LOCAL_CHANGES_PRESENT]` 1 line: `warning: could not open directory '.pytest_cache/': Permission denied`. 실제 porcelain 변경 경로는 해당 로그에 나타나지 않음. 최신 HEAD `1e186642fc1b` pytest PASS는 확인되지 않았고, 검증 마커는 이전 `3e697b3e...`를 가리킴.
- **PRODUCT_DEFECT:** PowerShell 5.1 `git 2>&1`의 `ErrorRecord`(stderr)를 일반 stdout과 결합해 `status --porcelain`을 잘못 해석함. **ENVIRONMENT_ISSUE:** 로컬 생성물 `.pytest_cache/` 접근 거부; 디렉터리 ACL/원인 자체는 아직 미해결.
- 해결: `Git-Run`에서 Git stdout/stderr를 별도 판정하고, status 시 stderr 메시지가 조금이라도 나오면 `[GIT_STATUS_INCOMPLETE]`로 안전 중단(변경 여부를 추측해 통과시키지 않음). 캐시는 표준 pytest 산출물이므로 `.gitignore`에 `.pytest_cache/`만 추가해 Git이 내부로 들어가 상태 스캔할 필요가 없도록 함. 사용자의 `.pytest_cache/`를 삭제·권한 변경하지 않고 다른 untracked/ignored 충돌 보호는 유지.
- 최신 GitHub commit 반영에는 현지 이전 스크립트의 동기화 차단으로 **안전 상태 확인 후 일회성 `git pull --ff-only`가 필요할 수 있음**. 원격 코드 수정만으로 Windows 예약 작업 실행 성공을 확정하지 않는다.
- 다음 단계: 최신 스크립트·ignore 동기화 → 기존 예약 작업 최종 한 번 실행 → 실제 `LastTaskResult`와 검증 SHA 일치 확인. 경고가 지속되면 `[GIT_STATUS_INCOMPLETE]`로 명확히 분류하여 캐시 ACL을 별도로 진단. ComfyUI 실제 생성은 NOT_RUN.

## 2026-11-21 — 예약 자동화 보류, 실제 ComfyUI 한 컷 P1 우선

- 사용자 결정: 10분 예약 자동화는 보류. GitHub 원본 직접 수정 → Windows 사용자가 한 번 fast-forward Pull → 해당 변경의 **일회성 자동 단위 검증 + 로컬 ComfyUI 실제 생성**으로 가능성을 먼저 확인한다.
- GitHub 새 진입점: `run-comfyui-proof.cmd` → `python -m unittest -q tests.test_comfyui_proof` → `scripts/prove_comfyui.py`. WAN 2.2 API JSON 원본은 보존한 채 샘플 이미지/저스텝·17프레임·512×320 인스턴스를 생성해 로컬 ComfyUI 노드/모델 확인, 큐 제출, history 결과 확인, /view 실영상 다운로드까지 시도. 출력은 ignored `outputs/p1_comfyui/`에 저장하고 원본 자산은 덮어쓰지 않는다.
- `workflows/ltx2_i2v_api.json`은 내용이 없으므로 이번 범위에서 제외. ComfyUI 미설치/노드/모델 없음 등은 명시적 FAIL; 실제 GPU 출력·동작은 Windows 검증 전에는 **NOT_RUN**.
- 기존 예약 작업은 Windows에서 `Disable-ScheduledTask -TaskName 'Murim-GitHub-Sync-Test'`로 한 번 비활성화하며, 스크립트는 자동으로 예약 작업을 설치·변경하지 않는다.
- 다음 한 단계: Windows에서 Pull 후 `run-comfyui-proof.cmd` 한 번 실행한 결과로 ComfyUI P1 실행 가능성 판단. 영상 생성 PASS는 실제 파일 증거가 있을 때만 선언.

## 2026-11-21 — 실영상 1컷 생성 성공, 화질 실패 원인과 재검증 설정

- **사용자 실제 Windows 증거:** ComfyUI에서 `WAN22` 로드, 샘플링 8/8, `Prompt executed in 64.24 seconds`. `run-comfyui-proof.cmd` 단위 검사 8개 PASS, 실제 MP4 `outputs/p1_comfyui/p1_c291b6686975_proof_95ba2d2b9c9a_00001_.mp4` 70,807 bytes 저장. 사용자 영상 프리뷰는 비현실적 왜곡과 색면으로 **시각적 품질 FAIL**. `GPU/API/MP4 PASS != CONTENT_QUALITY PASS`.
- **PRODUCT_DEFECT (평가 설정):** 기본 smoke 검증은 자체 생성한 가짜 산·하늘 PNG에 무협 인물을 요구하면서 512×320, 17프레임, 8스텝을 강제했다. 실 제작의 품질 검증에 이 설정을 사용하는 것은 부적절. 이 테스트는 연결 증명용으로만 유지하고 `[SMOKE_ONLY]` 표시.
- Windows 에이전트의 실제 파일 읽기: `E:\\ComfyUI_New\\ComfyUI\\input\\content_creator_identity_reference_portrait.png`는 896×1152 진짜 PNG, 1,340,385 bytes. `male_hero.png` 파일은 이름과 달리 JPEG 바이트. ComfyUI 시작 로그에는 RTX 4070 Laptop GPU, VRAM 8,188 MB / LOW_VRAM 표시.
- **변경:** `--quality --image <실제 PNG>`는 입력 파일의 PNG 형식·화면 방향을 검증하고 인물/복장/스타일 유지 프롬프트, 24샘플링 단계, 33프레임(24 FPS), 8GB 환경에 맞춘 576×768 세로/832×480 가로 설정을 적용. 기존 워크플로 템플릿/기본 smoke/영상 원본은 덮어쓰지 않고 `murim_p1/quality_...`로 신규 출력.
- **검증 범위:** GitHub 소스 구현과 단위 검사 추가; 품질 설정으로 Windows GPU 렌더와 영상 육안 판정은 **NOT_RUN / REVIEW_REQUIRED**. 높은 해상도와 단계 수는 시간이 더 걸리며 예술적 품질을 자동 보증하지 않는다. 우선 실제 참조 이미지로 비교한 후 필요 시 14B/LTX 기반 제작 품질 평가.
- **다음 한 단계:** Windows에서 1회 `git pull --ff-only origin main` 후 `run-comfyui-proof.cmd --quality --image "E:\\ComfyUI_New\\ComfyUI\\input\\content_creator_identity_reference_portrait.png"` 실행. 기존 에이전트/ComfyUI 상태 유지. 새 MP4 확인 후 영상 품질 별도 평가.
