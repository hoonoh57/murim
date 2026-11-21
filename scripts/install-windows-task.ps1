#requires -Version 5.1
<#
.SYNOPSIS
  One-time registration of Murim polling under the current interactive user.
  Uses Task Scheduler, not a new GitHub Actions run per commit.
  Run once from the approved Windows machine after the consumer clone exists.
#>
[CmdletBinding()]
param(
    [string]$TaskName = "Murim-GitHub-Sync-Test",
    [int]$IntervalMinutes = 10
)

$ErrorActionPreference = "Stop"
if ($IntervalMinutes -lt 5 -or $IntervalMinutes -gt 60) {
    throw "[INVALID_INTERVAL] Choose between 5 and 60 minutes."
}
$workspace = Split-Path -Parent $PSScriptRoot
if (-not (Test-Path -LiteralPath (Join-Path $workspace ".git"))) {
    throw "[NOT_A_GIT_CLONE] Refusing to register a task for an unverified directory."
}
$repoRoot = (& git -C $workspace rev-parse --show-toplevel 2>&1)
if ($LASTEXITCODE -ne 0) { throw "[GIT_UNAVAILABLE] Cannot determine repository root." }
$root = [IO.Path]::GetFullPath(($repoRoot -join "`n").Trim()).TrimEnd('\','/')
$expected = [IO.Path]::GetFullPath($workspace).TrimEnd('\','/')
if (-not [string]::Equals($root, $expected, [StringComparison]::OrdinalIgnoreCase)) {
    throw "[WORKSPACE_MISMATCH] Registration requires the repository root."
}
$origin = (& git -C $workspace remote get-url origin 2>&1)
if ($LASTEXITCODE -ne 0 -or (($origin -join "") -notmatch '^(https://github\.com/hoonoh57/murim(\.git)?|git@github\.com:hoonoh57/murim(\.git)?)$')) {
    throw "[REMOTE_MISMATCH] Refusing to register an unknown repository."
}
$old = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($null -ne $old) {
    throw "[TASK_ALREADY_EXISTS] An existing task with this name must be inspected; no overwrite."
}
$identity = [Security.Principal.WindowsIdentity]::GetCurrent().Name
$runnerPath = Join-Path $workspace "scripts\windows-sync-test.ps1"
if (-not (Test-Path -LiteralPath $runnerPath -PathType Leaf)) {
    throw "[SCRIPT_MISSING] Windows sync/test entrypoint not found."
}
$arguments = '-NoProfile -NonInteractive -ExecutionPolicy Bypass -File "' + $runnerPath + '" -Workspace "' + $workspace + '" -OnlyOnChange'
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $arguments -WorkingDirectory $workspace
$repeat = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes $IntervalMinutes) -RepetitionDuration (New-TimeSpan -Days 3650)
$logon = New-ScheduledTaskTrigger -AtLogOn -User $identity
$principal = New-ScheduledTaskPrincipal -UserId $identity -LogonType Interactive -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 30)
$null = Register-ScheduledTask -TaskName $TaskName -Description "Murim GitHub ff-only sync and changed-HEAD pytest; Windows interactive user context" -Action $action -Trigger @($logon, $repeat) -Principal $principal -Settings $settings -ErrorAction Stop
Write-Output ("[PASS] Registered " + $TaskName + " for " + $identity)
