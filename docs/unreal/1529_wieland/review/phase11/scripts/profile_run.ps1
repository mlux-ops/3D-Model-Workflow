# Phase 11, step 11.5: run the packaged build on the fixed paths and record a profile.
#
# Starts the packaged program on the level L_W1529_Profile, which plays the fixed paths and holds by itself, looping
# (SEQ_W1529_ProfilePaths). Picture 2,560 by 1,440 full screen; the real-time tier: screen percentage 67 (computed
# 1,715 by 965, upscaled by Temporal Super Resolution), every quality group at Epic (3), texture pool 4,000 MB; no frame
# cap and no wait for the screen (t.MaxFPS 0, r.VSync 0) so that the frame time is the true time per picture.
# The engine's frame-time recorder (CSV profiler) records $Frames frames from the start and then closes the program.
# Every second this script also reads the program's video memory from Windows ("GPU Process Memory", dedicated) and
# free commit memory. Output: D:\Wieland1529_delivery\profile_run\<label>\.
param([string]$Label = 'run1', [int]$Frames = 60000, [int]$MaxMinutes = 30)
$ErrorActionPreference = 'Stop'
$Build = 'D:\Wieland1529_delivery\package\1529_Wieland_UE5.9_Delivery_2026-11-14\build\Windows'
$Out = Join-Path 'D:\Wieland1529_delivery\profile_run' $Label
New-Item -ItemType Directory -Force -Path $Out | Out-Null
$Status = Join-Path $Out 'run_status.log'
function Say($text) { $line = '{0} {1}' -f (Get-Date -Format 'HH:mm:ss'), $text; Add-Content -Path $Status -Value $line -Encoding utf8; Write-Output $line }

$exe = Get-ChildItem -Path (Join-Path $Build 'Wieland1527\Binaries\Win64') -Filter '*.exe' | Where-Object { $_.Name -notmatch 'CrashReport' } | Select-Object -First 1
if (-not $exe) { Say 'STOP: no program found under the build'; exit 2 }
$csvDir = Join-Path $Build 'Wieland1527\Saved\Profiling\CSV'
$before = @(Get-ChildItem $csvDir -Filter '*.csv*' -ErrorAction SilentlyContinue | ForEach-Object FullName)
$exec = 'scalability 3,r.ScreenPercentage 67,r.Streaming.PoolSize 4000,t.MaxFPS 0,r.VSync 0,r.ScreenPercentage,sg.GlobalIlluminationQuality,sg.ShadowQuality,r.RayTracing.Nanite.Mode,t.MaxFPS,r.Streaming.PoolSize,r.AntiAliasingMethod'
$argList = @('/Game/Wieland1529/Delivery/L_W1529_Profile', '-ResX=2560', '-ResY=1440', '-FullScreen', '-nosplash', '-NoSound',
             ('-ExecCmds="{0}"' -f $exec), ('-csvCaptureFrames={0}' -f $Frames), '-ExitAfterCsvProfiling', '-csvGpuStats',
             ('-csvMetadata="label={0},tier=realtime_M7,output=2560x1440"' -f $Label))
# Windows' per-process counter ("GPU Process Memory") reads 296,753 MB for the editor on this machine (it counts
# reserved, not resident, memory of DirectX 12), so the whole card's use ("GPU Adapter Memory", the adapter with the
# most in use = the RTX 4080) is logged instead, with a baseline taken before the program starts. The program's own
# reading is the record's GPUMem/LocalUsedMB, as in Phase 9.
function CardMB($kind) {
    try {
        $c = Get-Counter -Counter ("\GPU Adapter Memory(*)\{0}" -f $kind) -ErrorAction Stop
        return [math]::Round((($c.CounterSamples | Measure-Object CookedValue -Maximum).Maximum / 1MB), 0)
    } catch { return '' }
}
$baseline = @(1..5 | ForEach-Object { CardMB 'Dedicated Usage'; Start-Sleep -Milliseconds 400 })
Say ('card dedicated memory in use before the program starts (the editor on an empty level, the desktop): {0} MB (five readings: {1})' -f ($baseline | Measure-Object -Maximum).Maximum, ($baseline -join ', '))
Say ('the editor stays open (it hosts the agent), on an empty level with its viewport not drawing in real time')
Say ('free commit {0:N1} GB; starting {1} {2}' -f ((Get-CimInstance Win32_OperatingSystem).FreeVirtualMemory / 1MB), $exe.FullName, ($argList -join ' '))
$p = Start-Process -FilePath $exe.FullName -ArgumentList $argList -PassThru
$null = $p.Handle
$mem = Join-Path $Out 'video_memory.csv'
'time,card_dedicated_mb,card_shared_mb,free_commit_gb,process_private_gb' | Out-File -FilePath $mem -Encoding ascii
$end = (Get-Date).AddMinutes($MaxMinutes)
while (-not $p.HasExited) {
    $ded = CardMB 'Dedicated Usage'
    $sha = CardMB 'Shared Usage'
    $priv = try { (Get-Process -Id $p.Id -ErrorAction Stop).PrivateMemorySize64 / 1GB } catch { 0 }
    '{0},{1},{2},{3:N2},{4:N2}' -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $ded, $sha, ((Get-CimInstance Win32_OperatingSystem).FreeVirtualMemory / 1MB), $priv | Out-File -FilePath $mem -Encoding ascii -Append
    if ((Get-Date) -gt $end) { Say ('STOP: still running after {0} minutes; program ended' -f $MaxMinutes); Stop-Process -Id $p.Id -Force; break }
    Start-Sleep -Milliseconds 500
}
$p.WaitForExit()
Say ('program ended, exit code {0}' -f $p.ExitCode)
Start-Sleep -Seconds 3
$new = @(Get-ChildItem $csvDir -Filter '*.csv*' -ErrorAction SilentlyContinue | Where-Object { $before -notcontains $_.FullName } | Sort-Object LastWriteTime)
foreach ($f in $new) { Copy-Item $f.FullName -Destination $Out -Force; Say ('frame-time record: {0} ({1:N1} MB)' -f $f.Name, ($f.Length / 1MB)) }
$log = Get-ChildItem (Join-Path $Build 'Wieland1527\Saved\Logs') -Filter 'Wieland1527*.log' -ErrorAction SilentlyContinue | Sort-Object LastWriteTime | Select-Object -Last 1
if ($log) { Copy-Item $log.FullName -Destination (Join-Path $Out 'program.log') -Force; Say ('program log copied: {0}' -f $log.Name) }
# The run leaves the program's own Saved folder (records, logs, settings) inside the build; it is moved (not deleted)
# out of the package so that the delivered build is as packaged.
$saved = Join-Path $Build 'Wieland1527\Saved'
if (Test-Path $saved) { Move-Item -Path $saved -Destination (Join-Path $Out 'program_Saved') -Force; Say 'the build''s Saved folder of this run moved out of the package to program_Saved' }
