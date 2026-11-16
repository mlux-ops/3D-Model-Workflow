$ErrorActionPreference='Stop'
if(Get-Process Revit -ErrorAction SilentlyContinue){throw 'Save and close Revit yourself first. This launcher never closes a Revit process.'}
$pluginDirectory='C:\ProgramData\CodexNativeRevit\plugins\belmont_window_trim'
if(!(Test-Path -LiteralPath (Join-Path $pluginDirectory 'BelmontBedroomTrimInspect.dll'))){throw 'Prepared native inspection module is missing.'}
$env:CODEX_REVIT_PLUGIN_DIR=$pluginDirectory
Start-Process -FilePath 'C:\Program Files\Autodesk\Revit 2025\Revit.exe' -WindowStyle Hidden
Write-Output 'Started Revit with the task-specific native inspection directory enabled. Open the Belmont model, then run doctor and fresh documents.list.'
