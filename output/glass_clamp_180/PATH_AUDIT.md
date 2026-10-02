# Write-path audit — output/glass_clamp_180 (2026-09-30)

`grep -n "SaveAs(\|ExportImage\|open(\|FilePath\|makedirs"` over `source/*.py`.

| File:line | Write | Guard |
|---|---|---|
| build_clamp.py `checkpoint` | `validation.json`, `logs/validation-<stamp>.json` | `out_path()` (raises outside run dir) |
| build_clamp.py `export_images` | `evidence/Clamp - *.png`, `evidence/Clamp_Project - *.png` | `out_path('evidence', prefix)` |
| build_clamp.py `build` | `SHB_Glass Clamp 180 Square.rfa` | `out_path(S.RFA_NAME)` |
| package_clamp.py | ZIP, `package_manifest.json` | local `out_path()` |
| preview_offline.py | `preview/analytic_preview.png` | fixed path under run dir |
| selftest_offline.py | temp dir from `tempfile.mkdtemp`, removed in `finally` | outside the repo by design |
| verify_clamp.py | none (reads only) | — |

Revit documents opened: new family from `Generic Model.rft`, the RFA it saved, a new blank project. No existing deliverable, `scripts/`, `docs/` or open model is written.

## Tool and checkout discovery (2026-10-02)

No fixed user, drive or install path remains in the kit (`grep -n 'C:\\\\' source/*.py run_clamp.ps1` is empty apart from documentation). `run_clamp.ps1` discovers pyRevit, Revit 2025, the template and Python 3 on the PC it runs on and prints what it found; `build_clamp.py` walks up from its own location (or `CLAMP_REPO_ROOT`) to the checkout and asks Revit for `FamilyTemplatePath`. Offline tests: `selftest_offline.py`, plus the runner against stub tools in a temporary copy (blocked, check-only, no-report, pass, verify-only, tampered).
