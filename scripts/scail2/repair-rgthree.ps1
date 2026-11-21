# Isolated, fail-closed repair for the official SCAIL-2 low-VRAM workflow.
# Only adds pinned rgthree-comfy to E:\comfyui-scail; no models or legacy ComfyUI changes.
Set-StrictMode -Version 2
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$ExpectedRoot = 'E:\comfyui-scail'
$Comfy = Join-Path $Root 'ComfyUI'
$Target = Join-Path $Comfy 'custom_nodes\rgthree-comfy'
$Launch = Join-Path $Root 'start-scail2.cmd'
$Repo = 'https://github.com/rgthree/rgthree-comfy.git'
$Pin = 'bc48c6aaeca87bedbc14245d89f9bc6be37a630e'
$ComfyPin = '72865f4f27eaf5396f8f36370e0a2be3a9a090ee'
$LogDir = Join-Path $Root 'logs'
$Log = Join-Path $LogDir 'repair-rgthree.log'
$Utf8 = New-Object System.Text.UTF8Encoding($false)
if (-not (Test-Path -LiteralPath $LogDir)) { New-Item -ItemType Directory -Path $LogDir | Out-Null }
function Note([string]$message) {
    [IO.File]::AppendAllText($Log, ('[' + (Get-Date -Format 's') + '] ' + $message + [Environment]::NewLine), $Utf8)
}
function GitRun([string[]]$argsList) {
    $previous = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        $global:LASTEXITCODE = 0
        & git.exe @argsList 2>&1 | ForEach-Object { Note ([string]$_) }
        $exitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previous
    }
    if ($exitCode -ne 0) { throw ('[GIT_FAILED] exit=' + $exitCode + ' see ' + $Log) }
}
try {
    Note 'START isolated rgthree missing-node repair.'
    if ([IO.Path]::GetFullPath($Root).TrimEnd('\') -ine $ExpectedRoot) { throw '[WRONG_WORKSPACE]' }
    if (-not (Test-Path -LiteralPath $Launch)) { throw '[LAUNCHER_MISSING] start-scail2.cmd' }
    if (-not (Test-Path -LiteralPath (Join-Path $Comfy '.git'))) { throw '[COMFY_MISSING]' }
    if (-not (Get-Command 'git.exe' -ErrorAction SilentlyContinue)) { throw '[GIT_MISSING]' }
    $comfyHead = (& git.exe -C $Comfy rev-parse HEAD).Trim()
    if ($LASTEXITCODE -ne 0 -or $comfyHead -ine $ComfyPin) { throw '[COMFY_VERSION_MISMATCH]' }

    # Do not replace an existing server process. Restart it explicitly before repair.
    $client = New-Object Net.Sockets.TcpClient
    try {
        $client.Connect('127.0.0.1', 8189)
        throw '[PORT_8189_IN_USE] Close the existing SCAIL ComfyUI console first.'
    } catch [Net.Sockets.SocketException] {
        # No listener: safe to install and launch this isolated instance.
    } finally {
        $client.Dispose()
    }

    # rgthree's __init__.py removes historic web/extension folders.
    # Reject any preexisting copies rather than silently allowing deletion.
    foreach ($legacy in @('web\extensions\rgthree','web\extensions\rgthree-comfy')) {
        if (Test-Path -LiteralPath (Join-Path $Comfy $legacy)) {
            throw ('[EXISTING_EXTENSION_CONFLICT] ' + $legacy)
        }
    }
    if (-not (Test-Path -LiteralPath $Target)) { GitRun @('clone', $Repo, $Target) }
    if (-not (Test-Path -LiteralPath (Join-Path $Target '.git'))) { throw '[RGTHREE_EXISTING_NOT_GIT]' }
    $origin = (& git.exe -C $Target remote get-url origin).Trim()
    if ($LASTEXITCODE -ne 0 -or $origin -ine $Repo) { throw '[RGTHREE_REPOSITORY_MISMATCH]' }
    $dirty = @(& git.exe -C $Target status --porcelain=v1 --untracked-files=all)
    if ($LASTEXITCODE -ne 0 -or $dirty.Count -ne 0) { throw '[RGTHREE_LOCAL_CHANGES]' }
    $head = (& git.exe -C $Target rev-parse HEAD).Trim()
    if ($LASTEXITCODE -ne 0) { throw '[RGTHREE_HEAD_UNAVAILABLE]' }
    if ($head -ine $Pin) { GitRun @('-C', $Target, 'checkout', '--detach', $Pin) }
    $head = (& git.exe -C $Target rev-parse HEAD).Trim()
    if ($LASTEXITCODE -ne 0 -or $head -ine $Pin) { throw '[RGTHREE_PIN_MISMATCH]' }
    $mapping = [IO.File]::ReadAllText((Join-Path $Target '__init__.py'))
    if (-not $mapping.Contains('RgthreeDisplayInt.NAME')) { throw '[RGTHREE_DISPLAY_INT_MISSING]' }
    Note ('PIN_VERIFIED ' + $Pin)

    Start-Process -FilePath $env:ComSpec -ArgumentList @('/k', ('"' + $Launch + '"')) -WorkingDirectory $Root | Out-Null
    $verified = $false
    for ($attempt = 0; $attempt -lt 80; $attempt++) {
        try {
            $info = Invoke-RestMethod -Uri 'http://127.0.0.1:8189/object_info' -TimeoutSec 20
            if ($info.PSObject.Properties['Display Int (rgthree)'] -and
                $info.PSObject.Properties['WanSCAILToVideo'] -and
                $info.PSObject.Properties['SCAIL2EasyConfig']) {
                $verified = $true
                break
            }
        } catch { }
        Start-Sleep -Seconds 3
    }
    if (-not $verified) { throw '[NODE_REGISTRATION_NOT_VERIFIED] Check the SCAIL server console.' }
    $receipt = [ordered]@{
        status = 'STARTUP_NODE_VERIFIED_NOT_RENDERED'
        rgthree_commit = $Pin
        required_node = 'Display Int (rgthree)'
        comfyui_version_pin = $ComfyPin
        ui = 'http://127.0.0.1:8189'
    }
    [IO.File]::WriteAllText((Join-Path $Root 'rgthree-repair-report.json'), (($receipt | ConvertTo-Json -Depth 4) + [Environment]::NewLine), $Utf8)
    Note 'PASS: rgthree Display Int + SCAIL-2 nodes registered on port 8189. Render NOT_RUN.'
    try { Start-Process 'http://127.0.0.1:8189' | Out-Null } catch { }
    Write-Output '[PASS]'
} catch {
    Note ('FAIL: ' + $_.Exception.Message)
    Write-Output ('[FAIL] ' + $_.Exception.Message)
    exit 1
}
