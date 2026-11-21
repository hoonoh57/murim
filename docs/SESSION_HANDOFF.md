# SESSION_HANDOFF — Murim 연속 개발 진입점

## 복구 순서

1. GitHub `hoonoh57/murim`의 `AGENTS.md`, `README.md`, `docs/CURRENT_STATE.md`, 이 문서, 대상 제품 코드를 읽는다.
2. GitHub `main` HEAD와 마지막 커밋·차이 확인. Windows `E:\gpt\projects\comfyui\murim`은 소비/테스트 전용이며 로컬 수정은 하지 않는다.
3. 기존 4-GATE, Human-Relay, ComfyUI 워크플로, 에셋 대시보드·렌더러·테스트의 실체를 먼저 확인한다. 기존 README/로드맵에서 완료라고 표현된 항목도 현 PC의 실제 PASS로 단정하지 않는다.
4. 필요한 작업은 GitHub에서 연속 수행, **마지막 단계에만** Windows 동기화+제품 테스트를 요청한다. Actions를 파일 단위로 반복하지 않는다.

## 현재 위치

- 사용자 요청: ComfyUI를 활용한 콘텐츠 자동화 완성 프로젝트의 README, 이후 **모든 GitHub CRUD / 로컬 자동 동기화·실행 테스트만** 하는 에이전트 방식.
- 확인된 저장소: `hoonoh57/murim` `main`, 검토 시작 HEAD `93cde6ee399a9e45911374a665c440855c79beea`.
- 기존 `README.md`와 `ROADMAP_P0_P1_P2.md`, ComfyUI 워크플로·Python 구현·pytest 존재. 기존 콘텐츠를 덮어쓰지 않도록 README 확장 방식 선택.
- 새 `windows-test.cmd` → `scripts/windows-sync-test.ps1`은 Windows 실행 시 safe Git ff-only 동기화 후 테스트하도록 작성. **실제로 Windows에 반영·예약·실행된 것은 별도 확인**.
- 제품·GPU·영상 실제 테스트는 이 문서 작업의 검증 범위 밖.

## 금지 및 안전

- GitHub 원본 대신 Windows에서 소스 CRUD하지 않는다.
- 다른 저장소의 기존 고정 runner operation을 murim 용도로 가장하지 않는다.
- 사용자 로컬 변경 무시한 강제 reset/clean/덮어쓰기, 로컬 비밀 커밋, 승인 없는 게시 금지.
- 원격 commit PASS = 실제 Windows/ComfyUI/영상 PASS라는 표현 금지.

## 다음 한 단계

실제 Windows runner와 `E:\gpt\projects\comfyui\murim` 클론 연결을 확인하고 안전 동기화/pytest를 **한 번** 실행하여 출처가 명확한 결과를 얻는다. 그 다음 실제 ComfyUI P1 장면 생성 API 테스트를 설계·구현한다.

## 2026-11-21 — Murim pytest 회귀 테스트 정합성 복구

- 사용자 Windows 로그: `3 failed, 55 passed, 12 skipped`. 실패 3건은 카메라 angle/shot 분리와 신규 ComfyUI 2개 백엔드 추가에 따른 구 규격 assertion 불일치.
- **TEST_DEFECT 판정**; `src/agents/camera.py`, `src/pipeline/prompt_combiner.py`는 그대로 두고 `tests/test_camera.py`, `tests/test_prompt_combiner.py`에서 스킬 기반 angle/shot/movement/lighting 및 7개 도구 규격으로 **명시적 확인 강화**.
- `outputs/` 에피소드가 없으면 기존 12개 fixture 의존 검사는 skip. 새로운 임시 2장면×7도구 테스트는 외부 데이터 없이 실행하여 이 부분을 지속 점검.
- GitHub 파일 검사와 원격 커밋을 Windows pytest PASS로 혼동하지 말 것. 다음 단계는 자동 예정 Windows 테스트 재실행의 최종 결과 확인이며 실패 시 실패 분류 후 원본 수정.

## 2026-11-21 — pytest 성공 후 예약 자동 반복 실행 실패

- Windows 최신 HEAD `3e697b3e13a8`, `last-verified-pytest.txt`는 `3e697b3e13a850b8a80eb8ad872311011cd614d8` (11:16:52 KST). 해당 커밋 pytest 성공 증거.
- 그 후 예약 작업 11:18:34 KST 실행 결과 1, 실패 로그 11:18:38 KST `[LOCAL_CHANGES_PRESENT]`; 사용자의 후속 `git status --short --untracked-files=all`는 clean. 실패 발생 순간 status 항목이 무엇이었는지는 **UNKNOWN**.
- 원본 보호를 약화하거나 reset/clean 하지 말 것. 진단용으로 GitHub 스크립트에서 실패 당시 porcelain 출력의 최대 20개 항목을 로컬 오류 로그에 기록하도록 강화.
- 최종 판정: Python 테스트는 특정 커밋에서 VERIFIED_ONCE, 정기 예약의 안정성 NOT_VERIFIED, ComfyUI 렌더 NOT_RUN. 다음 예약 실행의 상태와 새 진단 내용으로 원인을 판정할 것.

## 2026-11-21 — pytest 캐시 경고를 로컬 변경으로 오인한 동기화 실패

- Windows `12:24:44 KST` 상세 로그: Git status의 1줄 `warning: could not open directory '.pytest_cache/': Permission denied`가 `[LOCAL_CHANGES_PRESENT]`로 오분류됨.
- 분류: PowerShell 5.1 native stderr/stdout 혼합은 PRODUCT_DEFECT; 테스트 캐시 ACL 접근 불가는 ENVIRONMENT_ISSUE (권한 실원인 미해결).
- GitHub 변경: `Git-Run`에서 `ErrorRecord`를 stderr로 따로 구분, `status --porcelain`의 stderr는 `[GIT_STATUS_INCOMPLETE]`로 명시적 fail-closed. 표준 생성물 `.pytest_cache/` Git ignore 추가. 기존 사용자 파일/캐시 삭제·권한 변경 금지.
- Windows 최신 동기화는 이 변경 이후 다시 검증 필요. `last-verified-pytest.txt`에는 여전히 이전 `3e697b3e...` 결과가 남음; 이번 HEAD PASS로 오인 금지. 기존 예약 작업 유지.

## 2026-11-21 — 프로젝트 방향 재확정: 스케줄러보다 WAN 실영상 한 컷

- 사용자 요청: 반복 예약 자동화 중단/보류. GitHub에서만 코드 수정, 로컬은 한 번 Pull 뒤 일회성 검증. 성공 가능성을 확인한 뒤 자동화 구축 여부 결정.
- 실행 계약: 기존 예약 작업은 사용자 PowerShell에서 1회 비활성화(원본/예약 작업 삭제 불필요). `run-comfyui-proof.cmd`로 단위 검사 후 WAN 2.2 P1 실 생성 검증. 모델/노드 미비 시 사전 실패, 실제 파일 다운로드 성공까지 한 번에 증거 수집.
- 템플릿 `workflows/wan22_5b_api.json` 사용, `workflows/ltx2_i2v_api.json`은 빈 파일이므로 제외. 본 프로젝트 유효성 증명은 영상 한 컷 P1, 전체 콘텐츠 자동화는 후속.
- GitHub 코드/단위 검증/Windows ComfyUI 연결/실제 GPU 영상 생성 결과를 구분 보고. Windows 실행 결과 확보 전 `NOT_RUN`.

## 2026-11-21 — 실영상 1컷 생성 성공, 화질 실패 원인과 재검증 설정

- **사용자 실제 Windows 증거:** ComfyUI에서 `WAN22` 로드, 샘플링 8/8, `Prompt executed in 64.24 seconds`. `run-comfyui-proof.cmd` 단위 검사 8개 PASS, 실제 MP4 `outputs/p1_comfyui/p1_c291b6686975_proof_95ba2d2b9c9a_00001_.mp4` 70,807 bytes 저장. 사용자 영상 프리뷰는 비현실적 왜곡과 색면으로 **시각적 품질 FAIL**. `GPU/API/MP4 PASS != CONTENT_QUALITY PASS`.
- **PRODUCT_DEFECT (평가 설정):** 기본 smoke 검증은 자체 생성한 가짜 산·하늘 PNG에 무협 인물을 요구하면서 512×320, 17프레임, 8스텝을 강제했다. 실 제작의 품질 검증에 이 설정을 사용하는 것은 부적절. 이 테스트는 연결 증명용으로만 유지하고 `[SMOKE_ONLY]` 표시.
- Windows 에이전트의 실제 파일 읽기: `E:\\ComfyUI_New\\ComfyUI\\input\\content_creator_identity_reference_portrait.png`는 896×1152 진짜 PNG, 1,340,385 bytes. `male_hero.png` 파일은 이름과 달리 JPEG 바이트. ComfyUI 시작 로그에는 RTX 4070 Laptop GPU, VRAM 8,188 MB / LOW_VRAM 표시.
- **변경:** `--quality --image <실제 PNG>`는 입력 파일의 PNG 형식·화면 방향을 검증하고 인물/복장/스타일 유지 프롬프트, 24샘플링 단계, 33프레임(24 FPS), 8GB 환경에 맞춘 576×768 세로/832×480 가로 설정을 적용. 기존 워크플로 템플릿/기본 smoke/영상 원본은 덮어쓰지 않고 `murim_p1/quality_...`로 신규 출력.
- **검증 범위:** GitHub 소스 구현과 단위 검사 추가; 품질 설정으로 Windows GPU 렌더와 영상 육안 판정은 **NOT_RUN / REVIEW_REQUIRED**. 높은 해상도와 단계 수는 시간이 더 걸리며 예술적 품질을 자동 보증하지 않는다. 우선 실제 참조 이미지로 비교한 후 필요 시 14B/LTX 기반 제작 품질 평가.
- **다음 한 단계:** Windows에서 1회 `git pull --ff-only origin main` 후 `run-comfyui-proof.cmd --quality --image "E:\\ComfyUI_New\\ComfyUI\\input\\content_creator_identity_reference_portrait.png"` 실행. 기존 에이전트/ComfyUI 상태 유지. 새 MP4 확인 후 영상 품질 별도 평가.
