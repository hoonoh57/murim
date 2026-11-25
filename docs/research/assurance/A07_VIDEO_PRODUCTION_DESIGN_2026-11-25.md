# A07 영상 제작 기반기술·전문 생산 로직 설계 v0.1

2026-11-25 KST | 기준 ca38eee61cda7fd950e39095f00a36f886fecce1 | D2 설계 개선안(향후 구현 기준), D1/D3/D4/D5 HOLD, A07 NOT_QUALIFIED.
권위: [5축](../../MURIM_FIVE_AXIS_ARCHITECTURE.md), [D0~D5](../../MURIM_PRECODE_DESIGN_GATE.md), [품질 캐스케이드](../../MURIM_CASCADING_QUALITY_CONTRACT.md). 사용자 목적: 코딩 전 강한 실제 구현과 로직 비교 후 설계의 기반 높이기. 예시 콘텐츠 생성 대신 source-level GAP 및 보완 계약. 코드, 테스트, 설치, 유료 실행 없음.

## 2026-11-25 — 원본 Deno API prompt 복구 및 연출 계획 컴파일 계약

### 기존 실물에서 복구한 native 실행 형식

E:/ComfyUI_New의 기존 output/40c1230dd7244615_shot_001_00001.png (1452978 bytes) 첫 32768 bytes의 PNG tEXt prompt 전체(9114-byte chunk, CRC32 PASS)에서 API JSON 46 nodes / 79 links를 실제 복구, 각 connection pair의 source ID 및 index 구조 검사 PASS. prompt raw SHA256 eecc5342a7741715fddaca43098bf057bb370d2809064e549bd9948559f2c08a, CreationTime 메타데이터 2026-11-23 22:58:46(시간대 미상). 같은 prefix의 mp4/audio.mp4 목록 존재. 이미지 전체, MP4 decode/AV 품질, prompt_id history, 현재 object_info/schema 및 실제 실행 동일성은 미확인. 저장 metadata는 native API 구조 관측이지 성공·품질 증명이나 최신 runtime 보장 아님. 원본 prompt의 창작 텍스트나 이미지 bytes를 repo로 복제하지 않음. 상세 receipt CURRENT_STATE 참조.

- 실제 DenoLTX23PresetLoader 5314 GGUF Style, LTX2.3 distilled Q4_K_M, split audio/video VAE, Gemma FP4/projection, latent x2. 3 SamplerCustomAdvanced, euler/manual sigmas, CFG 1.0, NAG, tiled VAE decode, joint AV. 모델 다운로더·RAMCleanup은 이 native prompt class 목록에 없음. UI graph의 setup/bypass 노드가 자동 실행된다는 추정은 취소. README는 downloader가 Python-side 자동 다운로드를 하지 않는 helper라고 명시; 실제 다른 side-effect 및 runtime 검증은 여전히 필요.
- 관측된 native input mapping 후보: DenoMultiImageLoader 5281.image_paths string, resize profile; DenoLTXPromptGuide 5317.positive_prompt/negative_prompt string, language Korean; INTConstant 5036.value=8; PrimitiveFloat 5329.value=24.0→frame-rate casts 4983/5328/5385. 5038 SimpleCalculatorKJ expression 1 + 8*round((a*b - 1)/8), 이 입력에서는 산술상 193 requested frames(실제 렌더값 아님). DenoLTXSequencer 5284/5285 각각 num_images=1, insert_mode=frames, insert_frame_1=0, strength_1=1.0, strength_sync=false, bypass=false, frame_rate 및 multi_input은 연결값. 첫 stage는 preprocessing 5245, 후속은 5281 batch 직접 입력; 두 stage의 동일 역할·순서 매핑 필요. VHS_VideoCombine 4995 filename_prefix, save_output=true, audio/video linked. 이 ID들은 이 복구된 특정 graph에만 적용. 임의의 다른 recipe에 재사용 금지.
- 실제 설치 README(5293 bytes)는 multi-image reorder/crop/fit, batch guides, Sequencer auto num_images·strength manual·bypass, preset loading, per-LoRA A/V strengths, dialogue minimum duration estimate(Korean 포함)를 설명. 실제 metadata의 multi-image count=1이므로 2장 이상 API encoding(구분자/JSON 등)은 아직 확정하지 않음. UI field name만 보고 guessed list/string format 만들지 않음. 해당 기능 public INPUT_TYPES/실행 인자 계약 또는 정상 multi-image native export 확인이 다음 좁은 검증.

### A04/A05/A06/A07/A08 연출 계획의 연결 (설계)

현 src/studio/director_simple.py blob 27cf48324bfc5102d42fd9889f54b6d0ba9b68c3 L286~346은 character/style 및 scene당 storyboard 1장 승인 후 scene image track patch, production state HUMAN_RELAY_UNTIL_WORKFLOW_VALIDATED. 그대로 두고 향후 전문 Add-on이 승인 storyboard를 대체하지 않는 ShotDirectionPlan을 만든다.

1. A04 scene beat/관객에게 전달할 정보·인물 선택과 전후 상태를 받아 A05 shot 경계(공간/동선/시선/카메라/전후 손·소품 접촉)를 결정. 한 shot 내 복합 동작은 하나의 긴 prompt로 밀어넣지 않고, 필요시 서로 다른 연출 목적·제어 가능성에 따라 shot을 분리. 모든 scene을 같은 초/장면 수에 강제 금지.
2. A06 approved AssetBible에서 실제 필요한 가시 참조를 선택: 시작/전환/종료 프레임, identity/의상/prop state를 목적별로 구분. 캐릭터 시트 자체를 영상의 시간 키프레임으로 무조건 삽입하지 않는다. 각 guide에 asset digest, 역할, time range, 적용 강도 후보, 선행/후속 상태, crop/fit 시 보호할 손/소품/얼굴 영역을 명시. 자료가 부족한 shot만 asset generation/repair 제안. 미승인 asset 사용 금지.
3. Motion/Camera/Performance 계획은 각 beat별 시간 구간, 행동·반응·표정·카메라와 sound intent를 정의. Deno Prompt Guide의 대사 길이는 추정치로 사용하고 실제 고정 대사는 A08 발화 WAV/정렬 기준 사용. 생성 음성과 외부 고정 음성의 조건 의미를 혼용하지 않음. 편집 timeline range, engine requested frames 및 실제 output frames를 분리.
4. Adapter는 plan을 검증된 native recipe의 typed bindings로 compile. image_paths의 형식 미확인 또는 필수 역할 미지원이면 HOLD. 실제 native graph에서 두 Deno sequencer의 동일 이미지 순서/num_images/time/strength와 upstream fps를 일관되게 결속. 사용자가 승인한 원본 graph, 모델, sampling/resize/AV/quality profile 유지. graph topology와 비허용 field mutation은 diff 검사에서 거절. 모호한 경우 강제 fallback/임의 그래프 재작성 금지.
5. Manager의 기존 generic 실행/승격 계약에서 candidate를 평가: 객관 probe, 독립 시각·연기/원고/인접 shot 경계 평가. defect→원인 분류→해당 asset/guide/prompt/shot 경계 수정→영향받은 dependency만 다시 실행/평가. 승인된 다른 shot은 immutable refs로 유지. Deno 자체가 정상인 경우 Deno 개선이 아니라 연출 계획·입력·선택 정확도가 개선 대상.

검증 상태: native metadata 형식과 source 구조 확인, Deno 원형 재사용 설계 선택 강화. 실제 API 제출/실행/성능 동등성, 다중 image_paths serialization, output A/V decode, 권리 및 독립 평가 NOT_RUN. D0~D5 HOLD 유지, 코드 동결. 다음은 public input contract 및 기존 2장 이상 prompt metadata를 제한적으로 확인해 실제 multi-guide compiler binding을 확정하는 작업. 새 예시 콘텐츠/노드 구현/원본 설치 수정 없음.

## 2026-11-25 사용자 결정 반영 — Deno 원형 Adopt / 연동 경계 상세화 (이전 후보 선정 서술보다 우선)

사용자 직접 보고: "deno는 100% 그대로 활용해도 100% 성능 발휘함". 기존 Deno 기술을 재개발·최적화·축소하지 않고 원형 채택하는 **설계 선택** 확정. 사용자 경험은 채택 근거이며, 100%라는 수치를 독립 정량 시험 결과 또는 모든 shot/하드웨어에서의 성공 보증으로 바꾸지 않는다. D1/D3/D4/D5 및 권리/비용/실행 안전 심사는 유지. 기존 원본 graph/노드/가중치/환경 변경 0. Deno 소스 전체 역설계는 다음 작업에서 제외; 필요한 공개 입력/출력 계약과 부작용 경계만 확인.

### 실제 근거와 보완 범위

- CURRENT_STATE의 실제 E:/ComfyUI_New inventory 및 다섯 graph 복원 근거(기준 9b7d164533f767997bc18d76e2d050447627ddc1) 우선. GGUF author/author2/multi recipes와 FP8 Deno ver2는 별도 capability/profile로 구분. 저장된 1장 설정이 최대 기능 수를 의미하지 않음. multi_images graph 이름만으로 다중 입력 실증을 선언하지 않음. 기존 Deno 사용자 실행 품질을 존중, 동일 검증 예제 반복 대신 자동화가 원형 성능을 보존하는지 최소 대조.
- 직접 재확인한 src/studio/comfy.py blob 634e67ebfd8d6e51714e96218dce54be50c4ec10: parse_graph는 2MB/300 nodes/connection pair, HTTP URL 문자열 거부; describe_graph/resolve_binding은 기존 string 필드만 노출/수정; bind_inputs는 image/audio/motion/output 4 mapping 고정; generate는 image 1개와 optional untrimmed audio, upload 후 graph 기록, object_info class presence 확인. Deno UI graph 자체를 넣으면 거절되는 정상 경계이며, 숫자·boolean·다중 이미지 조건 전달 미구현. 타입 검증을 우회하거나 parse_graph allowlist/URL 검사를 약화하지 않음. Deno downloader 같은 별도 side effects를 포함한 실행 그래프는 사전 확인 없이 호출하지 않음.

### 원형 보존형 Add-on 계약 (D2 설계, 아직 구현 없음)

| 역할 | 입력/출력 계약 | 변경 금지/검증 |
|---|---|---|
| 승인 원본 recipe | source UI workflow SHA, ComfyUI 버전/installed node contract, 모델/LoRA/환경 refs, 실제 native API export digest | 원본 UI/노드/weights 불변; 지원되는 native export/실제 API history로 확보, 임의 flatten/rebuild 금지 |
| 전문 shot planner | shot_revision, 목표 연출, reference roles/asset digests, time/rational fps/strength, prompt, audio requirement, output constraints | Deno에만 맞춘 Core schema 금지. 필수 제어 미지원이면 HOLD |
| Deno adapter | 검증된 recipe별 typed input binding manifest, exact node id + class_type + field + type/limits + 연결 여부 | 실행 사본에 승인된 외부 입력만 bind; 구조·연결·알고리즘/기본 품질 profile 보존. 링크로 연결된 값은 실제 upstream 입력으로 매핑. 서로 다른 recipe의 ID/필드 추정 재사용 금지 |
| 결과 수집 | attempt/ref, provider prompt_id, 지정 output node, saved artifact digest, actual fps/frames/duration/audio streams | 출력 추측/최신 파일 검색으로 다른 job 결과 결속 금지. 실제 AV probe와 원본 대비 성능 평가 별도 |
| 공통 Manager/Bridge | capability manifest/lease/attempt/approval/reconcile/evidence | provider-specific if/else 금지. JSON persistence-only; direct addon-to-addon 호출 금지 |

이미지 선택/프롬프트/삽입 시간·강도는 전문 Add-on의 결정이며 Deno의 내부 conditioning/샘플러는 원저자 구현에 맡긴다. DenoMultiImageLoader 및 DenoLTXSequencer의 저장된 UI contract를 native API export에서 확인한다: 실제 필드와 숫자 타입, image count, insert mode, frame/second 단위, fps, strength, bypass/strength_sync, 첫/후속 stage 연결. 지원 범위를 읽기 전 자동 값 생성 금지. 순서/삽입 시간이 충돌하거나 필수 참조가 누락되면 실행 전 거절. seed/steps/CFG/sigmas/NAG/VAE/업스케일/메모리 설정은 기존 승인 profile에 그대로 결속, 품질 저하형 임의 대체 금지. 기존 audio joint generation을 external audio-driven lip sync로 간주 금지; A08 별도 capability가 담당.

### 최소 연동 검증 계획

1. 기존 성공한 Deno workflow의 native API export 또는 실제 저장 prompt metadata 및 output evidence를 먼저 재사용. UI 원본과 API의 활성 실행 경로/linked inputs, 동일 모델/precision/profile 확인. 기존 graph가 다운로드/외부 경로/시스템 메모리 정리 등 부작용을 요구하면 명시적으로 검토; 안전하게 동일 동작을 보존하는 기존 실행 경로가 없으면 HOLD, 임의 삭제/우회하지 않음.
2. 원본 UI run과 adapter run에 동일한 승인 입력/seed/profile를 결속하고 실제 실행 graph 차이가 허용 binding에 한정됨을 확인. 비결정적 GPU는 bitwise 동일을 요구하지 않고 사전 정의한 frame/audio/품질/시간·peak VRAM 동등성 측정. 비교 기준과 허용 편차는 실제 baseline 및 독립 평가 보정 전 임의 수치 확정 금지.
3. 다중 참조·시간 제어에서 필수 input 손실 없는지 경계 사례 확인. 미지원 유형/연결값 충돌/누락/출력 불일치/timeout은 명시 HOLD/UNCERTAIN. 실패 숨기는 fallback 금지.
4. 기존 Deno 엔진이 정상이어도 Murim 연동 자체의 실행/품질 판정은 별도. A07 NOT_QUALIFIED, PRODUCT_CODING_FROZEN 유지. 다음 우선 작업: native API export/기존 실제 출력 증거 확인 및 연동 가능한 입력 계약 확정; 이후 A06 참조자산/연출 계획과 A08 외부음성 capability 연결 설계. 새 작품 반복 제작·GPU 실행·모델 다운로드·노드 변경 없이 가능한 설계 작업 진행.

## 1. 실제 현재 수준과 강한 비교 기준

현재 main 직접 읽은 파일:
- src/studio/comfy.py blob 634e67ebfd8d6e51714e96218dce54be50c4ec10: LocalClient, parse_graph, bind_inputs, generate, output_video. 신뢰된 API graph hash, loopback/no redirect, object_info node class existence, 단일 image 필수 + optional audio/motion scalar text, 저장 영상 1개 명시 선택, media_info/해시, CANDIDATE_REQUIRES_VIEWING. 이 안전한 기존 경계 보존. UI graph 실행 형식으로 오인 금지.
- src/studio/web.py blob c3f6002887235c9661f84f024a012cc12daa7c49: generate_comfy L239~244는 generate 완료 후 store.save; 동기 HTTP path. 현재 프로젝트 버전/다중 실행이 바뀌는 동안 후보 결과 재결속/재시작은 해당 함수 경계에서 별도 입증되지 않음.
- src/studio/director_simple.py blob 27cf48324bfc5102d42fd9889f54b6d0ba9b68c3 L346/350 및 docs/DIRECTOR_SIMPLE_UI_20261124.md blob 8e5c58fd5c9a2b3deda27ec209e8538ec05e1378: 사람이 동작/키프레임 요청·결과 중계, 다중 키프레임 미검증.
- workflows/wan22_5b_api.json blob 1aab20f2888bf872576b3f175df9c9e81fddbe5a: 512x320/41 requested frames/24fps/20 steps/CFG5/단일 LoadImage→Wan22ImageToVideoLatent→sampler→decode→SaveVideo. graph 값이지 이번 GPU 실측 아님. workflows/ltx2_i2v_api.json blob e69de29bb2d1d6434b8b29ae775ad8c2e48c5391 빈 파일. LTX 자동 실행 미구현을 성공으로 표현 금지.

외부 원저자 직접 조회:
- [LTX easy_samplers.py](https://github.com/Lightricks/ComfyUI-LTXVideo/blob/master/easy_samplers.py) blob 4c5ad8613842fa4a94cc8f4162c8b80fcc153ea5, L80~118,176~244: image batch와 frame indices 개수 일치, index 0 VAE encode/noise mask, 다른 index는 LTXVAddGuide로 condition, sigma 구간 분리. 이 특정 sampler는 공통 strength를 사용. 개별 strength 지원은 해당 graph/node별 확인, 모든 모델에 일반화 금지.
- [LTX-2.5 workflows](https://github.com/Lightricks/ComfyUI-LTXVideo/blob/master/example_workflows/2.5/README.md) blob a7e0abedc4a4fc72183daa27306c36a0e8b8f6f4 L24~55: 8n+1, single vs latent x2/refine, depth/canny/pose, Ingredients sheet, sparse motion tracks, mask inpaint. [Q3 원장](../technology-library/Q3_LTX25_OFFICIAL_GRAPH_EVIDENCE_2026-11-24.md)의 3개 실제 graph 관측(README와 다른 Union stage 및 linked widget 우선) 유지. 별도 신규 graph 실행 없음.
- [ComfyUI server.py](https://github.com/Comfy-Org/ComfyUI/blob/master/server.py) blob 193793d484eba58932cb43034dcf240457a1dfe8 L1151~1246,1248~1290: prompt validation, 선택적 client prompt_id, queue/history 조회, ID별 pending delete 및 running interrupt, ID 없는 interrupt는 global. prompt_id를 받을 수 있다는 것이 서버 중복 방지 보장은 아님. 설치된 버전의 동일 API 지원 및 targeted interrupt 경쟁 안전성은 별도 확인. [공식 API routes](https://github.com/Comfy-Org/docs/blob/main/development/comfyui-server/comms_routes.mdx) 참고.
- 기존 공개 원본에서 확인한 기능이 강한 비교 기준 후보이지 모든 분야의 세계 최고/실제 동등 품질 확정 아님. SCAIL/기존 8GB workflow 및 상용 multi-shot 도구 추가 비교, 실제 설치/권리/품질 검증 필요.

## 2. GAP → 설계 선택 (현재 구현과 목표 설계 구분)

| ID | 실제 GAP | 보완 선택 | 근거/적용 경계 |
|---|---|---|---|
| V1 | bind_inputs는 1 image, audio, motion scalar; reference sequence, time/strength, mask/depth/pose/track 의미 없음 | Adopt 공식 조건화 graph; Compose shot 조건 계약 및 adapter binding | LTX sampler 및 Q3; 특정 index/strength와 frame 규격을 adapter가 검증 |
| V2 | 사용자가 graph/node/field를 지정, node 존재만 검사; 타입·shape·가중치 및 실제 호환 검증 부족 | Adopt object_info 및 공식 API export, Compose typed recipe manifest, 검증된 capability 선택 | UI/API format 별개; 실제 graph 변환 지원 없으면 HOLD, 임의 JSON surgery 금지 |
| V3 | preview/refine/identity/motion/repair 방법 선택이 사용자 graph 외부에 있음 | Adopt 기존 I2V, control, inpaint, upscale; Compose shot별 생산 계획 | 후보 지원 범위 내에서만, preview 성공이 final 성공 아님 |
| V4 | queue 검사→submit 사이 경쟁 가능; random client_id, prompt_id 영속화 전에 응답 유실 가능; 동기 wait timeout | Adopt provider job API; Compose Manager lease/attempt·reconcile, Bridge 실행 전달 | provider ID/version 확인; timeout=UNCERTAIN, 중복 submit 방지; 공유 GPU 전체 취소 금지 |
| V5 | receipt는 duration/hash/candidate 중심, fits는 길이 하한; 접촉/정체성/원고 정확성 없음 | Compose 객관적 probe+독립 의미 평가+승격 계약 | Q4 구조 검사 오용 반증, A06 생성 이미지의 가짜 수치 배제 |
| V6 | 단일 영상 후보 등록, 국소 결함의 의미 기반 수정/선후 쇼트 검증 미구현 | Adopt mask repair/clip edit, Compose dependency 기반 targeted repair | 수정 범위 안팎 실제 frame/경계 검사; 보존 입증 실패 시 HOLD/범위 재심사 |

Build는 비교 후 불가피한 전문 shot planner/recipe adapter·근거 결속에 한정, 새로운 diffusion/pose/flow/inpaint 엔진 자체 개발은 현재 근거 없음. 공용 orchestration은 기존 5축 계약 재사용, 별도 영상 Manager/queue 금지. 제품 채택 확정은 D1/D3/D4 실증 이후.

## 3. 목표 전문 로직 (비실행 상세 설계)

### A. ShotPlan 및 조건 정규화
입력: 승인된 project/scene/shot revision과 목적, 시작/끝 상태(인물 ID·의상·소품 소유/접촉·카메라 축/시선·장소), rational fps 및 half-open timeline range, dialogue/audio refs, 허용 비용·권리·시간·품질 요구, 앞/뒤 shot boundary refs. 전문 Add-on이 연출 대안을 생성하고 난제를 분리; 무조건 모든 shot에 모든 조건을 적용하지 않는다.
조건 목록: role (first/last/keyframe, identity, prop, environment, depth, pose, sparse_track, mask, source_clip, audio 등 열린 namespaced role), asset ref+digest, 적용 time/space 범위, strength/priority, 좌표계·색공간·transform·occlusion/coverage, 필수/선택. 필수 조건이 지원되지 않으면 해당 recipe 제외, 조용히 조건 삭제 금지. 원본 타임라인 frame index와 모델 latent/index를 혼동하지 않도록 adapter가 유효 범위·반올림·가이드 재매핑·crop/pad 계획을 명시. 생성 길이와 편집 사용 구간 별도 기록. 예: 24fps/5s 타임라인 120 frames, LTX recipe 121 요청 가능; 실제 출력 probe 및 trim 계획 확인 전 동기 보장 금지. 시각 변형이 손·자막/서명·음성 시간을 바꾸면 관련 검사 재실행.

### B. 전략 선택 및 단계적 생성
1. 난제 분류: 단순 카메라/동작→I2V; 접촉/자세/동선 제어→keyframes+depth/pose/tracks 후보; 인물/소품 연속성→권리 확보 reference conditioning; 정확한 문자는 결정적 합성 후보; 확정 대사→A2V 또는 별도 lip-sync 후보. 전문 Add-on이 생성 가능한 대안과 장단점/제약을 제안. pose/depth 자체는 접촉 정합 증거 아님.
2. Manager hard filter: capability/schema/설치 health/recipe validation, 권리·비용·승인·resource lease, 필수 조건/출력 contract. 품질·비용/시간 실측된 champion 우선; 연구 후보 별도. 8GB 과거 목표만으로 현재 GPU 적합 단정 금지. 필수 지원 없음=HOLD; 무단 downgrade/모델 substitution 금지.
3. Preview: 저비용 motion/composition 후보를 생성; 실제 frame·접촉·시공간·정체성·서사 기능 확인. preview는 최종 해상도 품질 증거 아님. final recipe가 동일 motion/latent/source를 재사용 가능한지 명시하고, 불가하면 새 후보로 전수 재평가. 독립적인 candidate 생성 실패도 기록, 정해진 자원 범위에서만 반복.
4. Final: 조건/모델/graph/seed/실제 입력 hash 및 preview dependency pin. 생성→output probe→필수 객관 검사→독립 전문 검사→인접 shot 및 시퀀스 통합 검사. quality evidence의 version/artifact hash 결속. 결과는 candidate; Manager만 전체 gate/승인 만족 시 승격.

### C. 결함 분류 및 복구
정확한 문자 결함은 문자 합성 후보, 손/접촉은 해당 motion/guide/shot 수정, identity drift는 reference/conditioning/해당 shot, 카메라 축은 인접 boundary/shot plan 재검토. 마스크 inpaint는 대상 영역·시간·보호 영역 및 접합부를 지정; 비대상 frame/pixel 동일성은 실제 측정하거나 명시적 허용 차이/독립 비교(실험 전 고정). engine이 보존을 지원하지 않으면 protected source 그대로 유지한 별도 합성/shot replacement 또는 상위 재심사. 이전 정상 revision을 immutable 보존하고 변경된 의존성만 stale 처리. 새 시퀀스에서 모든 기존 필수 결함 검사를 재확인. 실패한 평가자 수치로 무한 재시도/기준 완화 금지.

### D. 실행 및 실패 상태
Manager는 실행 이전 attempt/idempotency key, normalized plan/input digest, 승인·예산·lease와 request intent를 원자 기록. Add-on adapter가 provider graph/model/input mapping을 해석·검증 및 업로드, Bridge를 통한 job submit/status/cancel/reconcile 수행. provider 지원 시 미리 UUID를 할당/기록하고 요청에 결속(기능 미지원 버전은 자동 submit recovery 보장 불가). 기존 /queue empty check를 global GPU lock으로 간주하지 않음; 공유 외부 작업의 간섭 가능성 및 lease 충돌 확인. 제출 응답 유실/timeout→UNCERTAIN, 동일 logical attempt 자동 재전송 금지. queue/history/provider job ref·출력 검증으로 reconcile; 부재가 증명되지 않으면 HOLD 및 필요 시 인간 확인. targeted pending delete/interrupt는 작업 소유권·서버 버전·레이스 검증 필요; global interrupt/queue clear 금지. CANCELLED는 실제 취소 확인 후, stale result는 원래 attempt 증거로만 보존, 최신 revision에 자동 결속 금지. 실패 시 원본/부분 미디어 및 receipt 보존, 재시도는 새 attempt와 비용 승인.
기술 실행 상태와 품질 상태 독립: RUNNING/SUCCEEDED 등은 생성 job, candidate/quality HOLD/승격은 별도. HTTP 응답/MP4/해시 일치만으로 품질 승인 금지.

## 4. 5축 배치와 검증 계약

Core: 기존 generic artifact/revision/time/dependency/job contract만, 영상 키프레임/pose 의미 및 provider API 금지.
Bridge: 공통 lifecycle/routing/실행·취소·이벤트 전달, provider 상태 결과 전달. node/graph 선택·품질 의미 판단 금지.
Add-on: 전문 shot planning/conditions/recipe binding/engine adapter 및 평가·수정 제안, private state. 다른 Add-on 직접 호출 금지.
JSON: plan/recipe/attempt/event/artifact/evidence refs와 상태 이력 persistence-only; graph 실행/선택 판단 금지. 기존 M-VML 원본 보호, 이중 SSOT migration 금지.
Central Manager: 기존 공용 capability 선택, DAG/revision invalidation, 권한/비용/lease/시도·reconcile 정책, 증거 인증·승격. 영상별 if/else나 provider-specific SDK 금지. 공용 UI는 결과·창작 선택·중요 HOLD를 보여주고 노드 매핑은 전문가 진단 영역.

검증 전 고정할 hard cases: V1 서로 다른 keyframe indices/count·out-of-range 및 필수 strength 미지원; V2 UI graph/unknown node 및 잘못된 type/모델/권리; V3 unsupported conditioning·preview→final identity drift; V4 lost submit reply/timeout/재시작·외부 queue job/취소 race·stale result; V5 frame/time mismatch, 손-소품 분리, 본명 오류, 생성 이미지 가짜 PASS; V6 마스크 외 변화/인접 shot discontinuity. 기존 명백한 중대 결함 허용 0, 실제 전문가/비교군·샘플/시간·비용/허용 편차는 별도 사전 보정. 원본 clip 및 관측 구간, 실패 포함 동등 예산 비교(기존 WAN, 권리/설치 확인된 LTX/제어 후보, 적용 가능한 강한 외부 기준), equal-quality cost 별도. 기존 무협 검-손 접촉 시험도 유지. 과거 A06 격리 자산 사용 금지. 현재 모든 품질 실험 NOT_RUN.

## 5. 판정
실제 원본 비교로 V1~V6 설계 GAP 식별, 목표 계약의 구체화 및 반례에 대한 작성자 논리 검토 완료. 독립 설계 반대심사/실행 검증 아님. 실제 Windows/GPU, API version, graph 변환, 모델 라이선스, 동등 성능/비용·독립 평가 미해결. ENVIRONMENT_ISSUE 및 기존 구현과 목표 설계 GAP 구분; repo-wide audit 아님. A07 NOT_QUALIFIED, DESIGN_HOLD. 다음 A08 음성·연기·립싱크: 실제 기존 voice.py/worker와 원저자 한국어 TTS·정렬·audio-driven 영상 로직 비교 후 목표 계약 보완. A07 재개는 실제 환경·권리/비교 evidence 및 독립 심사 가능 시. 기존 D0~D5 전체 승인 전 제품 코딩 금지.
