# A09 전문 음악·효과음·믹싱 기반기술 및 생산 설계 v0.1

2026-11-25 KST | 기준 87dad6cb7f370f07f8e531adbefc3c80a3b51799 | D2 상세 설계 보완안 / A09 NOT_QUALIFIED / DESIGN_HOLD.
[5축](../../MURIM_FIVE_AXIS_ARCHITECTURE.md), [D0~D5](../../MURIM_PRECODE_DESIGN_GATE.md), [A07 영상](A07_VIDEO_PRODUCTION_DESIGN_2026-11-25.md), [A08 음성](A08_VOICE_PERFORMANCE_DESIGN_2026-11-25.md) 유지. 원본 코드와 공식 기술의 설계 비교이며 실행/청취/제품 코드 변경 없음.

## 2026-11-25 — 공동 AV 음향 보존·정밀 믹싱 계약 및 실제 격리 DSP 확인

A07 native Deno graph는 joint AV decode→VHS이며 원본 음성에는 대사/음악/효과가 혼합되어 있을 수 있다. 현재 render.py의 영상 branch는 [0:v]만 사용하고 독립 voice/bgm/sfx 또는 anullsrc를 [a]로 map한다. 현재 제품 변경 없이 해당 routing GAP을 확인. 기존 A08 Joint AV/Voice-first/Narration 구분을 A09/A10에 연결한다.

### 실제 격리 CPU 반증 (제품/GPU/Windows 아님)

격리 Linux /usr/bin/ffmpeg 7.1.5-0+deb13u1, numpy float32 PCM, 48000 Hz mono, 48000 samples, 0 기반 index 4800에 0.5, 24000에 1.2, 나머지 0. 입력/출력 f32le pipe, -af 단일 필터, 같은 rate/channel. -h filter=alimiter 실제 level default true, latency default false, attack default 5ms. 실행 returncode 0, 결과 직접 sample 측정:
| 필터 | samples | peak | nonzero indices |
|---|---:|---:|---|
| anull | 48000 | 1.2000000477 | 4800,24000 |
| alimiter=limit=0.95 | 48000 | 1.0 | 5039,24239 |
| alimiter=limit=0.95:level=0:latency=1 | 48000 | 0.9499999881 | 4800,24000 |
같은 입력에 adelay=42:all=1 first nonzero=6816, delay=2016; adelay=2000S:all=1 first=6800, delay=2000. 24fps 한 frame=2000 samples 정확; 기존 round(offset*1000)에서 42ms→16 samples 오차. 단일 offset 반올림 오차이며 기존 구현의 전편 누적 drift를 측정한 것은 아님. sample peak는 true peak와 다름. 실제 stereo/multi-cue/AAC codec priming/tail/quality 및 Windows 설치 지원은 NOT_RUN.

별도 1s 합성 FFV1 64x64 24fps black + 440Hz 48kHz mono PCM16 sine MKV를 임시 생성하고 audio mapping을 1초 f32le decode로 비교: -map 0:a RMS 0.0883687660 peak .1249694824; 별도 anullsrc -map 1:a RMS/peak 0; [0:a]asplit=2[a][b];[a][b]amix=inputs=2:normalize=0[m] RMS .1767375320 peak .2499389648. 전부 48000 samples. 동일 신호의 중복 합산은 진폭 2배, 독립 무음 선택은 원본 신호 누락. 실제 Deno 대사 의미/품질이 아니라 mapping 반례. 임시 합성 fixture만 생성/자동 제거, Windows/제품 소스/원본 콘텐츠 변경 없음. 전체 render_scene 및 실제 product tests NOT_RUN. 검증 결과를 일반화하지 않음.

### AudioRoutingPlan — 원본과 독립 stems의 명시적 의미 계약

| 입력 상황 | 경로 | 금지/검증 |
|---|---|---|
| Deno joint AV 승인 audio | protected joint mix bus, 원본 stream+range+PTS/digest pin, 별도 추가 cue는 의도와 충돌 여부 확인 후 | D/M/E stem으로 허위 분류 금지, 동일 대사/효과 다시 합산 금지, dialogue 없는 shot에 우발 발화 검사 |
| joint AV와 별도 승인 대사 | 해당 joint source의 대사/음악/효과가 무엇인지 확인; 승인된 교체 또는 별도 검증된 분리 capability 및 source coverage | 음성 교체만으로 립싱크 인정 금지; 혼합 원본에서 대사만 mute 가능한 것으로 가정 금지; 보존/분리 불가능하면 HOLD |
| voice-first / A2V | 승인 실제 take를 authority, generated embedded track과의 sample/content alignment 검사, 명시적 한 경로만 선택 | 원본 대사와 동일 내용 중복 방지; 얼굴/타임라인 정합 검증 |
| narration/offscreen | approved narration cue + 실제 승인 ambience/music/effect routing | 화면 밖 대사에 다른 인물 입동작 금지, 자동 전체 영상 음소거 금지 |
| 의미 미확인/권리 불명/분리 불충분 | unknown, HOLD 또는 명시적 승인된 mute가 창작 요구를 보존할 때만 | 신뢰 없는 자동 stem 추정/무단 모델 fallback 금지 |

각 source stream의 source provenance/asset digest, stream index/timebase, semantic role/coverage, ownership(utterance/event IDs), route action(keep/mute/replace/derive), 승인 이유/권리와 placement를 저장. 음원 종류뿐 아니라 사건/발화 identity 기준으로 중복 확인; waveform 유사도는 후보 신호이지 다른 녹음의 동일 발화 여부를 완전히 판정하지 못함. source audio를 포함한 영상 원본 불변. 실제 독립 stems가 없으면 protected joint mix라고 표시하고 D/M/E 납품 필수일 때는 HOLD. 분리 모델은 별도 capability로 artifact/누출/잔류 대사/음질 손상 및 재합산 일치 검증; original multitrack으로 표기 금지.

SoundPlan의 spotting: 실제 승인 shot와 A08 utterance/반응/접촉 event를 기준으로 silence, motif, score, Foley, ambience cue 결정. 동일 공간의 room tone 및 음악 phrase는 전편 timeline에서 연결. Deno의 원래 유효한 음악/효과를 자동 제거하거나 모든 장면에 음악을 생성하지 않는다. 기존 ACE-Step v1/Stable Audio Open 파일명은 실제 inventory 근거이며 신규 ACE-Step1.5 설치/권리/음향 품질 아님; 기존 승인 음원 재사용 우선, 생성·분리·믹싱 엔진 직접 개발 제외.

정밀 mix: target rate 초기 후보 48000, 각 경계는 전편 rational clock에서 정수 sample 위치로 한 번 결정. 독립 source clock과 output offset을 분리, adelay exact sample suffix S 또는 동등한 verified adapter 사용. output PCM sample count/PTS 및 source anchor를 probe. 기존 alimiter 후보를 무조건 적용하는 대신 explicit level/latency/attack/release 설정과 headroom, 실제 nonzero anchor/tail/peak/true peak 및 최종 loudness 재계측. 위 개선값은 반례 해결 후보이지 전체 mix preset 확정 아님. DSP/FFmpeg 원형 재사용. D/M/E 및 joint bus를 lossless intermediate로 보존, pre-master 합산과 nonlinear master 분리, 납품 profile별 loudness/TP/codec delay 검증. 전체 master 재렌더와 원본 AV 재생성은 별개.

5축: A09 Add-on만 음향 의미·route/spotting/FFmpeg DSP recipe·전문 평가를 소유. Core generic refs/time/ranges, Bridge generic route, JSON persistence, Manager generic policy/lease/DAG/promotion. A07/A08/A10 Add-on 직접 호출 없음. 이번 설계와 격리 DSP 관측은 D2 보완 근거; 실제 Windows stereo/codec/실제 Deno 음원 청취·독립 평가/권리 미확인, A09 NOT_QUALIFIED/DESIGN_HOLD.

## 1. 실제 현행 구현

- src/studio/render.py blob 24ab7cf85576d84d3d42d05bab2724e5b8e80d67: render_scene()은 voice/bgm/sfx를 48kHz stereo로 resample, 일정 gain, millisecond adelay, apad/atrim 후 amix=normalize=0, alimiter=limit=0.95. voice의 -45dB max_volume 무음 기준, 장면 길이 초과 시 차단. AAC stereo 192k 출력. 실제 영상 입력의 embedded audio는 명시적으로 사용하지 않고 최종 [a]만 map. 의도된 동시 생성 대사/효과음의 누락 또는 독립 트랙과 중복 위험을 후속 설계에서 처리. render()은 장면별 clip을 concatenate하여 전체 출력. 장면/자산 해시 기반 cache 및 원본 보존, 기술 성공과 품질 미승인 구분은 보존.
- src/studio/workspace.py blob a900fedf439c7003411f68c7e9de6e3c791c1e63: AUDIO=(voice,bgm,sfx), 장면당 kind 하나, gain/offset/in/text 및 음성 추가 속성. 독립 다중 cue, 장면을 넘어가는 트랙, gain envelope, bus/stem, loudness target, 공간/음향 연출 계획 없음.
- 위험: upstream FFmpeg alimiter의 auto level 기본 enabled, lookahead 지연 존재. 현재 limit=0.95만 지정했으므로 최종 true peak ceiling/무지연을 보장하지 않는다. normalize=0 자체는 합산 방식이며 loudness 정규화가 아니다. 실제 현 설치 버전에서의 동작 및 영향은 NOT_RUN; 현재 출력의 clipping/AV drift를 실측했다고 주장하지 않음.
- 실제 음성·BGM·SFX를 제공받은 후 합성하는 코드이며 음악 작곡, Foley, 대사 마스킹 평가 및 자동 음향 연출이 구현됐다고 볼 수 없음. repo-wide 감사 아님.

## 2. 강한 공식 비교 기준

- [FFmpeg filters.texi](https://github.com/FFmpeg/FFmpeg/blob/master/doc/filters.texi) blob 84993c59f3c28d6ead09250b321d03cad8632931: L895 adelay exact sample suffix S, L2269 alimiter lookahead/auto level/latency compensation, L2513 amix sum/normalize/dropout, L5855 loudnorm integrated/LRA/true peak, two-pass and linear→dynamic fallback, dynamic 192kHz resampling, L6323 sidechaincompress second stream detector/attack/release, L32654 ebur128 momentary/short-term/integrated/LRA. [공식 필터 문서](https://ffmpeg.org/ffmpeg-filters.html). 설치 버전 및 필터 옵션 지원은 확인 필요.
- [EBU R128 공식 페이지](https://tech.ebu.ch/publications/r128), [Tech 3343](https://tech.ebu.ch/publications/tech3343), [EBU loudness overview](https://tech.ebu.ch/loudness): programme integrated loudness -23 LUFS 및 LRA/maximum true peak 기준. 방송 programme 기준이며 전 배포 채널 또는 모든 개별 stem의 고정 target 아님. 최신 권위 profile 판본/허용차/short-form·streaming 적용 규칙을 납품별 확인. 이번 PDF 본문은 분석하지 않음.
- [Netflix BWAV ADM dubbing guide](https://partnerhelp.netflixstudios.com/hc/en-us/articles/38234663714835-BWAV-ADM-Creation-Guidelines-for-Dubbing) 공식 검색 본문: stems의 합이 의도된 5.1 mix를 재현, dialogue-gated -27 LKFS 사례. EBU programme integrated -23 LUFS와 서로 다른 측정 모드/납품 조건; Murim 기본 stereo에 Netflix 납품 요구를 강제하지 않음. 전문 DAW/편집 교환과 D/M/E 분리의 기준 후보이지 동일 품질 인증 아님.
- [ACE-Step 1.5 README](https://github.com/ace-step/ACE-Step-1.5/blob/main/README.md) blob f5c20302cde16e37e8a17ea28308495371befbfa L26,41~79,131~140,195~196: duration/BPM/key/time signature, repaint, stem separation, local/async API. 공급자 저VRAM/성능 주장은 해당 variant/조건에 한정. XL은 별도 >=12GB offload 조건으로 과거 8GB 목표에 자동 적합하지 않음. README 기능표 확인만으로 실제 정확한 cue 길이·음악 전문성·stem 분리·권리 확정 금지.
- [Stable Audio Tools generation.py](https://github.com/Stability-AI/stable-audio-tools/blob/main/stable_audio_tools/inference/generation.py) blob 6be95d5151d65e392d496ffe314caf5baa81f1f6 L85~147: conditioning, negative conditioning, initial audio, sample size, duration adaptation. [공식 repo](https://github.com/Stability-AI/stable-audio-tools). 툴 코드와 각 가중치/model card/license 별도. 실제 Foley 접촉 동기, 정확한 duration, 권리/장비/품질 미검증. 생성 모델·기존 권리 확보 음원 라이브러리·녹음/합성 음향을 같은 cue 목적별로 비교한다.

## 3. GAP 및 도입 선택

| ID | 현행 한계 | 개선 계약 |
|---|---|---|
| A91 | 장면별 음원 첨부, 서사·감정 음악 계획 없음 | Compose SoundPlan 및 MusicCue; Adopt 권리 확보 라이브러리/ACE-Step 후보 |
| A92 | 단일 SFX, 접촉·환경·공간 제어 없음 | Compose multi-cue Foley/ambience, 실제 영상 사건 시점, gain/pan/distance/reverb; Adopt 기존 음원·Stable Audio 후보 |
| A93 | 고정 gain, dialogue masking 제어 없음 | Adopt FFmpeg sidechaincompress/EQ/fade 등; Compose D/M/E bus 및 gain automation, 연기 보존 |
| A94 | 장면별 clip+concat, sample offset 반올림 | Compose 전편 sample-accurate timeline, 음악/room tone carry, J/L-cut/crossfade, A08/A10 연계 |
| A95 | peak/길이 위주, loudness/true peak 및 master 없음 | Adopt ebur128/loudnorm; Compose delivery-specific profile, measurement→adjust→remeasure |
| A96 | 영상 embedded audio 미사용, scene cache 단위 | Compose explicit audio source routing, immutable stems/takes, local repair+master revalidation |

Build는 전문 sound planning, cue/asset/rights/recipe adapter 및 evidence binding 차이에 한정. FFmpeg DSP·새 음악 신경망을 직접 재구현할 근거 없음. 현재 선택은 설계 후보이며 production 채택/권리/실측 미확정.

## 4. 전문 생산 및 입출력 계약

SoundPlan: 승인된 story/shot/utterance/video revisions, 시퀀스별 감정/관객 정보·음향 관점, scene space 및 acoustic continuity, silence intent, 음악 motif/변주/전환, 출처·권리·자원/채널 요구. Add-on이 spotting 단계에서 음악 시작/종료, 동작 사건, 화면 밖 음원, 대사 보호와 무음의 대안을 계획한다. 소리로 이야기 전달을 강화하되 모든 장면에 음악을 삽입하지 않는다.
Cue: stable id, role/dialogue/music/foley/ambience/effect(확장 가능한 전문 schema), asset+digest 또는 generation recipe ref, 실제 source interval 및 output interval half-open, sync anchor/uncertainty, tempo/beat/phrase 또는 contact event, gain envelope/fade/pan/space, intended continuity, speaker/prop/location refs, overlap/priority, rights and version. 한 장면에서 여러 cue/트랙 허용. 승인 음성 A08 원본 보존. 영상 embedded audio는 dialogue/music/effects/unknown으로 출처 및 내용 검사 후 explicit route 또는 mute; 같은 대사 double-mix 차단, unknown 의미/권리/분리 품질은 HOLD. 원본 스트림 보존.
Generation: 기존 승인 음원 검색/재사용 우선, 신규 음악/효과 생성은 요구에 맞는 검증된 capability/variant 및 rights·lease·budget filter 이후. 음악의 실제 beat/phrase/tempo 및 cut·fade 연결 후보 검사. 요청 BPM/length와 실제 output 구분, 생성된 음악을 임의로 연주자/기존 작품으로 사칭하지 않음. 권리 불명 음원/참조/상업 이용 범위/전송은 차단. 자산별 source, license revision, model/weight/recipe/seed/input digest 및 승인 evidence 보존. stem separation을 원본 multitrack과 동일하다고 가정하지 않는다.
Timeline: A08/A10 공통 rational timebase 및 asset refs 사용, sample rate별 source sample mapping과 resample/retime/latency transform 기록. target 48kHz는 현 stereo 렌더와의 초기 제작 profile 후보, 원본 그대로 보존. 24fps/48kHz는 frame당 2000 samples. 다른 fps에서 매 frame 반올림 누적 금지, 절대 경계 sample 계산 및 remainder 정책. 전편 음악/room tone을 장면별로 자동 재시작/절단하지 않는다. video frame 사건·실제 waveform cue를 결속, filter/codec delay 및 AAC priming을 측정. 영상 편집 승인 변경은 A10에 제안, 실제 영상/음성 불변.
Mix: dialogue, music, effects/ambience stem 및 필요 세부 bus를 개별 렌더. 고정 gain 합산 baseline과 전문 계획+ducking 비교. dialogue 활동/강세 및 음향 의도를 기반으로 음악·효과음 envelope/sidechain을 선택적으로 적용. ducking 자체가 명료도 보장 아님; attack/release로 pumping/첫 음절 마스킹/불필요한 음악 감쇠 방지 검사. EQ/dynamics/pan/room·fade는 실제 context에 따라 선택하고 원본 take/연기 훼손 검사. gain stage/headroom, explicit limiter auto-level/latency, sample alignment 검증. Stem sum과 master 재현 조건 명시: bus nonlinear processing 전 합산과 최종 master processing을 분리, nonlinear master를 각 stem 독립 적용한 합이 원래 master와 같다고 가정 금지.
Master: delivery profile id/version, programme/dialogue-gated 측정 모드, channels/layout, sample rate/codec, loudness/true peak/LRA 및 허용 편차, source specification/rights. EBU 방송과 타 플랫폼 기준을 구분. pre-master lossless stem/mix와 측정 기록; two-pass loudnorm 첫 측정→두 번째 설정에 actual measured values 전달→실제 linear/dynamic 모드 기록→최종 인코딩 후 재측정. 필터 자체의 latency/resampling/auto gain 및 codec peak 변화 확인. 단순 peak 제한과 true peak/dBTP 구분, LRA/short-term은 의도와 가독성의 추가 지표. 모든 stem/장면을 동일 LUFS로 normalize하여 서사 dynamics를 없애지 않는다.
Quality: 객관적으로 file/stream/sample count/duration/channel, clipping/dropout, source/cue coverage, AV sync, loudness/TP 및 stem/mix routing, 필수 음원 누락/중복·권리 검사. 전문 독립 청취로 대사 이해·감정·음악의 서사 기여·효과 타이밍·공간·전환/연속성/과도한 압축 평가. 무음악/현재 고정 gain/전문 믹싱 강한 대안을 동일 승인 원고·영상·음성/예산에서 비교. 청취 환경/음량 통제 및 bias/원어민 이해도/샘플·margin 사전 고정. 정규화 수치 합격만으로 음향 작품성 인정 금지.
Repair: 특정 cue/asset/automation 수정 시 영향을 받는 범위 및 reverb/fade/sidechain tail, adjacent cut 및 master global dynamics 의존성 포함. 원본 음성·영상·변경되지 않은 stem 보존, timing/전체 믹스의 새 revision 및 master remeasure. 무조건 전편 재생성 금지; 최종 master 재계측/재인코딩은 원본 재생성과 구분. 불확실 권리/누락 필수 cue/실제 품질 미검증 HOLD. A07 job/reconcile 및 A08 음성 결속 정책 재사용.

## 5. 5축 및 반증 계획

Core: generic media/time/asset/revision/evidence primitive, DSP/음악 의미 없음. Bridge: lifecycle/routing/격리·실행 상태 전달. Add-on: 음향 감독/음악·Foley 생성·음원 선택/믹싱 adapter/전문 품질 평가와 repair proposal, private state; 다른 Add-on 직접 호출 금지. JSON: cue/stem/recipe/profile/measurements/rights/evidence persistence-only. Central Manager: capability selection, approval, budget/lease, DAG/invalidation 및 evidence authentication/promotion. 공통 축에 ACE-Step/FFmpeg/채널별 하드코딩 금지. 기존 M-VML 및 실제 renderer 보존; 통합 migration은 전체 설계 심사 전 금지.

사전 반례: limit 0.95만으로 true peak 보장; EBU -23을 모든 채널/스템에 적용; 대사 peak가 크면 명료하다고 인정; 같은 대사를 embedded audio와 voice stem에서 중복; 장면마다 음악 초기화; 1ms rounding 누적 및 limiter/codec delay 미검증; stem separation과 multitrack 동일시; linear fallback을 미기록; 단일 cue 변경 후 global loudness 이전 값 재사용; 코드 MIT/Apache를 모델·음원 권리와 동일시. 실제 오류 검출/청취/환경/비용은 NOT_RUN. 독립 전문가·관객·비교군, 실측 허용치 및 기준 판본 확보 필요. D2 보완, D1/D3/D4/D5 HOLD, A09 NOT_QUALIFIED. 다음 A10 편집/합성/자막: 기존 render/workspace/M-VML과 OTIO, NLE, 자막/시간축 및 합성 원저자 기술 비교. 예시 작품 제작 반복 금지, 전체 코드 동결 유지.
