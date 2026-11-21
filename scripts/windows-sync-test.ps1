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


# The scheduled task does not retain PowerShell stdout/stderr by default.
# Record the last failure outside the source checkout without weakening
# fail-closed Git checks or storing credentials in the repository.
try {

function Git-Run {
    param([string[]]$ArgsList)
    # Windows PowerShell 5.1 converts native stderr (including harmless
    # "From https://..." fetch progress) into error records. Do not treat
    # those records as a failure: inspect the native exit code instead.
    $previousPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        $lines = @(& git -C $Workspace @ArgsList 2>&1)
        $code = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previousPreference
    }
    $output = (($lines | ForEach-Object { [string]$_ }) -join "`n").Trim()
    if ($code -ne 0) {
        throw ("[GIT_FAIL] git " + ($ArgsList -join " ") + " (exit " + $code + "): " + $output)
    }
    return $output
}

if ($null -eq (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "[GIT_MISSING] Git for Windows is not on PATH in the scheduled task account."
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
[void](Git-Run -ArgsList @("fetch", "--quiet", "--no-tags", "origin", "main"))
$target = Git-Run -ArgsList @("rev-parse", "refs/remotes/origin/main")
$base = Git-Run -ArgsList @("merge-base", "HEAD", "refs/remotes/origin/main")
if ($base -ne $before) {
    throw "[DIVERGED_OR_AHEAD] Windows branch is not an ancestor of GitHub main; no forced overwrite."
}
# Git may overwrite an ignored file when a new tracked path has the same name.
# Protect exact incoming paths even if local git status looks clean.
$incomingText = Git-Run -ArgsList @("-c", "core.quotePath=false", "diff", "--name-only", "--diff-filter=ACMRT", "HEAD", "refs/remotes/origin/main")
if (-not [string]::IsNullOrWhiteSpace($incomingText)) {
    foreach ($pathPart in ($incomingText -split '\r?\n')) {
        if ([string]::IsNullOrWhiteSpace($pathPart)) { continue }
        $currentPath = Join-Path $Workspace $pathPart
        $tracked = Git-Run -ArgsList @("ls-files", "--cached", "--", $pathPart)
        if ([string]::IsNullOrWhiteSpace($tracked) -and (Test-Path -LiteralPath $currentPath)) {
            throw "[IGNORED_FILE_CONFLICT] Incoming tracked path conflicts with an existing local file: $pathPart"
        }
    }
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

if ($null -eq (Get-Command -Name $PythonExe -ErrorAction SilentlyContinue)) {
    throw "[PYTHON_MISSING] Python executable is not on PATH in the scheduled task account: $PythonExe"
}
Push-Location -LiteralPath $Workspace
try {
    # Likewise, Python/pytest may emit useful diagnostics on stderr.
    # Capture them and fail only when the process returns a nonzero code.
    $previousPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        $testOutput = @(& $PythonExe -m pytest -q tests 2>&1)
        $testCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previousPreference
    }
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

} catch {
    $failure = $_
    $detail = "[FAIL] " + [string]$failure.Exception.Message
    $stack = [string]$failure.ScriptStackTrace
    $userLogRoot = $env:LOCALAPPDATA
    if ([string]::IsNullOrWhiteSpace($userLogRoot)) { $userLogRoot = $env:TEMP }
    try {
        if ([string]::IsNullOrWhiteSpace($userLogRoot)) { throw "No user log directory." }
        $diagnosticDir = Join-Path $userLogRoot "Murim"
        if (-not (Test-Path -LiteralPath $diagnosticDir -PathType Container)) {
            [void](New-Item -ItemType Directory -Path $diagnosticDir -Force)
        }
        $report = ([DateTime]::UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ") + [Environment]::NewLine +
                   $detail + [Environment]::NewLine + $stack + [Environment]::NewLine)
        $diagnosticFile = Join-Path $diagnosticDir "last-task-failure.txt"
        [IO.File]::WriteAllText($diagnosticFile, $report, [Text.UTF8Encoding]::new($false))
    } catch {
        # Preserve the original product failure even when diagnostics cannot be saved.
    }
    [Console]::Error.WriteLine($detail)
    exit 1
}
