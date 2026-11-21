# Prepare a licensed 2s sword-motion input for SCAIL-2; no baseline edits.
Set-StrictMode -Version 2
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$ExpectedRoot = 'E:\comfyui-scail'
$InputDir = Join-Path $Root 'ComfyUI\input'
$Workflow = Join-Path $Root 'ComfyUI\user\default\workflows\SCAIL-2-MURIM-SWORD-2S.json'
$Reference = Join-Path $InputDir 'murim_character_reference.png'
$AssetDir = Join-Path $Root 'samples\sword-pexels-4734306'
$Source = Join-Path $AssetDir 'source.mp4'
$SourcePart = Join-Path $AssetDir 'source.part.mp4'
$SourceNote = Join-Path $AssetDir 'SOURCE.txt'
$InputVideo = Join-Path $InputDir 'murim_sword_driving_2s.mp4'
$Staged = Join-Path $InputDir 'murim_sword_driving_2s.stage.mp4'
$Receipt = Join-Path $Root 'sword-trial-input-report.json'
$LogDir = Join-Path $Root 'logs'
$Log = Join-Path $LogDir 'prepare-scail2-sword.log'
$Url = 'https://www.pexels.com/download/video/4734306/'
$SourcePage = 'https://www.pexels.com/video/silhouette-of-a-person-holding-a-sword-4734306/'
$Utf8 = New-Object System.Text.UTF8Encoding($false)
if (-not (Test-Path -LiteralPath $LogDir)) { New-Item -ItemType Directory -Path $LogDir | Out-Null }
function Note([string]$msg) {
    [IO.File]::AppendAllText($Log, ('[' + (Get-Date -Format 's') + '] ' + $msg + [Environment]::NewLine), $Utf8)
}
function Native([string]$exe,[string[]]$argv) {
    $save = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        $global:LASTEXITCODE = 0
        & $exe @argv 2>&1 | ForEach-Object { Note ([string]$_) }
        $nativeExit = $LASTEXITCODE
    } finally { $ErrorActionPreference = $save }
    if ($nativeExit -ne 0) { throw ('[COMMAND_FAILED] exit=' + $nativeExit + ' log=' + $Log) }
}
function Probe([string]$ffprobe,[string]$path) {
    $lines = & $ffprobe '-v' 'error' '-show_entries' 'format=duration:stream=codec_type,codec_name' '-of' 'json' $path
    if ($LASTEXITCODE -ne 0) { throw ('[PROBE_FAILED] ' + $path) }
    return (($lines -join [Environment]::NewLine) | ConvertFrom-Json)
}
function Verify([string]$ffprobe,[string]$path,[bool]$target) {
    $info = Probe $ffprobe $path
    $v = @($info.streams | Where-Object { $_.codec_type -eq 'video' })
    $a = @($info.streams | Where-Object { $_.codec_type -eq 'audio' })
    if ($v.Count -ne 1) { throw ('[INVALID_VIDEO] ' + $path) }
    if ($target) {
        if ($a.Count -ne 1 -or $a[0].codec_name -ne 'aac' -or $v[0].codec_name -ne 'h264') {
            throw '[INVALID_TRANSCODE_STREAMS]'
        }
        $seconds = [double]::Parse([string]$info.format.duration,[Globalization.CultureInfo]::InvariantCulture)
        if ($seconds -lt 1.8 -or $seconds -gt 2.3) { throw ('[INVALID_DURATION] ' + $seconds) }
    }
}
try {
    Note 'START 2-second sword-motion input preparation.'
    if ([IO.Path]::GetFullPath($Root).TrimEnd('\') -ine $ExpectedRoot) { throw '[WORKSPACE_MISMATCH]' }
    foreach ($need in @($InputDir,$Workflow,$Reference)) {
        if (-not (Test-Path -LiteralPath $need)) { throw ('[REQUIRED_FILE_MISSING] ' + $need) }
    }
    $flow = [IO.File]::ReadAllText($Workflow)
    if (-not $flow.Contains('murim_sword_driving_2s.mp4') -or -not $flow.Contains('SCAIL-2-Q3_K_M.gguf')) {
        throw '[WORKFLOW_DRIFT]'
    }
    $ffmpegDir = Join-Path $Root '.venv\Lib\site-packages\imageio_ffmpeg\binaries'
    $ffmpegFiles = @(Get-ChildItem -LiteralPath $ffmpegDir -Filter 'ffmpeg*.exe' -File)
    if ($ffmpegFiles.Count -ne 1) { throw '[FFMPEG_MISSING_OR_AMBIGUOUS]' }
    $ffmpeg = $ffmpegFiles[0].FullName
    $probeDir = Join-Path $Root 'ffmpeg-build'
    $probeFiles = @(Get-ChildItem -LiteralPath $probeDir -Filter 'ffprobe.exe' -File -Recurse)
    if ($probeFiles.Count -ne 1) { throw '[FFPROBE_MISSING_OR_AMBIGUOUS]' }
    $ffprobe = $probeFiles[0].FullName
    if (Test-Path -LiteralPath $Receipt) {
        $r = ([IO.File]::ReadAllText($Receipt) | ConvertFrom-Json)
        if ($r.status -ne 'SWORD_INPUT_VERIFIED_NOT_RENDERED') { throw '[RECEIPT_CONFLICT]' }
        foreach ($pair in @(@($Source,$r.source_sha256),@($InputVideo,$r.input_sha256))) {
            if (-not (Test-Path -LiteralPath $pair[0])) { throw '[RECEIPT_FILE_MISSING]' }
            if ((Get-FileHash -LiteralPath $pair[0] -Algorithm SHA256).Hash -ine $pair[1]) {
                throw '[RECEIPT_HASH_MISMATCH]'
            }
        }
        Verify $ffprobe $InputVideo $true
        Note 'PASS: existing source and 2s video verified against receipt.'
        Write-Output '[PASS]'
        return
    }
    if (-not (Test-Path -LiteralPath $AssetDir)) { New-Item -ItemType Directory -Path $AssetDir | Out-Null }
    if (-not (Test-Path -LiteralPath $Source)) {
        if (Test-Path -LiteralPath $SourcePart) { throw '[PARTIAL_DOWNLOAD_CONFLICT]' }
        Native 'curl.exe' @('--location','--fail','--silent','--show-error','--retry','3','--output',$SourcePart,$Url)
        if ((Get-Item -LiteralPath $SourcePart).Length -lt 100000) { throw '[DOWNLOAD_TOO_SMALL]' }
        Verify $ffprobe $SourcePart $false
        Move-Item -LiteralPath $SourcePart -Destination $Source -ErrorAction Stop
    }
    Verify $ffprobe $Source $false
    if (Test-Path -LiteralPath $InputVideo) { throw '[USER_INPUT_CONFLICT]' }
    if (Test-Path -LiteralPath $Staged) { throw '[STAGED_FILE_CONFLICT]' }
    Native $ffmpeg @(
        '-hide_banner','-loglevel','warning','-nostdin','-n',
        '-i',$Source,'-f','lavfi','-i','anullsrc=r=48000:cl=stereo',
        '-t','2','-map','0:v:0','-map','1:a:0',
        '-vf','fps=16','-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p',
        '-c:a','aac','-b:a','96k','-shortest','-movflags','+faststart',$Staged
    )
    Verify $ffprobe $Staged $true
    Move-Item -LiteralPath $Staged -Destination $InputVideo -ErrorAction Stop
    if (-not (Test-Path -LiteralPath $SourceNote)) {
        $note = @(
            ('Source: ' + $SourcePage),
            'Creator: Alex Ch (Pexels)',
            ('Download: ' + $Url),
            'License: https://www.pexels.com/license/',
            'Adapted for a two-second motion experiment; no unaltered stock redistribution.'
        ) -join [Environment]::NewLine
        [IO.File]::WriteAllText($SourceNote,($note+[Environment]::NewLine),$Utf8)
    }
    $r = [ordered]@{
        status = 'SWORD_INPUT_VERIFIED_NOT_RENDERED'
        source_page = $SourcePage
        source_sha256 = (Get-FileHash -LiteralPath $Source -Algorithm SHA256).Hash
        input_path = $InputVideo
        input_sha256 = (Get-FileHash -LiteralPath $InputVideo -Algorithm SHA256).Hash
        workflow = $Workflow
        reference = $Reference
        format = '2 seconds, H264 16fps + silent AAC'
    }
    [IO.File]::WriteAllText($Receipt,(($r | ConvertTo-Json -Depth 4)+[Environment]::NewLine),$Utf8)
    Note 'PASS: input verified and staged for SCAIL-2; GPU render NOT_RUN.'
    Write-Output '[PASS]'
} catch {
    Note ('FAIL: ' + $_.Exception.Message)
    Write-Output ('[FAIL] ' + $_.Exception.Message)
    Write-Output ('Log: ' + $Log)
    exit 1
}
