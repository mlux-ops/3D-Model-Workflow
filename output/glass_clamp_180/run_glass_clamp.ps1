<#
    SHB_Glass Clamp 180 Square - native build and verification runner.

    Preflights the workstation, runs source\build_glass_clamp.py through the pyRevit CLI
    with an ABSOLUTE path, then runs source\verify_glass_clamp.py and exits on ITS code.

    pyrevit run has returned exit code 0 on crashed scripts (P01, 2026-09-18) and has
    silently skipped a relative script path (E026). Neither exit status is used as the result.

    Run from anywhere:
        powershell -ExecutionPolicy Bypass -File "<repo>\output\glass_clamp_180\run_glass_clamp.ps1"

    Exit codes: 0 technical pass, 1 technical fail, 2 blocked (prerequisite missing).
#>

$ErrorActionPreference = 'Stop'

$runDir   = $PSScriptRoot
$builder  = Join-Path $runDir 'source\build_glass_clamp.py'
$geometry = Join-Path $runDir 'source\clamp_geometry.py'
$verify   = Join-Path $runDir 'source\verify_glass_clamp.py'
$report   = Join-Path $runDir 'validation.json'
$logs     = Join-Path $runDir 'logs'
$rfa      = Join-Path $runDir 'SHB_Glass Clamp 180 Square.rfa'
$catalog  = Join-Path $runDir 'SHB_Glass Clamp 180 Square.txt'

$pyrevit  = 'C:\Program Files\pyRevit-Master\bin\pyrevit.exe'
$revit    = 'C:\Program Files\Autodesk\Revit 2025\Revit.exe'
$template = 'C:\ProgramData\Autodesk\RVT 2025\Family Templates\English-Imperial\Generic Model.rft'

# The verifier needs only the Python standard library. pyRevit's bundled CPython first.
$cpython = $null
foreach ($candidate in @('C:\Program Files\pyRevit-Master\bin\cengines\CPY3123\python.exe',
                         'C:\Python314\python.exe',
                         'C:\Users\mlux\AppData\Local\Programs\Python\Python312\python.exe')) {
    if (Test-Path -LiteralPath $candidate) { $cpython = $candidate; break }
}

Write-Host '== Preflight =='
$missing = @()
foreach ($p in @($builder, $geometry, $verify, $pyrevit, $revit, $template)) {
    if (Test-Path -LiteralPath $p) { Write-Host "  OK      $p" }
    else { Write-Host "  MISSING $p"; $missing += $p }
}
if ($cpython) { Write-Host "  OK      $cpython (verifier)" }
else { Write-Host '  MISSING a CPython for the verifier'; $missing += 'CPython' }
if ($missing.Count -gt 0) {
    Write-Host ''
    Write-Host "BLOCKED - $($missing.Count) required path(s) missing. Nothing was run."
    Write-Host 'A missing native prerequisite is BLOCKED, never FAIL and never PASS.'
    exit 2
}

if (-not (Test-Path -LiteralPath $logs)) { New-Item -ItemType Directory -Path $logs | Out-Null }

# Tell the builder which checkout to write into (it falls back to its own location).
$repoRoot = (Resolve-Path -LiteralPath (Join-Path $runDir '..\..')).Path
$env:GLASS_CLAMP_REPO_ROOT = $repoRoot
Write-Host "  checkout        $repoRoot"
Write-Host "  RFA will be     $rfa"
Write-Host "  catalog will be $catalog"

# Keep the previous report instead of letting this run overwrite the only copy.
if (Test-Path -LiteralPath $report) {
    $stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ')
    $keep  = Join-Path $logs "validation-previous-$stamp.json"
    Copy-Item -LiteralPath $report -Destination $keep
    Write-Host "  retained previous report as $keep"
}

Write-Host ''
Write-Host '== Build (pyrevit run, absolute path) =='
Write-Host '  pyRevit starts its own Revit 2025 session. If Autodesk sign-in or a'
Write-Host '  "device limit reached" screen appears, resolve it there; nothing in your'
Write-Host '  open models is touched and the Belmont model is never opened.'
& $pyrevit run $builder --revit=2025
Write-Host "  pyrevit exit code was $LASTEXITCODE - deliberately ignored, see header"

Write-Host ''
Write-Host '== Verify (verify_glass_clamp.py) =='
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
if (Test-Path -LiteralPath $catalog) { Write-Host "Type catalog: $catalog" }
Write-Host ''
if ($verdict -eq 0) {
    Write-Host 'TECHNICAL PASS. Next:'
    Write-Host '  1. Review exports\*.png (front, plan, side, iso) - the visual gate is a human one.'
    Write-Host '  2. Load the RFA into the Belmont model by hand (README.md, Place in the Belmont model).'
    Write-Host '  3. Upload the RFA, the catalog and README.md to Google Drive > 3D Model Workflow > 3D Models and verify fileSize.'
} else {
    Write-Host 'TECHNICAL FAIL. Read validation.json and logs\ before changing anything;'
    Write-Host 'record the error and its fix in PROJECT_MEMORY.md (AGENTS.md rule).'
}
exit $verdict
