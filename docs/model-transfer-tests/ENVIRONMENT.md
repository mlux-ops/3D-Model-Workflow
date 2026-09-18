# Environment and execution

## Local facts observed during setup

- Repository: `C:\Users\found\OneDrive\Documents\ChatGPT\3D Model Workflow`
- Revit executable exists: `C:\Program Files\Autodesk\Revit 2025\Revit.exe`
- pyRevit resolves to `C:\Program Files\pyRevit-Master\bin\pyrevit.exe`
- `python` resolves to `C:\Python314\python.exe`; dependencies for that interpreter were not tested during kit setup.
- Historical Mila builds ran in Revit 2025 through pyRevit. Source requires the Revit-hosted `__revit__.Application` and .NET Revit API; ordinary CPython cannot execute that builder.
- Native material rendering is historically blocked by V-Ray license error -98. Current license availability has not been tested.

These are machine observations, not a portable installation guarantee. Before a run, check the candidate agent can read files, view reference images, launch the application and observe results. Record client/tool restrictions separately from modeling defects.

## Preflight

1. Read root `AGENTS.md`, relevant `PROJECT_MEMORY.md` entries, and `WORKFLOW.md`.
2. Confirm Revit **2025** is available: generating in a newer release does not prove 2025 compatibility. Verify both template files exist under `C:\ProgramData\Autodesk\RVT 2025\Family Templates\English-Imperial`: `Generic Model face based.rft` and `Generic Model.rft`.
3. Confirm the actual Python interpreter used for map generation has `numpy` and `PIL`. Avoid assuming `scipy` is installed. Revit-hosted Python and CPython are separate environments.
4. Check native UI access for Material Browser library creation/import, and a licensed renderer for the material render gate. If unavailable, mark those gates blocked; continue independent map and project checks.
5. Create the unique run folder. Audit every write/copy path in adapted scripts. Preserve source builders and existing output directories.
6. Capture start time, exact model/client settings and assistance policy in the scorecard. Do not record credentials.

## Native family execution recipe

After copying/adapting the builder and checking its write paths, run from PowerShell with an **absolute** script path, for example:

```powershell
$trialBuilder = Join-Path (Get-Location) 'output\model-transfer-tests\candidate-20260918-01\pendant\build_pendant.py'
if (-not (Test-Path -LiteralPath $trialBuilder)) { throw 'Adapted trial builder is missing' }
& 'C:\Program Files\pyRevit-Master\bin\pyrevit.exe' run $trialBuilder --revit=2025
```

Use the actual run ID and repository working directory. First confirm syntax against the installed CLI if it differs. A completed process or exit code alone is insufficient: inspect the new validation record for errors, check fresh timestamps, reopen the saved artifact, and inspect geometry. Some historical builders catch exceptions and write JSON without returning a nonzero process status.

Do not kill unrelated Revit sessions or modify an active user project. Use disposable documents. If startup stalls, capture the exact process/action and log it; only clean up processes launched for this run. Request only permissions needed by the current client, and record environmental blocks honestly.

## Mandatory adaptation hazards

- `scripts/build_mila.py`: hard-coded ROOT, OUT, RFA and template paths; `OverwriteExistingFile=True`. Redirect OUT/RFA and nested family names before execution. Preparation scripts may also contain fixed destinations.
- `scripts/rebuild_adella_precision.py`: derives the repo root from its own location, writes `output/adella_highres_review`, **and copies generated maps back into `output/adella/textures`**. Copying this script elsewhere without adapting root/path logic is unsafe. Remove the write-back loop in the trial version.
- `scripts/build_adella_revit.py` and `scripts/build_adella_vrmat.py`: fixed Adella output destinations. Redirect all maps, previews, native outputs and validation files.
- The Revit material builder creates an RVT containing the material; it does **not** create an ADSKLIB. Historical library creation used Revit's Material Browser. Renaming an RVT/ZIP to ADSKLIB is not a valid substitute.
- Native libraries may retain absolute bitmap paths. Verify actual asset paths, and test explicit repathing after extracting a package to another directory.

## Packaging and delivery

Keep native files, companion textures, references, adapted scripts, validation logs and setup notes together. ZIP integrity is a packaging check, not a native application check.

Final model packages belong under Google Drive `3D Model Workflow` (folder ID `1Xsd3Y96SOi00cWNaxqYeqlp4tNe3Z8CD`) / `3D Models`; materials belong under `Material Packages`. Resolve child IDs from the parent, check for identical existing packages, upload under a clearly identified test-run name, and verify remote metadata/link. Standing authorization is in root AGENTS.md. If delivery tools are unavailable, record delivery pending independently of native build results.
