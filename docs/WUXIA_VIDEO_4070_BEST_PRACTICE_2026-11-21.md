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
