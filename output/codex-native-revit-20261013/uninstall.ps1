$ErrorActionPreference = 'Stop'
$manifest = Join-Path $env:APPDATA 'Autodesk\Revit\Addins\2025\CodexNativeRevit2025.addin'
if (Test-Path -LiteralPath $manifest) {
    $xml = [xml](Get-Content -LiteralPath $manifest -Raw)
    if ($xml.RevitAddIns.AddIn.AddInId -ne '5AA4F7DB-757D-4ED1-BD53-B78C2D1C9E56') { throw 'Manifest identity differs; refusing removal.' }
    Remove-Item -LiteralPath $manifest
}
Write-Output 'Unique add-in manifest removed. Running Revit unaffected. Receipts, token, releases and backups retained for recovery. Remove codex-native-revit-2025 with codex mcp remove when desired.'
