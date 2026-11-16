# Phase 5: log free commit memory and the editor's committed memory every few seconds.
# Usage: powershell -File memory_log.ps1 <output csv> [<seconds between lines>] [<minutes to run>]
param([string]$Out, [int]$Every = 5, [int]$Minutes = 110)
$logDirectory = Split-Path -Parent ([System.IO.Path]::GetFullPath($Out))
if (-not (Test-Path -LiteralPath $logDirectory)) { New-Item -ItemType Directory -Path $logDirectory -Force | Out-Null }
if (-not (Test-Path $Out)) { "time,free_commit_gb,free_physical_gb,editor_committed_gb,editor_pid,gpu_used_mib,gpu_total_mib" | Out-File -FilePath $Out -Encoding ascii }
$end = (Get-Date).AddMinutes($Minutes)
while ((Get-Date) -lt $end) {
    $os = Get-CimInstance Win32_OperatingSystem
    $editor = Get-Process UnrealEditor -ErrorAction SilentlyContinue | Sort-Object PrivateMemorySize64 -Descending | Select-Object -First 1
    $committed = if ($editor) { [math]::Round($editor.PrivateMemorySize64 / 1GB, 2) } else { "" }
    $id = if ($editor) { $editor.Id } else { "" }
    $gpu = & nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader,nounits
    "{0},{1:N2},{2:N2},{3},{4},{5}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), ($os.FreeVirtualMemory / 1MB), ($os.FreePhysicalMemory / 1MB), $committed, $id, $gpu.Trim() | Out-File -FilePath $Out -Encoding ascii -Append
    Start-Sleep -Seconds $Every
}
