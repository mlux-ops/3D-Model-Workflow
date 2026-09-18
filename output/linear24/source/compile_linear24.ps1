$ErrorActionPreference = 'Stop'
$taskRoot = 'C:\Users\mlux\Documents\GitHub\3D-Model-Workflow'
$refs = @(Get-ChildItem 'C:\Program Files\dotnet\shared\Microsoft.NETCore.App\8.0.21' -Filter '*.dll' | ForEach-Object { try { [void][System.Reflection.AssemblyName]::GetAssemblyName($_.FullName); $_.FullName } catch {} })
$refs += 'C:\Program Files\Autodesk\Revit 2025\RevitAPI.dll'
$refs += 'C:\Program Files\Autodesk\Revit 2025\RevitAPIUI.dll'
$tree = [Microsoft.CodeAnalysis.CSharp.CSharpSyntaxTree]::ParseText([string](Get-Content "$taskRoot\scripts\Linear24Builder.cs" -Raw))
$metadata = [System.Collections.Generic.List[Microsoft.CodeAnalysis.MetadataReference]]::new()
foreach ($ref in $refs) { $metadata.Add([Microsoft.CodeAnalysis.MetadataReference]::CreateFromFile($ref)) }
$options = [Microsoft.CodeAnalysis.CSharp.CSharpCompilationOptions]::new([Microsoft.CodeAnalysis.OutputKind]::DynamicallyLinkedLibrary)
$compilation = [Microsoft.CodeAnalysis.CSharp.CSharpCompilation]::Create('Linear24Builder', [Microsoft.CodeAnalysis.SyntaxTree[]]@($tree), $metadata, $options)
$stream = [System.IO.File]::Create("$taskRoot\tmp\Linear24Builder.dll")
try { $result = $compilation.Emit($stream); $result.Diagnostics | ForEach-Object { $_.ToString() }; if(-not $result.Success){throw 'Compilation failed'} } finally {$stream.Dispose()}

