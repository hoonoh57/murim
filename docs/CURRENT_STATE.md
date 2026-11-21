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
