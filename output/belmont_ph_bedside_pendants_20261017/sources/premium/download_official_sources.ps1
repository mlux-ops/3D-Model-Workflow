param(
  [string]$Destination = (Join-Path $PSScriptRoot 'originals')
)

$ErrorActionPreference = 'Stop'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
Add-Type -AssemblyName 'System.IO.Compression.FileSystem'

if (-not [IO.Directory]::Exists($Destination)) {
  [IO.Directory]::CreateDirectory($Destination) | Out-Null
}

# Exact URLs captured on 2026-10-17 from the manufacturer's own product pages.
# A manufacturer BIM link is intentionally retained for inspection, although its
# URL names the Dipping Light S TABLE lamp rather than the pendant.
$sources = @(
  @{id='schneid_stucco_datasheet'; name='SCHNEID_STUCCO_DataSheet.pdf'; url='https://schneidstudio.com/s/STUCCO_DataSheet.pdf'; origin='Schneid Studio'},
  @{id='marset_dipping_pendant_usa_datasheet'; name='MARSET_Dipping_Pendant_USA_Spec.pdf'; url='https://www.marset.com/wp-content/uploads/lamparas/pendant-light-fixtures/dipping-light-pendant/MARSET_Dipping-Susp_Spec-sheet_USA_new.pdf'; origin='Marset'},
  @{id='marset_pendant_installation'; name='MARSET_Dipping_Pendant_Assembly.zip'; url='https://www.marset.com/wp-content/uploads/lamparas/pendant-light-fixtures/dipping-light-pendant/Assembly-Instructions_Dipping_Light_-Pendant.zip'; origin='Marset'},
  @{id='marset_pendant_2d'; name='MARSET_Dipping_Pendant_2D.zip'; url='https://www.marset.com/wp-content/uploads/lamparas/suspension/dipping-light-2/2D_DIPPING-LIGHT-PENDANT.zip'; origin='Marset'},
  @{id='marset_pendant_3d_dwg'; name='MARSET_Dipping_Pendant_3D_DWG.zip'; url='https://www.marset.com/wp-content/uploads/lamparas/suspension/dipping-light-suspension/MARSET_3D_DIPPING-LIGHT_PENDANT_DWG.zip'; origin='Marset'},
  @{id='marset_pendant_3d_obj'; name='MARSET_Dipping_Pendant_3D_OBJ.zip'; url='https://www.marset.com/wp-content/uploads/lamparas/suspension/dipping-light-suspension/MARSET_3D_DIPPING-LIGHT_PENDANT_OBJ.zip'; origin='Marset'},
  @{id='marset_pendant_photometry'; name='MARSET_Dipping_Pendant_Photometry.zip'; url='https://www.marset.com/wp-content/uploads/lamparas/suspension/dipping-light-suspension/MARSET_Photometric-data_Dipping-Light-susp-13-20-30.zip'; origin='Marset'},
  @{id='marset_bim_link_check'; name='MARSET_Dipping_Light_S_BIM_Link_Check.zip'; url='https://www.marset.com/wp-content/uploads/lamparas/sobremesa/dipping-light-sobremesa/MARSET_Dipping-Light-S_Indoor-Lighting_RFA.zip'; origin='Marset; potentially table lamp only'},
  @{id='schneid_stucco_dropbox_3d'; name='SCHNEID_Stucco_Share_3D.zip'; url='https://www.dropbox.com/scl/fo/ilg9k5nqeb6od7xbihltv/AJhqNQ6n2bWNgEzoa700D-0?rlkey=ra335kifa8h4anjl5kk6j8yf5&dl=1'; origin='Schneid Studio official 3D link redirects to Dropbox'}
)

$maxFileBytes = 60MB
$maxTotalBytes = 140MB
$total = [long]0
$result = @()
foreach ($entry in $sources) {
  $dest = Join-Path $Destination $entry.name
  $tmp = $dest + '.part'
  $record = [ordered]@{id=$entry.id; manufacturer=$entry.origin; url=$entry.url; file=$dest; status='pending'; bytes=$null; sha256=$null; format=$null; archive_entries=$null; relevant_entries=$null; error=$null}
  try {
    if ([IO.File]::Exists($dest)) {
      $record.status = 'existing_file_verified'
    } else {
      $request = [Net.HttpWebRequest]::Create($entry.url)
      $request.UserAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
      $request.Timeout = 30000
      $request.ReadWriteTimeout = 30000
      $response = $request.GetResponse()
      try {
        if ($response.ContentLength -gt $maxFileBytes) {throw ('File too large: ' + $response.ContentLength)}
        if ($response.ContentLength -gt 0 -and ($total + $response.ContentLength) -gt $maxTotalBytes) {throw 'Aggregate download cap'}
        $stream = $response.GetResponseStream()
        $writer = [IO.File]::Open($tmp,[IO.FileMode]::Create,[IO.FileAccess]::Write)
        $buffer = New-Object byte[] 65536
        $count = [long]0
        try {
          while (($bytesRead = $stream.Read($buffer,0,$buffer.Length)) -gt 0) {
            $count += $bytesRead
            if ($count -gt $maxFileBytes -or ($total + $count) -gt $maxTotalBytes) {throw 'Stream size exceeded cap'}
            $writer.Write($buffer,0,$bytesRead)
          }
        } finally {
          $writer.Close()
          $stream.Close()
        }
        [IO.File]::Move($tmp,$dest)
        $total += $count
        $record.status = 'downloaded'
      } finally {
        $response.Close()
      }
    }
    $bytes = [IO.File]::ReadAllBytes($dest)
    if ($bytes.Length -ge 4) {
      if ($bytes[0] -eq 37 -and $bytes[1] -eq 80 -and $bytes[2] -eq 68 -and $bytes[3] -eq 70) {$record.format = 'PDF'}
      if ($bytes[0] -eq 80 -and $bytes[1] -eq 75) {$record.format = 'ZIP'}
    }
    if (-not $record.format) {throw 'Response not PDF/ZIP (HTML redirect or unexpected content)'}
    $record.bytes = $bytes.LongLength
    $record.sha256 = (Get-FileHash -LiteralPath $dest -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($record.format -eq 'ZIP') {
      $zip = [IO.Compression.ZipFile]::OpenRead($dest)
      try {
        $record.archive_entries = $zip.Entries.Count
        $record.relevant_entries = @($zip.Entries | Where-Object {$_.FullName -match '(?i)dipping|13|S13|\.rfa$|\.rvt$|\.ies$|\.ldt$|\.dwg$|\.obj$|\.fbx$|\.pdf$' } | Select-Object -First 60 -ExpandProperty FullName)
      } finally {
        $zip.Dispose()
      }
    }
  } catch {
    $record.status = 'failed'
    $record.error = $_.Exception.Message
    if ([IO.File]::Exists($tmp)) {[IO.File]::Delete($tmp)}
    if ([IO.File]::Exists($dest) -and -not $record.format) {[IO.File]::Delete($dest)}
  }
  $result += [pscustomobject]$record
  Write-Output ([string]$record.status + ' ' + $entry.name + ' ' + [string]$record.bytes)
}
$manifest = Join-Path $PSScriptRoot 'OEM_SOURCE_MANIFEST.json'
$result | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $manifest -Encoding UTF8
Write-Output ('Manifest ' + $manifest)
