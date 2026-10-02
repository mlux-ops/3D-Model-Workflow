# SHB_Glass Clamp 180 Square — Revit 2025 family (CRL SGC180BBRZ stand-in)

**Status 2026-09-30: RFA NOT YET BUILT.** Authored in a Linux cloud container (no Revit, pyRevit or .NET). This folder is a native build kit; the RFA, measurements and exports come from one command on the Windows workstation. Nothing below claims a native result.

Project: 651 W Belmont (25-012), primary bath enclosure. Task sheet: [TASK_Glass_Clamp_180_Family_Build_1.md](TASK_Glass_Clamp_180_Family_Build_1.md). Every value and deviation: [INFERENCES.md](INFERENCES.md).

## Run (any Windows PC with Revit 2025 + pyRevit)

The kit assumes no user name, drive, OneDrive folder or install path. `run_clamp.ps1` finds pyRevit, Revit 2025, `Generic Model.rft` and a Python 3 on the PC it runs on (override with `CLAMP_PYREVIT`, `CLAMP_REVIT`, `CLAMP_TEMPLATE`, `CLAMP_PYTHON`); the builder finds its checkout by walking up from its own location and the template through Revit's `FamilyTemplatePath`.

**Fresh or unknown PC: one block** (clones to `%USERPROFILE%\GitHub\3D-Model-Workflow`, never touches another checkout; sign in to GitHub if asked):

```powershell
& {
  $branch = 'claude/new-session-urnwm3'
  $url    = 'https://github.com/mlux-ops/3D-Model-Workflow.git'
  $dest   = Join-Path $env:USERPROFILE 'GitHub/3D-Model-Workflow'
  if (-not (Get-Command git -ErrorAction SilentlyContinue)) { Write-Host 'git is not installed (https://git-scm.com).'; return }
  $env:GIT_LFS_SKIP_SMUDGE = '1'      # skip the large LFS images; the build does not need them
  if (Test-Path (Join-Path $dest '.git')) {
    git -C $dest fetch origin $branch
    git -C $dest checkout $branch
    git -C $dest pull --ff-only origin $branch
  } elseif (Test-Path $dest) { Write-Host "$dest exists and is not a git repo - stopping."; return }
  else {
    New-Item -ItemType Directory -Force (Split-Path $dest) | Out-Null
    git clone --depth 1 --single-branch --branch $branch $url $dest
  }
  powershell -ExecutionPolicy Bypass -File (Join-Path $dest 'output/glass_clamp_180/run_clamp.ps1')
}
```

**Existing checkout:**

```powershell
cd "<your checkout>"
git fetch origin
git merge origin/claude/new-session-urnwm3
powershell -ExecutionPolicy Bypass -File ".\output\glass_clamp_180\run_clamp.ps1"
```

| Switch | Does |
|---|---|
| (none) | check this PC, build, verify |
| `-CheckOnly` | print what was found on this PC and stop (exit 0 found, 2 missing) |
| `-VerifyOnly` | verify an existing `validation.json` (after the in-Revit button); builds nothing |

- Output beside the script: `SHB_Glass Clamp 180 Square.rfa`, `SHB_Glass Clamp 180 Square.txt` (type catalog), `validation.json`, `evidence\*.png`, `logs\run-<stamp>.txt`, `logs\RUN_SUMMARY.txt` (also copied to the clipboard for pasting into the chat).
- Exit 0 technical pass, 1 technical fail, 2 blocked. The code comes from `source/verify_clamp.py`, never from `pyrevit run`.
- **"TECHNICAL FAIL" with `NO NEW validation.json`** means Revit never ran the builder (`pyrevit run` could not start it); it is not a geometry failure. Use the in-Revit button below. If the builder could not even locate the checkout it leaves `%TEMP%\clamp_builder_startup_error.txt`.

If `pyrevit run` does not start Revit:

```powershell
pyrevit extensions paths add "<checkout>\output\glass_clamp_180\pyrevit"
```

Revit -> pyRevit -> **Reload** -> **SHB** tab -> **Build Clamp 180**, then `run_clamp.ps1 -VerifyOnly`.

## Family

| Item | Value |
|---|---|
| Template / category | `Generic Model.rft` (imperial, non-hosted) / Generic Models |
| Settings | Always Vertical on · Work Plane-Based off · origin = joint centre, mid-height · +Y = room side |
| Types | `1-2 Glass` (default, Belmont IFC Note 45) · `3-8 Glass`; catalog `SHB_Glass Clamp 180 Square.txt` |
| Solids | 4 extrusions: front plate, back plate, 2 screw heads (back) |
| Subcategories | `Clamp Plate` · `Clamp Cap` |
| Material | type parameter `Clamp_Material` = `Vibrant Brushed Bronze` (finish-DB name), shading RGB 110/86/62, no surface pattern |
| Visibility | Coarse = plates only; Medium/Fine = plates + heads; all view orientations on |
| Identity | Manufacturer `CRL` · Model `SGC180BBRZ` · Description `Square 180 Deg Glass-to-Glass Clamp` · Type Comments `SGC180BBRZ - Brushed Bronze` · URL · Model Accuracy Notes |

### Parameters (all type)

| Name | Default | Formula | Source |
|---|---|---|---|
| Glass_Thickness | 1/2" | — | PROJECT |
| Plate_Thickness | 1/8" | — | ASSUMED |
| Clamp_Width | 5" | — | CRL |
| Clamp_Height | 2" | — | CRL |
| Joint_Gap | 1/16" | — | CRL template |
| Hole_Edge_Distance | 1-19/32" | — | CRL template |
| Cap_Diameter | 1/2" | — | ASSUMED |
| Cap_Height | 1/16" | — | ASSUMED |
| Cap_Spacing | 3-1/4" | `2 * Hole_Edge_Distance + Joint_Gap` | DERIVED |
| Cap_Offset | 1-5/8" | `Cap_Spacing / 2` | helper |
| Cap_Elevation | 1" | `Clamp_Height / 2` | helper |
| Clamp_Material | Vibrant Brushed Bronze | — | PROJECT |

### Constraints

| Plane | Driven by |
|---|---|
| Joint CL (X=0), Center (Front/Back) (Y=0), Glass Mid (Z=0, locked to Ref. Level) | template origin |
| Glass Face Front / Back | EQ about Y=0 + dimension labelled `Glass_Thickness` |
| Plate Outer Front / Back | dimension from glass face labelled `Plate_Thickness` |
| Clamp Left / Right | EQ about Joint CL + `Clamp_Width` |
| Clamp Top / Bottom | EQ about Glass Mid + `Clamp_Height` |

Plates: sketched on the glass-face planes, depth `Plate_Thickness`, four side faces aligned and locked. Screw heads: sketched on Plate Outer Back, depth `Cap_Height`; centre and diameter dimensioned inside each sketch (`Cap_Offset`, `Cap_Elevation`, `Cap_Diameter`).

## Native gates (`validation.json` → `gates`; re-derived by `verify_clamp.py`)

| Gate | Measured how |
|---|---|
| `fresh_rfa_reopen_category`, `always_vertical_on_work_plane_off` | save → close → reopen; family parameters |
| `types_present`, `type_parameters` | reopened types, formulas, every value per type, identity text |
| `reference_planes_named`, `labelled_dimensions`, `plate_sides_locked`, `screw_heads_sketch_constrained` | plane names; dimension labels + EQ count; 8 locked face alignments; sketch-edit result |
| `parts_separate_bound` | 4 extrusions, 1 solid each, subcategory, `Clamp_Material` binding, face materials, visibility flags |
| `default_geometry_measured` | 12 `Solid.IntersectWithCurve` rays: plate thickness/width/height, head X/Z/Y extents |
| `flex_all_steps`, `flex_default_restored` | Glass 3/8↔1/2, Width 4↔6, Head Ø 7/16↔5/8, Plate 3/16↔1/8: commit captured, no errors, all 12 rays re-measured each step |
| `project_load_place` | disposable project: both types load, rays through the placed instance for 1/2 and 3/8 types, vertical |
| `project_detail_levels` | instance solids: Coarse 2, Medium 4, Fine 4 |
| `project_material_substitution` | `Clamp_Material` swapped: 4/4 solids carry it; restored |
| `zero_warnings`, `purged_compact_under_500kb`, `visual_exports_present` | warnings + captured failures empty; purge ran, compact save, < 500 KB; ≥ 4 family + 1 project PNG |

`visual_verdict` stays `PENDING REVIEWER`.

## Pre-native evidence (this session)

| Check | Result |
|---|---|
| `source/selftest_offline.py` | analytic clamp through the same 12 part rays, 8 flex steps, 3 project rays → verifier PASS; 16 tampered reports all rejected |
| `source/preview_offline.py` → [preview/analytic_preview.png](preview/analytic_preview.png) | room face plain, 2 heads at ±1-5/8", plan section with 1/16" joint |
| `run_clamp.ps1` | PowerShell 7.4.6 parser 0 errors; preflight on Linux → BLOCKED exit 2 |
| `build_clamp.py` | CPython `py_compile` clean; Py2-safe syntax. **Not executed against Revit.** |

Untested API paths on first run (no precedent in this repo): `NewReferencePlane` + `Flip`, `NewDimension` with `FamilyLabel` / `AreSegmentsEqual`, `NewAlignment` locks, `SketchEditScope` with `CurveElement.CenterPointReference` and `NewDiameterDimension`, `FamilyElementVisibility`, `Document.GetUnusedElements`, `SaveAsOptions.Compact`. Each is recorded in `validation.json`; a failure there fails its gate, not silently.

## After a technical pass

1. Review `evidence\*.png` against `references\crl_sgc180\` (Back Oblique shows the heads; Coarse view shows plates only).
2. Write `REVIEW.md` containing `Visual verdict: ACCEPTED`, then `source\package_clamp.py`.
3. Upload the ZIP to Drive **3D Model Workflow › 3D Models**; verify `fileSize` through the Drive API.

## Load and place (Belmont model — manual, not in this kit)

1. Load the RFA; choose **`1-2 Glass`** (all Belmont shower glass 1/2" min, IFC A0.2 Note 45).
2. If the project has `Vibrant Brushed Bronze`, it is used unchanged; if not, the family's copy comes in.
3. Place on each panel-to-panel joint centreline, plates parallel to the glass; heads on the shower side.
4. Heights (ASSUMED, verify with the hardware layout): 6" from top, mid-height, 6" from bottom.
5. Type Comments already read `SGC180BBRZ - Brushed Bronze`; add to the hardware schedule if one exists.

## Open questions

- Plate thickness (CRL does not print it; confirm with CRL tech sales 1-800-421-6144 or a sample).
- Screw-head size and whether it sits flush.
- Number of panels / 180° joints in the primary enclosure; which unit (Duplex Down, Penthouse, Simplex).
