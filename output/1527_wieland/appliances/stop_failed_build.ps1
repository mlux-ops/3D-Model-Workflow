$ErrorActionPreference = 'Stop'
$failedRunner = Get-CimInstance Win32_Process -Filter 'ProcessId=43188'
$failedRevit = Get-CimInstance Win32_Process -Filter 'ProcessId=31944'
$scriptPath = 'E:\Claude\3D-Model-Workflow\output\1527_wieland\appliances\build_custom.py'
if ($failedRunner -and $failedRunner.ParentProcessId -eq 31392 -and $failedRunner.CommandLine.Contains($scriptPath) -and $failedRevit -and $failedRevit.ParentProcessId -eq 43188 -and $failedRevit.CommandLine.Contains('310f49d9-1b84-4a9c-ae8e-53128e935faf')) {
    & taskkill.exe /T /F /PID 43188
} else {
    Write-Output 'Recorded failed build tree is no longer present; no process stopped.'
}
