# Alora Mood Cassia SF549315AGOP — Revit 2025 family

**Status 2026-09-23: RFA NOT YET BUILT.** The authoring session was a Linux cloud container (no Revit, pyRevit or .NET). This folder is a complete, pre-tested native build kit; the RFA, native measurements and exports are produced by one command on the Windows workstation. Nothing below claims a native result.

## Run (Windows workstation, Revit 2025 + pyRevit)

```powershell
powershell -ExecutionPolicy Bypass -File "C:\Users\mlux\Documents\GitHub\3D-Model-Workflow\output\cassia\run_cassia.ps1"
```

- Exit 0 technical pass · 1 technical fail · 2 blocked (prerequisite missing). The exit code comes from `source/verify_cassia.py`, never from `pyrevit run`.
- Produces `Alora_Cassia_SF549315AGOP_Aged_Gold_Opal_R2025.rfa`, `validation.json`, `evidence/*.png` (5 family + 3 hosted views).
- Cloud-session branch: `claude/light-fixture-rfa-yw6npk` — merge or check it out first (`git merge --ff-only origin/claude/light-fixture-rfa-yw6npk`).

## Family

| Item | Value |
|---|---|
| Category / template | Lighting Fixtures / Generic Model face based (hosts on ceiling undersides; local +Z hangs down) |
| Type | `SF549315AGOP - Aged Gold - Opal Matte Glass` |
| Material parameters (type) | `Metal Finish` (Cassia - Aged Gold) · `Glass Finish` (Cassia - Opal Matte Glass) · `Lamp Finish` (Cassia - Candle Lamp) |
| Subcategories | Canopy and Hub · Arms and Fitters · Glass Globes · Lamps and Sockets |
| Informational parameters | Overall Diameter 17.75 · Overall Height 7.625 · Canopy Diameter 4.75 · Canopy Height 0.875 · Globe Diameter 6 (formula-locked; geometry is fixed) |
| Identity | Manufacturer, Model, Description, URL (spec sheet), Model Accuracy Notes |
| Solids | 19 revolved FreeFormElements: canopy, 2 screws, hub, 3 × (arm, stepped fitter, opal globe, socket sleeve, candle lamp) |
| Excluded by convention | MEP connectors, light source/IES, electrical data |

Geometry sources and every inferred value: [INFERENCES.md](INFERENCES.md). Shared constants: `source/cassia_geometry.py`.

## Native gates (all must pass; `validation.json` → `gates`)

| Gate | Measured how |
|---|---|
| `fresh_rfa_reopen_category` | save → close → reopen; category Lighting Fixtures |
| `all_parts_bound` | 19 parts resolve by id, keep subcategory and material-parameter binding |
| `measured_dimensions` | 37 `Solid.IntersectWithCurve` rays: canopy, hub, 3 × globe height/diameters/wall/centre radius/spread, arm Ø, fitter Ø, glass opening |
| `measured_arm_angles` | slope between two vertical arm sections, 30° ± 0.25° |
| `fitter_covers_glass_opening` | measured flange radius > measured glass opening radius |
| `internal_clearances` | 27 rays: glass inner surface ≥ 0.05 in outside lamp and sleeve |
| `saved_dimension_parameters` | reopened type values |
| `native_ceiling_hosting` | disposable project, native floor underside, host id, local Z = (0,0,−1), nothing above the face |
| `hosted_drop_and_spread` | rays through the hosted instance: drop 7.625, spread radius 8.875 (± 0.02) |
| `material_substitution` | each parameter swapped: 13 metal / 3 glass / 3 lamp solids carry the substitute; restored |
| `zero_warnings`, `visual_exports_present` | family + project warnings empty; ≥ 5 + 3 PNGs on disk |

`visual_verdict` stays `PENDING REVIEWER`; no script awards the visual gate.

## Pre-native evidence (this session)

| Check | Result |
|---|---|
| `source/preview_geometry.py` — offline mesh dry-run of the same rays | 37/37 rays, 3/3 angles, 27/27 clearances pass (min clearance 0.55 in); 0 profile problems |
| Model edges over supplied drawing | [elevation](preview/overlay_elevation_on_drawing.png) · [plan](preview/overlay_plan_on_drawing.png) — coincide except globe centres ≈1.5 px inward (published 5.875 vs drawn 5.945) |
| Shaded model vs supplied render | [compare_render_view.png](preview/compare_render_view.png) · [views_contact_sheet.png](preview/views_contact_sheet.png) — estimated camera, not solved |
| `source/mock_revit_dryrun.py` — real builder executed against a geometric mock Revit API | complete, all gates true, verifier exit 0; verifier rejects tampered reports; mutations (swapped revolve axes, skipped material restore) are caught |
| `run_cassia.ps1` | PowerShell 7.4 parser: 0 errors; preflight on Linux → BLOCKED exit 2 as designed |

These establish geometry intent and script logic only. API binding, appearance behaviour, warnings and file validity are established only by the native run.

## After a technical pass

1. Review `evidence/*.png` against `references/cassia/` (silhouette, arm angle, fitter, globe overlap, finish). Write `REVIEW.md` including the line `Visual verdict: ACCEPTED` (or record the corrections needed).
2. Package: `& "C:\Program Files\pyRevit-Master\bin\cengines\CPY3123\python.exe" output\cassia\source\package_cassia.py` → allow-listed ZIP, `testzip()`, SHA-256 in `package_manifest.json`.
3. Deliver (AGENTS.md): dedup-search Drive `3D Model Workflow/3D Models` (`1WoLM7G88CPMq-7-w_dloZiqDmk7hjd7W`), copy the ZIP to `F:\My Drive\3D Model Workflow\3D Models`, confirm file id + `fileSize` through the Drive API, record in `PROJECT_MEMORY.md`.

## Known risks for the first native run

- API calls not used by earlier builds in this repo: `FamilyManager.GetAssociatedFamilyParameter` (guarded; failure is recorded, not fatal), `Application.ShortCurveTolerance` (guarded).
- `generic_is_metal = True` on Aged Gold (Realistic view untested here; flip in `MATERIALS` if it reads wrong).
- Autodesk sign-in / device-limit screens stall batch startup (E018, Kamden) — resolve in the spawned Revit window.
- Brushed grain is not modelled (texture-free appearances, fixture convention).
