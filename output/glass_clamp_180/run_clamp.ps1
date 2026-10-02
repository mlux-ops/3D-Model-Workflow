<#
    SHB_Glass Clamp 180 Square - native build and verification runner.

    Finds pyRevit, Revit 2025, the Generic Model template and a Python 3 on THIS PC (no user
    name, drive or folder is assumed), runs source\build_clamp.py through the pyRevit CLI with
    an absolute path, then runs source\verify_clamp.py and exits on ITS code.

    pyrevit run has returned exit code 0 on crashed scripts (P01, 2026-09-18) and has silently
    skipped a relative script path (E026). Neither exit status is used as the result.

    Run from anywhere:
        powershell -ExecutionPolicy Bypass -File "<repo>\output\glass_clamp_180\run_clamp.ps1"
    Check this PC only (builds nothing):
        powershell -ExecutionPolicy Bypass -File "<repo>\output\glass_clamp_180\run_clamp.ps1" -CheckOnly
    Verify a report written by the in-Revit button (builds nothing):
        powershell -ExecutionPolicy Bypass -File "<repo>\output\glass_clamp_180\run_clamp.ps1" -VerifyOnly

    Overrides (environment variables, all optional): CLAMP_PYREVIT, CLAMP_REVIT, CLAMP_TEMPLATE,
    CLAMP_PYTHON.

    Exit codes: 0 technical pass, 1 technical fail, 2 blocked (prerequisite missing).
    Every run writes logs\run-<stamp>.txt and logs\RUN_SUMMARY.txt, and copies the summary to
    the clipboard so it can be pasted into the chat.
#>
[CmdletBinding()]
param([switch]$CheckOnly, [switch]$VerifyOnly)

# Continue, not Stop: Windows PowerShell 5.1 turns native stderr into terminating errors under Stop.
$ErrorActionPreference = 'Continue'

$runDir   = $PSScriptRoot
$builder  = Join-Path $runDir 'source/build_clamp.py'
$spec     = Join-Path $runDir 'source/clamp_spec.py'
$verify   = Join-Path $runDir 'source/verify_clamp.py'
$catalog  = Join-Path $runDir 'SHB_Glass Clamp 180 Square.txt'
$report   = Join-Path $runDir 'validation.json'
$logs     = Join-Path $runDir 'logs'
$rfa      = Join-Path $runDir 'SHB_Glass Clamp 180 Square.rfa'

if (-not (Test-Path -LiteralPath $logs)) { New-Item -ItemType Directory -Path $logs | Out-Null }
$stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ')
try { Start-Transcript -Path (Join-Path $logs "run-$stamp.txt") | Out-Null } catch { }

$summary = New-Object System.Collections.Generic.List[string]
function Note([string]$text) { $summary.Add($text); Write-Host $text }

function J([string]$base, [string]$child) { if ($base) { Join-Path $base $child } else { $null } }
function First-Existing($paths) {
    foreach ($p in $paths) { if ($p -and (Test-Path -LiteralPath $p -PathType Leaf)) { return $p } }
    return $null
}
function Find-First([string]$name, $roots, [int]$depth, [string]$mustMatch) {
    foreach ($r in $roots) {
        if ($r -and (Test-Path -LiteralPath $r)) {
            $hits = Get-ChildItem -LiteralPath $r -Filter $name -Recurse -Depth $depth -File -ErrorAction SilentlyContinue
            if ($mustMatch) { $hits = $hits | Where-Object { $_.FullName -match $mustMatch } }
            $hit = $hits | Select-Object -First 1
            if ($hit) { return $hit.FullName }
        }
    }
    return $null
}
function Works([string]$exe, $exeArgs) {
    try {
        $o = & $exe @exeArgs -c "import sys; print(sys.version_info[0])" 2>$null
        return (($o | Select-Object -First 1) -eq '3')
    } catch { return $false }
}

$pf   = $env:ProgramFiles
$pf86 = ${env:ProgramFiles(x86)}

# ---- locate this PC's tools -------------------------------------------------------------
$fromPath = $null
$cmd = Get-Command pyrevit -ErrorAction SilentlyContinue | Select-Object -First 1
if ($cmd) { $fromPath = $cmd.Source }
$pyrevit = First-Existing @($env:CLAMP_PYREVIT, $fromPath,
    (J $pf 'pyRevit CLI/pyrevit.exe'), (J $pf 'pyRevit-Master/bin/pyrevit.exe'),
    (J $env:APPDATA 'pyRevit-Master/bin/pyrevit.exe'), (J $env:LOCALAPPDATA 'Programs/pyRevit CLI/pyrevit.exe'))
if (-not $pyrevit) { $pyrevit = Find-First 'pyrevit.exe' @($pf, $pf86, $env:APPDATA, $env:LOCALAPPDATA) 4 $null }

$revit = First-Existing @($env:CLAMP_REVIT, (J $pf 'Autodesk/Revit 2025/Revit.exe'))
if (-not $revit) { $revit = Find-First 'Revit.exe' @((J $pf 'Autodesk')) 2 '2025' }
$otherRevits = @()
if ($pf -and (Test-Path -LiteralPath (J $pf 'Autodesk'))) {
    $otherRevits = @(Get-ChildItem -LiteralPath (J $pf 'Autodesk') -Filter Revit.exe -Recurse -Depth 2 -File -ErrorAction SilentlyContinue |
        ForEach-Object { $_.FullName })
}

$template = $env:CLAMP_TEMPLATE
if (-not ($template -and (Test-Path -LiteralPath $template -PathType Leaf))) {
    $tRoots = @((J $env:ProgramData 'Autodesk/RVT 2025/Family Templates'))
    $hits = @()
    foreach ($r in $tRoots) {
        if ($r -and (Test-Path -LiteralPath $r)) {
            $hits += @(Get-ChildItem -LiteralPath $r -Filter 'Generic Model.rft' -Recurse -Depth 2 -File -ErrorAction SilentlyContinue)
        }
    }
    $template = $null
    if ($hits.Count -gt 0) { $template = ($hits | Sort-Object { $_.FullName -notmatch 'Imperial' }, FullName | Select-Object -First 1).FullName }
}

# a Python 3 for the verifier: pyRevit's bundled CPython, CLAMP_PYTHON, the py launcher, python
$pyExe = $null; $pyArgs = @()
if ($env:CLAMP_PYTHON -and (Works $env:CLAMP_PYTHON @())) { $pyExe = $env:CLAMP_PYTHON }
if (-not $pyExe -and $pyrevit) {
    $cp = Find-First 'python.exe' @((Join-Path (Split-Path -Parent $pyrevit) 'cengines')) 3 $null
    if ($cp -and (Works $cp @())) { $pyExe = $cp }
}
if (-not $pyExe) {
    $py = Get-Command py -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($py -and (Works $py.Source @('-3'))) { $pyExe = $py.Source; $pyArgs = @('-3') }
}
if (-not $pyExe) {
    foreach ($n in 'python', 'python3') {
        $c = Get-Command $n -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($c -and (Works $c.Source @())) { $pyExe = $c.Source; break }
    }
}

$repoRoot = $null
try { $repoRoot = (Resolve-Path -LiteralPath (Join-Path $runDir '../..')).Path } catch { }

Note '== This PC =='
Note ("  user / machine   {0} / {1}" -f $env:USERNAME, $env:COMPUTERNAME)
Note "  PowerShell       $($PSVersionTable.PSVersion)"
Note "  kit folder       $runDir"
$hasAgents = [bool]($repoRoot -and (Test-Path -LiteralPath (Join-Path $repoRoot 'AGENTS.md')))
Note "  checkout         $repoRoot   AGENTS.md present: $hasAgents"
foreach ($row in @(@('pyRevit CLI', $pyrevit), @('Revit 2025', $revit), @('Generic Model.rft', $template),
                   @('Python 3 (verifier)', $pyExe), @('builder', $builder), @('spec', $spec),
                   @('verifier', $verify), @('type catalog', $catalog))) {
    if ($row[1]) { Note ("  OK       {0,-20} {1}" -f $row[0], $row[1]) } else { Note ("  MISSING  {0}" -f $row[0]) }
}
if ($otherRevits.Count -gt 0) { Note ("  Revit installs seen: " + ($otherRevits -join ' | ')) }

$missing = @()
foreach ($row in @(@('pyRevit CLI', $pyrevit), @('Revit 2025', $revit), @('Generic Model.rft', $template),
                   @('Python 3', $pyExe), @('build_clamp.py', (First-Existing @($builder))),
                   @('clamp_spec.py', (First-Existing @($spec))), @('verify_clamp.py', (First-Existing @($verify))),
                   @('type catalog', (First-Existing @($catalog))))) {
    if (-not $row[1]) { $missing += $row[0] }
}
if (-not $hasAgents) { $missing += 'AGENTS.md two folders above the kit (not a full checkout)' }

if ($pyrevit) {
    Note '  pyrevit env (attached Revits):'
    try { & $pyrevit env 2>&1 | Select-Object -First 25 | ForEach-Object { Note ("    " + $_) } } catch { Note "    pyrevit env failed: $_" }
}

function Finish([int]$code) {
    $text = ($summary -join "`r`n")
    try { Set-Content -LiteralPath (Join-Path $logs 'RUN_SUMMARY.txt') -Value $text -Encoding UTF8 } catch { }
    try { Set-Clipboard -Value $text; Write-Host 'Summary copied to the clipboard and saved to logs\RUN_SUMMARY.txt - paste it into the chat.' } catch { Write-Host 'Summary saved to logs\RUN_SUMMARY.txt.' }
    try { Stop-Transcript | Out-Null } catch { }
    exit $code
}

if ($missing.Count -gt 0) {
    Note ''
    Note ("BLOCKED - missing on this PC: " + ($missing -join '; ') + '. Nothing was run.')
    Note 'A missing prerequisite is BLOCKED, never FAIL and never PASS. Set CLAMP_PYREVIT / CLAMP_REVIT / CLAMP_TEMPLATE / CLAMP_PYTHON to point at it.'
    Finish 2
}
if ($CheckOnly) {
    Note ''
    Note 'CHECK OK - everything needed was found. Nothing was built (-CheckOnly).'
    Finish 0
}

# ---- build ---------------------------------------------------------------------------------
$env:CLAMP_REPO_ROOT = $repoRoot
$env:CLAMP_TEMPLATE  = $template
Note ''
Note "  RFA will be      $rfa"
if ($VerifyOnly) {
    Note '  -VerifyOnly: nothing is built; the existing validation.json is verified.'
    $oldStart = Join-Path $logs 'run-start.txt'
    if (Test-Path -LiteralPath $oldStart) { Remove-Item -LiteralPath $oldStart; Note '  removed logs\run-start.txt so an older runner stamp cannot mark the report stale' }
} else {
if (Test-Path -LiteralPath $report) {
    $keep = Join-Path $logs "validation-previous-$stamp.json"
    Copy-Item -LiteralPath $report -Destination $keep
    Note "  previous report kept as $keep"
}
$start = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ss')
Set-Content -LiteralPath (Join-Path $logs 'run-start.txt') -Value $start -Encoding ASCII
Note "  run start (UTC)  $start"

Note ''
Note '== Build (pyrevit run, absolute path) =='
Note '  pyRevit starts its own Revit 2025 session; open models are not touched.'
& $pyrevit run $builder --revit=2025
Note "  pyrevit exit code was $LASTEXITCODE - deliberately ignored, see header"

$fresh = $false
if (Test-Path -LiteralPath $report) {
    $fresh = ((Get-Item -LiteralPath $report).LastWriteTimeUtc -ge [datetime]::ParseExact($start, "yyyy-MM-dd'T'HH:mm:ss", $null).AddSeconds(-1))
}
if (-not $fresh) {
    Note ''
    Note 'NO NEW validation.json: the builder never ran inside Revit. pyrevit run could not start it'
    Note '(native startup exception 0xe06d7363 on 2026-09-23). Use the in-Revit button, README.md:'
    Note '  Revit > pyRevit tab > SHB > Build Clamp 180, then run this script again with -VerifyOnly.'
    $tmp = Join-Path ([System.IO.Path]::GetTempPath()) 'clamp_builder_startup_error.txt'
    if (Test-Path -LiteralPath $tmp) {
        Note "  startup error left by the builder ($tmp):"
        Get-Content -LiteralPath $tmp | Select-Object -First 15 | ForEach-Object { Note ("    " + $_) }
    }
}
}

# ---- verify ------------------------------------------------------------------------------------
Note ''
Note '== Verify (verify_clamp.py) =='
$vout = & $pyExe @pyArgs $verify 2>&1
$verdict = $LASTEXITCODE
$vout | ForEach-Object { Note ([string]$_) }
Note "  verifier exit code: $verdict"

if (Test-Path -LiteralPath $report) {
    try {
        $r = Get-Content -LiteralPath $report -Raw | ConvertFrom-Json
        Note ''
        Note '== Report =='
        Note "  stage: $($r.stage)   script: $($r.script_version)   revit: $($r.revit_version)   started: $($r.started_utc)"
        Note "  template used: $($r.template.path)   (source: $($r.template.source), imperial: $($r.template.imperial))"
        Note "  failed gates: $($r.failed_gates -join ', ')"
        if ($r.error) { Note '  builder error (last 12 lines):'; ($r.error -split "`n" | Select-Object -Last 12) | ForEach-Object { Note ("    " + $_) } }
        Note "  cap sketches constrained: left=$($r.build.parts.cap_left.sketch_constrained) right=$($r.build.parts.cap_right.sketch_constrained)"
        foreach ($e in @($r.build_errors)) {
            if ($e) { Note "  build step failed: $($e.step)"; ($e.error -split "`n" | Where-Object { $_.Trim() } | Select-Object -Last 4) | ForEach-Object { Note ("    " + $_) } }
        }
        foreach ($d in @($r.build.planes.dimension_errors)) { if ($d) { Note "  dimension problem: $d" } }
        if ($r.build.planes.dimension_attempts) {
            foreach ($prop in $r.build.planes.dimension_attempts.PSObject.Properties) {
                $made = @($prop.Value | Where-Object { $_.created }).Count
                if ($made -eq 0) { Note ("  dimension '" + $prop.Name + "' attempts: " + ($prop.Value | ConvertTo-Json -Depth 8 -Compress)) }
            }
        }
        $cf = @($r.captured_failures | Where-Object { $_ } | ForEach-Object { $_.severity + ': ' + $_.text })
        if ($cf.Count -gt 0) { Note ("  captured failures: " + ($cf -join ' | ')) }
    } catch { Note "  could not read validation.json: $_" }
}

Note ''
if (Test-Path -LiteralPath $rfa) {
    $item = Get-Item -LiteralPath $rfa
    Note ("RFA written: {0}  ({1:N0} bytes, {2})" -f $item.FullName, $item.Length, $item.LastWriteTime)
} else {
    Note "NO RFA was written to $runDir"
}
if ($verdict -eq 0) {
    Note 'TECHNICAL PASS. Next: review evidence\*.png against references\crl_sgc180\ (visual gate, human);'
    Note '  then write REVIEW.md with "Visual verdict: ACCEPTED" and run source\package_clamp.py.'
} else {
    Note 'TECHNICAL FAIL. Read the lines above; the error and its fix go in PROJECT_MEMORY.md (AGENTS.md rule).'
}
Finish $verdict
