# A05-01 스토리보드·도식 프리비즈 실제 산출물 및 동선 수정 — 2026-11-24

기준 main a9fd71d6d3bd9c00fe46e3803c7c8f395e580401. 연구 입력 [A04 B r2](a04-01/B_MASTER_PACK_R2.md) blob 1d29bae951a7a83085213ffc08c07303700e6edb. A04 승인 아님. 상위 [공정 심사 원장](STAGE_ACCEPTANCE_REGISTER.md), [압축 실물 계약](../../MURIM_SHORT_FORM_MARKET_VALIDATION.md), [전문 집필 설계](../../skills/screenplay-master/references/production-design-review.md)의 필수 조건 유지. A05 NOT_QUALIFIED / PARTIAL_SCHEMATIC_PREVIS_EVIDENCE.

## 1. 실제 쇼트 설계 및 시간축

[연구 쇼트 타임라인 JSON](a05-01/SHOT_TIMELINE_R2.json)에는 원고 줄 번호, shot ID, frame 단위 half-open 범위, 대사 원문·cue 시간, 공간/소품 상태와 이산 전환을 결속. 원고 실제 20개 비어 있지 않은 본문 줄(끝 표기 포함)을 13개 쇼트에 한 번씩 연결, 11개 대사 cue 원문 위치·순서 전수 대조. 0~1992 frame, 24/1 fps, 83초, gap/overlap 없음, 모든 cue는 해당 shot 안. 실제 Python 생성 시에도 줄 번호 집합 및 cue 개수/범위 검사. 60~90초 brief의 계획된 상영 길이 안에 있으나 배우 낭독·연기 기반 상영시간 아님.

공간 계획은 연구자 선택: 화면 좌측 도윤/장부·붓, 우측 관문·종, 소연은 좌측 상대를 바라보다 관문 방향으로 화면 오른쪽 통과; 카메라 후보는 동일 축 wide/two-shot/close insert/인물 close. shot S01~S03 도입 0–17s, S04~S07 갈등 17–46s, S08~S10 전환 46–64s, S11~S13 선택 및 결말 64–83s. S05 장부 닫힘, S09 재개방, S11 백무진 서명, S12 통과 후 종 시작(텍스트 표시), S13 문 폐쇄·장부 공개 유지. 약상자 소연 소지 유지, 환자 회복 미표현. 추가 인물/전투/사건 없음. 공간 축과 연기 실현은 전문 판단 후보, 실제 3D 카메라/배우 시선·물리 검증 아님.

## 2. 실제 렌더 및 검증 (제품 코드 없음)

격리 Linux 기존 Python/Pillow 12.3.0, FFmpeg 7.1.5-0+deb13u1 사용. 연구용 ephemeral script로 960x540 기하학적 blocking frame을 1초 간격 83장 생성, 24fps H.264/yuv420p MP4 인코딩(프레임 반복), 13컷 PNG contact sheet 생성. 표시 대사 원문 및 상태 label, 오디오 트랙 없음. r1, r2 모두 ffprobe 960x540 / 24/1 / 1992 frames / 83.000000s / video stream 1개, ffmpeg 전체 디코딩 오류 없이 종료. 실제 파일은 대화 첨부로 제공; GitHub에는 아래 해시 및 연구 타임라인·원장만 보존(바이너리/ephemeral render script 미전송, exact rerender source 저장 안 됨). 세션에서 파일 재접근 불가 시 첨부 원본/해시로 검증하거나 timeline에서 새 revision으로 재제작; 새 렌더를 기존 byte-identical artifact로 주장하지 않음.

| 파일 | bytes | SHA-256 |
|---|---:|---|
| A05_storyboard.png | 216130 | 062bcdd07cef8705ed1bca659549069f7e6bbafa40ed002255c2352e6e4b36a3 |
| A05_animatic.mp4 | 300426 | f52fb4cefba77cda3d8878db53b2c7864a5665b310e396e3b94ce2147251e4c1 |
| A05_storyboard_r2.png | 217282 | fb4c889e034bf61bb5c4f8414c3c6a915d50966c7c562e90fb1731a44ae5dd00 |
| A05_animatic_r2.mp4 | 302774 | 30de6e1608ffecaf68495e8c87142868d48d99db2794bac4e3c48ffcd136b7a4 |

실제 전환 프레임 contact sheet를 작성자 시각 검토. r1에서 70초 도윤/소연 도식이 겹침, 75초 도윤이 문에서 책상 앞으로 즉시 이동. 원본 보존, S12/S13 도식 위치만 r2 표적 수정: 70초 도윤 x650/소연 x745, 71/72초 소연 x790/x835, 73초 이후 소연 부재, 75~76초 문 옆 도윤 x650, 76초 문 닫힘, 77초 x450, 78초 x225. r2 contact sheet에서 두 실험 결함 완화 관측; 실제 물리적 비충돌, 걷기 자연스러움, 문 손잡이 접촉, 이동 속도는 미검증. 1Hz 도식 단계 전환을 실제 연속 애니메이션으로 간주 금지.
두 MP4 전체 framemd5 디코딩 검사: 0~68.999초(1656/1656 frames) 해시 동일; 69~82.999초(336 frames) 중 250 decoded frame hash 변경. 실제 관측된 수정 범위 S12/S13 이외 변화 없음. r1/r2의 전체 길이/shot ID/대사 cue/source blob 동일. 이후 원고·기존 좋은 구간 재작성 불필요. 해당 결과는 연구 fixture의 국소 변경 증거이며 제품 캐스케이드 구현 검증 아님.

## 3. A05 심사 범위 및 다음

| 요구 | 이번 실제 증거 | 판정 경계 |
|---|---|---|
| 원고/쇼트 양방향 추적 | 20줄 13컷, 11 대사 cue | 선언된 전체 본문 전수 연결 확인; semantic 누락 독립 검사 미실행 |
| 시간·공간·시선 연속성 | 83초 디코딩, 위치/장부/문 도식, S12/S13 수정 | 실제 배우·카메라/연속 모션 미실측 |
| 실제 animatic | 무음 도식 r1/r2 렌더 및 디코딩, 표적 수정 | 완성 영상/실제 연기·대사 아님 |
| 이해·리듬·전문 비교 | 작성자 확인만 | 독립 관객·전문가·강한 동등 비교 NOT_RUN |

A05 NOT_QUALIFIED. 평가자 접근 및 실제 연기/음향/ComfyUI 환경 미확보 ENVIRONMENT_ISSUE; r1 두 결함은 연구 산출물 결함으로 분류, 제품 소스 결함 아님. 비교/전문성 검증 기준 하향 금지. 다음 A06 캐릭터·미술·자산 상세 심사: 같은 원고와 shot timeline을 미승인 연구 입력으로 pin, 필요한 인물/소품/환경 asset 목록, 같은 인물 각도/표정/조명 비교를 위한 실물 참조 가능 범위, 권리 및 정체성 검증. 승인 없는 외부 전송/유료 생성/설치/게시 금지. A05 재개 조건은 실제 낭독/영상/독립 animatic 비교 및 시선·동작·공간 검증. Q1~Q4/A04 미달 유지. 신규 제품 코드/테스트/UI/DB/Windows 변경 0. DESIGN_HOLD / PRODUCT_CODING_FROZEN / REMEDIATION_REQUIRED.
