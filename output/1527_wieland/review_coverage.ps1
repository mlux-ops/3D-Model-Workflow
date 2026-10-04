param(
    [string]$Root = (Join-Path $PSScriptRoot ".")
)

$sections = @("appliances", "plumbing_fixtures", "electrical_fixtures")
$result = @()

foreach ($section in $sections) {
    $dir = Join-Path $Root $section
    $itemsPath = Join-Path $dir "ITEMS.json"
    $reportPath = Join-Path $dir "SECTION_REPORT.md"

    if (-not (Test-Path -LiteralPath $itemsPath)) {
        $result += [pscustomobject]@{
            Section = $section
            Expected = 0
            ReportPresent = $false
            Missing = "ITEMS.json missing"
            MissingCount = 0
        }
        continue
    }

    $items = (Get-Content -LiteralPath $itemsPath -Raw | ConvertFrom-Json).items
    $reportPresent = Test-Path -LiteralPath $reportPath
    $report = if ($reportPresent) { Get-Content -LiteralPath $reportPath -Raw } else { "" }
    $missing = @()
    foreach ($item in $items) {
        if ($report -notmatch [regex]::Escape([string]$item.row_id)) {
            $missing += [string]$item.row_id
        }
    }
    $result += [pscustomobject]@{
        Section = $section
        Expected = $items.Count
        ReportPresent = $reportPresent
        Missing = ($missing -join ",")
        MissingCount = $missing.Count
    }
}

$result | Format-Table -AutoSize
if (($result | Measure-Object -Property MissingCount -Sum).Sum -gt 0) {
    exit 2
}
