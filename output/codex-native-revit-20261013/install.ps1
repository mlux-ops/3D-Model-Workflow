#requires -Version 7.0
param([switch]$ConfigureCodex, [int]$Port = 49327)
$ErrorActionPreference = 'Stop'
$packageRoot = $PSScriptRoot
$sourceDll = Join-Path $packageRoot 'src\NativeRevit\bin\Release\net8.0-windows\CodexNativeRevit.dll'
if (!(Test-Path -LiteralPath $sourceDll)) { throw 'Build the Revit 2025 release assembly first.' }
$version = (Get-FileHash -LiteralPath $sourceDll -Algorithm SHA256).Hash.Substring(0,12).ToLowerInvariant()
$installRoot = Join-Path $env:LOCALAPPDATA "CodexNativeRevit\releases\$version"
New-Item -ItemType Directory -Path $installRoot -Force | Out-Null
Copy-Item -LiteralPath $sourceDll -Destination $installRoot
Copy-Item -LiteralPath (Join-Path $packageRoot 'controller') -Destination $installRoot -Recurse -Force
$stateRoot = Join-Path $env:LOCALAPPDATA 'CodexNativeRevit'
$tokenFile = Join-Path $stateRoot 'token'
if (!(Test-Path -LiteralPath $tokenFile)) {
    $tokenBytes = New-Object byte[] 32
    [Security.Cryptography.RandomNumberGenerator]::Fill($tokenBytes)
    [IO.File]::WriteAllText($tokenFile,[Convert]::ToHexString($tokenBytes))
}
$userAccount = [Security.Principal.WindowsIdentity]::GetCurrent().Name
& icacls $stateRoot /inheritance:r /grant:r "${userAccount}:(OI)(CI)F" 'SYSTEM:(OI)(CI)F' | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'Could not restrict bridge state directory permissions.' }
$addinRoot = Join-Path $env:APPDATA 'Autodesk\Revit\Addins\2025'
New-Item -ItemType Directory -Path $addinRoot -Force | Out-Null
$manifest = Join-Path $addinRoot 'CodexNativeRevit2025.addin'
if (Test-Path -LiteralPath $manifest) {
    Copy-Item -LiteralPath $manifest -Destination (Join-Path $stateRoot ('manifest-backup-'+(Get-Date -Format 'yyyyMMdd-HHmmss')+'.addin'))
}
$dll = [Security.SecurityElement]::Escape((Join-Path $installRoot 'CodexNativeRevit.dll'))
$xml = @"
<?xml version="1.0" encoding="utf-8"?>
<RevitAddIns><AddIn Type="Application"><Name>Codex Native Revit 2025</Name><Assembly>$dll</Assembly><AddInId>5AA4F7DB-757D-4ED1-BD53-B78C2D1C9E56</AddInId><FullClassName>CodexNativeRevit.App</FullClassName><VendorId>CDXN</VendorId><VendorDescription>Local Codex Native Revit connection</VendorDescription></AddIn></RevitAddIns>
"@
[IO.File]::WriteAllText($manifest,$xml)
$python = (& py -3 -c 'import sys; print(sys.executable)').Trim()
if ($LASTEXITCODE -ne 0) { throw 'Python 3 is required for the MCP controller.' }
$controller = Join-Path $installRoot 'controller\native_revit.py'
$configPath = Join-Path $packageRoot 'codex-native-revit.toml'
$pythonToml = $python.Replace('\','\\')
$controllerToml = $controller.Replace('\','\\')
$tokenToml = $tokenFile.Replace('\','\\')
$config = @"
[mcp_servers.codex-native-revit-2025]
command = "$pythonToml"
args = ["$controllerToml", "stdio"]
startup_timeout_sec = 15
tool_timeout_sec = 90
[mcp_servers.codex-native-revit-2025.env]
CODEX_NATIVE_REVIT_URL = "http://127.0.0.1:$Port"
CODEX_NATIVE_REVIT_TOKEN_FILE = "$tokenToml"
"@
[IO.File]::WriteAllText($configPath,$config)
if ($ConfigureCodex) {
    & codex mcp add codex-native-revit-2025 --env "CODEX_NATIVE_REVIT_URL=http://127.0.0.1:$Port" --env "CODEX_NATIVE_REVIT_TOKEN_FILE=$tokenFile" -- $python $controller stdio
    if ($LASTEXITCODE -ne 0) { throw 'Codex MCP registration failed; use the generated TOML.' }
}
Write-Output "Installed $manifest. Release $version. Existing extensions preserved. Loads in a NEW Revit session; this script never closes Revit. MCP config: $configPath"
