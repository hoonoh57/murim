# Recover the official silent-driving-video sample for SCAIL-2 without altering source frames.
# PowerShell 5.1 compatible; limited to E:\comfyui-scail. No legacy ComfyUI or model edits.
Set-StrictMode -Version 2
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$ExpectedRoot = 'E:\comfyui-scail'
$Comfy = Join-Path $Root 'ComfyUI'
$InputVideo = Join-Path $Comfy 'input\your_driving_video.mp4'
$Original = Join-Path $Root 'samples\official-animation-001\driving.mp4'
$Backup = Join-Path $Comfy 'input\your_driving_video.before_silent_audio.mp4'
$Staged = Join-Path $Comfy 'input\your_driving_video.silent-audio-staged.mp4'
$Launcher = Join-Path $Root 'start-scail2.cmd'
$Venv = Join-Path $Root '.venv'
$LogDir = Join-Path $Root 'logs'
$Log = Join-Path $LogDir 'repair-scail-audio.log'
$Report = Join-Path $Root 'scail-audio-repair-report.json'
$Utf8 = New-Object System.Text.UTF8Encoding($false)

if (-not (Test-Path -LiteralPath $LogDir)) { New-Item -ItemType Directory -Path $LogDir | Out-Null }
function Note([string]$message) {
    [IO.File]::AppendAllText($Log, ('[' + (Get-Date -Format 's') + '] ' + $message + [Environment]::NewLine), $Utf8)
}
function Native([string]$exe, [string[]]$argv) {
    $oldErrorPreference = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        $global:LASTEXITCODE = 0
        & $exe @argv 2>&1 | ForEach-Object { Note ([string]$_) }
        $nativeExit = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $oldErrorPreference
    }
    if ($nativeExit -ne 0) { throw ('[NATIVE_FAILED] exit=' + $nativeExit + ', exe=' + $exe + ', see ' + $Log) }
}
function Probe([string]$probeExe, [string]$path) {
    $output = & $probeExe '-v' 'error' '-show_entries' 'stream=codec_type,codec_name,nb_frames' '-of' 'json' $path
    if ($LASTEXITCODE -ne 0) { throw ('[FFPROBE_FAILED] ' + $path) }
    return (($output -join [Environment]::NewLine) | ConvertFrom-Json)
}
function StreamCount($info, [string]$kind) {
    return @($info.streams | Where-Object { $_.codec_type -eq $kind }).Count
}
try {
    Note 'START official sample silent-audio recovery.'
    if ([IO.Path]::GetFullPath($Root).TrimEnd('\') -ine $ExpectedRoot) { throw '[WRONG_WORKSPACE]' }
    foreach ($required in @($Comfy, $Launcher, $Original, $InputVideo)) {
        if (-not (Test-Path -LiteralPath $required)) { throw ('[MISSING_INPUT] ' + $required) }
    }
    # Do not replace the active input while the 8189 server can cache it.
    $client = New-Object Net.Sockets.TcpClient
    try {
        $client.Connect('127.0.0.1', 8189)
        throw '[PORT_8189_IN_USE] Close only the SCAIL-2 server console before repair.'
    } catch [Net.Sockets.SocketException] {
        # No listener; safe to repair the experiment's sample.
    } finally { $client.Dispose() }

    # The VideoHelperSuite installation includes a working local ffmpeg binary.
    $binaryDir = Join-Path $Venv 'Lib\site-packages\imageio_ffmpeg\binaries'
    $ffmpegFiles = @(Get-ChildItem -LiteralPath $binaryDir -Filter 'ffmpeg*.exe' -File)
    if ($ffmpegFiles.Count -ne 1) { throw '[FFMPEG_BINARY_MISSING_OR_AMBIGUOUS]' }
    $ffmpeg = $ffmpegFiles[0].FullName
    $probeDir = Join-Path $Root 'ffmpeg-build'
    if (-not (Test-Path -LiteralPath $probeDir)) { throw '[FFPROBE_BUILD_MISSING]' }
    $probeFiles = @(Get-ChildItem -LiteralPath $probeDir -Filter 'ffprobe.exe' -File -Recurse)
    if ($probeFiles.Count -ne 1) { throw '[FFPROBE_BINARY_MISSING_OR_AMBIGUOUS]' }
    $ffprobe = $probeFiles[0].FullName

    $sourceProbe = Probe $ffprobe $Original
    if ((StreamCount $sourceProbe 'video') -ne 1 -or (StreamCount $sourceProbe 'audio') -ne 0) {
        throw '[OFFICIAL_SAMPLE_STREAMS_CHANGED] Expected one video stream, no audio.'
    }
    $sourceHash = (Get-FileHash -LiteralPath $Original -Algorithm SHA256).Hash
    $inputProbe = Probe $ffprobe $InputVideo
    $audioCount = StreamCount $inputProbe 'audio'
    if ($audioCount -eq 0) {
        if ((Get-FileHash -LiteralPath $InputVideo -Algorithm SHA256).Hash -ne $sourceHash) {
            throw '[USER_INPUT_CHANGED] Input differs from official sample, no overwrite.'
        }
        if (Test-Path -LiteralPath $Backup) { throw '[BACKUP_CONFLICT] Existing backup requires inspection.' }
        if (Test-Path -LiteralPath $Staged) { throw '[STAGED_FILE_CONFLICT] Existing staged file requires inspection.' }
        Note 'Original input matches official sample. Remuxing with silent AAC; video codec is COPY.'
        Native $ffmpeg @(
            '-hide_banner','-loglevel','warning','-nostdin','-n',
            '-i',$Original,
            '-f','lavfi','-i','anullsrc=r=48000:cl=stereo',
            '-map','0:v:0','-map','1:a:0',
            '-c:v','copy','-c:a','aac','-b:a','96k','-shortest','-movflags','+faststart',
            $Staged
        )
        if (-not (Test-Path -LiteralPath $Staged)) { throw '[STAGED_FILE_MISSING]' }
        $test = Probe $ffprobe $Staged
        if ((StreamCount $test 'video') -ne 1 -or (StreamCount $test 'audio') -ne 1) {
            throw '[SILENT_AUDIO_STAGE_INVALID] Expected video and audio streams.'
        }
        $audioStreams = @($test.streams | Where-Object { $_.codec_type -eq 'audio' })
        $videoStreams = @($test.streams | Where-Object { $_.codec_type -eq 'video' })
        if ($audioStreams[0].codec_name -ne 'aac' -or $videoStreams[0].codec_name -ne 'h264') {
            throw '[SILENT_AUDIO_CODEC_MISMATCH]'
        }
        if ((Get-FileHash -LiteralPath $InputVideo -Algorithm SHA256).Hash -ne $sourceHash) {
            throw '[INPUT_CHANGED_DURING_REPAIR]'
        }
        # Atomic same-volume replacement; backup retains byte-identical original input.
        [IO.File]::Replace($Staged, $InputVideo, $Backup, $true)
        if ((Get-FileHash -LiteralPath $Backup -Algorithm SHA256).Hash -ne $sourceHash) {
            throw '[BACKUP_HASH_MISMATCH]'
        }
        Note 'REPAIR_APPLIED: original backed up, silent AAC added, H264 copied.'
    } else {
        # A prior successful repair can be restarted without modifying any files again.
        if (-not (Test-Path -LiteralPath $Backup)) { throw '[AUDIO_PRESENT_WITHOUT_OUR_BACKUP] Stop to protect user file.' }
        if ((Get-FileHash -LiteralPath $Backup -Algorithm SHA256).Hash -ne $sourceHash) {
            throw '[EXISTING_BACKUP_NOT_ORIGINAL]'
        }
        if ($audioCount -ne 1 -or (StreamCount $inputProbe 'video') -ne 1) {
            throw '[EXISTING_REPAIR_STREAM_MISMATCH]'
        }
        Note 'REPAIR_ALREADY_APPLIED: found expected backup and audio-bearing input.'
    }

    $final = Probe $ffprobe $InputVideo
    $finalAudio = @($final.streams | Where-Object { $_.codec_type -eq 'audio' })
    $finalVideo = @($final.streams | Where-Object { $_.codec_type -eq 'video' })
    if ($finalAudio.Count -ne 1 -or $finalAudio[0].codec_name -ne 'aac' -or
        $finalVideo.Count -ne 1 -or $finalVideo[0].codec_name -ne 'h264') {
        throw '[POSTREPAIR_PROBE_FAILED]'
    }
    $receipt = [ordered]@{
        status = 'INPUT_AUDIO_VERIFIED_NOT_RENDERED'
        source_sha256 = $sourceHash
        input_sha256 = (Get-FileHash -LiteralPath $InputVideo -Algorithm SHA256).Hash
        backup_path = $Backup
        video_codec = 'h264'
        audio_codec = 'aac'
        ui = 'http://127.0.0.1:8189'
    }
    [IO.File]::WriteAllText($Report, (($receipt | ConvertTo-Json -Depth 4) + [Environment]::NewLine), $Utf8)
    Start-Process -FilePath $env:ComSpec -ArgumentList @('/k', ('"' + $Launcher + '"')) -WorkingDirectory $Root | Out-Null
    $ready = $false
    for ($i = 0; $i -lt 80; $i++) {
        try {
            $nodes = Invoke-RestMethod -Uri 'http://127.0.0.1:8189/object_info' -TimeoutSec 15
            if ($nodes.PSObject.Properties['VHS_LoadVideo'] -and
                $nodes.PSObject.Properties['SCAIL2EasyConfig'] -and
                $nodes.PSObject.Properties['Display Int (rgthree)']) {
                $ready = $true
                break
            }
        } catch { }
        Start-Sleep -Seconds 3
    }
    if (-not $ready) { throw '[STARTUP_NODE_CHECK_FAILED] Review the SCAIL server console.' }
    $receipt.status = 'STARTUP_AND_INPUT_AUDIO_VERIFIED_NOT_RENDERED'
    [IO.File]::WriteAllText($Report, (($receipt | ConvertTo-Json -Depth 4) + [Environment]::NewLine), $Utf8)
    Note 'PASS: video retained, silent AAC available, server 8189 + VHS/SCAIL nodes ready. RENDER NOT_RUN.'
    try { Start-Process 'http://127.0.0.1:8189' | Out-Null } catch { }
    Write-Output '[PASS]'
} catch {
    Note ('FAIL: ' + $_.Exception.Message)
    Write-Output ('[FAIL] ' + $_.Exception.Message)
    Write-Output ('Log: ' + $Log)
    exit 1
}
