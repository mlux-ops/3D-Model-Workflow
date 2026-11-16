# Phase 11: hard floor for free commit memory while the editor renders or packages.
# Every 5 s reads free commit memory; under $Floor GB it asks the editor to cancel the running render
# (cancel_render.py), logs it, and then waits 2 minutes before looking again. Runs for $Minutes minutes.
param([double]$Floor = 15, [int]$Minutes = 1440)
$Plan = 'E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland'
$Log = Join-Path $Plan 'review\phase11\floor_watch.log'
Set-Location $Plan
Add-Content -Path $Log -Value ("{0} floor_watch started (pid {1}, floor {2} GB)" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $PID, $Floor)
$end = (Get-Date).AddMinutes($Minutes)
while ((Get-Date) -lt $end) {
    $free = (Get-CimInstance Win32_OperatingSystem).FreeVirtualMemory / 1MB
    if ($free -lt $Floor) {
        $reply = & python -B tools/ue_call.py py review/phase11/scripts/cancel_render.py 60 2>&1 | Out-String
        Add-Content -Path $Log -Value ("{0} free commit {1:N1} GB under the floor; cancel asked: {2}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $free, ($reply -replace '\s+', ' '))
        Start-Sleep -Seconds 120
    }
    Start-Sleep -Seconds 5
}
