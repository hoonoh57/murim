# Murim 무협 액션 영상: RTX 4070 Laptop 8GB Best Practice 검토

**조사 시점:** 2026-11-21  
**판정:** 문헌·실제 로컬 자산 조사 / 모델·워크플로 호환성 검토. 새 코드·모델 설치·GPU 추가 렌더 없음.

## 1. 핵심 결론

이전 검증의 WAN2.2 5B 입력 이미지·8→24 스텝·화면 크기·프롬프트 변경은 **GPU/API/파일 생성의 연결 검증**에는 적합했으나, 검과 손의 연결, 무술 동작, 장면 간 캐릭터 일관성을 보장하지 못한다. 실제 사용자 영상에서도 검·손 분리 및 얼굴·의상 변형을 확인했다. 더 많은 스텝과 고해상도가 이 구조적 문제를 해결한다는 근거가 없다.

**올바른 제작 순서는:** 저작권 또는 사용권이 확인된 **검술 동작 영상/모션캡처** 확보 → 그 동작과 첫 자세·화각이 맞는 **일관된 인물 레퍼런스** → **동작 전이/pose·mask 제어** → 검을 손에 실제로 고정하는 3D rig 또는 후처리 합성 → 짧은 샷 검증 → 통과한 workflow만 제작 자동화. 검은 일반 사람 skeleton 관절만으로 추적되지 않으므로 검의 손잡이, 강체 길이, 궤적은 별도 검증·제어 대상이다.

## 2. 사용자 PC에서 실증된 조건

| 구분 | 확인한 로컬 상태 | 실무상 영향 |
|---|---|---|
| GPU | NVIDIA RTX **4070 Laptop** 8,188 MB VRAM, 32GB RAM | 데스크톱 RTX4070 12GB 벤치마크와 다름; CPU offload 시간 고려 |
| ComfyUI | E:\ComfyUI_New\ComfyUI, comfyui_version.py=**0.20.1** | 신형 SCAIL-2 워크플로의 요구 버전과 차이; inplace 업데이트 금지 |
| Python | python_embeded, **3.13** | SCAIL-2 공식 환경 Python 3.10~3.12와 직접 호환 미입증 |
| 일반 WAN | WAN2.2 TI2V-5B FP16, WAN2.2 I2V-14B High/Low FP8 | **일반 I2V는 Animate/동작 전이 모델이 아님** |
| 양자화 | WAN2.2 I2V-14B High/Low Q4_K_S, Q5_K_S GGUF, ComfyUI-GGUF | 기존 설치만으로 독립 품질 벤치 가능; offload 속도 우려 |
| 가속 | WAN I2V High/Low LightX2V·Lightning 4-step LoRA | LoRA가 요구하는 모델·스텝·CFG·샘플러 쌍을 지켜야 함 |
| 노드 | comfyui_controlnet_aux, Advanced-ControlNet, AnimateDiff-Evolved, KJNodes, VideoHelperSuite, IPAdapter 등 | 폴더 존재는 확인. 특정 노드/버전 기능은 별도 점검 |
| 레퍼런스 | identity_reference_portrait, character_sheet, pose_04_sword_draw, canny_04_sword_draw 등 | 파일 존재 확인. **정지 PNG가 연속 driving video를 대체하지 않음** |
| LTX | LTX-2.3 22B FP8, distilled Q4, text projection, VAEs | 기존 자산은 있음. GPU 8GB 및 무협 소품 제어는 미검증 |
| P1 영상 | 5B 실제 64.24초 생성, MP4 유효 | **파일 생성 PASS / 시각적 품질 FAIL** 분리 |

## 3. 공개 문헌 기반 기술 우선순위

### A. SCAIL-2 (2026.06, motion transfer 연구 1순위)

공식 2026년 공개 모델. Driving video → 캐릭터, reference mask·driving mask, **multi-reference**를 지원하며 공식 저장소에 **Fighting.mp4** 예제가 있다. 기존 DWPose 중간 지도만으로 표현하기 어려운 복잡한 동작을 직접 입력 영상 기반으로 처리하는 방향. 공식 자료에는 배경/인물 영역별 mask 의미가 명시돼 있다. 8~12GB용 GGUF 커뮤니티 워크플로는 있으나 **원 PC RTX4070 8GB에서의 동일 품질/속도는 아직 확인되지 않음**. 그 워크플로는 ComfyUI **0.33.1+**를 요구하며 약 8.1GB GGUF 모델을 RAM offload할 수 있으므로 현재 0.20.1/32GB RAM 설치에 무단 도입 금지.

공식: https://github.com/zai-org/SCAIL-2  
8GB 레시피(커뮤니티): https://github.com/dvelm/SCAIL-2-Unlimited-Video-Low-VRAM  
설치 조건: https://github.com/dvelm/SCAIL-2-Unlimited-Video-Low-VRAM/blob/main/INSTALL.md

### B. WAN2.2 Animate (공식 Move / Mix: 기술 교육 1순위)

ComfyUI 공식 영상: 레퍼런스 인물 이미지 + 동작 동영상, DWPose·분할 마스크·첫 프레임 맞춤. Move는 캐릭터를 동작 영상처럼 움직이게 하고 Mix는 기존 영상의 인물 교체. Wan 개발팀은 실제로 **체형·초기 포즈 차이와 다인물/추적 실패**를 명시해 경고한다. 이 공식 워크플로는 현재 설치된 **WAN2.2 I2V-A14B** 모델과 *서로 다른* Animate-14B 가중치가 필요하다. 단순히 기존 14B를 노드만 바꾸어 쓰지 않는다.

한국어 공식: https://github.com/Comfy-Org/docs/blob/main/ko/tutorials/video/wan/wan2-2-animate.mdx  
개발팀 안내: https://github.com/Wan-Video/Wan2.2/blob/main/wan/modules/animate/preprocess/UserGuider.md  
ComfyUI 공식 영상 강의: https://www.youtube.com/watch?v=-zJm53J7r9s  
시연+설정 강의(MDMZ): https://www.youtube.com/watch?v=tSaJuj0yQkI

### C. WAN-Animate-2 (2026.08: 차세대 비교 기준)

개발팀 공식 구현은 driving video를 중간 skeleton으로만 간접 제어하지 않고 모델에 입력하는 방식, view control 및 distilled 파이프라인. **공식 README의 720p 구성은 8×A800 GPU 기준**, 480p 역시 2×A800 시험으로 제시되었다. 현 RTX4070 Laptop 8GB 로컬 영상 엔진으로 즉시 추천하지 않는다. 별도 고VRAM/외부 GPU 기술 비교 기준이다. 외부 파일 업로드·유료 사용은 별도 사용자 승인 필요.

공식: https://github.com/Wan-Video/Wan-Animate-2  
ComfyUI 공개 workflow: https://comfy.org/hub/workflows/wan-animate-2-motion-transfer-9394f9968da3/  
2026-08 빠른 동작 시연: https://www.youtube.com/watch?v=-OnJS4JA-v4

### D. 기존 WAN2.2 I2V-14B High/Low GGUF (로컬 비교 1순위, 검술 제어용 아님)

이미 두 개의 High/Low Noise Q4_K_S 및 Q5_K_S GGUF, 모델 로더와 관련 LoRA가 설치돼 있다. 공식/검증된 양전문가(two-expert) 워크플로만 기준선으로 삼아 모델 품질, VRAM, CPU 오프로드, 시간 비교. **서로 다른 4-step LoRA/기본 24-step을 임의 혼용하지 않는다.** 얼굴·장면 품질 비교에는 유용할 수 있으나 sword+hand joint contact의 시간적 연속성을 직접 보증하지 않는다.

기본 공식 WAN2.2: https://github.com/Wan-Video/Wan2.2  
GPU/노드 메모리: https://github.com/kijai/ComfyUI-WanVideoWrapper  
저VRAM 공개 workflow와 모델 구분: https://github.com/Thefrizzy1/The_frizzy1-Workflows  
실제 4070 Laptop 8GB의 실패 사례: https://www.reddit.com/r/comfyui/comments/1vyv80l/generating_videos_on_8gb_vram/

### E. FramePack 및 LTX (목적별 예비 후보)

**FramePack:** 개발팀 공식 6GB VRAM·60초 지원, 노트북 생성 속도는 데스크톱보다 상당히 느릴 수 있음. 긴 비전투 샷/장면 연장에 적합하지만 검-손 소품 결합 문제의 직접 해법 아님.

**LTX-2.5 motion IC-LoRA:** sparse motion tracks/pose/depth와 구조 제어를 제공하지만 공식 시스템 권장 **32GB+ VRAM**. 8GB 관련 커뮤니티 작업과 공식 요구가 다르므로 당장 기본 엔진으로 삼지 않는다. LTX2.3이 설치돼 있다고 LTX2.5 가중치/LoRA가 준비됐다고 주장하지 않는다.

FramePack 원개발: https://github.com/lllyasviel/FramePack  
LTX 공식 GPU 조건: https://docs.ltx.io/open-source-model/getting-started/system-requirements/  
공식 motion control: https://docs.ltx.io/open-source-model/feature-guides/structural-control/motion-control/

### F. 무협 검/손 소품의 물리적 제어: rigging + 합성

1. 손에 붙은 검은 사람 skeleton만으로는 자세·검신 방향·강체 길이 보장이 불가능하다. Blender에서 검 3D 오브젝트를 해당 손 bone에 **parent/constraint**로 연결하면 source 프리비즈 단계에서 그 관계가 보존된다.
2. 검술 연속 동작은 **권리 확인된 실제 촬영 영상** 또는 Adobe Mixamo/라이선스 확인된 combat FBX 등으로 구성. 3D rig를 이용해 모션에 따라 검을 움직인 뒤 driving video, pose/canny/depth 가이드 또는 소품 합성 pass로 활용한다.
3. 최종 생성 영상에서 칼이 분리되면 프레임 보간·프롬프트 재시도보다 **motion driver, 첫 포즈, mask, 손-검 constraint**를 수정한다.
4. 액션은 발도→베기→반응 등 **1~3초 샷**으로 분리해 편집한다. 카메라 고정·1인·한 검부터 PASS 후 다인 교전/카메라 이동으로 확장.

Blender bone parenting: https://docs.blender.org/manual/en/5.2/scene_layout/object/editing/parent.html  
Adobe Mixamo 사용권: https://helpx.adobe.com/kr/creative-cloud/faq/mixamo-faq.html  
검술 motion 후보 예시(개별 라이선스 확인): https://cosindra.ai/motionsmith/free-animations/combat

## 4. 동작·화질 재현성 평가 기준

| 게이트 | 확인할 것 | 실패 시 먼저 조사 |
|---|---|---|
| A 동작 입력 | 정확한 1개 발도/베기 driving video, 첫 자세/검 유무/프레이밍 일치 | motion source와 시작 프레임 |
| B 인물 일관성 | 전후 얼굴·헤어·의상·검 모양, 장면 간 identity | reference sheet/multi-reference/mask |
| C 신체와 검의 접촉 | 손잡이-손 분리 없음, 검신 길이·방향·궤적 일관성 | rigging, mask/prop tracking, 3D+합성 |
| D 연속성 | 깜빡임·분절·관절 비정상·부자연스러운 발 이동 없음 | frame conditioning, shot 분할 |
| E 하드웨어 | peak VRAM/RAM, CPU offload, 초/프레임, OOM, 모델/노드 버전 기록 | 실제 측정 후 quant/오프로딩 조정 |
| F 승인 | 전체 프레임/고정 구간 WYSIWYG 확인, 사람이 품질 PASS | 기능상 MP4 PASS를 콘텐츠 PASS로 승격 금지 |

**1차 베이스라인:** 한 인물이 칼을 뽑는 **1~2초 고정 카메라 샷**, 저작권/사용권 검증된 driving video, 검이 있는 레퍼런스 이미지, 최초 프레임 포즈 일치. **검과 손이 한 프레임이라도 명백히 분리되면 품질 FAIL**. 통과 workflow의 원본 JSON/모델 SHA/LoRA/step/CFG/sampler/seed/입력 자산·fps/컴퓨팅 시간을 잠근다.

## 5. 진행 순서 / 변경 금지

**G0 연구 PASS(문헌/설치 파일):** 공식 구현, 저VRAM 사례, 설치 모델·노드·GPU·버전 확인. 2026-11-21 본 문서로 현재 기준선 확보.

**G1 준비(아직 미완료):** 사용권 검토된 검술 driving clip/모션 파일, 캐릭터 레퍼런스와 동일 첫 자세, 검 손잡이 tracking/rig 방법 확보. SCAIL-2/Wan2.2 Animate의 정확한 노드/가중치/패키지/VRAM/ComfyUI 버전 차이를 검토. **새 코드, 대규모 다운로드, ComfyUI 원본 inplace 업데이트, 무분별한 GPU 반복 테스트 금지.**

**G2 단일 승인 실험(미시작):** 기존 ComfyUI 보존, 필요 시 분리 설치. 공식 또는 출처 추적 가능한 원본 워크플로 1개만 선택해 1~2초 단일 무협 액션 검증. VRAM·시간·실제 프레임을 모두 기록. 문제는 모델 defect / motion control defect / input mismatch / environment issue 등으로 분류.

**G3 Murim 통합(미시작):** 동작·검·얼굴·영상 연결이 확실히 PASS한 방법만 기존 4-GATE와 실제 콘텐츠 생성으로 이식. 자동화·장편 제작·새 기능 개발은 그 이후.

**현재 전체 판정:** RESEARCH_BASELINE_DOCUMENTED / CURRENT_GPU_RENDER_FUNCTIONAL / WUXIA_VISUAL_QUALITY_FAIL / NEW_CONTROL_PIPELINE_NOT_VERIFIED. 이 문서는 보증된 단일 만능 워크플로의 발표가 아니라 공식 증거와 로컬 제약으로 후보를 선별한 운영 판단이다.


## 6. 실제 성공 워크플로를 기준으로 하는 '최고 품질' 제작 방식 (2026-11-21 추가)

**사용자 재확정:** 한 장의 사진·한국어 대사로 높은 완성도의 영상이 나온 기존 LTX 워크플로를 보여준 것은 '마지막 프레임 무한 반복' 자체를 개발하라는 뜻이 아니다. **검증된 최고의 제작법을 발굴·재현·조합하고, 무협 액션의 손/검/신체/인물 일관성을 대형 상용 생성형 서비스 수준에 가깝게 끌어올리라**는 품질 기준이다. 우선 문헌/작동 예제와 실제 8GB 제약을 조사하고, 제품 코드를 새로 쓰지 않는다.

### 6.1 사용자 PC 내 검증 자산 (Drive↔Windows 로컬 에이전트가 read-only로 직접 조회)

| 로컬 원본 | 실제 조사 증거 | 활용/주의 |
|---|---|---|
| `E:\ComfyUI_New\ComfyUI\user\default\workflows\ltx_author_workflow_real.json` | 원본 JSON 142,498 bytes, **60 nodes**; `DenoLTX23PresetLoader`는 'GGUF Style' 및 로컬 Q4, Gemma FP4, video/audio VAE를 선택. `DenoLTXPromptGuide`, 다중 이미지, AV latent, VHS 영상 저장·보간·후처리 계열 | **최우선 보존/기준선**. 사용자 제시 스크린샷의 LTX 제작 계열과 연결된 로컬 그래프이지만, 특정 결과물이 정확히 어느 저장 버전에서 나왔는지는 출력 메타데이터 검증 전 확정하지 않는다. 자체 새 그래프로 재구축하지 않는다. |
| `.../ltx_author_workflow_real2.json` | 원본 JSON 92,801 bytes, **55 nodes**; 동일 프리셋, 단계별 샘플러·latent upscale·tiled decode·VHS AV 출력 구성 | 이미 있는 고품질 변형 워크플로. 품질 비교 시 원본 보존. |
| `.../flux_dwpose_workflow.json` | 14 nodes: DWPose video preprocessing / FLUX GGUF / ControlNet / image output | **자세 제어 자산**으로 재검토. 3D 검-손 물리 결합이나 동작 전이 전체의 대체물이 아님. |
| `.../animate_video_workflow.json` | AnimateDiff 구형 10 nodes | 참고 이력이지 최고 품질 무협의 기본 엔진으로 자동 승격하지 않음. |

실제로 성공한 **8초 한국어 동기 발화 LTX 영상은 사용자 스크린샷과 사용자의 관찰**로 유력한 제작 기준선이다. 단, 전체 영상의 객관적 품질·프레임별 손/소품·재현성을 제가 별도로 평가한 결과라고 표현하지 않는다. 저장된 그래프/모델·각 출력의 정확한 대응은 추후 메타데이터로 확인한다.

### 6.2 무협 액션에 적용할 외부 '이미 실증한' 원본 워크플로 소스

| 우선 | 원본/증거 | 결정 |
|---|---|---|
| A. **Wan2.2 Animate 공식 Move/Mix** | [ComfyUI 공식 튜토리얼](https://github.com/Comfy-Org/docs/blob/main/ko/tutorials/video/wan/wan2-2-animate.mdx), [공식 workflow](https://comfy.org/hub/workflows/wan2-2-animate-character-animation-and-replacement-c2c4b45b7df5/) | 복잡한 동작은 **source video → pose/video+mask → identity reference** 경로부터 학습/복제. 현재 14B I2V 모델 파일은 Animate 전용 가중치가 아님. |
| B. **SCAIL-2 공식 (2026년)** | [개발팀 코드/설명](https://github.com/zai-org/SCAIL-2): fighting demo, source driving video, semantic masks, multi-ref, 손 왜곡 완화 DPO LoRA; [8GB용 GGUF 커뮤니티 패키지](https://github.com/dvelm/SCAIL-2-Unlimited-Video-Low-VRAM) | 실전 동작 전이 1순위 **후보**. 커뮤니티는 Q3_K_M 약 8.1GB 파일과 81프레임 오버랩 연장 구조를 설명하지만, 파일이 8GB보다 크며 **시스템 RAM 오프로드와 품질·속도 검증**이 필수. 해당 워크플로 최소 ComfyUI 0.33.1 vs 현재 0.20.1; 원본 설치 inplace 수정 금지. |
| C. **Wan Animate GGUF 12GB 실측** | [The_frizzy1 실행 문서](https://github.com/Thefrizzy1/The_frizzy1-Workflows/blob/main/workflows/wan2.2/animate-ultimate/README.md), [벤치마크](https://github.com/Thefrizzy1/The_frizzy1-Workflows/blob/main/docs/BENCHMARKS.md) | 480×864, 81프레임 Q5_K_S 결과: **7m05 총 소요, peak VRAM 11.7GB, peak RAM 24.6GB**는 12GB RTX3060 환경 실측. 이 레시피 그대로 8GB로 성공했다고 간주할 수 없다. 작은 GGUF의 별도 검증이 필요. |
| D. **LTX-2.3 공식 구조 제어 + 현 성공 계열** | [LTX IC-LoRA 모션 제어](https://docs.ltx.io/open-source-model/feature-guides/structural-control/motion-control/), [LTX 영상/음성 공식 워크플로](https://comfy.org/hub/workflows/ltx-2-3-image-audio-to-video-adca306765ce/), [실행 경험 공유](https://github.com/koala-penguin/ltx23-toolkit) | 성공한 인물·발화 품질 유지 + 동작을 구조화하는 후보. 모션 컨트롤 IC-LoRA 가중치/노드가 지금 PC에 설치됐는지는 **미확인**. 12GB 사례를 8GB 검증으로 치환하지 않는다. |
| E. **최상위 외부 벤치마크** | [ComfyUI Kling 3 Motion Control](https://comfy.org/hub/workflows/kling-3-0-motion-control-f7078f72ad4b/) | 동작/얼굴 일관성의 **품질 비교 표준**으로 연구. Partner Node/API는 외부 서비스이며 업로드·과금·인증 연결은 **별도 승인 전 사용하지 않음**. |
| F. **손/검 강결합** | [Blender 공식 Bone Parenting](https://docs.blender.org/manual/en/latest/animation/armatures/bones/editing/parenting.html), source 영상 소품 tracking + mask/inpaint | **물리적으로 제어 가능한 계층**에서 손과 검을 결합. diffusion 영상이 보증하지 않는 rigid prop attachment를 별도 rig/holdout/compositing으로 보완하고, 프레임별 WYSIWYG에서 검이 분리되면 FAIL. |

**중요한 반례:** LTX 커뮤니티 사용자는 [검이 잔/다른 물체로 모핑되는 소품 교체 문제](https://github.com/koala-penguin/ltx23-toolkit)를 명시하고, 물체를 내려놓고 새 물체를 잡는 등의 action beats 구분을 권장한다. **대사와 간단한 동작 성공은 검술의 물리적 일관성 성공과 다르다.**

### 6.3 재현할 것은 workflow 내부를 섞은 새 하이브리드가 아니라 '검증된 제작 공정'

1. **LTX 2.3 AV 촬영 엔진:** 사용자가 실제 성공한 그래프와 참조 이미지/대사 입력 형식을 SSOT로 잠근다. 검술 action shot의 바깥 대사·감정·인물 설정 및 샷 간 continuity에 활용. 사소한 sampler/CFG 노드 변경 금지.
2. **Wan Animate/SCAIL-2 동작 엔진:** 저작권 확인된 실제 검술 driving clip + **첫 동작 프레임과 일치하는 identity reference** + 필요한 mask/pose. 공식/공개 버전 고정 JSON을 별도 환경에서 로드해 **완성된 모션 전이 공정으로** 재현한다.
3. **검-손 물리 계층:** 칼은 소품 개체로 추적하고 손잡이 기준 좌표·회전·길이를 유지한다. 라이선스 확인된 모션/Blender 본(bone) 결합 또는 소품 holdout/compositing이 후보. 생성 모델이 검을 재구성한다면 도구 연결과 변형을 실제 프레임에서 반드시 평가.
4. **편집/후처리:** 성공한 숏만 FFmpeg/NLE로 이어 붙이고 검 궤적·타격·와이어 액션을 과도한 한 번의 긴 생성이 아니라 숏별 컷/효과음/움직임으로 표현. 공간/캐릭터/조명 레퍼런스와 마지막 프레임을 상태로 보관하되, **다음 프레임 하나로 무한 루프**를 단독 제작 방식으로 승격하지 않음.
5. **품질 게이트:** 샷별 '손잡이와 손 연결/검신 길이/인물 얼굴/관절/발 접촉/동작 궤적/시간 일관성/음성 싱크'를 전 프레임/필요 sampling과 직접 영상 재생으로 평가. GPU/API/렌더 PASS와 CONTENT_PASS 분리.

### 6.4 향후 적용 순서: 코드 작성 전에 먼저

- **E0:** 현 LTX 성공 workflow와 비디오 출력의 정확한 대응, 기술 스택/버전/모델/LoRA/원본 input hashes 및 재현 실행 조건을 목록화. 그래프는 고치지 않음.
- **E1:** 검술 **실제 driving video** (저작/사용권 확인) 1개 확보하고 오른손·손잡이·검신이 프레임마다 보이는지 확인. 1~2초 복합 동작이 아닌 단일 발도 또는 수평 베기부터. 기존 pose/canny PNG는 driving video 대용으로 간주하지 않음.
- **E2:** A/B 후보의 정확한 원본 JSON, 모델 크기, 필수 설치 버전, 로컬 8GB peak VRAM/RAM 예상 병목, 8GB 동급 실제 실측 **증거를 확보한 뒤** 1개만 분리 환경에서 원본 그대로 재현.
- **E3:** 실제 결과에서 손-검 FAIL이면 재시도 횟수/스텝을 늘리지 않고 motion source·prop control·mask를 교정. identity FAIL이면 ref·캐릭터 시트를 조정. 물리/시각적 PASS가 확보된 샷만 LTX AV와 **결과 단위**로 연결.
- **E4:** 통과한 각 제작 공정의 원본 SHA와 재현 레시피, 실패 조건 및 품질 증거를 버전 고정. 장편 생성/자동화는 별도 승인 후.

**작업 상태:** BUILT_FROM_VERIFIED_WORKFLOWS_POLICY / LOCAL_LTX_WORKFLOW_AUDIT_PASS / EXTERNAL_ACTION_WORKFLOW_RESEARCH_PASS / WUXIA_ACTION_RESULT_NOT_VERIFIED / NEW_GPU_RENDER_NOT_RUN. 이번 추가 연구에서 새 모델을 설치하거나 영상·프로그램 코드를 변경하지 않았다.
