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
