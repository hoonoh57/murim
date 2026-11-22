# GPT-SoVITS v2 TTS 요청·실행·반환 운영 설명서 (Murim)

> **용도:** 앞으로 다른 ChatGPT 세션·작업 프로젝트에서도 기존 Windows GPT-SoVITS v2 설치를 재사용하여 **한국어 문장 + 속도 + Temperature → 실제 WAV 파일**을 얻기 위한 상세 SSOT.
>
> **소스 기준:** `hoonoh57/murim` main, 커밋 `7e786954213e` (2026-11-23에 대조). 작업이 시작될 때는 **현재 HEAD에서 소스를 다시 읽어** 경로/모델/파라미터 변경을 확인한다.
>
> **상태:** 소스 호출·출력 계약을 확인하여 문서화함. **이 문서 작성 시 현재 Windows 엔진 실행/새 음성 생성은 NOT_RUN.** 기존 사용자 음성의 권리·실제 청취 및 게시 승인은 별도.
>
> **중요:** 이 문서는 음성 *합성 호출*에 대한 설명이다. 전체 원문에서 TTS용 문장을 선별하는 고차원 문서 파싱·요약 로직이나 신규 API 서비스가 구현되었다고 주장하지 않는다. 임의 텍스트를 직접 합성하는 A 경로와 **사전 제작 승인 이후** Studio 장면 음성을 합성하는 B 경로를 구분한다.

## 0. 가장 빠른 선택

| 원하는 결과 | 사용 경로 | 호출의 실제 반환 |
|---|---|---|
| 다른 세션/다른 작품의 **문장 하나를 독립 WAV로** 받기 | **A. 기존 `scripts/studio_sovits_worker.py` 직접 실행** | 입력 JSON 옆 `voice.wav`, `resolved_tts.yaml`, 프로세스 종료코드 |
| 승인된 Murim 작품의 **장면 `voice` 트랙을 재합성**하고 자산으로 연결하기 | **B. Studio UI 또는 localhost REST** | `voice_result.asset`, `seconds`, `fits`, `job`; 해당 자산을 GET하여 WAV 받기 |
| 기존 무협 `AudioAgent.tts()` 사용 | **이 목적으로 사용하지 않음** | mock이면 `mock_tts_ko.mp3` 경로, real-provider는 스텁, 역사서사 모드는 차단 |

Studio의 승인/권리/리비전 검사를 피해 미승인 작품의 결과를 바꾸려면 A를 쓰라는 의미가 **아니다**. A는 독립 음성 자료 생성용이며 Studio 자산 등록/제작 승인을 자동으로 하지 않는다.

## 1. 설치 및 파일 위치 (실제 코드 기본값)

| 항목 | 기본 위치 또는 역할 |
|---|---|
| Murim 소스 | `E:\gpt\projects\comfyui\murim` |
| 기존 GPT-SoVITS 루트 | `E:\GPT-SoVITS` |
| GPT-SoVITS 실행기 | `E:\GPT-SoVITS\runtime\python.exe` |
| 호출 워커 | `<Murim>\scripts\studio_sovits_worker.py` |
| 고정 참조 음성 | `E:\GPT-SoVITS\refs\narrator_ref_7s.wav` |
| 합성 설정 원본 | `E:\GPT-SoVITS\GPT_SoVITS\configs\tts_infer.yaml`의 `v2` 항목 |
| GPT-SoVITS GPT/SoVITS 가중치 | 아래 2절의 v2 pretrained 쌍 |
| Studio 작업 결과 | `<Murim>\outputs\studio\<project-id>\voice-jobs\<job-id>\` |
| 독립 워커 예시 결과 | `<Murim>\outputs\tts-standalone\<job-id>\` (**이 문서에서 정한 예시 경로**, 기존 API 고정 경로 아님) |

`src/studio/voice.py`는 `MURIM_SOVITS_ROOT` 환경변수가 있으면 기본 `E:/GPT-SoVITS` 대신 그 루트를 사용한다. 직접 워커는 환경변수를 읽지 않고 **현재 작업 디렉터리(`Path.cwd()`)를 GPT-SoVITS 루트로 사용**한다. 반드시 그 디렉터리에서 실행한다.

**실제 실행 전에 확인:** 기존 실행기·참조 음성·워커·가중치가 존재하는지 확인. 기존에 정상 동작한 설치를 보존하고 설치/모델 교체/자동 다운로드를 시도하지 않는다. 사용 권한이 없는 성우 참조 음성을 합성에 쓰지 않는다.

### v2 모델/사전학습 경로 (워커 하드코딩)

- `GPT_SoVITS/pretrained_models/gsv-v2final-pretrained/s1bert25hz-5kh-longer-epoch=12-step=369668.ckpt` → `t2s_weights_path`
- `GPT_SoVITS/pretrained_models/gsv-v2final-pretrained/s2G2333k.pth` → `vits_weights_path`
- `GPT_SoVITS/pretrained_models/chinese-roberta-wwm-ext-large` → `bert_base_path`
- `GPT_SoVITS/pretrained_models/chinese-hubert-base` → `cnhuhbert_base_path`

워커는 `tts_infer.yaml`의 `v2` 부분을 복사하고 위 네 경로, `device`, `version='v2'`, `is_half`를 설정하여 **작업 디렉터리가 아닌 요청 JSON 옆**에 `resolved_tts.yaml`을 작성한다. GPU가 있다면 CUDA/half, 없다면 CPU/non-half를 선택한다. CPU 실행이 품질·속도까지 검증됐다는 뜻은 아니다.

## 2. 실제 Python 워커 요청 계약

**호출 형태:**

```powershell
# 현재 작업 폴더가 반드시 GPT-SoVITS 루트여야 합니다.
& 'E:\GPT-SoVITS\runtime\python.exe' 'E:\gpt\projects\comfyui\murim\scripts\studio_sovits_worker.py' 'E:\gpt\projects\comfyui\murim\outputs\tts-standalone\<job-id>\request.json'
```

워커는 **명령줄 첫 번째 인수**(`sys.argv[1]`)에서 JSON 파일을 읽는다. JSON 파일의 실제 필수 입력은 다음 네 항목이다.

```json
{
  "text": "이 작품은 한 폭의 그림이 어떻게 여러 사람의 손을 거쳤는지 보여줍니다.",
  "prompt_text": "안녕하세요. 오늘은 단순히 줄거리를 훑는게 아니라, 한편의 이야기가 어떻게 첫 순간부터 우리를 완벽하게 사로잡는",
  "speed": 0.92,
  "temperature": 0.65
}
```

**실제 필드와 선택 가능한 설정**

| 입력 | 자료형 | 소스상 동작 |
|---|---|---|
| `text` | string | 실제로 읽을 한국어 발화 전체; `text_lang='ko'` |
| `prompt_text` | string | 참조 음성에 대응하는 실제 발화 전사. 기존 기본값은 상기 한국어 `REF_TEXT`; `prompt_lang='ko'` |
| `speed` | number | `speed_factor`; Studio 기본 `0.92`, M-VML에서 허용 `0.75..1.25` |
| `temperature` | number | 샘플링 온도; Studio 기본 `0.65`, M-VML 허용 `0.2..1.2` |
| `model` | string | Studio가 `GPT-SoVITS-v2`라고 기록하는 **감사 메타데이터**. 워커는 이 키를 사용해 모델을 선택하지 않음 |
| `reference_sha256`, `worker_sha256` | string | Studio가 작업 요청에 넣는 **증거 메타데이터**. 현재 워커는 이 키를 재검증하지 않음 |

**현재 워커에서 고정된 합성 파라미터** (JSON을 추가한다고 임의로 변경되지 않음):

| TTS 인수 | 값 |
|---|---|
| `text_lang`, `prompt_lang` | `ko`, `ko` |
| `ref_audio_path` | `<GPT-SoVITS 루트>/refs/narrator_ref_7s.wav` |
| `top_k` / `top_p` | `10` / `0.8` |
| `text_split_method` | `cut0` |
| `batch_size`, `split_bucket` | `1`, `false` |
| `fragment_interval` | `0.3` |
| `parallel_infer`, `streaming_mode`, `return_fragment` | 모두 `false` |
| `repetition_penalty` | `1.35` |
| `sample_steps` / `seed` | `32` / `42` |

참조 WAV, 모델 쌍, 샘플링 설정을 매번 변경하는 범용 TTS API는 **현재 구현되어 있지 않다**. 다른 참조 성우를 사용하고 싶다면 워커 인터페이스/권리/실행 검증을 별도 설계해야 한다.

## 3. A 경로: **독립 TTS 1건 생성 — Windows PowerShell 5.1 실행 예**

> 아래 명령은 실행 예시이며 이 문서 작성 과정에서 실행하지 않았다. **새 출력 작업 폴더만 만들고** 기존 GPT-SoVITS 설치/모델/레퍼런스 파일은 수정하지 않는다. 해당 참조 성우의 사용권과 입력 문장을 먼저 확인한다.

PowerShell 5.1 창에서 아래 **한 묶음** 실행. `$ttsText`만 바꿔 다른 한국어 문장을 합성한다.

```powershell
$murim = 'E:\gpt\projects\comfyui\murim'
$engine = if ($env:MURIM_SOVITS_ROOT) { $env:MURIM_SOVITS_ROOT } else { 'E:\GPT-SoVITS' }
$runtime = Join-Path $engine 'runtime\python.exe'
$reference = Join-Path $engine 'refs\narrator_ref_7s.wav'
$worker = Join-Path $murim 'scripts\studio_sovits_worker.py'

# 사용할 성우 참조 음성의 권리를 확인한 경우에만 진행
$referenceRightsConfirmed = $false
if (-not $referenceRightsConfirmed) { throw '먼저 참조 음성 이용 권한을 확인한 후 $referenceRightsConfirmed를 $true로 설정하십시오.' }

$ttsText = @'
이 작품은 한 폭의 그림이 어떻게 여러 사람의 손을 거쳤는지 보여줍니다.
'@

foreach ($file in @($runtime, $reference, $worker)) {
    if (-not (Test-Path -LiteralPath $file -PathType Leaf)) {
        throw ("필수 파일 없음: " + $file)
    }
}
if ([string]::IsNullOrWhiteSpace($ttsText)) { throw '합성할 발화 텍스트가 비어 있습니다.' }

# 요청마다 유일한 폴더. 기존 결과물 덮어쓰기 금지.
$jobId = [Guid]::NewGuid().ToString('N').Substring(0, 12)
$baseDir = Join-Path $murim 'outputs\tts-standalone'
if (-not (Test-Path -LiteralPath $baseDir)) {
    $null = New-Item -ItemType Directory -Path $baseDir -ErrorAction Stop
}
$jobDir = Join-Path $baseDir $jobId
$null = New-Item -ItemType Directory -Path $jobDir -ErrorAction Stop
$requestPath = Join-Path $jobDir 'request.json'
$wavPath = Join-Path $jobDir 'voice.wav'

$payload = [ordered]@{
    text = $ttsText
    prompt_text = '안녕하세요. 오늘은 단순히 줄거리를 훑는게 아니라, 한편의 이야기가 어떻게 첫 순간부터 우리를 완벽하게 사로잡는'
    speed = 0.92
    temperature = 0.65
    model = 'GPT-SoVITS-v2'
    reference_sha256 = (Get-FileHash -LiteralPath $reference -Algorithm SHA256).Hash.ToLowerInvariant()
    worker_sha256 = (Get-FileHash -LiteralPath $worker -Algorithm SHA256).Hash.ToLowerInvariant()
}

# PowerShell 5.1의 Out-File -Encoding utf8은 BOM을 만들 수 있음.
# 워커가 utf-8로 읽으므로 BOM 없는 UTF-8을 직접 기록한다.
$json = $payload | ConvertTo-Json -Depth 8
$utf8 = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($requestPath, $json, $utf8)

# worker.py의 Path.cwd()가 GPT-SoVITS 루트를 가리키도록 한다.
$previous = Get-Location
try {
    Set-Location -LiteralPath $engine
    & $runtime $worker $requestPath
    $exitCode = $LASTEXITCODE
} finally {
    Set-Location -LiteralPath $previous
}
if ($exitCode -ne 0) { throw ("GPT-SoVITS 프로세스 실패. 종료코드 " + $exitCode + "; 요청폴더 " + $jobDir) }
if (-not (Test-Path -LiteralPath $wavPath -PathType Leaf)) { throw ("합성 반환 WAV 없음: " + $wavPath) }
if ((Get-Item -LiteralPath $wavPath).Length -le 44) { throw 'WAV 파일 크기 비정상' }

Write-Output ("[PASS] " + $wavPath)
```

**예상되는 산출물 경로(실제 생성 검증 전):**

```text
outputs/tts-standalone/<job-id>/
  request.json        # 실제 요청 문장·파라미터·참조/워커 SHA
  resolved_tts.yaml   # 해당 호출에 사용한 모델/장치 설정
  voice.wav           # 실제 생성된 음성 (16-bit PCM, 샘플레이트는 엔진 반환값)
```

워크스페이스에 저장할 수 없는 환경에서는 **실제로 승인된 작업 폴더**의 새로운 하위 폴더를 사용한다. **기존 파일은 삭제·이름 변경·덮어쓰지 않는다.** `$jobDir`과 `$wavPath`는 실행 후 새 출력 폴더·실제 반환 파일을 확인할 때 사용하는 변수일 뿐, 새로운 서버의 응답 JSON이 아니다.

### A 경로의 실제 반환

워커가 성공하면 `sr, audio = next(pipe.run(params))`을 받아 다음을 검사한다.

1. 파형 값에 `NaN/Inf`가 없음.
2. 길이가 **0.35초 이상**.
3. 파형 RMS가 **0.002 이상**.
4. 최대 절대 진폭이 **0.02 이상**.

이 검사에 실패하면 `Silent or invalid synthesis` 예외로 실패한다. 통과한 경우 `np.int16` 형식으로 변환하여 **요청 JSON과 같은 폴더의 `voice.wav`**에 저장하고 `[PASS] actual waveform synthesized; audition required`를 출력한다.

**출력 WAV는 직접 파일로 반환**되는 것이며, `stdout`에 음성 바이너리나 base64를 출력하거나 HTTP로 반환하지 않는다. 새 세션에서 결과를 확인할 때는 **실제 존재하는 경로**를 읽고, 해시/길이/청취 결과와 함께 사용자에게 전달한다. 실제 파일을 확인하기 전 가상 링크를 만들지 않는다.

### A 경로의 추가 확인

```powershell
Get-Item -LiteralPath $wavPath | Select-Object FullName, Length
Get-FileHash -LiteralPath $wavPath -Algorithm SHA256
# ffprobe가 설치되어 있고 경로가 확인된 경우:
# & 'E:\GPT-SoVITS\ffprobe.exe' -v error -show_entries format=duration -of default=nw=1:nk=1 $wavPath
```

파일 존재/해시/무음 통과와 실제 한국어 발음·억양·끊김·잡음·권리 적합성은 **서로 별도 검증**이다. 반드시 WAV를 직접 듣고 판단한다.

## 4. B 경로: Murim Studio의 실제 요청 → 응답 → WAV 다운로드

### 호출 순서

1. `run-studio.cmd`로 로컬 Studio 실행: `http://127.0.0.1:8080/studio/`.
2. 기존 프로젝트의 **00A/B/C 사전 제작 품질 게이트**, 실제 원고 제작 연결, 독립 재심사 및 인간 승인을 마친다. 불합격/미완성에서는 서버가 합성을 **차단**한다.
3. Studio `03 성우·음향` 탭에서 장면 선택. 실제 발화 `voice` 트랙의 텍스트 확인, 속도/Temperature/음량 설정 저장, 참조 음성 사용 권한 체크.
4. **기존 GPT-SoVITS v2로 합성** 클릭 → 서버 `POST /studio/api/project/<pid>/voice`.
5. 서버가 해당 장면의 `voice` 트랙을 읽고 워커를 실행. 출력 `voice.wav`의 오디오 스트림과 길이를 `ffprobe`로 확인하고 프로젝트의 **신규 오디오 자산**에 등록.
6. 응답의 `voice_result.asset` ID로 `GET /studio/api/project/<pid>/asset/<aid>`하면 WAV가 반환된다. UI의 **현재 음성 듣기**도 같은 자산 URL을 재생.

### Studio HTTP 요청 본문

```http
POST /studio/api/project/<pid>/voice
Host: 127.0.0.1:8080
Content-Type: application/json
X-Murim-Studio: <현재 실행 중인 Studio 화면의 meta token>

{
  "revision": "<GET 프로젝트 API에서 읽은 현재 M-VML SHA256>",
  "scene": "<현재 승인 작품의 실제 장면 ID>",
  "rights_confirmed": true
}
```

**주의:** HTTP 요청 본문에는 발화 텍스트·속도·Temperature가 직접 들어가지 않는다. **먼저 저장되어 있는 해당 장면 `voice` 트랙의 `text` / `speed` / `temperature` 값**을 합성한다. 따라서 사용하려는 텍스트가 실제 M-VML에 저장되어 있는지 확인한다. 리비전 SHA가 오래되면 `Revision conflict`로 실패한다.

`X-Murim-Studio` 토큰은 서버 시작 시 임의 생성되며 Studio HTML `<meta name="studio-token">`에 주입된다. **매번 실행 중인 현재 세션의 토큰**을 사용한다. 비밀 값을 문서, Git 저장소, 공유 로그에 붙여 넣지 않는다. 서버는 loopback (`127.0.0.1` / `::1`) 요청만 허용한다.

**실제 브라우저 UI가 호출하는 흐름** (`static/studio.js`):

```javascript
// UI에서 선택한 장면의 설정을 저장한 뒤:
const response = await fetch('/studio/api/project/' + pid + '/voice', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Murim-Studio': document.querySelector('meta[name="studio-token"]').content
  },
  body: JSON.stringify({
    revision: currentProjectRevision,
    scene: selectedSceneId,
    rights_confirmed: true
  })
});
if (!response.ok) throw new Error(await response.text());
const payload = await response.json();
const result = payload.voice_result;
const wavUrl = '/studio/api/project/' + pid + '/asset/' + result.asset;
```

위 코드는 **현재 Studio 페이지에서 동작하는 API 사용 예시**이며, 변수 `pid`, `currentProjectRevision`, `selectedSceneId`는 그 페이지에서 실제 조회한 값을 넣어야 한다. 이 예시는 외부에 공개된 인증 없는 TTS 서비스가 아님.

### B 경로의 서버 내부 요청 JSON

`src/studio/voice.py`가 작업 디렉터리에 아래와 같은 형태로 작성한다.

```json
{
  "text": "<voice 트랙에 저장된 실제 한국어 텍스트>",
  "prompt_text": "안녕하세요. 오늘은 단순히 줄거리를 훑는게 아니라, 한편의 이야기가 어떻게 첫 순간부터 우리를 완벽하게 사로잡는",
  "speed": 0.92,
  "temperature": 0.65,
  "reference_sha256": "<실제 참조 WAV SHA256>",
  "worker_sha256": "<실제 워커 SHA256>",
  "model": "GPT-SoVITS-v2"
}
```

위 `speed` / `temperature`는 **기본값 예시**다. 실제 호출은 현재 트랙 속성값을 넣는다. 실재하는 SHA 값은 소스 코드에서 동적으로 계산하며 문서에 고정해두지 않는다.

서버는 다음처럼 실행한다.

```text
cwd: <GPT-SoVITS 루트>
exe: <GPT-SoVITS 루트>/runtime/python.exe
argv: <Murim>/scripts/studio_sovits_worker.py
      <Murim>/outputs/studio/<pid>/voice-jobs/<job-id>/request.json
timeout: 1800초
stdout/stderr: <job-id>/engine.log
생성: <job-id>/resolved_tts.yaml
      <job-id>/voice.wav
```

**B 경로의 응답 스키마** (`voice_result`, 실제 ID/시간은 실행 후에만 생성):

```text
{
  "voice_result": {
    "asset": <등록된 오디오 자산 ID>,
    "seconds": <ffprobe로 확인한 음성 실제 길이, 초>,
    "fits": <음성 길이 + 장면 offset <= 장면 길이>,
    "job": <12자리 작업 폴더명>
  },
  "id": <프로젝트 ID>,
  "revision": <저장 후 새로운 M-VML 리비전 SHA>,
  "scenes": <업데이트된 상태>,
  ...
}
```

합성된 새 음성은 `kind='audio'`, `origin='SOVITS_V2'`, `profile='narrator-v2'`로 등록되고 해당 장면 `voice` 트랙의 `asset`과 `bound`가 업데이트된다. `bound`는 **발화 텍스트/속도/Temperature/profile의 해시**에 연결된다. 발화를 수정하면 옛 음성 바인딩이 제거되고, 기존 립싱크 바인딩도 해제된다. 원본 WAV 및 기존 리비전은 보존된다.

`gain`은 Studio 믹서/렌더의 **dB 레벨**이며 현재 `studio_sovits_worker.py` 요청 파라미터가 아니다. `fits=false`는 합성 요청 자체의 실패가 아니라 **장면 길이 불일치**. 최종 렌더는 음성을 잘라 맞추지 않고 초과 시 실패한다.

## 5. 실제 오류 복구 표

| 관찰한 메시지·상태 | 실제 코드상 가능한 원인 | 확인·처리 |
|---|---|---|
| `Existing GPT-SoVITS runtime/reference not found` | 실행기·참조 WAV·워커 파일 중 하나 없음 | 경로 확인; 기존 설치 임의 수정/신규 설치 금지 |
| `GPT-SoVITS inference failed; inspect .../engine.log` | 워커 비정상 종료 | 해당 작업 폴더 `engine.log` 및 `resolved_tts.yaml` 확인, 모델 경로/환경 의존성/CUDA 점검 |
| `Silent or invalid synthesis` | NaN/무음/과소 신호/0.35초 미만 | 요청 문장·참조·모델·파형 확인; 무음/SAPI로 자동 대체 금지 |
| `Another production job is running` | Studio 단일 GPU 작업 lock 사용 중 | 기존 작업 완료/실패 원인 확인 후 안전하게 재시도 |
| `Revision conflict; reload current project` | 요청 SHA와 최신 M-VML 버전 불일치 | 프로젝트를 재조회하고 실제 장면/설정 확인 |
| `Enter spoken text first` | 해당 장면 `voice` 트랙의 실제 텍스트가 없음 | 승인된 원문과 연결된 발화 확인 |
| `Confirm reference voice use rights before synthesis` | 참조 이용권 확인 누락 | 권리 확인 후에만 요청 |
| `Narration exceeds scene duration` | 합성 WAV가 장면보다 김 | 실제 발화 시간을 기준으로 장면 재설계; 자동 잘라내기 금지 |
| `Stale voice binding` | 텍스트/속도/Temperature/profile 변경 후 이전 음성 사용 | 승인된 새 발화로 재합성, 리비전 재조회 |
| HTTP 403 | 비-localhost 요청 또는 `X-Murim-Studio` 토큰 불일치 | Studio의 실제 현재 토큰과 loopback 주소 확인 |
| `FFmpeg/ffprobe not found` | Studio 오디오 확인 도구 부재 | 기존 FFmpeg/ffprobe 설치 위치·PATH·`MURIM_FFMPEG_DIR` 확인 |
| `FileNotFoundError` for v2 weights | 모델/전처리기 경로 없음 | 정확한 4개 하드코딩 경로를 기존 설치와 대조 |
| `ModuleNotFoundError`, CUDA 오류 | 기존 runtime 의존성, GPU 상태 불일치 | 실행한 python이 `runtime/python.exe`인지, CUDA 설정·로그 확인 |
| `voice.wav` 없음 | 프로세스 실패 또는 결과 생성 전 검사 | 종료코드·작업 폴더 확인, 성공으로 처리 금지 |

워커 직접 실행(A)은 `engine.log`를 **자동 생성하지 않는다**. 필요하면 승인된 새 로그 파일로 stdout/stderr를 명시적으로 리다이렉트한다. Studio(B)만 `engine.log`를 기록한다. 발생한 원본 오류 파일은 보존하고 무차별 삭제·수정하지 않는다.

## 6. 다른 ChatGPT 세션에 전달할 표준 요청

다른 세션의 시작 메시지에 다음 텍스트를 사용한다. 이 문서를 **권위 기반 문서**로 지정하면 세션 간 추측을 줄일 수 있다.

> `hoonoh57/murim`의 `docs/GPT_SOVITS_V2_TTS_OPERATIONS.md`를 먼저 읽고 현재 HEAD의 `scripts/studio_sovits_worker.py`, `src/studio/voice.py`와 대조하세요. 기존 `E:\GPT-SoVITS` v2 모델·`narrator_ref_7s.wav`을 변경/재설치하지 마세요. **다음 문장**을 `speed=0.92`, `temperature=0.65`로 새 작업 폴더에 합성하세요: "여기에 합성할 실제 원문". 참조 음성 이용권은 먼저 확인하고, 로컬 실행 권한/연결이 없다면 **실행했다고 주장하지 말고** 요청 JSON·정확한 실행 명령과 반환 WAV 경로를 제시하세요. 실행할 수 있다면 실제 파일 존재·SHA256·길이·청취 필요 여부를 보고하고 새 WAV를 제공하세요.

다른 세션에 필요한 최소 정보: **실제 문장**, 속도/Temperature(기본 유지 가능), 참조 음성 권리 확인, 파일을 저장할 승인된 로컬 출력 폴더, 실제 Windows 실행 연결 상태. 별도 LLM 평가 점수·영상 시나리오·ComfyUI 자동 설치는 필요하지 않다.

## 7. 출처/구현상 확인이 필요한 사항

- [`src/studio/voice.py`](../src/studio/voice.py): Studio → JSON → Python 프로세스 → 자산 등록 → `voice_result`.
- [`scripts/studio_sovits_worker.py`](../scripts/studio_sovits_worker.py): JSON 읽기, 참조 WAV, v2 모델 쌍, 모든 합성 인수, 실제 `voice.wav` 쓰기.
- [`src/studio/web.py`](../src/studio/web.py): localhost 요청 제한, 리비전/승인 잠금, TTS REST 및 오디오 자산 다운로드.
- [`src/studio/workspace.py`](../src/studio/workspace.py): `voice` 트랙, SHA 바인딩/변경 무효화, 자산 해시와 경로.
- [`src/studio/render.py`](../src/studio/render.py): ffprobe 길이·스트림 검증, 렌더 길이/무음 검사와 믹싱.
- [`static/studio.js`](../static/studio.js), [`templates/studio.html`](../templates/studio.html): 실제 UI의 `generateVoice`, `listen`, 속도/Temperature/참조권리 및 token.
- [`src/agents/audio.py`](../src/agents/audio.py) 및 [`src/api/ai_clients.py`](../src/api/ai_clients.py): 별도의 레거시 mock/stub TTS. **GPT-SoVITS v2 실제 합성과 혼동하지 말 것.**

최종 기술 판정은 **기존 인터페이스 문서화 완료 / 새 Windows 실행 NOT_RUN / TTS 콘텐츠 청취 품질 NOT_VERIFIED**. 문서가 있다고 합성 서버나 GPT-SoVITS 모델이 자동 실행·다운로드되는 것은 아니다.
