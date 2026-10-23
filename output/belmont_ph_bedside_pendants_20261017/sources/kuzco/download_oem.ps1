$ErrorActionPreference = 'Stop'
$dir = Split-Path -Parent $MyInvocation.MyCommand.Path
$items = @(
 @('41411_Spec_Sheet.pdf','https://s3-us-west-2.amazonaws.com/catsy.870/41411_Spec_Sheet.pdf'),
 @('41411_Installation_Instructions.pdf','https://s3-us-west-2.amazonaws.com/catsy.870/41411_Installation_Instructions.pdf'),
 @('REVIT-41411-Jarvis.zip','https://s3.us-west-2.amazonaws.com/catsy.870/REVIT-41411-Jarvis.zip'),
 @('402401-LED_Spec_Sheet.pdf','https://s3-us-west-2.amazonaws.com/catsy.870/402401-LED_Spec_Sheet.pdf'),
 @('402401-LED_Installation_Instructions.pdf','https://s3-us-west-2.amazonaws.com/catsy.870/402401-LED_Installation_Instructions.pdf'),
 @('IES-402401-LED-Malabar.zip','https://s3.us-west-2.amazonaws.com/catsy.870/IES-402401-LED-Malabar.zip'),
 @('REVIT-402401-LED-Malabar.zip','https://s3.us-west-2.amazonaws.com/catsy.870/REVIT-402401-LED-Malabar.zip'),
 @('494502M_Spec_Sheet.pdf','https://s3-us-west-2.amazonaws.com/catsy.870/494502M_Spec_Sheet.pdf'),
 @('494502M_Installation_Instructions.pdf','https://s3-us-west-2.amazonaws.com/catsy.870/494502M_Installation_Instructions.pdf'),
 @('REVIT-494502M-Milca.zip','https://s3.us-west-2.amazonaws.com/catsy.870/REVIT-494502M-Milca.zip')
)
$manifest = @()
foreach ($item in $items) {
 $path = Join-Path $dir $item[0]
 Invoke-WebRequest -UseBasicParsing -Uri $item[1] -OutFile $path -TimeoutSec 60
 $file = Get-Item -LiteralPath $path
 $hash = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
 $manifest += [pscustomobject]@{filename=$item[0];url=$item[1];bytes=$file.Length;sha256=$hash}
 Write-Output "$($item[0]) $($file.Length) $hash"
}
$manifest | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $dir 'SOURCE_MANIFEST.json') -Encoding UTF8
