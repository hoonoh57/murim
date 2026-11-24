# A08 전문 음성·연기·립싱크 기반기술 및 생산 설계 v0.1

2026-11-25 KST | 기준 6ec3ede4b163fd8796f37d2fa7b371e226703e24 | D2 상세 설계 보완안 / A08 NOT_QUALIFIED / DESIGN_HOLD.
[5축](../../MURIM_FIVE_AXIS_ARCHITECTURE.md), [D0~D5](../../MURIM_PRECODE_DESIGN_GATE.md), [A07](A07_VIDEO_PRODUCTION_DESIGN_2026-11-25.md) 및 기존 공정 기준 유지. 현재 소스와 원저자 처리 로직 비교; 실측/코드/설치/지출 없음.

## 1. 현재 실제 구현 및 GAP

- src/studio/voice.py blob 3f901f8243a595d30b228d3bb581818df9d8d761: rights_confirmed, 장면 voice 트랙 text/speed/temperature, 고정 narrator ref와 transcript, reference/worker digest 기록, subprocess 1800s, media_info, 자동 트랙 바인딩 및 기존 lip-bound 제거. 청취 승인 별도. 기존 권리·원본·무단 fallback 금지 유지.
- scripts/studio_sovits_worker.py blob d7c0e410eff4548ad3f019454a27a6ccb9a8132c: 고정 GPT/SoVITS v2 쌍·ko·ref, cut0, batch 1, seed 42, speed/temperature, CUDA 있으면 half, 없으면 CPU. 첫 반환 파형 finite/0.35s/RMS/peak 검사, PCM16 저장. worker가 입력 reference/worker digest를 검증하지 않음. 모델/설정/전처리기 전체 digest 및 실제 device evidence 계약 부족. 파형 성공은 발음/감정/원문 일치 아님.
- src/studio/workspace.py blob a900fedf439c7003411f68c7e9de6e3c791c1e63 L169~171,207~249: voice_key=text/speed/temperature/profile, lip-bound=video/voice/image asset IDs+motion text. 기존 무효화 로직은 좋은 출발점이나 실제 음성 hash/발화별 timing/offset/in/retime/정렬 버전/얼굴 추적에 대한 의존을 완전히 결속하지 않음. lip_sync=yes는 선택 및 바인딩이지 동기 정확도 증명 아님.
- [기존 운영 SSOT](../../GPT_SOVITS_V2_TTS_OPERATIONS.md) blob fa65f1760952747aca6219c2f6706d628a0665ff: 기존 Windows 경로·호출 계약 보존. 독립 워커 실행은 작품 승인 우회 아님. 현 Windows 설치·권리·청취·실행 품질은 미검증. 이 문서가 기존 사용 방법을 변경하지 않음.

## 2. 강한 원저자 기반과 선택 근거

1. [GPT-SoVITS API](https://github.com/RVC-Boss/GPT-SoVITS/blob/main/api_v2.py) blob 36891ed2ba3972801d45b8ad8e4d0b3eb0bd2f5b L185~207,392~423: reference/prompt language, auxiliary refs, splitting/sampling/speed/seed, 언어·필수 입력 validation. [한국어 처리](https://github.com/RVC-Boss/GPT-SoVITS/blob/main/GPT_SoVITS/text/korean.py) blob 254b05cf3d9c8af364fa15a0555e4cd363e07724 L170~328: 숫자/라틴문자 변환과 g2pk2 G2P 및 오류 보정. 현재 upstream과 사용자의 고정 v2는 다른 버전 가능; API 필드를 그대로 이식하거나 감정 전달 지원을 추정하지 않음.
2. [Qwen3-TTS 공식 README](https://github.com/QwenLM/Qwen3-TTS/blob/main/README.md) blob 8287bac4e611b907688a74b90a1d39cf7dbeec58 L73~79,150~199,203~290: 한국어 포함 10개 언어; 1.7B VoiceDesign/CustomVoice는 instruction control, 1.7B/0.6B Base는 voice clone, 0.6B CustomVoice는 공식 표에 instruction control 표시 없음. 설계 음성 reference를 create_voice_clone_prompt로 재사용하는 조합 제안. Base에 독립 감정 instruction이 지원된다고 가정 금지. [원저자 보고서](https://arxiv.org/abs/2601.15621) 초록 검색 확인, 전체 논문 검증 아님. Qwen은 강한 challenger, 기존 설치/품질/권리/VRAM/비용 미확인. 기존 GPT-SoVITS 교체 결정 아님.
3. [Whisper transcribe.py](https://github.com/openai/whisper/blob/main/whisper/transcribe.py) blob 56b29fbc888dd607c464ca90c427cf633b24f147 L401~439,556~557: word timestamps experimental, no-speech/hallucination 처리 존재. 독립 ASR 후보; 번역이 아니라 한국어 transcription, 원고를 답으로 주입하지 않은 진단, hallucination/문자 정규화 오류 검사. 자체 ASR 인식 일치만으로 발음/연기 합격 금지.
4. [Korean MFA acoustic v3.0.0](https://github.com/MontrealCorpusTools/mfa-models/blob/main/acoustic/korean/mfa/v3.0.0/README.md) blob 74bdb1ccaccd048999797ecac317d975327436d7: 한국어 강제 정렬, GMM-HMM/MFCC, CC BY 4.0, 저잡음 낭독 데이터 기반. 문서의 0% WER/CER는 동일 훈련 자료의 sanity check, holdout 성능 아님. [MFA align](https://montreal-forced-aligner.readthedocs.io/en/latest/user_guide/workflows/alignment.html) 사전+음향 모델 기반. 정확한 발화 transcript 및 호환 사전/phone set 필요; 잘못 읽은 음성을 강제로 정렬했다고 정상 발화 아님. 감정/속삭임/전투 발화 전이 검증 필요.
5. [MuseTalk](https://github.com/TMElyralab/MuseTalk) README blob 49e76c449c13ec29daef1bdf9b48457cb8909d33: 얼굴 256x256 영역, frozen VAE/whisper-tiny audio embeddings, single-step latent inpainting, 1.5 perceptual/GAN/sync loss 및 시공간 sampling 훈련. 저자 V100 30fps+는 해당 조건 주장, 8GB/한국어/무협 캐릭터 실측 아님. README 언어 예시는 중/영/일이며 한국어 품질 미입증. 얼굴 bbox, pose, 가림, identity 및 주변 보존 별도.
6. [Q3 LTX G02](../technology-library/Q3_LTX25_OFFICIAL_GRAPH_EVIDENCE_2026-11-24.md): 음성 latent freeze 및 원본 trimmed waveform mux. 입력 음성 보존과 정확한 lip sync 구분. A07 영상 계획에서 A2V/별도 face dubbing 후보를 비교한다.
7. [Azure Speech SSML](https://learn.microsoft.com/ko-kr/azure/ai-services/speech-service/speech-synthesis-markup-voice) 및 [언어 지원](https://learn.microsoft.com/en-us/azure/ai-services/Speech-Service/language-support) 공식 검색 본문: 음성·스타일·역할을 선언하는 상용 비교 기준 후보. 음성별 지원 차이/지출/전송·권리 확인 필요, 실제 API 호출 없음. SSML을 모든 엔진에 그대로 보내지 않음.

## 3. GAP 및 도입 결정

| ID | 현행 한계 | 보완 설계 / 기술 선택 |
|---|---|---|
| A81 | 고정 내레이터와 단일 scene voice | Compose character→VoiceProfile revision, 여러 utterance 및 take, 승인 음색 일관성. Adopt 기존 v2와 비교 Qwen variant |
| A82 | 속도/temperature만으로 연기 요구 전달 | Compose PerformancePlan, 가능한 reference/instruction/SSML 매핑; 엔진 미지원 필수 연기 제어는 HOLD, 무단 대체 금지 |
| A83 | 원문/발음/G2P가 별도 상태 없음 | Adopt 한국어 G2P 및 사전 후보; Compose 원문/발화문/발음 변환 trace와 인명·한자어 lexicon |
| A84 | 음량/길이/해시만 확인 | Adopt ASR+MFA 후보; Compose transcript/발음/정렬 및 독립 청취·불확실성 |
| A85 | scene length와 lip-bound ID에 의존 | Compose 실제 sample/frame 정렬, 음성 구간/화자/face track 및 lipsync proof; Adopt LTX A2V/MuseTalk 후보 |
| A86 | scene 단위 재합성, provenance 일부 누락 | Compose immutable takes, 입출력/model/reference/lexicon/aligner/version/time dependencies, targeted retry/reconcile (A07 공통 job) |

Build는 전문 연기 계획·engine adapter mapping·한국어 lexicon/trace·검증 evidence orchestration 연결 등 남은 차이로 한정. 자체 TTS/ASR/aligner/lipsync 신경망 개발 근거 없음. 모든 도입은 설계 후보이며 production qualification 전 교체 금지.

## 4. 목표 전문 생산 로직

### 입력/계약
VoiceProfile: character id, profile revision, voice identity description, approved reference asset hashes 및 실제 대응 transcript/lang, voice consent/license scope(복제/언어/상업/외부전송/철회·만료), provider capability/variant, approved reference style, baseline take. 가상 설계 음성도 생성/모델 권리 및 유사성 확인 필요. 참조와 원고 권리 확인 없이 업로드/복제 금지.
UtterancePlan: script/scene/shot revision, utterance id/speaker id, 원문 span/원문 hash, spoken_text 및 정규화·발음 override trace/lexicon revision, 감정의 원인/행동 목적/상대/억양/강세/호흡/강도/속도·pause·목표 시간, 겹침/화면 안팎 여부, 전후 맥락. 비언어 소리는 별도 role, 연기 지시가 대사로 읽히지 않게 분리. 원문 변경과 발화 정규화 구분; 의미 변경은 상위 원고 승인 경계.
Take: request/recipe/profile/weights/worker/runtime/seed/actual device/input digest, immutable original WAV sample rate/channels/sample count/hash/attempt/evidence. 모델 fallback/CPU 사용은 선택 정책과 자원 계약에서 명시, quality gate 자동 통과 금지.

### 생산 및 평가 흐름
(1) 전문 연기 Add-on이 원고에서 발화/화자와 서사적 연기 방향을 제안. 동일 character voice와 상황별 감정은 별도. 원고와 매핑 누락/중복·잘못된 화자 차단.
(2) 한국어 정규화·G2P/lexicon: 숫자/단위/외래어/인명/동음이의어를 문맥에 맞춰 발화형으로 변환, 원문 보존 및 명시 예외. engine에 따라 실제 지원하는 pronunciation mechanism만 전달. 정확한 발음 확인 전 승인하지 않음.
(3) Manager가 A07과 동일한 capability/권리/예산/lease/version hard filter. 기존 v2 baseline(실측 전 champion 아님) 유지, Qwen 1.7B instruction variant/clone Base 등 서로 다른 기능을 명시 비교. 필요한 감정/identity를 함께 보장 못하면 다른 authorized reference/연기/엔진 대안 또는 HOLD. 단순 temperature를 emotion label과 동일시하지 않음. 후보 take 생성은 예산 범위.
(4) 객관 검사: 실제 decode·sample rate/count, finite/clipping/silence/dropout, independent ASR transcription과 spoken_text 비교(CER/WER, 누락/반복/핵심 인명 오류, normalization policy 고정). 낮은 ASR confidence/모델 간 충돌/짧은 감탄사는 HOLD 및 독립 원어민 판단. ASR 통과한 발화에서 MFA 사전/음향 모델로 정렬 후보 생성. OOV/누락/비정상 duration, coverage, alignment uncertainty 별도. ASR로 정렬 참조를 무단 바꾸지 않음. 독립 한국어 청취로 의미, 발음, 목소리 유지, 감정/자연스러움, 전후 대화 호응 검증. score 단독 승인 금지.
(5) 승인 voice take의 실제 sample 시간을 영상 rational frame timeline에 매핑. sample interval [start,end), rational PTS/timebase, trim/offset/resample/retime transform 및 rounding policy 기록. overlap은 명시된 트랙/화자별로 허용, 무단 truncation/과속으로 scene에 맞추기 금지. 길이 초과는 take 재연기 또는 A05/A07 scene timeline 수정 승인으로 반환. 자막은 확정 원문과 실제 alignment를 사용하며 word timestamp 미검증이면 단어별 자막 금지.
(6) 화면에 보이는 화자에게만 A07 video recipe의 A2V 또는 face-dubbing 조건 제공. 화자별 face track, 실제 voice range, 주변 보존/pose/occlusion/시선/컷 경계. 화면 밖 대사에 다른 인물 입을 움직이지 않음. 복수 화자/교차 대사 지원 여부 hard filter. 최종 mux source audio와 실제 출력 audio의 정렬/내용 확인; resampling/encoding 때문에 byte hash 불일치 가능하므로 허용된 transform 및 sample/신호 비교를 구분. 동기화 검사는 독립적인 audio-visual sync 후보 및 눈으로 확인할 mouth/phoneme event, signed offset과 분포/드리프트·누락 검증. Sync metric 모델/언어/캐릭터 보정 및 기준 선고정. LTX audio freeze나 수동 lip-bound는 합격 증거가 아님.
(7) 발음/누락→해당 utterance의 lexicon/발화형 또는 take 재생성; 감정/identity→performance/ref/voice recipe 재검토; 길이→발화 또는 상위 timeline; 립싱크만 불량→음성 원본 보존, 해당 얼굴/시간 범위 수정. 앞뒤 대화 연결과 편집 접합부 검사. 변경되지 않은 발화/자막/영상·음악을 자동 재생성하지 않되 timing 이동/의존 변화는 정확히 stale 처리. 동일 오디오를 사용하고도 offset/in/retime이 변경되면 alignment/lipsync/subtitle/mix affected revision 재검증. 원본/실패 take/선택/승인 이력 보존. revoked reference는 향후 사용 차단 및 기존 결과 권리 재심사, 임의 삭제 금지.

## 5. 5축 및 검증 경계

Core: generic media/time/revision/evidence/job contracts, 언어·음성 엔진 특수 로직 없음. Bridge: feature-blind route, lifecycle, execution/cancel/reconcile; Add-on: voice director, lexicon/normalizer, synthesis adapter, ASR/aligner/lip-sync adapter, 분야 전문 evaluation/repair proposal, private state. 다른 Add-on 직접 호출 금지. Central Manager: capability/정책·승인·권리·resource lease·dependency invalidation·evidence authentication/quality promotion, 공급자별 분기 없음. JSON: 데이터/이력/pin/evidence refs persistence-only. 실제 M-VML 변경/migration과 실행 코드는 현재 없음.

사전 반례: 같은 narrator가 복수 화자를 읽어도 승인; Qwen Base가 instruction control 지원한다고 가정; ASR가 원고를 반복했다고 정확한 낭독 인정; MFA 훈련 WER 0%를 실제 감정 발화 정확도로 인용; 실제 음성 시간 변경에도 이전 lip-bound 사용; offscreen 대사를 다른 화자가 입모양으로 표현; waveform hash/길이만으로 sync 합격; 권리 만료 ref의 새 생성. 알려진 중대한 오류는 차단, 미측정은 HOLD. 실제 비교 표본/원어민·독립 평가·ASR CER/정렬·sync 허용치/비용/속도·identity 평가의 보정은 실험 전에 별도 확정. 현재 모델·발음·감정·립싱크/실제 GPU 및 모델 권리 검증 NOT_RUN. 임의 숫자 합격선 설정 금지. A08 NOT_QUALIFIED, D1/D3/D4/D5 HOLD. 다음 A09 음악·효과·믹싱 실제 기존 renderer와 전문 loudness/ducking/stem·권리·시간축 비교. 전체 코드 동결 유지.
