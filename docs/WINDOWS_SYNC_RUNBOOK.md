# Murim Windows 자동 동기화 및 실제 ComfyUI 검증 안내

> **GitHub 개발 원본:** https://github.com/hoonoh57/murim (`main`)  
> **Windows 실행 클론:** `E:\gpt\projects\comfyui\murim`  
> **상태:** GitHub 코드 준비 완료. **Windows 작업 등록/실행은 아직 검증되지 않음.**

> **2026-11-21 우선순위 변경:** 이 문서의 10분 예약 자동 동기화 절차는 현재 **보류**다. 사용자 결정에 따라 예약 작업을 비활성화하고, GitHub에서 수정한 뒤 Windows에서 한 번 Pull해 `run-comfyui-proof.cmd`를 실행하는 **실제 ComfyUI WAN 한 컷 검증**을 먼저 진행한다. 성공 후에만 예약 자동화를 재검토한다.

## 1. 기존 runner와 자동 동기화의 역할 구분

- 기존 `hoonoh57/agent`의 GitHub Actions self-hosted runner는 *해당 저장소에서 승인된 고정 연산*에 연결되어 있다. 다른 저장소의 모든 명령이 자동으로 실행되는 범용 PC 에이전트는 아니다.
- `murim`은 **GitHub에만 코드를 기록**한다. 각 커밋마다 GitHub Actions를 실행하지 않으려면 Windows Task Scheduler가 `scripts/windows-sync-test.ps1`을 **주기적으로 실행**하면 된다.
- Task Scheduler는 실제 사용자 계정으로 동작하도록 등록한다. 과거 runner 서비스 계정 `NETWORK SERVICE`에서는 사용자 Python·ComfyUI·GPU 접근이 다를 수 있으므로 작업 계정과 Python 경로를 분리 확인한다.
- 최초 1회 클론/정확한 `origin` 확인/작업 등록은 필요하다. 이 저장소의 파일만 GitHub에 넣었다고 Windows 작업이 등록되지는 않는다.

## 2. Windows 최초 한 번 준비

**절대 기존 폴더를 빈 폴더라고 가정하여 삭제하거나 강제 덮어쓰지 않는다.**

1. `E:\gpt\projects\comfyui\murim`의 기존 파일, `.git`, 사용자 수정과 `git remote -v`를 읽기 전용으로 확인한다.
2. 이미 `hoonoh57/murim`의 정상 클론이면 변경을 보호하면서 `git pull --ff-only origin main`으로 원격 코드를 한 번 반영한다. 깨끗한 새 폴더가 **확인**된 경우만 신규 클론을 만든다.
3. 해당 Windows PC에서 **한 번만** 아래 명령을 실행하여 일반 사용자 로그온 계정의 예약 작업을 등록한다. Windows에서 직접 실행할 수 있는 연결된 에이전트 작업이 있다면 그 경로에서 수행한다. 없다면 최초 한 번 PC의 작업 등록은 필요하다.

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "E:\gpt\projects\comfyui\murim\scripts\install-windows-task.ps1"
```

설치된 예약 작업: `Murim-GitHub-Sync-Test` (로그온 시 + 기본 10분 간격).

작업 등록 스크립트는 지정 경로가 **정확한 저장소 루트**, `origin`이 `hoonoh57/murim`인지 확인하며, 같은 이름의 기존 예약 작업을 무단 덮어쓰지 않는다. Windows 소스 파일을 직접 편집하거나 인증정보를 생성하지 않는다.

## 3. 자동 동기화 동작

```text
GitHub main 커밋 → 최대 10분 이내 다음 Windows Task Scheduler 실행
    → 실제 로컬 저장소/원격/브랜치/사용자 변경 검사
    → git fetch origin main
    → git merge --ff-only origin/main
    → 같은 HEAD가 테스트 성공했던 기록이면 pytest 생략
    → 아직 성공 검증되지 않은 HEAD면 python -m pytest -q tests
    → 통과한 HEAD를 %LOCALAPPDATA%\Murim 에 기록
```

- Windows 작업공간의 staged/unstaged/untracked 변경이 있으면 **중단**, 자동 삭제나 force reset을 하지 않는다.
- 사용자 `.env`, `outputs/`, 모델, 렌더 산출물 등 ignored 파일은 안전하게 보호해야 하며, Git이 기존 비추적/무시 파일과 충돌하는 변경을 가져오려 하면 강제로 진행하지 않는다.
- 마지막 성공 SHA 마커는 Git 외부의 `%LOCALAPPDATA%\Murim\last-verified-pytest.txt`에 저장한다. 검사 실패 시 마커를 갱신하지 않아 다음 예약 실행에서 재검사한다.
- **GitHub Actions는 소스 변경마다 실행되지 않는다.** Windows Task Scheduler 로그의 최종 실행 결과와 성공 마커는 별개이며, 원격 push 성공을 Windows PASS로 표현하지 않는다.

## 4. 실제 ComfyUI 검증 구분

다음 3개 판정을 혼동하지 않는다.

1. **로컬 연결 검사:** `windows-test.cmd -RequireComfy`는 `GET http://127.0.0.1:8188/system_stats`를 호출해 서버의 응답 여부를 확인한다. 포트는 실제 서버 설정에 맞춰 옵션으로 변경한다. 이 검사는 생성 성공이 아니다.
2. **실제 생성 검사:** 검증된 API 워크플로 JSON을 `POST /prompt`로 큐에 넣고 반환된 `prompt_id`의 `GET /history/{prompt_id}` 결과를 확인하며 실제 출력 파일이 존재하는지 검사한다. 모델/입력 파일/커스텀 노드와 GPU/VRAM 확인 후 실행한다.
3. **영상 수용 검사:** 완성 MP4를 열어 화면·음성·자막·싱크·장면/캐릭터 일관성과 오류 로그를 확인한다. 생성 API 통과만으로 영상 품질 PASS를 선언하지 않는다.

**현재 발견된 워크플로 주의사항:** `workflows/wan22_5b_api.json`은 `LoadImage`의 `example.png` 입력 및 WAN/CLIP/VAE 모델 파일을 요구한다. `workflows/ltx2_i2v_api.json`은 현재 GitHub에서는 내용이 비어 있다. 따라서 현재 상태에서는 아무 워크플로나 무조건 제출하지 말고, 실제 Windows 설치 자산·노드/모델 확인 후 한 장면 P1 작업을 연결해야 한다.

## 5. 검증·실패 분류 및 다음 단계

- **GitHub HEAD/문서/스크립트:** GitHub 소스가 존재한다는 증거.
- **작업 등록:** `Get-ScheduledTask -TaskName Murim-GitHub-Sync-Test`와 Windows의 실제 LastRunTime/LastTaskResult가 있어야 확인된다.
- **동기화/pytest:** Windows 실행기의 현행 SHA와 실제 pytest 결과가 있어야 한다.
- **ComfyUI API/렌더/영상:** 각각 실제 응답, 출력 파일, 최종 눈·귀로 확인한 영상이 필요하다.

실패는 `ENVIRONMENT_ISSUE`(경로/계정/Python/GPU), `PRODUCT_DEFECT`(파이프라인), `TEST_DEFECT`(검사기), `AUTHORITY_DRIFT`(원본/정책), `UNKNOWN`으로 먼저 분류한다.

**다음 한 단계:** Windows의 해당 경로·원격 및 사용자 변경을 안전하게 확인하고 위 예약 작업을 최초 1회 등록해 실제 동기화·pytest 증거를 얻는다. 그 뒤 WAN 입력과 모델을 확인한 **실제 ComfyUI 영상 한 컷 생성**으로 진행한다.

참조: [Microsoft ScheduledTasks](https://learn.microsoft.com/en-us/powershell/module/scheduledtasks/register-scheduledtask), [ComfyUI 서버 API](https://github.com/Comfy-Org/docs/blob/main/development/comfyui-server/comms_routes.mdx).


## 6. 기존 폴더가 Git 저장소가 아닐 때 (최초 부트스트랩)

Windows PowerShell에서 `git -C E:\gpt\projects\comfyui\murim pull`이 `not a git repository`를 반환하면 **pull할 대상이 아직 없는 상태**다. 이어서 `scripts/install-windows-task.ps1`을 실행하면 로컬에 체크아웃되지 않았으므로 파일이 없다는 오류가 발생한다.

`scripts/bootstrap-windows-murim.ps1`이 이 문제를 한 번에 처리한다.

- 목적 경로는 `E:\gpt\projects\comfyui\murim`으로 고정하며, junction/symlink 및 다른 경로를 거부한다.
- **폴더가 없거나 비어 있으면:** GitHub `hoonoh57/murim`를 최초 clone → 예약 작업 등록.
- **같은 Git 클론이 이미 있으면:** 사용자 변경이 없는지 확인 → 안전한 기존 sync 스크립트 실행 → 예약 작업 확인.
- **기존 파일이 있고 `.git`이 없으면:** 어떤 파일도 삭제·이동·덮어쓰지 않고 `[NONEMPTY_NOT_GIT]`으로 중지한다. 로컬 파일 실사 후 병합/보존 방법을 별도로 확정한다.
- 성공 뒤에는 10분 단위 Windows Task Scheduler가 변경을 감지하며 **매 커밋마다 GitHub Actions를 호출하지 않는다**.
- `-ProbeComfy`는 선택 옵션으로 로컬 `/system_stats` **연결만** 검사한다. 진짜 이미지/영상 생성 검증은 별도 단계다.

부트스트랩은 `README.md`와 기존 제품 소스를 덮어쓰지 않는다. 검증된 `main` commit에 고정된 스크립트를 사용할 것을 권장한다.
