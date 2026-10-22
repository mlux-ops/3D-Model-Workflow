<#
    Miele KM 3054-1 gas cooktop family - native build and verification runner.

    Preflights every path, runs source\build_km3054.py through the pyRevit CLI with an
    ABSOLUTE path, then runs source\verify_km3054.py and exits on ITS code.
    pyrevit run has returned 0 on crashed scripts (P01, 2026-09-18) and has silently
    skipped a relative script path (E026); its exit status is ignored.

        powershell -ExecutionPolicy Bypass -File "<checkout>\output\miele_km3054_1\run_km3054.ps1"

    Exit codes: 0 technical pass, 1 technical fail, 2 blocked (prerequisite missing / nothing ran).
#>
$ErrorActionPreference = 'Stop'

$runDir   = $PSScriptRoot
$repoRoot = (Resolve-Path -LiteralPath (Join-Path $runDir '..\..')).Path
$rfa      = Join-Path $runDir 'Miele_KM3054-1_Gas_Cooktop_R2025.rfa'
Write-Host "checkout        $repoRoot"
Write-Host "RFA will be     $rfa"

$builder  = Join-Path $runDir 'source\build_km3054.py'
$geometry = Join-Path $runDir 'source\km3054_geometry.py'
$verify   = Join-Path $runDir 'source\verify_km3054.py'
$report   = Join-Path $runDir 'validation.json'
$logs     = Join-Path $runDir 'logs'
$agents   = Join-Path $repoRoot 'AGENTS.md'
$pyrevit  = 'C:\Program Files\pyRevit-Master\bin\pyrevit.exe'
$cpython  = 'C:\Program Files\pyRevit-Master\bin\cengines\CPY3123\python.exe'
$revit    = 'C:\Program Files\Autodesk\Revit 2025\Revit.exe'
$template = 'C:\ProgramData\Autodesk\RVT 2025\Family Templates\English-Imperial\Generic Model face based.rft'

Write-Host '== Preflight =='
$missing = @()
foreach ($p in @($agents, $builder, $geometry, $verify, $pyrevit, $cpython, $revit, $template)) {
    if (Test-Path -LiteralPath $p) { Write-Host "  OK      $p" } else { Write-Host "  MISSING $p"; $missing += $p }
}
if ($missing.Count -gt 0) {
    Write-Host "BLOCKED - $($missing.Count) required path(s) missing. Nothing was run."
    Write-Host 'NO RFA was written'
    exit 2
}
if (-not (Test-Path -LiteralPath $logs)) { New-Item -ItemType Directory -Path $logs | Out-Null }

$stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ')
if (Test-Path -LiteralPath $report) {
    Copy-Item -LiteralPath $report -Destination (Join-Path $logs "validation-previous-$stamp.json")
    Write-Host "  retained previous report as logs\validation-previous-$stamp.json"
}
# Keep every attempt's RFA; also stops Revit writing .0001.rfa backups beside the new one.
$attempts = Join-Path $logs 'attempt-rfas'
Get-ChildItem -LiteralPath $runDir -Filter '*.rfa' -File | ForEach-Object {
    if (-not (Test-Path -LiteralPath $attempts)) { New-Item -ItemType Directory -Path $attempts | Out-Null }
    $dest = Join-Path $attempts ("{0}.before-{1}.rfa" -f $_.BaseName, $stamp)
    Move-Item -LiteralPath $_.FullName -Destination $dest
    Write-Host "  moved earlier RFA to $dest"
}

$env:KM3054_REPO_ROOT = $repoRoot
$start = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ss')
Set-Content -LiteralPath (Join-Path $logs 'run-start.txt') -Value $start -Encoding ASCII
Write-Host "  run start (UTC) $start"

Write-Host ''
Write-Host '== Build (pyrevit run, absolute path) =='
$pyLog = Join-Path $logs "pyrevit-$stamp.log"
& $pyrevit run $builder --revit=2025 2>&1 | Tee-Object -FilePath $pyLog
Write-Host "  pyrevit exit code was $LASTEXITCODE - deliberately ignored; log $pyLog"

Write-Host ''
Write-Host '== Verify (verify_km3054.py) =='
& $cpython $verify
$verdict = $LASTEXITCODE
Write-Host "  verifier exit code $verdict"
Write-Host ''
if (Test-Path -LiteralPath $rfa) {
    $item = Get-Item -LiteralPath $rfa
    Write-Host ("RFA written: {0}  ({1:N0} bytes, {2})" -f $item.FullName, $item.Length, $item.LastWriteTime)
} else {
    Write-Host "NO RFA was written to $runDir"
    Write-Host 'If no validation.json appeared, use the in-Revit button (README.md, Route B).'
}
exit $verdict
