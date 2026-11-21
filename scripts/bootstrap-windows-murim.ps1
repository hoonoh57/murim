#requires -Version 5.1
<#
One-time Windows consumer bootstrap for hoonoh57/murim.
- Never deletes, renames, stages, or overwrites existing non-Git files.
- Reuses an existing matching clean Git clone, or clones into an absent/empty directory.
- Registers a periodic Windows task once; GitHub remains the only source of code CRUD.
#>
[CmdletBinding()]
param(
    [string]$Workspace = 'E:\gpt\projects\comfyui\murim',
    [switch]$ProbeComfy
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$target = [IO.Path]::GetFullPath('E:\gpt\projects\comfyui\murim').TrimEnd('\', '/')
$actual = [IO.Path]::GetFullPath($Workspace).TrimEnd('\', '/')
if (-not [string]::Equals($actual, $target, [StringComparison]::OrdinalIgnoreCase)) {
    throw '[UNAPPROVED_PATH] This bootstrap is restricted to E:\gpt\projects\comfyui\murim.'
}

# Reject junction/symlink paths without following them for writes.
$cursor = $actual
while ($true) {
    if (Test-Path -LiteralPath $cursor) {
        $info = Get-Item -LiteralPath $cursor -Force -ErrorAction Stop
        if (($info.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
            throw ('[REPARSE_POINT_DENIED] ' + $cursor)
        }
    }
    $parent = Split-Path -Parent $cursor
    if ([string]::IsNullOrWhiteSpace($parent) -or $parent -eq $cursor) { break }
    $cursor = $parent
}
$parentDir = Split-Path -Parent $actual
if (-not (Test-Path -LiteralPath $parentDir -PathType Container)) {
    throw ('[PARENT_MISSING] Preserve/create the approved workspace parent first: ' + $parentDir)
}
if ($null -eq (Get-Command git -ErrorAction SilentlyContinue)) {
    throw '[GIT_MISSING] Git for Windows must already be installed.'
}
if (Test-Path -LiteralPath $actual -PathType Leaf) {
    throw '[FILE_AT_WORKSPACE] Expected a directory.'
}

$hasClone = $false
if (Test-Path -LiteralPath $actual -PathType Container) {
    if (Test-Path -LiteralPath (Join-Path $actual '.git')) {
        $hasClone = $true
    } else {
        $first = Get-ChildItem -LiteralPath $actual -Force -ErrorAction Stop | Select-Object -First 1
        if ($null -ne $first) {
            throw '[NONEMPTY_NOT_GIT] Existing murim files are preserved. Do not clone/overwrite until this folder is reviewed.'
        }
    }
}

function Invoke-GitChecked {
    param([string[]]$Arguments)
    $output = & git -C $actual @Arguments 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw ('[GIT_FAILED] git ' + ($Arguments -join ' ') + ' (exit ' + $LASTEXITCODE + ') ' + ($output -join ' '))
    }
    return (($output -join "`n").Trim())
}

if (-not $hasClone) {
    & git clone --branch main --single-branch https://github.com/hoonoh57/murim.git $actual
    if ($LASTEXITCODE -ne 0) {
        throw '[CLONE_FAILED] Git clone did not finish; inspect the folder before retrying.'
    }
} else {
    $top = Invoke-GitChecked -Arguments @('rev-parse', '--show-toplevel')
    if (-not [string]::Equals([IO.Path]::GetFullPath($top).TrimEnd('\', '/'), $actual, [StringComparison]::OrdinalIgnoreCase)) {
        throw '[WRONG_GIT_ROOT] Refusing to reuse a different repository.'
    }
    $remote = Invoke-GitChecked -Arguments @('remote', 'get-url', 'origin')
    if ($remote -notmatch '^(https://github\.com/hoonoh57/murim(\.git)?|git@github\.com:hoonoh57/murim(\.git)?)$') {
        throw '[WRONG_ORIGIN] Refusing to reuse a different repository.'
    }
    $branch = Invoke-GitChecked -Arguments @('branch', '--show-current')
    if ($branch -cne 'main') { throw '[WRONG_BRANCH] Refusing non-main local branch.' }
    $changes = Invoke-GitChecked -Arguments @('status', '--porcelain=v1', '--untracked-files=all')
    if (-not [string]::IsNullOrWhiteSpace($changes)) {
        throw '[USER_CHANGES] Local changes detected. No automatic overwrite.'
    }
    # The repository-owned sync guard checks incoming ignored-file collisions as well.
    $sync = Join-Path $actual 'scripts\windows-sync-test.ps1'
    if (-not (Test-Path -LiteralPath $sync -PathType Leaf)) {
        throw '[SYNC_SCRIPT_MISSING] Existing clone is not yet a verified consumer checkout.'
    }
    & powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File $sync -Workspace $actual -OnlyOnChange
    if ($LASTEXITCODE -ne 0) { throw '[SYNC_FAILED] Consumer sync/test failed.' }
}

$installer = Join-Path $actual 'scripts\install-windows-task.ps1'
if (-not (Test-Path -LiteralPath $installer -PathType Leaf)) {
    throw '[INSTALLER_MISSING] Repository checkout is incomplete.'
}
$existing = Get-ScheduledTask -TaskName 'Murim-GitHub-Sync-Test' -ErrorAction SilentlyContinue
if ($null -eq $existing) {
    & powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File $installer
    if ($LASTEXITCODE -ne 0) { throw '[TASK_REGISTRATION_FAILED] Git checkout remains intact.' }
} else {
    $arguments = @($existing.Actions | ForEach-Object { [string]$_.Arguments })
    if ($arguments.Count -ne 1 -or $arguments[0] -notlike '*windows-sync-test.ps1*' -or $arguments[0] -notlike '*-OnlyOnChange*') {
        throw '[EXISTING_TASK_CONFLICT] Task name already exists with an unexpected action. No overwrite.'
    }
}

if ($ProbeComfy) {
    $stats = Invoke-RestMethod -Method Get -Uri 'http://127.0.0.1:8188/system_stats' -TimeoutSec 15
    if ($null -eq $stats) { throw '[COMFY_PROBE_FAILED] Empty /system_stats response.' }
}
$head = Invoke-GitChecked -Arguments @('rev-parse', 'HEAD')
Write-Output ('[PASS] murim clone + scheduled sync registered HEAD=' + $head.Substring(0, 12))
