$ErrorActionPreference='Stop'
$runtimeRoot='C:\Program Files\dotnet\shared\Microsoft.NETCore.App\8.0.25'
$references=@(Get-ChildItem -LiteralPath $runtimeRoot -Filter '*.dll' | ForEach-Object {
    try { [void][Reflection.AssemblyName]::GetAssemblyName($_.FullName); $_.FullName } catch {}
})
$references += 'C:\Program Files\Autodesk\Revit 2025\RevitAPI.dll'
$references += 'C:\Program Files\Autodesk\Revit 2025\RevitAPIUI.dll'
$references += 'C:\ProgramData\CodexNativeRevit\2025\3f41f299be45\CodexNativeRevit.dll'
$tree=[Microsoft.CodeAnalysis.CSharp.CSharpSyntaxTree]::ParseText([IO.File]::ReadAllText((Join-Path $PSScriptRoot 'BedroomTrimInspect.cs')))
$metadata=[Collections.Generic.List[Microsoft.CodeAnalysis.MetadataReference]]::new()
foreach($reference in $references){$metadata.Add([Microsoft.CodeAnalysis.MetadataReference]::CreateFromFile($reference))}
$options=[Microsoft.CodeAnalysis.CSharp.CSharpCompilationOptions]::new([Microsoft.CodeAnalysis.OutputKind]::DynamicallyLinkedLibrary)
$compilation=[Microsoft.CodeAnalysis.CSharp.CSharpCompilation]::Create('BelmontBedroomTrimInspect',[Microsoft.CodeAnalysis.SyntaxTree[]]@($tree),$metadata,$options)
$output=Join-Path $PSScriptRoot 'BelmontBedroomTrimInspect.dll'
$stream=[IO.File]::Create($output)
try {
    $result=$compilation.Emit($stream)
    $result.Diagnostics | ForEach-Object {$_.ToString()}
    if(-not $result.Success){throw 'Compilation failed'}
} finally {$stream.Dispose()}
Write-Output "Compiled $output"
