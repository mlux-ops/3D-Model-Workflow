param([string]$Pdf, [string]$OutPrefix, [int]$Width = 1800)
# Renders each PDF page to PNG with the Windows built-in PDF renderer (Poppler's pdftoppm is not installed).
$run = 'E:\Claude\3D-Model-Workflow\output\effort-trial-2026-09-29-sonnet\sconce\max'
$outFull = [System.IO.Path]::GetFullPath($OutPrefix)
if (-not $outFull.StartsWith($run, [System.StringComparison]::OrdinalIgnoreCase)) { throw "write outside run folder refused: $outFull" }

Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null = [Windows.Storage.StorageFile, Windows.Storage, ContentType = WindowsRuntime]
$null = [Windows.Data.Pdf.PdfDocument, Windows.Data.Pdf, ContentType = WindowsRuntime]
$null = [Windows.Storage.Streams.InMemoryRandomAccessStream, Windows.Storage.Streams, ContentType = WindowsRuntime]

$ext = [System.WindowsRuntimeSystemExtensions].GetMethods()
$asTaskGeneric = ($ext | Where-Object { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' })[0]
$asTaskAction = ($ext | Where-Object { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncAction' })[0]

function Await($op, $type) {
    $t = $asTaskGeneric.MakeGenericMethod($type).Invoke($null, @($op))
    $t.Wait(-1) | Out-Null
    $t.Result
}
function AwaitAction($op) {
    $t = $asTaskAction.Invoke($null, @($op))
    $t.Wait(-1) | Out-Null
}

$pdfFull = [System.IO.Path]::GetFullPath($Pdf)
$file = Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync($pdfFull)) ([Windows.Storage.StorageFile])
$doc = Await ([Windows.Data.Pdf.PdfDocument]::LoadFromFileAsync($file)) ([Windows.Data.Pdf.PdfDocument])
for ($i = 0; $i -lt $doc.PageCount; $i++) {
    $page = $doc.GetPage($i)
    $ms = New-Object Windows.Storage.Streams.InMemoryRandomAccessStream
    $opts = New-Object Windows.Data.Pdf.PdfPageRenderOptions
    $opts.DestinationWidth = [uint32]$Width
    AwaitAction ($page.RenderToStreamAsync($ms, $opts))
    $in = [System.IO.WindowsRuntimeStreamExtensions]::AsStreamForRead($ms.GetInputStreamAt(0))
    $out = "$outFull-p$($i + 1).png"
    $fs = [System.IO.File]::Create($out)
    $in.CopyTo($fs)
    $fs.Close()
    Write-Output "wrote $out ($($page.Size.Width) x $($page.Size.Height) pt)"
    $page.Dispose()
}
