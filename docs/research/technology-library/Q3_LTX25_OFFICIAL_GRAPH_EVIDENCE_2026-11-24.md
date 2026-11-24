# Q3 / A03 T001~T003 LTX-2.5 공식 워크플로 정적 분석 — 2026-11-24

기준 main f7687d6a847df93440bf3a373cbbc00b14406007. 기존 기술 연구/설계 심사 기준 불변. SOURCE_RESEARCH_PARTIAL / A03 NOT_QUALIFIED / TECHNOLOGY_INTELLIGENCE_HOLD. 연구자가 선택한 공식 원본 대체 분석 경로이며 T001 영상 강의 관측, Gemini 응답, 실제 실행 및 제품 채택 아님.

## 1. 실제 원출처 및 관측 범위

- T001 [LTX-2.5 in ComfyUI: The Upgrade Guide](https://www.youtube.com/watch?v=Sl0jn8ucDqE): 검색 결과 제목 확인, 강의 영상/음향 및 타임스탬프 미관측. Q2에서 Gemini 연결 미확보 확인; 신규 호출하지 않음. canonical 기술 분석 schema에 맞는 실제 provider 응답 NOT_RUN.
- T002 [LTX-2 CHANGELOG.md](https://github.com/Lightricks/LTX-2/blob/main/CHANGELOG.md), Git blob 0df1049d94379bbde9e20ecb5e71fb94c8982de0, 상단 직접 열람. 조회한 문서의 첫 버전 1.6.2 (2026-11-12), 1.6.1 (11-04), 1.6.0 (11-03). releases 웹 직접 열기 결과 오래된 cache와 검색 결과가 불일치하여 최신 release tag 확정하지 않음. Python pipeline 버전과 ComfyUI graph/runtime 버전은 별개.
- T003 [공식 ComfyUI-LTXVideo example_workflows/2.5 README](https://github.com/Lightricks/ComfyUI-LTXVideo/blob/master/example_workflows/2.5/README.md), Git blob a7e0abedc4a4fc72183daa27306c36a0e8b8f6f4, 전체 본문 직접 열람.
- 아래 3개 공식 JSON은 GitHub 파일 읽기 및 JSON.parse 성공, top-level nodes/definitions.subgraphs/nodes/input links/widget values 추출. 파일 blob으로 판본 결속. ComfyUI import/object_info/API 실행/렌더 검증과 다름.
- [공식 시스템 요구사항](https://docs.ltx.io/open-source-model/getting-started/system-requirements): 검색 제공 공식 본문 32GB+ GPU VRAM, RAM 32GB, 여유 디스크 100GB, CUDA 12.7+, Python 3.12+; 권장 A100 80GB 또는 H100, RAM 64GB+. 직접 페이지 열기는 cache miss. [공식 LTX Desktop README](https://github.com/Lightricks/LTX-Desktop) 검색 제공 본문: Windows 권장 24GB+ VRAM(32GB 권장), fp8 지원 GPU에서 앱 자체 하한 9GiB. Desktop 제한을 ComfyUI 일반 실행 제한으로 전용하지 않음.
- [LTX-2.5 model card](https://huggingface.co/Lightricks/LTX-2.5): 검색 본문으로 가중치 존재 확인, 직접 본문 열기 cache miss. Changelog 1.6.0 명시 코드 Apache-2.0, 모델은 LTX-2.x Community License (2.3은 별도 LTX-2 Community License). 실제 모델/LoRA/인코더/자산 권리와 상업 이용 조건 및 가중치 hash/접근 승인 미확정. 사용/다운로드 승인으로 해석 금지.

## 2. 공식 graph 정적 관측 — 재현 후보

원본 경로 공통: https://github.com/Lightricks/ComfyUI-LTXVideo/blob/master/example_workflows/2.5/

| ID | 파일 / Git blob | 관측된 처리 |
|---|---|---|
| G01 | LTX-2.5_T2V_I2V_Single_Stage_Distilled.json / 2320366da6e9a6c506fd498de29550e9ed5ddbab | top fps node 5511=24, duration 5512=5, preprocess 5514 width 960 height 544; optional first image; joint AV latent, 8-step distilled, tiled video decode + audio decode |
| G02 | LTX-2.5_A2V_Two_Stage_Distilled.json / f265ce431a4d1b7bb5722761a59a29ee6fe7130a | same base size/fps/duration, audio start 5601=0; TrimAudioDuration node 6001, LTXVAudioVAEEncode 6002, SetLatentNoiseMask 6004/6006; latent 2x spatial upscale, second 3-step pass, original trimmed audio wired to CreateVideo input via decode link 14040; no audio VAE decode in Decode subgraph |
| G03 | LTX-2.5_ICLoRA_Union_Control_Distilled.json / 5bcd656a6a376904154fac64ed089e2c73a259e4 | LoadVideo, VideoDepthAnything (5060/5061/5062), LTXAddVideoICLoRAGuide 5012, LTXVCropGuides; mode-0 8-step sampler and upscale/re-sampler 5517 with 3-step schedule and 2x latent upscaler. README comparison says single stage; actual graph contains active two-stage path. Runtime verification pending. |

Model loader graph values common: ltx-2.5-22b-distilled-transformer-bf16.safetensors; ltx-2.5-video-vae-bf16.safetensors; ltx-2.5-audio-vae-bf16.safetensors; gemma4-12b-with-proj-ltx-2.5-bf16.safetensors; gemma4_e2b_it_bf16.safetensors. G02/G03 additionally ltx-2.5-latent-spatial-upscaler-x2-bf16-1.0.safetensors. G03 exact LoRA loader node 5607: ltx-2.3-22b-ic-lora-union-control-ref0.5.safetensors (strength 1); reference depth model video_depth_anything_vits.pth. Cross-version pairing exists in official JSON; actual compatibility and weight access still unverified.

G01/G02 frame expression node 5561: 1 + floor(a*b/8)*8; 24fps × 5s gives 121 frames. Do not infer exact output media duration or audio alignment without probe. G01/G02 stage1 top 5516 [42,1,euler_ancestral], cfg 1; nested noise widget 43 is overridden by parent input, not a separate runtime seed. Eight intervals from sigma schedule node 4984: 1.0,0.99375,0.9875,0.98125,0.975,0.909375,0.725,0.421875,0.0. G02/G03 stage2 3 intervals from 0.909375,0.725,0.421875,0.0; G02 parent 5517 [false,1,euler,1,42], exposed sampler_name link 13690 from subgraph input to KSamplerSelect 4976 overrides nested euler_ancestral. Do not copy nested stale widget as effective input. G01/G02 parent decode node 5518 widgets [30,8,512,64,128,32], actual fps wired from external value; nested VAEDecodeTiled defaults [512,64,64,8] are not all effective values. Parent mapping and runtime must be checked; do not report stored fps=30 as generated fps. G01/G02 input parameter widgets contain ltx-2.3-22b-dev.safetensors but ckpt_name is linked from loader; do not treat stale stored text as active model. Empty prompts and example.png placeholders are not executable complete benchmark input.

## 3. Technical candidate decisions and limits

- First experiment candidate G01 for previews (no execution). G02 for fixed authorized Korean dialogue audio + image: preserve source waveform path, inspect actual output ASR/transcript/audio mux and visual lip timing independently. Frozen audio is not proof of perfect lip sync. G03 depth guidance for sword/hand motion with separately authorized reference; contact/geometry/identity and failure tail require actual independent frame inspection, not MP4 success.
- Official README also documents reference sheets (Ingredients), motion tracks, inpaint/outpaint, and tiled fusion. Other graphs not parsed, performance unverified. Adoption cannot be inferred from descriptions.
- Actual target GPU/RAM/free storage/driver/Python/Torch/ComfyUI/node versions/object_info/weight files/rights/host RAM offload conditions unknown. Previously documented RTX4070 Laptop 8GB target is below general official 32GB guidance; not a current hardware measurement. Community low-VRAM 8GB + 16GB RAM claims https://www.reddit.com/r/comfyui/comments/1w8bjun/ and https://www.reddit.com/r/comfyui/comments/1w9kt9p/ are discovery only; no independent workflow/outputs verified. Do not assume either impossible on all offloaded variants or viable on target. Quantization/offload/tiled decoding candidates need version/rights and fixed-brief comparison, not blind installation.
- Before running approved existing engine: obtain exact Windows inventory/read-only version and capabilities, pin graph/model variants/license and same permitted reference/input, select installed strong 2.3 or other current champion only after inventory. Record all attempted runs including OOM, CPU/RAM/disk offload, peak GPU memory, load and wall time, re-generation costs, actual frames/audio. Same brief/seed policy, resolution/duration/fps and quality constraints; compare equal-budget quality and cost per accepted clip separately. No production promotion until independent Korean speech/visual motion checks and target feasibility are demonstrated. No thresholds weakened; exact acceptance criteria and sample sizes still require pre-experiment expert calibration.

## 4. Q4 reference counterexamples (candidates, evaluator test NOT_RUN)

R09: G02 stage2 effective sampler is euler_ancestral because nested stored value says so → FAIL (parent link 13690).
R10: Union Control is single-stage solely because README says so → FAIL (G03 graph disagreement; runtime unknown).
R11: 5 seconds × 24 fps means 120 generated frames in G01 → FAIL (node 5561 yields 121; real output probe pending).
R12: source audio preserved by G02 guarantees correct Korean lip sync → FAIL (no visual sync observation).
R13: official low-VRAM tuning or a community 8GB report proves target production feasibility → FAIL (unverified hardware/workflow/quality/cost).
R14: Apache-2.0 code license automatically licenses model weights → FAIL (T002 distinct license).
No independent evaluator or controlled actual test.

## 5. Status

Q3 official source/graph analysis boundary completed: three actual JSON blobs parsed, version/recipe/linked-widget and documentation discrepancies observed. T001 video NOT_OBSERVED, Gemini NOT_CONNECTED/NOT_RUN, runtime/target benchmark/independent quality/cost/rights NOT_VERIFIED or NOT_RUN. A03 NOT_QUALIFIED, not REPRODUCED or TARGET_BENCHMARKED. ENVIRONMENT_ISSUE: missing video/API connection and target inventory/authorized execution; AUTHORITY_DRIFT candidate in upstream README vs actual graph, no upstream modification. New product code/test implementation/UI/DB/installation/payment/Windows writes none. Q4 next, preserve Q1/Q2 unresolved conditions. Reopen Q3 when authorized target inventory and actual reference/output comparison available, not repeat the same searches. DESIGN_HOLD / PRODUCT_CODING_FROZEN / REMEDIATION_REQUIRED.
