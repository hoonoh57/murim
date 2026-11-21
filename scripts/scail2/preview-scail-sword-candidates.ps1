# Preview-only candidate video inspection. No ComfyUI workflow, model, or input modifications.
# Windows PowerShell 5.1; isolated to E:\comfyui-scail\samples\sword-candidate-review.
Set-StrictMode -Version 2
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$ExpectedRoot = 'E:\comfyui-scail'
$OutDir = Join-Path $Root 'samples\sword-candidate-review'
$LogDir = Join-Path $Root 'logs'
$Log = Join-Path $LogDir 'preview-sword-candidates.log'
$Report = Join-Path $OutDir 'preview-report.json'
$Utf8 = New-Object System.Text.UTF8Encoding($false)
$Candidates = @(
    [ordered]@{
        id = 'pexels-6536346'
        title = 'Solo indoor fencing training'
        page = 'https://www.pexels.com/video/a-person-is-practicing-fencing-alone-6536346/'
        download = 'https://www.pexels.com/download/video/6536346/'
        author = 'Tima Miroshnichenko'
        license = 'https://www.pexels.com/license/'
        suitability = 'UNVERIFIED_FRAMES'
    },
    [ordered]@{
        id = 'pexels-5973868'
        title = 'Fencing motion practice'
        page = 'https://www.pexels.com/video/a-woman-practicing-her-fencing-skill-5973868/'
        download = 'https://www.pexels.com/download/video/5973868/'
        author = 'Artem Podrez'
        license = 'https://www.pexels.com/license/'
        suitability = 'UNVERIFIED_FRAMES'
    }
)
if (-not (Test-Path -LiteralPath $LogDir)) { New-Item -ItemType Directory -Path $LogDir | Out-Null }
function Note([string]$message) {
    [IO.File]::AppendAllText($Log, ('[' + (Get-Date -Format 's') + '] ' + $message + [Environment]::NewLine), $Utf8)
}
function Native([string]$exe, [string[]]$argsList) {
    $prior = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        $global:LASTEXITCODE = 0
        & $exe @argsList 2>&1 | ForEach-Object { Note ([string]$_) }
        $code = $LASTEXITCODE
    } finally { $ErrorActionPreference = $prior }
    if ($code -ne 0) { throw ('[NATIVE_FAILED] code=' + $code + ', exe=' + $exe + ', log=' + $Log) }
}
function Probe([string]$probeExe,[string]$sourcePath) {
    $result = & $probeExe '-v' 'error' '-show_entries' 'format=duration:stream=codec_type' '-of' 'json' $sourcePath
    if ($LASTEXITCODE -ne 0) { throw ('[FFPROBE_FAILED] ' + $sourcePath) }
    $obj = (($result -join [Environment]::NewLine) | ConvertFrom-Json)
    if (@($obj.streams | Where-Object { $_.codec_type -eq 'video' }).Count -ne 1) {
        throw ('[NOT_SINGLE_VIDEO_STREAM] ' + $sourcePath)
    }
    $duration = [double]::Parse([string]$obj.format.duration,[Globalization.CultureInfo]::InvariantCulture)
    if ($duration -lt 2.5 -or $duration -gt 120) { throw ('[DURATION_OUT_OF_RANGE] ' + $duration) }
    return $duration
}
try {
    Note 'START candidate review, preview only, no ComfyUI mutation.'
    if ([IO.Path]::GetFullPath($Root).TrimEnd('\') -ine $ExpectedRoot) { throw '[WRONG_WORKSPACE]' }
    foreach ($required in @((Join-Path $Root 'ComfyUI'),(Join-Path $Root '.venv'))) {
        if (-not (Test-Path -LiteralPath $required)) { throw ('[MISSING_ENV] ' + $required) }
    }
    if (-not (Get-Command 'curl.exe' -ErrorAction SilentlyContinue)) { throw '[CURL_MISSING]' }
    $ffDir = Join-Path $Root '.venv\Lib\site-packages\imageio_ffmpeg\binaries'
    $ffmpegFiles = @(Get-ChildItem -LiteralPath $ffDir -Filter 'ffmpeg*.exe' -File)
    if ($ffmpegFiles.Count -ne 1) { throw '[FFMPEG_MISSING_OR_AMBIGUOUS]' }
    $ffmpeg = $ffmpegFiles[0].FullName
    $probes = @(Get-ChildItem -LiteralPath (Join-Path $Root 'ffmpeg-build') -Recurse -File -Filter 'ffprobe.exe')
    if ($probes.Count -ne 1) { throw '[FFPROBE_MISSING_OR_AMBIGUOUS]' }
    $ffprobe = $probes[0].FullName
    if (-not (Test-Path -LiteralPath $OutDir)) { New-Item -ItemType Directory -Path $OutDir | Out-Null }
    if (Test-Path -LiteralPath $Report) { throw '[REVIEW_RECEIPT_ALREADY_EXISTS] Check prior output, no overwrite.' }

    $results = @()
    foreach ($candidate in $Candidates) {
        $source = Join-Path $OutDir ($candidate.id + '-source.mp4')
        $partial = Join-Path $OutDir ($candidate.id + '-download.part')
        $preview = Join-Path $OutDir ($candidate.id + '-contact-sheet.png')
        if (-not (Test-Path -LiteralPath $source)) {
            if (Test-Path -LiteralPath $partial) { throw ('[PARTIAL_DOWNLOAD_CONFLICT] ' + $partial) }
            Note ('Downloading ' + $candidate.id + ' from official Pexels URL.')
            Native 'curl.exe' @('--location','--fail','--silent','--show-error','--retry','3','--output',$partial,$candidate.download)
            if ((Get-Item -LiteralPath $partial).Length -lt 100000) { throw ('[DOWNLOAD_TOO_SMALL] ' + $candidate.id) }
            [void](Probe $ffprobe $partial)
            Move-Item -LiteralPath $partial -Destination $source -ErrorAction Stop
        }
        $duration = Probe $ffprobe $source
        if (Test-Path -LiteralPath $preview) { throw ('[PREVIEW_CONFLICT] ' + $preview) }
        # One thumbnail per second, tiled in chronological order, first 16 seconds maximum.
        $filter = 'fps=1,scale=240:240:force_original_aspect_ratio=decrease,pad=240:240:(ow-iw)/2:(oh-ih)/2:color=black,tile=4x4:nb_frames=16:padding=6:margin=6'
        Native $ffmpeg @('-hide_banner','-loglevel','warning','-nostdin','-n','-i',$source,'-t','16','-an','-vf',$filter,'-frames:v','1',$preview)
        if (-not (Test-Path -LiteralPath $preview) -or (Get-Item -LiteralPath $preview).Length -lt 10000) {
            throw ('[PREVIEW_MISSING_OR_INVALID] ' + $candidate.id)
        }
        $results += [ordered]@{
            id = $candidate.id
            title = $candidate.title
            page = $candidate.page
            author = $candidate.author
            license = $candidate.license
            source_sha256 = (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash
            duration_sec = $duration
            source_file = $source
            contact_sheet = $preview
            content_review = 'PENDING_VISUAL_REVIEW'
            approved_for_scail = $false
        }
    }
    $receipt = [ordered]@{
        status = 'CONTACT_SHEETS_READY_ASSETS_NOT_APPROVED'
        disclaimer = 'Contact sheets are visual candidates only; no driving input or workflow changed.'
        candidates = $results
    }
    [IO.File]::WriteAllText($Report,(($receipt | ConvertTo-Json -Depth 6) + [Environment]::NewLine),$Utf8)
    Note 'PASS contact sheets and source hashes ready. SCAIL video selection NOT_APPROVED; render NOT_RUN.'
    try { Start-Process -FilePath 'explorer.exe' -ArgumentList ('"' + $OutDir + '"') | Out-Null } catch { }
    Write-Output '[PASS]'
} catch {
    Note ('FAIL ' + $_.Exception.Message)
    Write-Output ('[FAIL] ' + $_.Exception.Message)
    Write-Output ('Log: ' + $Log)
    exit 1
}
