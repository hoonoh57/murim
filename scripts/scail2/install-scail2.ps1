# SCAIL-2 isolated Windows setup - PowerShell 5.1 compatible.
# This script is intentionally limited to its own E:\comfyui-scail install.
# No original ComfyUI models or source files are modified.
param([switch]$NoStart)
Set-StrictMode -Version 2
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$ExpectedRoot = 'E:\comfyui-scail'
if (-not ([IO.Path]::GetFullPath($Root).TrimEnd('\') -ieq $ExpectedRoot)) {
    throw '[WORKSPACE] Run only from E:\comfyui-scail.'
}
$Old = 'E:\ComfyUI_New\ComfyUI'
$Comfy = Join-Path $Root 'ComfyUI'
$Recipe = Join-Path $Root 'SCAIL-2-LowVRAM-Recipe'
$Venv = Join-Path $Root '.venv'
$Python = Join-Path $Venv 'Scripts\python.exe'
$Logs = Join-Path $Root 'logs'
if (-not (Test-Path -LiteralPath $Logs)) { New-Item -ItemType Directory -Path $Logs | Out-Null }
$Log = Join-Path $Logs 'install-scail2.log'
$Utf8 = [System.Text.UTF8Encoding]::new($false)
function Write-Note([string]$message) {
    [IO.File]::AppendAllText($Log, ('[' + (Get-Date -Format 's') + '] ' + $message + "`r`n"), $Utf8)
}
function Write-Exclusive([string]$file,[string]$content) {
    if (Test-Path -LiteralPath $file) {
        $previous = [IO.File]::ReadAllText($file)
        if ($previous -cne $content) { throw "[USER_FILE_CONFLICT] $file" }
        return
    }
    $parent = Split-Path -Parent $file
    if (-not (Test-Path -LiteralPath $parent)) { New-Item -ItemType Directory -Force -Path $parent | Out-Null }
    [IO.File]::WriteAllText($file,$content,$Utf8)
}
function Invoke-Native([string]$exe,[string[]]$arglist) {
    Write-Note ('RUN ' + $exe + ' ' + ($arglist -join ' '))
    $before = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        $global:LASTEXITCODE = 0
        & $exe @arglist 2>&1 | ForEach-Object { Write-Note ([string]$_) }
        $code = $LASTEXITCODE
    } finally { $ErrorActionPreference = $before }
    if ($code -ne 0) { throw ('[COMMAND_FAILED] exit=' + $code + ', exe=' + $exe + ', see ' + $Log) }
}
function Assert-Tool([string]$name) {
    if (-not (Get-Command $name -ErrorAction SilentlyContinue)) { throw "[MISSING_TOOL] $name" }
}
function Clone-Pinned([string]$dest,[string]$url,[string]$sha) {
    if (-not (Test-Path -LiteralPath $dest)) {
        Invoke-Native 'git.exe' @('clone',$url,$dest)
    }
    if (-not (Test-Path -LiteralPath (Join-Path $dest '.git'))) { throw "[EXISTING_FOLDER_NOT_GIT] $dest" }
    $dirty = @(& git.exe -C $dest status --porcelain=v1 --untracked-files=no)
    if ($dirty.Count -gt 0) { throw "[USER_SOURCE_CHANGES] $dest" }
    $actual = (& git.exe -C $dest rev-parse HEAD).Trim()
    if ($actual -ine $sha) {
        # Safe recovery from interrupted checkout: no local modifications allowed.
        Invoke-Native 'git.exe' @('-C',$dest,'checkout','--detach',$sha)
    }
    $actual = (& git.exe -C $dest rev-parse HEAD).Trim()
    if ($actual -ine $sha) { throw "[PIN_MISMATCH] $dest expected $sha got $actual" }
}
function Download-Safe([string]$name,[string]$relative,[string]$url,[long]$minimum,[string]$sharedDir='') {
    $dest = Join-Path $Comfy ('models\' + $relative)
    $filename = Join-Path $dest $name
    if ($sharedDir) {
        $existing = Join-Path (Join-Path $Old ('models\' + $sharedDir)) $name
        if ((Test-Path -LiteralPath $existing) -and ((Get-Item -LiteralPath $existing).Length -ge $minimum)) {
            Write-Note ('REUSE_SHARED ' + $existing)
            return
        }
    }
    if (-not (Test-Path -LiteralPath $dest)) { New-Item -ItemType Directory -Force -Path $dest | Out-Null }
    if (Test-Path -LiteralPath $filename) {
        if ((Get-Item -LiteralPath $filename).Length -lt $minimum) { throw "[MODEL_TOO_SMALL] $filename" }
        Write-Note ('REUSE_LOCAL ' + $filename)
        return
    }
    $part = $filename + '.part'
    # Resume is safe only for the documented fixed URL. On failure keep .part untouched.
    Invoke-Native 'curl.exe' @('--location','--fail','--silent','--show-error','--retry','4','--retry-delay','5','--continue-at','-','--output',$part,$url)
    if ((Get-Item -LiteralPath $part).Length -lt $minimum) { throw "[MODEL_DOWNLOAD_INCOMPLETE] $part" }
    Move-Item -LiteralPath $part -Destination $filename -ErrorAction Stop
    Write-Note ('MODEL_READY ' + $filename)
}
function Python312() {
    $local = Join-Path $Root 'python312\python.exe'
    if (Test-Path -LiteralPath $local) { return $local }
    $launcher = Get-Command 'py.exe' -ErrorAction SilentlyContinue
    if ($launcher) {
        $oldEap = $ErrorActionPreference
        $ErrorActionPreference = 'Continue'
        try { $found = & py.exe -3.12 -c 'import sys; print(sys.executable)' 2>$null; $pyExit=$LASTEXITCODE }
        finally { $ErrorActionPreference=$oldEap }
        if (($pyExit -eq 0) -and $found) { return ($found | Select-Object -Last 1).Trim() }
    }
    $setup = Join-Path $Root 'python-3.12.10-amd64.exe'
    if (-not (Test-Path -LiteralPath $setup)) {
        Invoke-Native 'curl.exe' @('--location','--fail','--silent','--show-error','--retry','4','--output',($setup + '.part'),'https://www.python.org/ftp/python/3.12.10/python-3.12.10-amd64.exe')
        if ((Get-Item -LiteralPath ($setup + '.part')).Length -lt 25000000) { throw '[PYTHON_INSTALLER_INCOMPLETE]' }
        Move-Item -LiteralPath ($setup + '.part') -Destination $setup
    }
    Write-Note 'Installing official Python 3.12.10 in experiment folder (no PATH change).'
    $p = Start-Process -FilePath $setup -ArgumentList @('/quiet','InstallAllUsers=0',('TargetDir=' + (Join-Path $Root 'python312')),'PrependPath=0','Include_launcher=0','Include_test=0','Shortcuts=0','Include_pip=1') -PassThru -Wait
    if ($p.ExitCode -ne 0 -or -not (Test-Path -LiteralPath $local)) { throw ('[PYTHON_INSTALL_FAILED] '+ $p.ExitCode) }
    return $local
}
try {
    Write-Note 'START isolated SCAIL-2 setup.'
    if (-not (Test-Path -LiteralPath $Old)) { throw '[LEGACY_MISSING] E:\ComfyUI_New\ComfyUI' }
    Assert-Tool 'git.exe'; Assert-Tool 'curl.exe'
    $volume = (Get-PSDrive -Name E -ErrorAction Stop).Free
    if ($volume -lt 24000000000) { throw '[DISK_SPACE] Need at least 24 GB free on E: for SCAIL + PyTorch; no files were removed.' }

    # Known compatible source releases. Never update the existing ComfyUI installation.
    Clone-Pinned $Comfy 'https://github.com/Comfy-Org/ComfyUI.git' '72865f4f27eaf5396f8f36370e0a2be3a9a090ee'
    Clone-Pinned $Recipe 'https://github.com/dvelm/SCAIL-2-Unlimited-Video-Low-VRAM.git' '2a0d3c0d613e206b4222d61462cf214304488ffd'
    $packs = @(
        @('ComfyUI-GGUF','https://github.com/city96/ComfyUI-GGUF.git','6ea2651e7df66d7585f6ffee804b20e92fb38b8a'),
        @('ComfyUI-VideoHelperSuite','https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git','4d907bee61e92c2e65af3bd6383a4e4d356126d1'),
        @('ComfyUI-KJNodes','https://github.com/kijai/ComfyUI-KJNodes.git','aa2b5ea5e7f61b51f5d26d726f23c1d74e951016')
    )
    foreach($pack in $packs) { Clone-Pinned (Join-Path (Join-Path $Comfy 'custom_nodes') $pack[0]) $pack[1] $pack[2] }
    $sourceNode = Join-Path $Recipe 'custom_nodes\scail2-easy-config'
    $targetNode = Join-Path $Comfy 'custom_nodes\scail2-easy-config'
    if (-not (Test-Path -LiteralPath $targetNode)) { Copy-Item -LiteralPath $sourceNode -Destination $targetNode -Recurse }

    # Point to shared checkpoints without junctions or copying. Legacy models stay untouched.
    $sharedYaml = @'
legacy_models:
  base_path: E:/ComfyUI_New/ComfyUI
  checkpoints: models/checkpoints
  unet: models/unet
  diffusion_models: models/diffusion_models
  clip: models/clip
  text_encoders: models/text_encoders
  clip_vision: models/clip_vision
  vae: models/vae
  loras: models/loras
'@
    Write-Exclusive (Join-Path $Comfy 'extra_model_paths.yaml') ($sharedYaml + "`n")

    $pyBase = Python312
    if (-not (Test-Path -LiteralPath $Python)) { Invoke-Native $pyBase @('-m','venv',$Venv) }
    Invoke-Native $Python @('-m','pip','install','--disable-pip-version-check','--upgrade','pip')
    # Official PyTorch's published CUDA 12.6 wheel combination for RTX 4070.
    Invoke-Native $Python @('-m','pip','install','--disable-pip-version-check','torch==2.8.0','torchvision==0.23.0','torchaudio==2.8.0','--index-url','https://download.pytorch.org/whl/cu126')
    Invoke-Native $Python @('-m','pip','install','--disable-pip-version-check','-r',(Join-Path $Comfy 'requirements.txt'))
    foreach($pack in $packs) {
        $requirements = Join-Path (Join-Path (Join-Path $Comfy 'custom_nodes') $pack[0]) 'requirements.txt'
        if (Test-Path -LiteralPath $requirements) { Invoke-Native $Python @('-m','pip','install','--disable-pip-version-check','-r',$requirements) }
    }
    Invoke-Native $Python @('-c','import torch; assert torch.cuda.is_available(), "CUDA NOT AVAILABLE"; print("GPU",torch.cuda.get_device_name(0),"CUDA",torch.version.cuda)')

    # Reuse two legacy models by model-path configuration. Download only missing SCAIL-specific weights.
    Download-Safe 'SCAIL-2-Q3_K_M.gguf' 'unet' 'https://huggingface.co/realrebelai/SCAIL-2_GGUF/resolve/main/SCAIL-2-Q3_K_M.gguf' 7000000000
    Download-Safe 'umt5_xxl_fp8_e4m3fn_scaled.safetensors' 'text_encoders' 'https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors' 6000000000 'text_encoders'
    Download-Safe 'sam3.1_multiplex_fp16.safetensors' 'checkpoints' 'https://huggingface.co/Comfy-Org/sam3.1/resolve/main/checkpoints/sam3.1_multiplex_fp16.safetensors' 1400000000
    Download-Safe 'clip_vision_h.safetensors' 'clip_vision' 'https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/clip_vision/clip_vision_h.safetensors' 900000000 'clip_vision'
    Download-Safe 'wan_2.1_vae.safetensors' 'vae' 'https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/vae/wan_2.1_vae.safetensors' 180000000 'vae'
    Download-Safe 'Wan21_I2V_14B_lightx2v_cfg_step_distill_lora_rank64.safetensors' 'loras' 'https://huggingface.co/lightx2v/Wan2.1-I2V-14B-480P-StepDistill-CfgDistill-Lightx2v/resolve/main/loras/Wan21_I2V_14B_lightx2v_cfg_step_distill_lora_rank64.safetensors' 500000000 'loras'

    # Reproduce the project's small official animation demo. These are NOT martial-arts source assets.
    $demo = Join-Path $Root 'samples\official-animation-001'
    if (-not (Test-Path -LiteralPath $demo)) { New-Item -ItemType Directory -Path $demo -Force | Out-Null }
    $upstream = 'https://raw.githubusercontent.com/zai-org/SCAIL-2/78fe19576bb06be96c2375e088574a262a300edb/examples/animation_001/'
    $demoVideo = Join-Path $demo 'driving.mp4'
    $demoImage = Join-Path $demo 'ref.jpg'
    if (-not (Test-Path -LiteralPath $demoVideo)) {
        Invoke-Native 'curl.exe' @('--location','--fail','--silent','--show-error','--retry','4','--output',($demoVideo + '.part'),($upstream + 'driving.mp4'))
        if ((Get-Item -LiteralPath ($demoVideo + '.part')).Length -lt 500000) { throw '[OFFICIAL_DEMO_VIDEO_INCOMPLETE]' }
        Move-Item -LiteralPath ($demoVideo + '.part') -Destination $demoVideo
    }
    if (-not (Test-Path -LiteralPath $demoImage)) {
        Invoke-Native 'curl.exe' @('--location','--fail','--silent','--show-error','--retry','4','--output',($demoImage + '.part'),($upstream + 'ref.jpg'))
        if ((Get-Item -LiteralPath ($demoImage + '.part')).Length -lt 200000) { throw '[OFFICIAL_DEMO_IMAGE_INCOMPLETE]' }
        Move-Item -LiteralPath ($demoImage + '.part') -Destination $demoImage
    }
    $demoVideoTarget = Join-Path $Comfy 'input\your_driving_video.mp4'
    if (-not (Test-Path -LiteralPath $demoVideoTarget)) { Copy-Item -LiteralPath $demoVideo -Destination $demoVideoTarget }
    $demoPngTarget = Join-Path $Comfy 'input\your_reference_image.png'
    if (-not (Test-Path -LiteralPath $demoPngTarget)) {
        # PNG must be genuine PNG (never a .jpg renamed to .png).
        Invoke-Native $Python @('-c','from PIL import Image; import sys; Image.open(sys.argv[1]).convert("RGB").save(sys.argv[2], format="PNG")',$demoImage,$demoPngTarget)
    }
    # Keep user's local Murim character reference available as a separate, non-default asset.
    $murimRef = Join-Path $Old 'input\content_creator_identity_reference_portrait.png'
    $murimTarget = Join-Path $Comfy 'input\murim_character_reference.png'
    if ((Test-Path -LiteralPath $murimRef) -and -not (Test-Path -LiteralPath $murimTarget)) { Copy-Item -LiteralPath $murimRef -Destination $murimTarget }

    # Supply the published original workflow and ONE derived variant (only Q3 filename and clip length).
    $rawFlow = Join-Path $Recipe 'workflows\SCAIL-2 GGUF 12GB (Easy Config).json'
    $inputJson = [IO.File]::ReadAllText($rawFlow)
    $original = $inputJson | ConvertFrom-Json
    $modelNode = @($original.nodes | Where-Object { $_.type -eq 'UnetLoaderGGUF' })
    $controlNode = @($original.nodes | Where-Object { $_.type -eq 'SCAIL2EasyConfig' })
    if ($modelNode.Count -ne 1 -or $controlNode.Count -ne 1) { throw '[WORKFLOW_SOURCE_DRIFT] Unexpected model/config nodes' }
    if ($modelNode[0].widgets_values[0] -ne 'SCAIL-2-Q4_K_M.gguf') { throw '[WORKFLOW_Q4_SOURCE_CHANGED]' }
    $modelNode[0].widgets_values[0] = 'SCAIL-2-Q3_K_M.gguf'
    $controlNode[0].widgets_values[0] = 2 # 2-second first feasibility study; original workflow unchanged.
    $workdir = Join-Path $Comfy 'user\default\workflows'
    if (-not (Test-Path -LiteralPath $workdir)) { New-Item -ItemType Directory -Force -Path $workdir | Out-Null }
    $derived = Join-Path $workdir 'SCAIL-2-Q3-8GB-FIRST-TEST.json'
    Write-Exclusive $derived (($original | ConvertTo-Json -Depth 100) + "`n")

    # ffprobe is required for the original Easy Config node's source video inspection.
    $ff = Get-Command 'ffprobe.exe' -ErrorAction SilentlyContinue
    if (-not $ff) {
        $ffZip = Join-Path $Root 'ffmpeg-essentials.zip'
        if (-not (Test-Path -LiteralPath $ffZip)) {
            Invoke-Native 'curl.exe' @('--location','--fail','--silent','--show-error','--retry','4','--output',($ffZip + '.part'),'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip')
            Move-Item -LiteralPath ($ffZip + '.part') -Destination $ffZip
        }
        $ffExtract = Join-Path $Root 'ffmpeg-build'
        if (-not (Test-Path -LiteralPath $ffExtract)) { Expand-Archive -LiteralPath $ffZip -DestinationPath $ffExtract }
        $ffProbe = @(Get-ChildItem -LiteralPath $ffExtract -Recurse -Filter 'ffprobe.exe' -File)
        if ($ffProbe.Count -ne 1) { throw '[FFPROBE_MISSING] ffmpeg package invalid' }
        $ffDir = $ffProbe[0].DirectoryName
    } else { $ffDir = Split-Path -Parent $ff.Source }
    $launch = Join-Path $Root 'start-scail2.cmd'
    $startCmd = "@echo off`r`nsetlocal`r`nset `"PATH=$ffDir;%PATH%`"`r`ncd /d `"$Comfy`"`r`n`"$Python`" main.py --listen 127.0.0.1 --port 8189 --lowvram`r`n"
    Write-Exclusive $launch $startCmd

    $report = [ordered]@{ schema_version=1; installation='PREPARED_NOT_RENDERED'; version='0.33.1'; comfy_root=$Comfy; low_vram_model='SCAIL-2-Q3_K_M.gguf'; reused_model_root=$Old; workflow=$derived; reference_image=(Test-Path -LiteralPath $demoPngTarget); driving_video=(Test-Path -LiteralPath (Join-Path $Comfy 'input\your_driving_video.mp4')); gpu_verified=$true; ui_url='http://127.0.0.1:8189' }
    $out = ($report | ConvertTo-Json -Depth 4) + "`n"
    [IO.File]::WriteAllText((Join-Path $Root 'setup-report.json'),$out,$Utf8)
    if (-not $NoStart) {
        $client = New-Object Net.Sockets.TcpClient
        try { $client.Connect('127.0.0.1',8189); throw '[PORT_IN_USE] 8189 is already in use' }
        catch [Net.Sockets.SocketException] { }
        finally { $client.Dispose() }
        Start-Process -FilePath $env:ComSpec -ArgumentList @('/k',('"' + $launch + '"')) -WorkingDirectory $Root | Out-Null
        $ready = $false
        for ($i=0; $i -lt 80; $i++) {
            try {
                $response = Invoke-RestMethod -Uri 'http://127.0.0.1:8189/system_stats' -TimeoutSec 3
                if ($response -ne $null) { $ready=$true; break }
            } catch { Start-Sleep -Seconds 3 }
        }
        if (-not $ready) { throw '[COMFY_START_TIMEOUT] Server did not respond; check the separate console and log' }
        $nodes = Invoke-RestMethod -Uri 'http://127.0.0.1:8189/object_info' -TimeoutSec 30
        foreach ($required in @('WanSCAILToVideo','SCAIL2ColoredMask','SAM3_VideoTrack','UnetLoaderGGUF','VHS_LoadVideo','VHS_VideoCombine','ImageResizeKJv2','SCAIL2EasyConfig','SCAIL2AutoVideo')) {
            if (-not $nodes.PSObject.Properties[$required]) { throw ('[NODE_MISSING] ' + $required) }
        }
        $report.installation='STARTUP_VERIFIED_NOT_RENDERED'
        [IO.File]::WriteAllText((Join-Path $Root 'setup-report.json'),(($report | ConvertTo-Json -Depth 4) + "`n"),$Utf8)
        Write-Note 'PASS: GPU, shared models, SCAIL2 original workflow, node registry, 8189 HTTP.'
        try { Start-Process 'http://127.0.0.1:8189' | Out-Null }
        catch { Write-Note 'Browser opening skipped; ComfyUI server is ready on port 8189.' }
        Write-Output '[PASS]'
    } else {
        Write-Output '[PASS]'
    }
    Write-Note 'Official SCAIL demo input staged. To render, open the Q3 workflow and Queue; sword study needs a licensed sword-driving clip.'
} catch {
    Write-Note ('FAIL: ' + $_.Exception.Message)
    Write-Output ('[FAIL] ' + $_.Exception.Message)
    Write-Output ('Log: ' + $Log)
    exit 1
}
