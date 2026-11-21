## 2026-11-21 — SCAIL-2 검술 입력 준비 Windows 실행 PASS; CMD 즉시 닫힘은 정상 종료

- 사용자 보고: `E:\comfyui-scail\PREPARE-SCAIL2-SWORD.cmd` 더블클릭 후 CMD 창 즉시 닫힘. 실제 결과 확인 전 실패 단정 금지. 기존 CMD 정상 성공 분기는 `[PASS]` 출력 후 `pause` 없이 종료하도록 구현되어 있음.
- 기존 범용 Windows 파일 에이전트 읽기 전용 요청 `scail2-sword-prep-diagnose-20261121-a`, 응답 `res-scail2-sword-prep-diagnose-20261121-a.json` (Google Drive id `1qiW9pJsoAru_qPx_IRWLPVLF-DE5Ir7H`) status PASS. `comfyui-scail/logs/prepare-scail2-sword.log` size 312 bytes, 내용: `2026-11-21T20:15:02 START` → `20:15:04 PASS: input verified and staged for SCAIL-2; GPU render NOT_RUN.`, `20:15:51 START` → `PASS: existing source and 2s video verified against receipt.` → 초기 생성과 반복 실행의 idempotent 검증이 모두 PASS.
- Windows 파일 목록: `E:\comfyui-scail\ComfyUI\input\murim_sword_driving_2s.mp4` 실제 존재, `E:\comfyui-scail\sword-trial-input-report.json` 실제 존재, `samples\sword-pexels-4734306` 폴더 존재. 기존 `your_driving_video.mp4`와 `murim_character_reference.png` 그대로 존재. 모델/기존 ComfyUI 변경 없음.
- 판정: **INPUT_PREPARE_PASS / REPEAT_IDEMPOTENCE_PASS / GPU_RENDER_NOT_RUN**. 다음 한 단계: ComfyUI `http://127.0.0.1:8189`에서 `SCAIL-2-MURIM-SWORD-2S.json` 워크플로 로드 후 `실행` 1회, 생성 `SCAIL2_MURIM_SWORD_*.mp4`의 검·손 추종과 동작을 실제 육안 검증. CMD 재실행이나 신규 패치 불필요.

## 2026-11-21 — SCAIL-2 2초 무협 캐릭터/검술 동작 실험: Windows 파일 배포 PASS, 실행 대기

- 기준 확인: 사용자 검증 공식 `SCAIL2_FULL_00001.mp4` 2초 SCAIL Q3 동작 전이 재생 PASS. Windows 범용 파일 에이전트 read-only 응답 `res-scail2-sword-assets-readonly-20261121-a.json`: `E:\comfyui-scail\ComfyUI\input\murim_character_reference.png` 및 손상 없이 유지 중인 `your_driving_video.mp4`, 백업 파일 확인; 원본 ComfyUI 출력 `SCAIL2_FULL_00001.mp4`, PNG, audio.mp4 등 확인. `ComfyUI_New\ComfyUI\input` 307개 목록에서 sword_draw PNG 두 개 확인, 검술 motion MP4는 확인되지 않음. Windows 원본 `E:\ComfyUI_New` 보호.
- 테스트 1 — GitHub `12c8b9a5f0d8f0979523f8f28ccf659f0bdcb035`: `workflows/scail2/SCAIL-2-MURIM-IDENTITY-2S.json`, 공식 upstream pinned `2a0d3c0d613e206b4222d61462cf214304488ffd` JSON을 Q3 / 2초로 변형 후 참조 이미지 `murim_character_reference.png` 지정, output prefix `SCAIL2_MURIM_IDENTITY`. 실제 Windows `ComfyUI\user\default\workflows`로 CREATE PASS, `res-scail2-deploy-murim-identity-20261121-a.json`; SHA256 `79e71306dfb3a961bbde9afba75af883ce256ab56033d26a3cbfe50e507073a4`. GPU 렌더 NOT_RUN.
- 테스트 2 — GitHub `dab5e9c777e2213e6e8a51e44406955a61ce53d7`: `SCAIL-2-MURIM-SWORD-2S.json`은 identity 실험과 비교해 3개 노드 위젯만 변화 (VHS_LoadVideo video, SCAIL2EasyConfig video, VHS_VideoCombine output prefix). Q3, 2초 16fps 6steps, 동일 참조 인물 이미지는 그대로. `PREPARE-SCAIL2-SWORD.cmd`, `prepare-scail2-sword.ps1`는 Pexels `https://www.pexels.com/video/silhouette-of-a-person-holding-a-sword-4734306/` (creator Alex Ch, Pexels free-use license `https://www.pexels.com/license/`) 공개 목검 훈련 영상 다운로드 → 독립 실험 경로 `samples\sword-pexels-4734306\source.mp4` 보존 → 새 `ComfyUI\input\murim_sword_driving_2s.mp4` (H264 16fps 2초 + silent AAC)로 생성, ffprobe 검증. 기존 입력/사용자 파일이 있으면 충돌 중단, script 양쪽 원본 및 output SHA 영수증 `sword-trial-input-report.json`. 실패 시 `logs\prepare-scail2-sword.log`. Pexels 네트워크 다운로드 및 실제 동영상 모션 품질은 아직 NOT_VERIFIED.
- 사용자 Windows 동일 승인 `E:\comfyui-scail` 폴더로 검술 workflow / CMD / PS1 세 파일 CREATE PASS (`res-scail2-sword-trial-deploy-20261121-a.json`), SHA256 workflow `df0dcd37c8a56f0421e52d2e8c7462fff388e21ffb1e58f866e08150cb61b57a`, CMD `de66194a5233c09fcee56d6ef1e375ba10caf4acfc85a8087330a876d8b0d4e4`, PS1 `e02c277be9c2cfcf6fc79710114779b186e35d808785f161f424a37610190cef`. 변경 전 원본은 사용자 Windows agent preimage snapshot. GitHub vs Windows 배포 성공은 실제 렌더 PASS로 혼용하지 않음.
- 오프라인 감사: upstream expected Q4 → Q3/2s 변환, graph 27 노드 고유 id, 정확한 입력/출력 참조, identity variant와 sword variant의 3-node-only 차분, license/source/backup/fail-closed/무삭제 검사는 PASS. Python 테스트 파일 `tests/test_scail2_murim_identity.py`, `tests/test_scail2_sword_trial.py` 작성. Windows PowerShell 5.1 실제 다운로드·인코딩·GPU 영상 생성 = NOT_RUN.
- 다음 한 단계: 사용자는 **기존 8189 SCAIL 서버를 끌 필요 없이** `E:\comfyui-scail\PREPARE-SCAIL2-SWORD.cmd` 1회 더블클릭. [PASS] 후 SCAIL UI에 `ComfyUI\user\default\workflows\SCAIL-2-MURIM-SWORD-2S.json` 로드 및 Queue 1회. 영상에 검이 실제로 보이는지/몸 추종·손 접촉·검 길이 일관성을 실제 출력으로 판정. 8GB RAM/VRAM 속도·품질 및 AI 2x upscaling은 이 단계 성공 후 독립 후처리 실험으로 추진.

## 2026-11-21 — SCAIL-2 공식 예제 첫 GPU 영상 생성 및 사용자 동작 전이 평가 PASS

- 사용자가 Windows 미디어 플레이어에서 `SCAIL2_FULL_00001` 출력 영상을 재생 중인 스크린샷을 제공. 재생 UI에 전체 길이 00:00:02가 보이고 해안가 인물 이미지가 출력됨. 원본 입력은 `your_driving_video.mp4`. 사용자는 "your_driving_video.mp4 동작을 잘 따라합니다"라고 직접 평가. 이는 실제 8189 ComfyUI 워크플로의 산출물 생성·재생 및 2초 모션 전이의 사용자 관찰 PASS 근거임.
- 따라서 과거 2026-11-21 19:49 오디오 없는 MP4의 `VHS_LoadVideo` 실패는 **현재 렌더 경로에서 차단 문제가 해소됨**. 다만 `repair-scail-audio.log`/`scail-audio-repair-report.json` 원문 및 실제 출력 MP4 바이트·frame/sample 상세는 전달되지 않았으므로 복구 스크립트 내부 단계별 PASS는 추정하지 않음.
- 분리 판정: 설치/GUI/노드 그래프/생성 영상 재생 PASS (화면 및 사용자 보고), 2초 공식 동작 전이 사용자 평가 PASS, 정량 동작 유사도·원본과 생성본 전 프레임 비교 NOT_VERIFIED, 손·얼굴·신체·의상 시간적 일관성 NOT_VERIFIED, 무협 검술·검 위치/길이/접촉·무기 일관성 NOT_TESTED, 4축 REA 전체 구조 준수는 이 ComfyUI 실험과 별도.
- 기존 `E:\comfyui-scail` 모델 및 `E:\ComfyUI_New` 보존. 이미 성공한 SCAIL-2 Q3_K_M 8GB / `SCAIL-2-Q3-8GB-FIRST-TEST` / 2초 16fps 약 480x256/6steps 조건을 첫 검술 전이까지 baseline으로 유지. `SCAIL2EasyConfig.object_indices='True'`가 이전 로그에서 전체 인물로 해석되어 warning 발생한 점은 이후 차분 검증 과제로 유지. 성공한 예제와 별도 사본 워크플로 사용.
- 다음 한 단계: 사용 권한이 확보된 검술 driving clip과 캐릭터 참조 이미지로 **동일 조건의 2초 1회 검술 전이**를 구성. 변경 축은 driving video/ref image 입력만. 처음부터 모델, 리소스, steps, 해상도, 길이를 여러 개 동시에 변경하지 않음. 결과에 대해 포즈 추종, 좌우 손/검 접촉, 칼날 형상·길이 일관성, 얼굴/몸 일관성, 배경/카메라 안정성을 별도 평가. 실제 검술 입력 자산이 없으면 출력 PASS를 선포하지 않음.

## 2026-11-21 — SCAIL-2 첫 실제 Queue 실패: 공식 예제 무음 비디오의 VHS 오디오 추출 오류; 복구기 배포 PASS

- 사용자 2026-11-21 19:49 KST 실제 `SCAIL-2-Q3-8GB-FIRST-TEST` 실행 오류 리포트: `VHS_LoadVideo` Node 33에서 `VHS failed to extract audio from E:\comfyui-scail\ComfyUI\input\your_driving_video.mp4`; FFmpeg가 2048×1080 H264 16fps 4.06초 영상 스트림만 식별하고 `Output file does not contain any stream` 반환. `ComfyUI 0.33.1`, `PyTorch 2.8.0+cu126`, CUDA RTX 4070 Laptop GPU 8188MB 실제 구동 확인. 이전 rgthree 누락 UI 오류는 해소됐음. 분류 PRODUCT_DEFECT (공식 audio-free 샘플과 VHS 오디오 경로 불일치). 영상 생성/render NOT_RUN/FAIL, GPU OOM의 증거 없음.
- 공식 pinned `ComfyUI-VideoHelperSuite` `videohelpersuite/utils.py` `LazyAudioMap.__iter__`/`get_audio` 로직 검토: FFmpeg 무조건 `-f f32le -`로 오디오 디코딩하여 음성 없는 영상에서 예외 발생. VAE/모델 수정 또는 테스트 assertion 약화 금지.
- GitHub `hoonoh57/murim` 커밋 `ebc6314a7164cc6c5a84d7fd6bb0ffb692b8c61b`: `scripts/scail2/REPAIR-SCAIL-AUDIO.cmd`, `repair-scail-audio.ps1`, 오프라인 계약검사 `tests/test_scail2_audio_repair.py` 신규. 별도 임시 2초 H264 영상으로 FFmpeg `-c:v copy`+무음 AAC remux 시험 PASS (원본/출력 32개 영상 프레임 유지, 오디오 1개 신설), 단 사용자 PC Windows 구문/제품 실사용은 미검증.
- 현재 Windows 로컬 승인 작업공간 `E:\comfyui-scail`에 기존 파일 없는 복구 CMD/PS1 각각 **CREATE PASS**. 결과 `res-scail2-silent-audio-repair-deploy-20261121-a.json` (Google Drive ID `1f6-r2ACtssrTVY3aczxwnfXNVdnk-uxY`) `workspace_apply PASS`, SHA256 CMD `819113e711ac1bd757a1df09ceb53af03f7a0008af967ab2467cb4c444c2158d`; PS1 `f8feedcaa14a52562a461ffa59cefa95a6edaf28cde48ba6f085d789b11db18f`. preimage snapshot 기록. 승인되지 않은 로컬 폴더, 구 ComfyUI/대용량 가중치 불변.
- 단일 다음 작업: **8189 새 SCAIL 전용 서버 CMD 창만 정상 종료**한 뒤 `E:\comfyui-scail\REPAIR-SCAIL-AUDIO.cmd` 더블클릭. 스크립트가 official `samples\official-animation-001\driving.mp4`와 `input\your_driving_video.mp4` SHA 동일성을 검증하고, 백업 `input\your_driving_video.before_silent_audio.mp4`로 보존하면서 FFmpeg copy-video+silent-AAC, ffprobe로 1 video/1 AAC audio 검증, 8189 서버 재기동과 3개 노드 API 등록 확인. 성공 영수증 `scail-audio-repair-report.json`, 실패 로그 `logs\repair-scail-audio.log`. 그 뒤 브라우저 Ctrl+F5와 워크플로 1회 Queue. 실제 오디오/영상 GPU 렌더 PASS와 시각 검증은 별도로 판정. 정상 완료 후 첫 설치기에도 동일 샘플 audio-safe 준비 반영 필요.
- 별도 경고: `SCAIL2EasyConfig object_indices='True'`는 사용자 로그에서 empty/all-people로 자동 보정됨. 이번 에러 직접 원인은 아니며 추후 입력 의미를 감사할 것.

## 2026-11-21 — SCAIL-2 workflow rgthree Display Int 누락: 원격 복구 파일 Windows CAS 배포 PASS, 실행 미검증

- 사용자 ComfyUI 8189 화면에서 `SCAIL-2-Q3-8GB-FIRST-TEST.json` 그래프 로딩 확인. 단, `Display Int (rgthree)` 노드 한 종류 누락 경고. `GPU 영상/품질 PASS`로 표현하지 않음.
- 공식 `rgthree/rgthree-comfy` (고정 커밋 `bc48c6aaeca87bedbc14245d89f9bc6be37a630e`)의 `__init__.py` 노드 등록 및 `py/display_any.py` `RgthreeDisplayInt` 실체 확인; requirements.txt는 비어 있음. 원본 공식 SCAIL 예제 JSON에도 같은 노드 포함.
- GitHub `hoonoh57/murim` 구현 `06aa58ac895da010d19c02105bed093c70e3cccf`: 최초 설치기 `scripts/scail2/install-scail2.ps1` 패키지 목록에 rgthree 핀 추가, 복구 전용 `REPAIR-RGTHREE.cmd`/`repair-rgthree.ps1` 추가. 복구기는 `E:\comfyui-scail`만 대상으로 기존 8189 서버가 꺼져 있어야 실행하며 원본 충돌/기존 rgthree 파일 변경 시 fail-closed, 노드 API 등록 확인 후 서버 재시작.
- Windows 현 폴더 에이전트 Google Drive `res-scail2-rgthree-deploy-20261121-a.json` (ID `1mGcatrfNbzRMnS0JpYbtRzz2WxrgZGQ9`): `status=PASS`, 복구 CMD/PS1 2개 CREATE, before=null, SHA256 원본/로컬 영수증 일치. 복구 CMD `e4da87275ebe3ca7cdc0090ef92b74734041f29d258803ed65e73a2489b32021`, PS1 `9e3c4717db1b569315c70690f6f76b91f966367662628f09fb26b3dcf8c4fd24`. 기존 ComfyUI 모델·가중치 미삭제/미재다운로드. 전용 검증 8개 정적 체크 PASS, PowerShell 5.1 현 PC 구문 및 실제 복구 실행은 아직 NOT_RUN.
- 다음 1단계: 사용자 기존 8189 ComfyUI **서버 CMD 창만 정상 종료** 후 `E:\comfyui-scail\REPAIR-RGTHREE.cmd` 더블클릭. 정상 시 `logs\repair-rgthree.log`, `rgthree-repair-report.json` 생성과 8189 `/object_info`에서 `Display Int (rgthree)` 확인. 이후 워크플로 새로 로딩해 누락 표시 0, 실제 1회 큐 영상 렌더 및 육안 품질은 별도 판정.

## 2026-11-21 — SCAIL2 one-click installer 최종 로컬 소스 CAS PASS, 설치 실행 대기

- 실제 Windows 파일 에이전트 최종 응답: Google Drive `res-scail2-install-final-20261121-a.json` (ID `1ZrQS50iPpQDuRKluE7IhtmZ6Oy3Itp1V`) `status=PASS`, `workspace_apply=PASS`, `side_effects_possible=true`; `E:\comfyui-scail\INSTALL-SCAIL2.cmd` SHA256 `676f6bdb46f3f5e819c2f2077d366b95993eb873ef1eb2c3d2e0e516918e384d`, `install-scail2.ps1` SHA256 `84d30859cea8fe9de5ca709e44b989d359a04ea46119f066f774394df1b47510`. 구 README 파일 `README-SCAIL2.txt`도 원본 sha 확인 완료.
- 이 최종본은 GitHub `scripts/scail2/`의 최신 코드와 같다. 사용자의 기존 파일을 전혀 삭제하지 않고 CAS 안전 수정·독립 preimage snapshot까지 수행. 현재 허용된 Windows agent에는 명령 실행 기능이 없어 **실제 Windows 설치 프로그램은 NOT_RUN**. 별도 ComfyUI GPU/서버/노드/모션 렌더도 NOT_VERIFIED.
- 사용자 PC에서 필요 작업 하나: `E:\comfyui-scail\INSTALL-SCAIL2.cmd` 더블클릭. 로컬 코드가 Python3.12 / ComfyUI0.33.1 / PyTorch2.8 CUDA12.6 / pinned SCAIL GGUF·모델·커스텀노드, 모델 공유 및 8189 서버 검증과 공식 animation_001 데모 준비를 단일 호출로 실행. 기존 E:\ComfyUI_New 원본 보존. 실행 완료 리포트 `E:\comfyui-scail\setup-report.json`, 문제 발생 시 `logs\install-scail2.log`. 실제 사용량/성공 여부는 리포트 수신 후 판단.

## 2026-11-21 — SCAIL-2 설치 실행기 실제 Windows 로컬 파일 배포 PASS

- Windows E:\ workspace Google Drive 에이전트의 `workspace_apply` 실응답 `res-scail2-install-deploy-20261121-a.json`: E:\comfyui-scail 폴더에 `INSTALL-SCAIL2.cmd`, `install-scail2.ps1`, `README-SCAIL2.txt` 3개 CREATE PASS, original before=null, after SHA256 대조 완료. 해당 폴더는 사전에 빈 폴더로 확인됨.
- `res-scail2-install-ps51-fix-20261121-a.json`: PS5.1 UTF-8 안전 생성자 수정 1개 UPDATE PASS, 원본 CAS와 preimage snapshot 보존, after SHA256 확인. 재배포 이력은 기존 Windows 에이전트와 원본 ComfyUI를 변경하지 않음.
- 최종 실행기 정리: 성공 console은 정확히 `[PASS]` 한 줄(초기 구조에서 추가 출력 제거), 오류는 로그에 남기고 유지, ComfyUI 8189 정상 기동 시 브라우저 열기. GitHub와 로컬 최신 2파일의 CAS 일치 여부를 별도 영수증으로 확정해야 함.
- **아직 설치 작업을 Windows에서 실행한 것은 아님**: 현 로컬 agent 기능은 file CRUD만 있고 OS process 실행 명령은 없다. 사용자는 `E:\comfyui-scail\INSTALL-SCAIL2.cmd` 1회 더블클릭하면 설치/모델 재사용/누락 모델 다운로드/Python+PyTorch/노드 등록/8189 서버 검증을 연속 진행한다. 실제 GPU 생성/검술 품질은 사용자 시각 검증까지 NOT_RUN.

## 2026-11-21 — 별도 SCAIL-2 8GB 실험 설치기 제작 및 로컬 배포 단계

- 사용자 승인: 새로 만든 `E:\comfyui-scail` 폴더에 **최신 호환 SCAIL-2 전용 ComfyUI 별도 설치**, 기존 `E:\ComfyUI_New`는 원본 보존, 대형 기존 모델 경로 재사용, 설치/준비/검증은 Windows PowerShell5.1 **1회 CMD**로 처리.
- 사전 확인: 범용 Windows 에이전트 workspace=`E:\` read-only 영수증으로 `E:\comfyui-scail` 폴더 비어 있음을 확인, 기존 모델 폴더에는 `umt5_xxl_fp8_e4m3fn_scaled.safetensors`와 `wan_2.1_vae.safetensors` 존재. SCAIL 전용 GGUF/SAM3.1/CLIP H/21 LightX2V LoRA는 파일명 기준 미확인. 실제 ComfyUI GitHub v0.33.1에 SCAIL 핵심 노드 소스 존재.
- `scripts/scail2/install-scail2.ps1`, `INSTALL-SCAIL2.cmd` 및 실행 가이드 추가. ComfyUI v0.33.1 `72865f4`, dvelm SCAIL 저VRAM 원본 `2a0d3c0`, GGUF/VHS/KJNodes 버전 고정, Python 3.12 + PyTorch 2.8 cu126 isolated .venv, 원본 모델 공유는 `extra_model_paths.yaml` (junction 불필요). 미설치 가중치만 원본 출처에서 재개 가능 다운로드. **기존 ComfyUI source/models 절대 수정/삭제하지 않음**.
- SCAIL 원본 workflow 보존, 로컬 8GB 전용 Q3 파일명·2초 설정만 변경한 파생본 준비. 공식 SCAIL-2 개발팀 `animation_001`의 공개 driving/reference demo를 입력으로 준비(검술이 아닌 설치 기술 검증). 본인 캐릭터 입력은 별도 파일로 보존. 새 서버는 8189에서 실행/필수 노드 확인, 실제 렌더는 사용자 시각 검사 전 자동 큐잉하지 않음.
- 정적 오프라인 테스트 `tests/test_scail2_bootstrap.py` 4 PASS. **Windows 설치/CUDA/ComfyUI 8189/실제 SCAIL GPU 렌더 = NOT_VERIFIED**. 실행기 원본의 PS5.1 실제 파싱/설치 검증은 사용자 PC에서 1회 `E:\comfyui-scail\INSTALL-SCAIL2.cmd` 실행 및 `setup-report.json`/콘솔 영수증 후에 판정. 로컬 에이전트에는 shell 명령 실행 기능이 없으므로 원격 파일 CRUD로 CMD·PS1을 배치하되 실행을 허위 주장하지 않는다.


## 2026-11-21 — 로컬 LTX 성공 그래프 직접 감사 + 실증된 액션 원본 워크플로 shortlist

- 사용자 지시: 기존 사진+한국어 발화의 매우 좋은 LTX 영상은 **검증된 완성형 workflow의 효과를 보여주는 기준**이며, 무한 연장 루프를 제작하라는 뜻이 아님. 임의 설정 변경/새 워크플로 조립 금지, 최고 품질 무협 액션의 기존 성공 레시피 발굴·원본 재현·결과 단위 조합 우선.
- 실제 Drive Windows E:\ 로컬 read-only 영수증: `E:\ComfyUI_New\ComfyUI\user\default\workflows\ltx_author_workflow_real.json` 142,498B/60 nodes, `ltx_author_workflow_real2.json` 92,801B/55 nodes, 14-node FLUX DWPose, 10-node AnimateDiff. 원본 LTX GGUF 프리셋·오디오/영상·VHS 후처리 계열 파악. **현재 스크린샷 영상과 이 JSON 중 어느 버전의 완벽한 output pairing인지는 아직 추적 미완료.** 기존 그래프 변경하지 않음.
- 새로운 출처 검증: 공식 SCAIL-2 fighting/multi-ref/mask/DPO, 공식 Wan2.2 Animate Move/Mix, LTX IC-LoRA, community SCAIL2 Q3 low-VRAM과 The_frizzy1 Wan Animate GGUF 측정자료. 12GB RTX3060 실측 81f/480x864=7m05·peakVRAM11.7GB를 8GB 증거로 왜곡하지 않음. PC ComfyUI 0.20.1과 신형 패키지 요구 버전 불일치, 외부 API/신규 다운로드 무단 실행 금지.
- 상세 적용 프로토콜은 `docs/WUXIA_VIDEO_4070_BEST_PRACTICE_2026-11-21.md` 6절. 다음 한 단계: 검술 소유/라이선스 확인된 driving clip과 동작 시작 자세·검/손 실제 접촉 구성을 확보/심사하고 A/B 원본 워크플로의 독립 호환성 심사. PRODUCT QUALITY = NOT_VERIFIED; 기존 5B 검/손 FAIL 유지.

## 2026-11-21 — 무협 검·손 일관성 FAIL, best practice 선행 조사

- 사용자 영상 결과: WAN 2.2 GPU MP4 생성 성공, 그러나 검이 손과 분리되고 소품/신체 동작이 무너지는 **콘텐츠 품질 FAIL**. 기존 5B 스텝·프롬프트·해상도만 반복 수정한 접근은 제작용 best practice가 아니었음.
- 조사 SSOT: `docs/WUXIA_VIDEO_4070_BEST_PRACTICE_2026-11-21.md` (ComfyUI 공식 Wan2.2 Animate, 2026 SCAIL-2/Wan-Animate-2, 저VRAM, Blender prop rig, 공식 강의와 커뮤니티 실패/성공 사례).
- 실제 PC: RTX4070 Laptop VRAM 8,188MB / RAM32GB, ComfyUI 0.20.1 / Python 3.13, 설치된 5B 및 14B I2V FP8/GGUF, 관련 LoRA/노드, sword pose/canny/identity 파일. **I2V 14B와 Animate 14B 가중치는 다르다.** 신형 SCAIL2 저VRAM 워크플로 요구 ComfyUI 0.33.1+와 불일치.
- 코딩·설치·GPU 반복 렌더 보류. 다음: 사용권 확인된 1인 1~2초 검술 driving motion 및 시작 포즈·캐릭터 identity·hand/sword rigid control 자산 심사 → 공식 워크플로 호환성/라이선스/8GB 비용 검토 → 독립 환경에서 제한된 1회 품질 검증. 기능 PASS≠품질 PASS.
- 현재: RESEARCH_BASELINE_DOCUMENTED, WUXIA_VISUAL_QUALITY_FAIL, NEW_PIPELINE_NOT_IMPLEMENTED, NEW_GPU_QUALITY_TEST_NOT_RUN.

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
