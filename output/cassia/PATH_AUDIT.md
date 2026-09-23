# Cassia run — write-path audit

Rule (skill rule 10): new work writes only inside `output/cassia/`; `scripts/`, `docs/` and every existing deliverable are read-only.

| Script | Writes | Guard |
|---|---|---|
| `source/build_cassia.py` | `validation.json`, `logs/validation-<start>.json`, `Alora_Cassia_SF549315AGOP_Aged_Gold_Opal_R2025.rfa`, `evidence/Cassia - 3D View - *.png`, `evidence/Cassia_Hosted - 3D View - *.png` | every path via `out_path()`, which raises outside `output/cassia` |
| `source/preview_geometry.py` | `preview/*.png`, `preview/offline_checks.json` | `out_path()` |
| `source/package_cassia.py` | `Alora_Cassia_SF549315AGOP_Aged_Gold_Opal_R2025_Package.zip`, `package_manifest.json` | `out_path()` |
| `source/verify_cassia.py` | nothing | read-only (also lists Cassia files found in the other known checkout) |
| `pyrevit/Cassia.extension/.../BuildCassia.pushbutton/script.py` | nothing itself; runs `build_cassia.py` in the open Revit session | builder path resolved from the button's own location, so writes land in that checkout's `output/cassia` |
| `source/mock_revit_dryrun.py` | a fresh system temp directory only | refuses a temp path inside the repository |
| `run_cassia.ps1` | `logs/run-start.txt`, `logs/validation-previous-*.json`; sets `CASSIA_REPO_ROOT` for the builder | `$PSScriptRoot`-relative |

Revit-side: only documents the builder creates (new family, disposable project) are modified; both are closed without saving except the RFA itself. No open user model is touched; `pyrevit run` starts its own Revit session.

Audit command: `grep -n "open(\|SaveAs\|FilePath\|makedirs" output/cassia/source/*.py` — every hit resolves through `out_path()` or is a read.
