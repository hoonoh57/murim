# AGENTS.md — Murim GitHub 원본 개발 / Windows 실행 계약

**적용 저장소:** `hoonoh57/murim` (`main`)  
**Windows 목표 경로:** `E:\gpt\projects\comfyui\murim`  
**제정:** 2026-11-21

## 1. 우선순위와 책임

- 이 저장소의 소스, README, ComfyUI 워크플로 JSON, 테스트, 문서 및 제품 기능 CRUD는 **GitHub에서만 수행**한다. Windows는 동기화된 파일의 **실제 실행·검증 소비 환경**이다.
- 이전 로컬 직접 CRUD를 성공시킨 중앙 Windows runner 이력과 이번 GitHub-원본 운영 방식은 구분한다. 기존 runner가 다른 프로젝트에서 성공한 사실만으로 이 Windows 경로가 등록·작동한다고 단정하지 않는다.
- 작업 시작 시 이 문서 → `README.md` → `docs/CURRENT_STATE.md` → `docs/SESSION_HANDOFF.md` → 변경 대상 파일을 읽고 현재 GitHub HEAD와 필요한 실제 Windows 상태를 확인한다. 기존 기능과 사용자 자산을 보존한다.
- 콘텐츠 제작의 고유 설계는 **4-GATE + 멀티 에이전트**다. 새 기능은 기존 Director/Writer/Council/Imaging/Video/Audio/Camera/Art Direction/Marketing 경계를 우선 재사용한다. 거래 시스템의 REA 구조를 무관한 이 프로젝트에 기계적으로 강제하지 않는다.

## 2. 빠른 원격 집중 개발

1. GitHub `main`에서 변경 전 HEAD·대상 원본 내용·다른 사용자 변경을 확인한다.
2. 관련 변경을 논리적으로 나눠 **원격에서 연속 수정→정적/국소 검증→오류 복구**한다.
3. 파일 하나마다 Windows 테스트/Actions/push·pull/승인을 반복하지 않는다. 여러 파일 변경을 한 Git commit/tree 체크포인트로 묶는 것을 우선한다.
4. 최종 통합에서 **필요한 Windows 실제 테스트만** 실행한다. GitHub Action은 Windows 실행 진입점이 정식 연결된 경우에만 최종 테스트용으로 사용하며 파일별 확인 용도로 남발하지 않는다.
5. 저장소 커밋, GitHub 검사, Windows 실제 ComfyUI 렌더, 최종 영상/음성/자막 품질 PASS는 각각 별도 기록한다.

## 3. Windows 동기화와 보호

- Windows 작업공간은 자동 생성된 **소비용 클론**이 목표다. `windows-test.cmd`는 GitHub `origin/main`을 읽어 안전한 `--ff-only` 갱신을 시도한 뒤 테스트한다.
- **자동 덮어쓰기는 원본 보호를 충족하는 범위**에서만 허용한다. 기존 staged/unstaged/untracked/ignored 파일, 인증정보, 사용자 생성 산출물에 충돌·손실 위험이 있으면 fail-closed로 중단하고 원인을 기록한다.
- `git reset --hard`, `git clean`, force-push, 예기치 않은 삭제, 비밀/모델 가중치/미디어 원본의 Git 전송, Windows 로컬 소스 수동 편집을 금지한다.
- `E:\gpt\projects\comfyui\murim` 경로에 **실제로 자동 동기화 실행기가 설치/연결/검증됐다고 주장하지 않는다**. 예약/runner 트리거가 없으면 기능상 '준비된 실행 진입점'으로만 기록한다.
- Windows 테스트는 승인된 실행 계정과 실제 Python/ComfyUI/GPU 환경에서만 실행한다. 사용자에게 비밀번호나 장치 토큰을 요구하지 않는다.

## 4. ComfyUI 콘텐츠 자동화 방향

기존 4-GATE 파이프라인을 유지하며 **시나리오→장면·캐릭터→ComfyUI 이미지/비디오→내레이션/TTS/BGM/SFX→자막·편집→마케팅 패키지→사람 게시 승인**으로 확장한다. 모델·노드·워크플로 변경 시 버전/시드/프롬프트/라이선스 및 재현 조건을 기록한다. 승인 없는 채널 게시나 라이선스 불명 자산 사용은 하지 않는다.

## 5. 보고 방식

각 작업은 **변경 내용 / 검증 증거 / 미실행 범위 / 현재 상태 / 다음 한 단계**만 간결하게 보고한다. 상태는 `docs/CURRENT_STATE.md`, 다음 세션의 진입점은 `docs/SESSION_HANDOFF.md`에서 관리한다. 테스트를 돌리지 않았으면 `NOT_RUN`, Windows 연결이 미확인이면 `NOT_VERIFIED`로 기록한다.
