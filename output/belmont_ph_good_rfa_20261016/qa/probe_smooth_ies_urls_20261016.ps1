# Read-only HTTP metadata probe for exact Modern Forms FR-W2502-52L LM-63 assets.
# A 200 HEAD alone cannot validate photometry: identity and LM-63 require bytes.
# The local record is a fresh diagnostic JSON (no overwrite).
$ErrorActionPreference = 'Stop'
$rootPath = 'E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016'
$destination = Join-Path $rootPath 'qa\smooth_frw2502_ies_http_probe_20261016.json'
if (Test-Path -LiteralPath $destination) { throw "Refusing to overwrite $destination" }

$files = @(
    'FH-W2502-52_IES.zip',       # Manufacturer linked comparator, different product
    'FR-W2501_IES.zip',          # Manufacturer indexed comparator, different product
    'FR-W2502_IES.zip',
    'FR-W2502-52_IES.zip',
    'FR-W2502-52L_IES.zip',
    'FR-W2502-52L.IES',
    'FR-W2502_IESF.zip',
    'FR-W2502-52_IESF.zip',
    'FR-W2502-52L_IESF.zip',
    'FR-W2502-52L-SBMB_IES.zip',
    'FR-W2502-52L-SB-MB_IES.zip'
)
$results = @()
foreach ($filename in $files) {
    $url = 'https://modernforms.com/images/products/IES_FILES/' + $filename
    $entry = [ordered]@{ filename=$filename; url=$url; status=$null; content_type=$null; content_length=$null; error=$null }
    try {
        $response = Invoke-WebRequest -Uri $url -Method Head -UseBasicParsing -TimeoutSec 15 -MaximumRedirection 4
        $entry.status = [int]$response.StatusCode
        $entry.content_type = [string]$response.Headers['Content-Type']
        $entry.content_length = [string]$response.Headers['Content-Length']
    }
    catch [System.Net.WebException] {
        if ($_.Exception.Response -ne $null) {
            $entry.status = [int]$_.Exception.Response.StatusCode
            $entry.content_type = [string]$_.Exception.Response.ContentType
        }
        $entry.error = $_.Exception.Message
    }
    catch { $entry.error = $_.Exception.Message }
    $results += [pscustomobject]$entry
}
$report = [ordered]@{
    observed_at_utc = [DateTime]::UtcNow.ToString('o')
    manufacturer = 'Modern Forms / WAC'
    exact_model = 'FR-W2502-52L'
    role = 'PATH_EXISTENCE_ONLY_NOT_LM63_VALIDATION'
    urls = $results
}
$report | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $destination -Encoding utf8 -NoNewline
$results | Format-Table filename,status,content_type,content_length,error -AutoSize
Write-Output "Probe written: $destination"
