$ErrorActionPreference='Stop'
$env:PATH='C:/Program Files/Chaos/V-Ray/V-Ray for Revit/libraries/vrayappsdk/bin;'+$env:PATH
Add-Type -Path 'C:/Program Files/Chaos/V-Ray/V-Ray for Revit/VRaySDK.Net.dll'
[VRay.VRMat]::PluginLibraryPath='C:/Program Files/Chaos/V-Ray/V-Ray for Revit/libraries/vrayappsdk/bin/plugins/vray_MtlVRmat.dll'
$samplePath='C:/Users/found/OneDrive/Documents/Chaos Cosmos/Packages/3D_Models/Accessories/Rug_002_9785c537/9785c537_3dh_Rug_002.vrmat'
$tilePath='C:/Users/found/OneDrive/Documents/ChatGPT/3D Model Workflow/output/adella/MSI_Adella_Viso_White.vrmat'
foreach ($candidate in @($samplePath,$tilePath)) {
  Write-Output $candidate
  $candidateMtl=[VRay.VRMat]::new($candidate)
  $names=@($candidateMtl.GetMaterialList())
  Write-Output ($names | ConvertTo-Json)
}
