# Path audit: output/miele_km3054_1

No user, drive or OneDrive path is hard-coded. The repo root is resolved at run time:
`KM3054_REPO_ROOT` (set by `run_km3054.ps1`), then a walk up from the builder's own
`__file__`; a root must contain `AGENTS.md` and `output/miele_km3054_1/source/km3054_geometry.py`.
The run that produced the RFA recorded `repo_root_source: KM3054_REPO_ROOT` and
`repo_root: C:\Users\found\Documents\3\3D-Model-Workflow` in `validation.json`.

Fixed machine paths (checked with `Test-Path` before anything runs; exit 2 BLOCKED if missing):
`C:\Program Files\pyRevit-Master\bin\pyrevit.exe`, `...\bin\cengines\CPY3123\python.exe`,
`C:\Program Files\Autodesk\Revit 2025\Revit.exe`,
`C:\ProgramData\Autodesk\RVT 2025\Family Templates\English-Imperial\Generic Model face based.rft`.

## Write call sites

| File | Line | Write | Guard |
|---|---|---|---|
| source/build_km3054.py | 128 | `validation.json` | `out_path()` (raises if outside the run dir) |
| source/build_km3054.py | 131 | `logs/validation-<start>.json` (per attempt) | `out_path()` |
| source/build_km3054.py | 346-352 | `ExportImage` to `evidence/<prefix>*` | `out_path('evidence', prefix)` |
| source/build_km3054.py | 482-483 | `SaveAs` of the RFA | `out_path(RFA_NAME)` |
| source/build_km3054.py | 120 | `os.makedirs` for parents | inside `out_path()` |
| source/package_km3054.py | 76, 92 | package ZIP and `package_manifest.json` | its own `out_path()` (run dir only) |
| source/compare_km3054.py | 45, 55 | comparison sheets in `evidence/` | fixed join under the run dir |
| run_km3054.ps1 | - | `logs/run-start.txt`, `logs/pyrevit-<stamp>.log`, `logs/validation-previous-<stamp>.json`, moves earlier RFAs to `logs/attempt-rfas/` | `$PSScriptRoot`-relative only |

Reads only: `verify_km3054.py` (validation.json, run-start.txt, exports), the pushbutton
(reads the builder next to itself), `compare_km3054.py` (references/miele_km3054_1/).
Revit documents: the builder creates a family document and a project document, saves only
the RFA, and closes both without saving the project. It never opens or modifies another model.
