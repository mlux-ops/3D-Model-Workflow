<#
    P01 pendant transfer test - runner for candidate-20260918-01.

    Preflights the native environment, runs the builder through the pyRevit CLI,
    then verifies the result with verify_run.py and exits on THAT code.

    pyrevit run returned exit code 0 on both failing attempts of this run
    (2026-09-18). Its exit status is not evidence and this script never uses it
    as the result.

    Run from anywhere:  powershell -ExecutionPolicy Bypass -File run_pendant.ps1
#>

$ErrorActionPreference = 'Stop'

$runDir  = $PSScriptRoot
$builder = Join-Path $runDir 'build_pendant.py'
$verify  = Join-Path $runDir 'verify_run.py'
$report  = Join-Path $runDir 'validation.json'

$pyrevit  = 'C:\Program Files\pyRevit-Master\bin\pyrevit.exe'
$cpython  = 'C:\Program Files\pyRevit-Master\bin\cengines\CPY3123\python.exe'
$revit    = 'C:\Program Files\Autodesk\Revit 2025\Revit.exe'
$templates = @(
    'C:\ProgramData\Autodesk\RVT 2025\Family Templates\English-Imperial\Generic Model face based.rft',
    'C:\ProgramData\Autodesk\RVT 2025\Family Templates\English-Imperial\Generic Model.rft'
)

Write-Host '== Preflight =='
$missing = @()
foreach ($p in @($builder, $verify, $pyrevit, $cpython, $revit) + $templates) {
    if (Test-Path -LiteralPath $p) { Write-Host "  OK      $p" }
    else { Write-Host "  MISSING $p"; $missing += $p }
}
if ($missing.Count -gt 0) {
    Write-Host ''
    Write-Host "BLOCKED - $($missing.Count) required path(s) missing. Nothing was run."
    Write-Host 'A missing native prerequisite is BLOCKED, never FAIL and never PASS.'
    exit 2
}

# Retain the previous report rather than letting this run overwrite the only copy.
if (Test-Path -LiteralPath $report) {
    $stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ')
    $keep  = Join-Path $runDir "logs\validation-previous-$stamp.json"
    Copy-Item -LiteralPath $report -Destination $keep
    Write-Host "  retained previous report as $keep"
}

Write-Host ''
Write-Host '== Build (pyrevit run) =='
& $pyrevit run $builder --revit=2025
Write-Host "  pyrevit exit code was $LASTEXITCODE - deliberately ignored, see header"

Write-Host ''
Write-Host '== Verify (verify_run.py) =='
& $cpython $verify
$verdict = $LASTEXITCODE

Write-Host ''
if ($verdict -eq 0) {
    Write-Host 'TECHNICAL PASS. Visual review is still outstanding - see README.md.'
} else {
    Write-Host 'TECHNICAL FAIL. Read validation.json and logs\ before changing anything.'
    Write-Host 'Assistance policy: one initial attempt, then at most two repair cycles.'
}
exit $verdict
