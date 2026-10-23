# Bolla PD3106-BG - native IES binding candidate R02

**Status: SOURCE ONLY. Revit 2025 has not been launched and no RFA has been produced by this task.**

## Command for the prime agent's separate native run

```powershell
& 'D:\Games\pyRevit-Master\bin\pyrevit.exe' run 'E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\scripts\bind_bolla_bg_ies.py' --revit=2025
```

The script requires the isolated Revit 2025 pyRevit IronPython 2.7 context. It
checks original family SHA256, IES SHA256, the photometry manifest and
exactly one family type `Type 1`. It requires the existing reference to
still name a CH IES file. Any unanticipated source change causes a hold.

Source: `E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\families\Kuzco_Bolla_PD3106_BG_R2025.rfa`

Original source SHA256: `eb5cf17c25531152acc8e51ccb0ad5bd80913ae547f878d9108d059090e6f2f3`

Validated manufacturer companion: `E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\sources\photometry\PD3106-BG - Bolla.IES`

IES SHA256: `9e9f70e2eecc3b1c4130bea2f3fcb3c5a1798fb61363185348b635cd71737ce4`

Official archive: https://s3.us-west-2.amazonaws.com/catsy.870/IES-PD3106-Bolla.zip

New RFA only after successful staged SaveAs and reopen:
`E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\candidates\Kuzco_Bolla_PD3106_BG_R2025_IES_R02.rfa`

New native receipt:
`E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\qa\bolla_bg_ies_r02_native_receipt.json`

## API basis (Revit 2025)

Autodesk's API example uses:

1. `DB.Lighting.LightFamily.GetLightFamily(doc)` and
   `lightFamily.GetLightType(index).GetLightDistribution()`.
2. `DB.Lighting.PhotometricWebLightDistribution.PhotometricWebFile = <IES full path>`.
3. `lightType.SetLightDistribution(distribution)`.
4. The family type built-in `FBX_LIGHT_PHOTOMETRIC_FILE` is also read/written
   using `doc.FamilyManager.get_Parameter(...)` /
   `doc.FamilyManager.Set(param, absolute_IES_path)`. No localized label lookup.

Autodesk Revit API 2025 documentation:

- https://www.revitapidocs.com/2025/c572d26c-9344-9256-64b0-88b19b6d768d.htm
- https://www.revitapidocs.com/2025/e9f78e79-9a67-e911-3fb9-bd9a316043dc.htm
- https://help.autodesk.com/cloudhelp/2025/ENU/Revit-DocumentPresent/files/GUID-4F1C8175-0F14-4C45-AA08-CE0304A15700.htm

The Autodesk developer discussion explains why directly setting
`FBX_LIGHT_PHOTOMETRIC_FILE` alone can leave the IES cached data stale,
especially across machines:

https://forums.autodesk.com/t5/revit-api-forum/fbx-light-photometric-file-absolute-ies-path-issue/td-p/6869026

## Verification and portability

The converter holds the candidate until the source file hash, native light
distribution and family type value have all been checked. The temp family is
closed/reopened and checked for retained BG IES filename, unchanged nonemitter
geometry, unchanged materials and no additional warnings; only then it is
renamed to the requested candidate filename.

The IES is passed into the Revit API using its **absolute existing path**. Revit
may store a filename or an absolute path in the saved type, and caching is
version/context dependent. A reopened parameter referencing the correct file
does not independently prove the IES data is embedded and portable. Keep the
companion IES with the new RFA package. For use on another machine, copy the
same IES to an accessible path (Autodesk's normal Revit 2025 IES folder is
`C:\ProgramData\Autodesk\RVT 2025\IES`) and use Family Types > Photometrics
> Photometric Web File to reselect if Revit cannot resolve its reference.
Reopen the installed family in that environment and verify the rendered light
distribution against the official file. No IES files are copied into
ProgramData by this converter.

**No geometry/material or worker-3 finish changes are included.** This R02
starts only from the independently hashed OEM source family and is a separate
photometric branch. A future combined finish+IES build must be freshly audited
and re-hashed; neither candidate implicitly includes the other one's edits.
