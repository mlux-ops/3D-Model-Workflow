<#
    Cassia SF549315AGOP family - native build and verification runner.

    Preflights the workstation, runs source\build_cassia.py through the pyRevit CLI
    with an absolute path, then runs source\verify_cassia.py and exits on ITS code.

    pyrevit run has returned exit code 0 on crashed scripts (P01, 2026-09-18) and
    has silently skipped a relative script path (E026). Neither exit status is used
    as the result.

    Run from anywhere:
        powershell -ExecutionPolicy Bypass -File "<repo>\output\cassia\run_cassia.ps1"

    Exit codes: 0 technical pass, 1 technical fail, 2 blocked (prerequisite missing).
#>

$ErrorActionPreference = 'Stop'

$runDir   = $PSScriptRoot
$builder  = Join-Path $runDir 'source\build_cassia.py'
$geometry = Join-Path $runDir 'source\cassia_geometry.py'
$verify   = Join-Path $runDir 'source\verify_cassia.py'
$report   = Join-Path $runDir 'validation.json'
$logs     = Join-Path $runDir 'logs'

$pyrevit  = 'C:\Program Files\pyRevit-Master\bin\pyrevit.exe'
$cpython  = 'C:\Program Files\pyRevit-Master\bin\cengines\CPY3123\python.exe'
$revit    = 'C:\Program Files\Autodesk\Revit 2025\Revit.exe'
$template = 'C:\ProgramData\Autodesk\RVT 2025\Family Templates\English-Imperial\Generic Model face based.rft'

Write-Host '== Preflight =='
$missing = @()
foreach ($p in @($builder, $geometry, $verify, $pyrevit, $cpython, $revit, $template)) {
    if (Test-Path -LiteralPath $p) { Write-Host "  OK      $p" }
    else { Write-Host "  MISSING $p"; $missing += $p }
}
if ($missing.Count -gt 0) {
    Write-Host ''
    Write-Host "BLOCKED - $($missing.Count) required path(s) missing. Nothing was run."
    Write-Host 'A missing native prerequisite is BLOCKED, never FAIL and never PASS.'
    exit 2
}

if (-not (Test-Path -LiteralPath $logs)) { New-Item -ItemType Directory -Path $logs | Out-Null }

# Keep the previous report instead of letting this run overwrite the only copy.
if (Test-Path -LiteralPath $report) {
    $stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ')
    $keep  = Join-Path $logs "validation-previous-$stamp.json"
    Copy-Item -LiteralPath $report -Destination $keep
    Write-Host "  retained previous report as $keep"
}

# The verifier rejects a report older than this stamp (stale-report guard).
$start = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ss')
Set-Content -LiteralPath (Join-Path $logs 'run-start.txt') -Value $start -Encoding ASCII
Write-Host "  run start (UTC) $start"

Write-Host ''
Write-Host '== Build (pyrevit run, absolute path) =='
Write-Host '  pyRevit starts its own Revit 2025 session. If Autodesk sign-in or a'
Write-Host '  "device limit reached" screen appears, resolve it there; nothing in your'
Write-Host '  open models is touched.'
& $pyrevit run $builder --revit=2025
Write-Host "  pyrevit exit code was $LASTEXITCODE - deliberately ignored, see header"

Write-Host ''
Write-Host '== Verify (verify_cassia.py) =='
& $cpython $verify
$verdict = $LASTEXITCODE

Write-Host ''
if ($verdict -eq 0) {
    Write-Host 'TECHNICAL PASS. Next:'
    Write-Host '  1. Review evidence\*.png against references\cassia\ (visual gate, human).'
    Write-Host "  2. Write REVIEW.md with 'Visual verdict: ACCEPTED', then package:"
    Write-Host "       & `"$cpython`" `"$runDir\source\package_cassia.py`""
    Write-Host '  3. Upload the ZIP to Google Drive > 3D Model Workflow > 3D Models and verify its size.'
} else {
    Write-Host 'TECHNICAL FAIL. Read validation.json and logs\ before changing anything;'
    Write-Host 'record the error and its fix in PROJECT_MEMORY.md (AGENTS.md rule).'
}
exit $verdict
