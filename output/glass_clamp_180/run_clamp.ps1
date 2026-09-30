<#
    SHB_Glass Clamp 180 Square - native build and verification runner.

    Preflights the workstation, runs source\build_clamp.py through the pyRevit CLI
    with an absolute path, then runs source\verify_clamp.py and exits on ITS code.

    pyrevit run has returned exit code 0 on crashed scripts (P01, 2026-09-18) and
    has silently skipped a relative script path (E026). Neither exit status is used
    as the result.

    Run from anywhere:
        powershell -ExecutionPolicy Bypass -File "<repo>\output\glass_clamp_180\run_clamp.ps1"

    Exit codes: 0 technical pass, 1 technical fail, 2 blocked (prerequisite missing).
#>

$ErrorActionPreference = 'Stop'

$runDir   = $PSScriptRoot
$builder  = Join-Path $runDir 'source\build_clamp.py'
$spec     = Join-Path $runDir 'source\clamp_spec.py'
$verify   = Join-Path $runDir 'source\verify_clamp.py'
$catalog  = Join-Path $runDir 'SHB_Glass Clamp 180 Square.txt'
$report   = Join-Path $runDir 'validation.json'
$logs     = Join-Path $runDir 'logs'

$pyrevit  = 'C:\Program Files\pyRevit-Master\bin\pyrevit.exe'
$cpython  = 'C:\Program Files\pyRevit-Master\bin\cengines\CPY3123\python.exe'
$revit    = 'C:\Program Files\Autodesk\Revit 2025\Revit.exe'
$template = 'C:\ProgramData\Autodesk\RVT 2025\Family Templates\English-Imperial\Generic Model.rft'

Write-Host '== Preflight =='
$missing = @()
foreach ($p in @($builder, $spec, $verify, $catalog, $pyrevit, $cpython, $revit, $template)) {
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

$repoRoot = (Resolve-Path -LiteralPath (Join-Path $runDir '..\..')).Path
$env:CLAMP_REPO_ROOT = $repoRoot
$rfa = Join-Path $runDir 'SHB_Glass Clamp 180 Square.rfa'
Write-Host "  checkout        $repoRoot"
Write-Host "  RFA will be     $rfa"

if (Test-Path -LiteralPath $report) {
    $stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ')
    $keep  = Join-Path $logs "validation-previous-$stamp.json"
    Copy-Item -LiteralPath $report -Destination $keep
    Write-Host "  retained previous report as $keep"
}

$start = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ss')
Set-Content -LiteralPath (Join-Path $logs 'run-start.txt') -Value $start -Encoding ASCII
Write-Host "  run start (UTC) $start"

Write-Host ''
Write-Host '== Build (pyrevit run, absolute path) =='
Write-Host '  pyRevit starts its own Revit 2025 session; open models are not touched.'
& $pyrevit run $builder --revit=2025
Write-Host "  pyrevit exit code was $LASTEXITCODE - deliberately ignored, see header"

Write-Host ''
Write-Host '== Verify (verify_clamp.py) =='
& $cpython $verify
$verdict = $LASTEXITCODE

Write-Host ''
if (Test-Path -LiteralPath $rfa) {
    $item = Get-Item -LiteralPath $rfa
    Write-Host ("RFA written: {0}  ({1:N0} bytes, {2})" -f $item.FullName, $item.Length, $item.LastWriteTime)
} else {
    Write-Host "NO RFA was written to $runDir"
    Write-Host 'If Revit never opened the build (no validation.json), use the in-Revit button: README.md.'
}
Write-Host ''
if ($verdict -eq 0) {
    Write-Host 'TECHNICAL PASS. Next:'
    Write-Host '  1. Review evidence\*.png against references\crl_sgc180\ (visual gate, human).'
    Write-Host "  2. Write REVIEW.md with 'Visual verdict: ACCEPTED', then package:"
    Write-Host "       & `"$cpython`" `"$runDir\source\package_clamp.py`""
    Write-Host '  3. Upload the ZIP to Google Drive > 3D Model Workflow > 3D Models and verify its size.'
} else {
    Write-Host 'TECHNICAL FAIL. Read validation.json and logs\ before changing anything;'
    Write-Host 'record the error and its fix in PROJECT_MEMORY.md (AGENTS.md rule).'
}
exit $verdict
