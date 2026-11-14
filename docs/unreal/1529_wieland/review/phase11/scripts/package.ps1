# Phase 11, step 11.4: package the real-time scene for Windows (Development configuration, so that the frame-time
# recorder of step 11.5 and the console work in the build).
#
# - Refuses to start under $MinFree GB of free commit memory.
# - The project's game start level names the earlier production level L_R15_Production, which is not packaged. For the
#   length of packaging only, Config\DefaultEngine.ini names L_Site_M4 instead, so the packaged program opens the
#   walk-through by itself. The file is copied first and put back byte for byte afterwards (checked by SHA-256).
# - Packages the two levels L_Site_M4 (walk-through) and L_W1529_Profile (the fixed paths of step 11.5) with
#   everything they use, into D:\Wieland1529_delivery\package\1529_Wieland_UE5.9_Delivery_2026-11-14\build\.
# - Every 5 s logs free commit memory and the memory of the packaging processes; under $Floor GB it stops packaging
#   (the editor, which hosts the agent, must not be starved).
param([double]$MinFree = 30, [double]$Floor = 12)
$ErrorActionPreference = 'Stop'
$Plan = 'E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland'
$Proj = 'D:\Unreal_Engine_Projects\Wieland1527 5.9\Wieland1527.uproject'
$Ini = 'D:\Unreal_Engine_Projects\Wieland1527 5.9\Config\DefaultEngine.ini'
$Backup = Join-Path $Plan 'review\phase11\DefaultEngine.ini.before_packaging'
$Uat = 'D:\Games\UE_5.9\Engine\Build\BatchFiles\RunUAT.bat'
$Archive = 'D:\Wieland1529_delivery\package\1529_Wieland_UE5.9_Delivery_2026-11-14\build'
$Logs = 'D:\Wieland1529_delivery\logs'
$Status = Join-Path $Plan 'review\phase11\package_status.log'
$Mem = Join-Path $Plan 'review\phase11\memory_log_packaging.csv'
$OldMap = 'GameDefaultMap=/Game/Wieland/R15_Landscape/L_R15_Production.L_R15_Production'
$NewMap = 'GameDefaultMap=/Game/Wieland1529/L_Site_M4.L_Site_M4'

function Say($text) { $line = '{0} {1}' -f (Get-Date -Format 'HH:mm:ss'), $text; Add-Content -Path $Status -Value $line -Encoding utf8; Write-Output $line }
function FreeGB { [math]::Round((Get-CimInstance Win32_OperatingSystem).FreeVirtualMemory / 1MB, 2) }
function Restore {
    if (Test-Path $Backup) {
        Copy-Item -Path $Backup -Destination $Ini -Force
        $a = (Get-FileHash $Backup -Algorithm SHA256).Hash; $b = (Get-FileHash $Ini -Algorithm SHA256).Hash
        Say ("DefaultEngine.ini put back; SHA-256 equal to the copy: {0} ({1})" -f ($a -eq $b), $b)
        $line = (Select-String -Path $Ini -Pattern '^GameDefaultMap=' | Select-Object -First 1).Line
        Say ("read back: {0}" -f $line)
    }
}

New-Item -ItemType Directory -Force -Path $Archive, $Logs | Out-Null
$free = FreeGB
Say ("packaging asked; free commit {0} GB (line {1})" -f $free, $MinFree)
if ($free -lt $MinFree) { Say 'STOP: under the line; not started'; exit 2 }
if (Get-Process -Name 'UnrealEditor-Cmd' -ErrorAction SilentlyContinue) { Say 'STOP: a packaging or cook process is already running'; exit 3 }

Copy-Item -Path $Ini -Destination $Backup -Force
Say ("DefaultEngine.ini copied to {0} (SHA-256 {1})" -f $Backup, (Get-FileHash $Backup -Algorithm SHA256).Hash)
$text = [IO.File]::ReadAllText($Ini)
if (-not $text.Contains($OldMap)) { Say 'STOP: the game start level line is not as expected; nothing changed'; exit 4 }
$bom = [IO.File]::ReadAllBytes($Ini)[0..2] -join ',' -eq '239,187,191'
[IO.File]::WriteAllText($Ini, $text.Replace($OldMap, $NewMap), (New-Object System.Text.UTF8Encoding($bom)))
Say ("game start level set to L_Site_M4 for packaging: {0}" -f (Select-String -Path $Ini -Pattern '^GameDefaultMap=').Line)

$uatLog = Join-Path $Logs 'package_uat.log'
$uatArgs = @('BuildCookRun', ('-project="{0}"' -f $Proj), '-noP4', '-platform=Win64', '-clientconfig=Development',
          '-build', '-cook', '-stage', '-pak', '-iostore', '-compressed', '-prereqs', '-archive',
          ('-archivedirectory="{0}"' -f $Archive), '-map=/Game/Wieland1529/L_Site_M4+/Game/Wieland1529/Delivery/L_W1529_Profile',
          '-unattended', '-utf8output', '-nocompileeditor', '-nodebuginfo')
Say ('RunUAT ' + ($uatArgs -join ' '))
if (-not (Test-Path $Mem)) { 'time,free_commit_gb,cook_processes_gb,shader_workers_gb,shader_workers,editor_gb' | Out-File -FilePath $Mem -Encoding ascii }
$started = Get-Date
try {
    $p = Start-Process -FilePath $Uat -ArgumentList $uatArgs -RedirectStandardOutput $uatLog -RedirectStandardError (Join-Path $Logs 'package_uat.err') -PassThru -WindowStyle Hidden
    $null = $p.Handle  # keeps the exit code readable after the process ends
    Say ("RunUAT started, process {0}" -f $p.Id)
    while (-not $p.HasExited) {
        Start-Sleep -Seconds 5
        $f = FreeGB
        $cook = (Get-Process -Name 'UnrealEditor-Cmd' -ErrorAction SilentlyContinue | Measure-Object PrivateMemorySize64 -Sum).Sum / 1GB
        $scw = Get-Process -Name 'ShaderCompileWorker' -ErrorAction SilentlyContinue
        $scwGB = ($scw | Measure-Object PrivateMemorySize64 -Sum).Sum / 1GB
        $ed = (Get-Process -Name 'UnrealEditor' -ErrorAction SilentlyContinue | Measure-Object PrivateMemorySize64 -Sum).Sum / 1GB
        '{0},{1:N2},{2:N2},{3:N2},{4},{5:N2}' -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $f, $cook, $scwGB, @($scw).Count, $ed | Out-File -FilePath $Mem -Encoding ascii -Append
        if ($f -lt $Floor) {
            Say ("STOP: free commit {0} GB under the floor {1}; packaging processes ended" -f $f, $Floor)
            & taskkill.exe /PID $p.Id /T /F | Out-Null
            Get-Process -Name 'UnrealEditor-Cmd', 'ShaderCompileWorker' -ErrorAction SilentlyContinue | Stop-Process -Force
            break
        }
    }
    $p.WaitForExit()
    Say ("RunUAT ended with exit code {0} after {1:N0} s" -f $p.ExitCode, ((Get-Date) - $started).TotalSeconds)
} finally {
    Restore
}
