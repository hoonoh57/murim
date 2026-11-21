#requires -Version 5.1
<#
.SYNOPSIS
  Read-only-to-source Windows consumer entrypoint: fast-forward from GitHub and run local tests.
  Never resets, cleans, installs packages, or changes user-authored files.
  This script becomes active only when executed by an approved Windows runner/task.
#>
[CmdletBinding()]
param(
    [string]$Workspace = (Split-Path -Parent $PSScriptRoot),
    [string]$PythonExe = "python",
    [switch]$RequireComfy,
    [switch]$OnlyOnChange,
    [string]$ComfyUrl = "http://127.0.0.1:8188"
)

$ErrorActionPreference = "Stop"

function Git-Run {
    param([string[]]$ArgsList)
    $lines = & git -C $Workspace @ArgsList 2>&1
    $code = $LASTEXITCODE
    if ($code -ne 0) {
        throw ("[GIT_FAIL] git " + ($ArgsList -join " ") + " (exit " + $code + "): " + ($lines -join " "))
    }
    return (($lines -join "`n").Trim())
}

if (-not (Test-Path -LiteralPath $Workspace -PathType Container)) {
    throw "[WORKSPACE_MISSING] Windows clone path does not exist: $Workspace"
}
$full = [IO.Path]::GetFullPath((Resolve-Path -LiteralPath $Workspace).ProviderPath).TrimEnd('\', '/')
$root = Git-Run -ArgsList @("rev-parse", "--show-toplevel")
$normalizedRoot = [IO.Path]::GetFullPath($root).TrimEnd('\', '/')
if (-not [string]::Equals($full, $normalizedRoot, [StringComparison]::OrdinalIgnoreCase)) {
    throw "[WORKSPACE_MISMATCH] Expected repository root, not a parent or nested path."
}
$origin = Git-Run -ArgsList @("remote", "get-url", "origin")
if ($origin -notmatch '^(https://github\.com/hoonoh57/murim(\.git)?|git@github\.com:hoonoh57/murim(\.git)?)$') {
    throw "[REMOTE_MISMATCH] Refusing to synchronize an unknown origin."
}
$branch = Git-Run -ArgsList @("branch", "--show-current")
if ($branch -ne "main") {
    throw "[BRANCH_MISMATCH] Expected main, actual: $branch"
}
$dirty = Git-Run -ArgsList @("status", "--porcelain=v1", "--untracked-files=all")
if (-not [string]::IsNullOrWhiteSpace($dirty)) {
    throw "[LOCAL_CHANGES_PRESENT] Local staged/unstaged/untracked files found; no overwrite performed."
}
$before = Git-Run -ArgsList @("rev-parse", "HEAD")
[void](Git-Run -ArgsList @("fetch", "--no-tags", "origin", "main"))
$target = Git-Run -ArgsList @("rev-parse", "refs/remotes/origin/main")
$base = Git-Run -ArgsList @("merge-base", "HEAD", "refs/remotes/origin/main")
if ($base -ne $before) {
    throw "[DIVERGED_OR_AHEAD] Windows branch is not an ancestor of GitHub main; no forced overwrite."
}
[void](Git-Run -ArgsList @("merge", "--ff-only", "refs/remotes/origin/main"))
$after = Git-Run -ArgsList @("rev-parse", "HEAD")
if ($after -ne $target) {
    throw "[SYNC_MISMATCH] Windows HEAD is not origin/main."
}


# A successful-HEAD marker lives outside the repository so a polling task can
# leave generated local assets and git status untouched. Never record failures.
$verifiedRoot = Join-Path $env:LOCALAPPDATA "Murim"
$mode = $(if ($RequireComfy) { "pytest-comfy" } else { "pytest" })
$verifiedFile = Join-Path $verifiedRoot ("last-verified-" + $mode + ".txt")
if ($OnlyOnChange -and (Test-Path -LiteralPath $verifiedFile -PathType Leaf)) {
    $verified = [IO.File]::ReadAllText($verifiedFile).Trim()
    if ($verified -eq $after) {
        Write-Output ("[PASS] murim unchanged; previously verified HEAD=" + $after.Substring(0, 12))
        return
    }
}

Push-Location -LiteralPath $Workspace
try {
    $testOutput = & $PythonExe -m pytest -q tests 2>&1
    $testCode = $LASTEXITCODE
    if ($testCode -ne 0) {
        throw ("[PYTEST_FAIL] Exit " + $testCode + ": " + ($testOutput -join "`n"))
    }
    if ($RequireComfy) {
        if ($ComfyUrl -notmatch '^http://(127\.0\.0\.1|localhost)(:[0-9]+)?/?$') {
            throw "[COMFY_URL_DENIED] Only explicit loopback HTTP ComfyUI addresses are accepted."
        }
        $response = Invoke-RestMethod -Method Get -Uri ($ComfyUrl.TrimEnd('/') + "/system_stats") -TimeoutSec 15
        if ($null -eq $response) {
            throw "[COMFY_PROBE_FAIL] ComfyUI did not return system stats."
        }
    }
} finally {
    Pop-Location
}
if ($OnlyOnChange) {
    if (-not (Test-Path -LiteralPath $verifiedRoot -PathType Container)) {
        [void](New-Item -ItemType Directory -Path $verifiedRoot -Force)
    }
    $tmpFile = $verifiedFile + ".tmp"
    [IO.File]::WriteAllText($tmpFile, $after + "`n", [Text.Encoding]::ASCII)
    Move-Item -LiteralPath $tmpFile -Destination $verifiedFile -Force
}
Write-Output ("[PASS] murim Windows sync+pytest HEAD=" + $after.Substring(0, 12) + $(if ($RequireComfy) { "+ComfyUI" } else { "" }))
