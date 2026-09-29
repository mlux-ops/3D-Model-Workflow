# SHB_Glass Clamp 180 Square — Revit 2025 family build kit

Task: `Glass_Clamp_180_Family_Build.md` (supplied 2026-09-29). Stand-in for CRL SGC180BBRZ, Brushed Bronze, square 180° glass-to-glass clamp, 651 W Belmont (25-012) primary bath.

| Item | Status |
|---|---|
| RFA `SHB_Glass Clamp 180 Square.rfa` | **NOT BUILT — BLOCKED, not failed.** Built by the script below on the Windows workstation; this session had no Revit. |
| Type catalog `SHB_Glass Clamp 180 Square.txt` | written (this folder); the builder rewrites the identical bytes |
| Builder, verifier, runner, in-Revit button | written; mock dry-run PASS in 4 scenarios; PowerShell parse 0 errors; no Revit-API claim |
| Native run, visual review, Belmont placement, FBX export, Drive upload | **NOT DONE** (see Limitations) |

## Run (one command, on the workstation)

```powershell
git fetch origin; git checkout claude/light-fixture-rfa-yw6npk; git pull
powershell -ExecutionPolicy Bypass -File "<checkout>\output\glass_clamp_180\run_glass_clamp.ps1"
```

Checkouts seen on this machine: `C:\Users\found\OneDrive\Documents\ChatGPT\3DModelWorkflow` (live, 2026-09-25 native run) and `C:\Users\mlux\Documents\GitHub\3D-Model-Workflow`. The runner writes into the checkout it is run from and prints the RFA path first and last.

| Output (all in `output\glass_clamp_180\`) | Meaning |
|---|---|
| `SHB_Glass Clamp 180 Square.rfa` | the family (a `.0001.rfa` beside it is Revit's backup of the previous save; not a deliverable) |
| `SHB_Glass Clamp 180 Square.txt` | type catalog, one row per glass thickness |
| `validation.json` | every measurement and the 29 gates (`logs\` keeps one copy per attempt) |
| `exports\*.png` | Realistic-style views of the placed clamp: front, plan, side, iso — for the human visual review |

Read the **verifier** output (`verify_glass_clamp.py`, exit code = result), not pyRevit's exit code. `PASS` lines are re-derived from the raw measurements; `WARN` lines are soft gates or refused non-essential steps (`family.errors` in `validation.json` names each one and Revit's message); the builder's own flags must agree. `validation.json` also holds `api_probe` (the Revit overloads and property names actually present) and `family.alignments` / `family.sketch_plane_modes` (which strategy was used).

If pyRevit prints nothing or no `validation.json` appears, use the button route instead: register `output\glass_clamp_180\pyrevit` as a pyRevit extension folder, open Revit, press **Build Glass Clamp**, then run `source\verify_glass_clamp.py`.

## What the builder does

Creates the family from `Generic Model.rft`, then flexes, purges, saves compact, reopens, loads into a disposable project, places both types and measures the instances. Writes only under `output\glass_clamp_180\`; never opens the user's Revit models or the Belmont model.

| Task file requirement | How it is met | Gate |
|---|---|---|
| Generic Model, non-hosted; Always vertical ON; Work Plane-Based OFF | template category; both flags set and read back | G01, G02 (soft), G03 |
| 6 named reference planes, dimension-labelled | `Joint CL` (the template's X=0 plane, renamed), `Glass Mid` (pinned), `Glass Face Front/Back`, `Plate Outer Front/Back`; positions driven by labelled dimensions (EQ + overall), no plane formulas | G04 |
| Type parameters + `Cap_Spacing = Clamp_Width - 2 in` | as listed; Manufacturer/Model/Description/Type Comments use Revit's built-in identity parameters | G05–G08 |
| Front/back plates, 4 caps, separate solids | 2 extrusions + 4 revolves (see decision 1) | G09, G10 |
| Subcategories `Clamp Plate`, `Clamp Cap` | assigned per form | G11 |
| Material bound to `Clamp_Material` on every solid; `Brushed Bronze` 110/86/62, roughness 0.35, metallic 1.0 | material looked up, else created; Generic appearance (glossiness 0.65, metal on) | G12, G13, G29 (soft) |
| Coarse = plates only; Medium/Fine = plates and caps | `FamilyElementVisibility` per form | G14, G25 (soft) |
| Flex Glass_Thickness 3/8↔1/2 and Clamp_Width 4↔6 | measured solids and plane positions after each step, then rolled back | G15, G16 |
| Purge unused, compact save, under 500 KB | `GetUnusedElements` (material kept), `SaveAsOptions.Compact`, size measured | G19, G20 |
| Type catalog | `,Glass_Thickness##length##inches` rows `3-8 Glass,0.375` and `1-2 Glass,0.5` | G21 |
| FBX-clean | 6 solids, one material source, no nested families/imports, safe material name | G27 |

Extra measured checks: reopen from disk (G22), both types placed in a project (G23), material substitution reaches every face (G24), no warnings (G18, G26), informational flex of Clamp_Height / Cap_Diameter / Cap_Height / Plate_Thickness (G17, soft).

## Decisions and deviations (mine, all disclosed)

1. **Caps are 360° revolves, not extruded circles.** Identical cylinder and the same solid count. Every profile edge of a revolve is a straight line that can be locked to a reference plane through the API (the method that built `scripts/add_gola_cutting.py`); an extruded circle's centre and diameter cannot be. The cap's sketch plane is bound to `Cap Center Left/Right`, so it follows `Cap_Spacing`. `SketchPlane.Create(Document, Reference)` has no precedent in this repo: if Revit refuses it the builder falls back to a fixed plane, records that in `family.sketch_plane_modes`, and G16 fails (caps would not follow Clamp_Width).
2. **Five helper formula parameters** are added (`Cap_Radius`, `Glass_Face_Front_Y`, `Plate_Outer_Front_Y`, `Glass_Face_Back_Y`, `Plate_Outer_Back_Y`). Extrusion START/END offsets can only be tied to parameters, while planes are positioned by dimension labels only (task rule), so the plates take their Y extents from these formulas and the gate checks the planes and plates coincide.
3. **Task conflict, resolved:** the back-plate step says "mirror about Glass Mid-plane Y=0", but `Glass Mid` is defined as the horizontal Z=0 plane. Read as the Y=0 plane (the template's `Center (Front/Back)`); the back plate is its own extrusion, not a mirror.
4. **Front = +Y** as the task states; Revit's template "Front" elevation looks the other way. The clamp is symmetric front/back, so nothing visible depends on it.
5. **`Joint_Gap` is informational** (drives no solid): the task says omit the gap spacer.
6. **Fillets skipped** (optional and cosmetic per the task).
7. **Always vertical** is normally a Work-Plane-Based option; with Work Plane-Based OFF the API may refuse it. G02 is soft and records the read-back; not a builder defect if it reads 0 with `read_only: true`.
8. **Material name.** The finish database (Smartsheet 6391628162879364) names the Primary Bath bronze **Kohler Vibrant Brushed Bronze (BV)**; it holds no glass-clamp row and no `SGC180` SKU. CRL's finish is "Brushed Bronze", used as the task specifies and **not claimed to match Kohler BV**. Loading the family never overwrites an existing project material; if Belmont already has a Primary Bath bronze, point `Clamp_Material` at it per type.
9. **No bitmap** on the material: the task defines a numeric appearance and the family ships no ADSKLIB (the bound-bitmap rule is an ADSKLIB rule).

## Source status (never present ASSUMED values as CRL data)

| Value | Status |
|---|---|
| Height 2 in, width 5 in, glass 3/8–1/2 in, finish Brushed Bronze | VERIFIED per task file (CRL page returned 403 to this session; a web search snippet repeats 2 in, 5 in, 3/8–1/2 in, solid brass) |
| Plate 1/8 in, joint gap 1/8 in, cap Ø 3/4 in, cap 1/8 in, 2 caps per side | ASSUMED. The same snippet says CRL requires 3/4 in glass holes, so a 3/4 in **cap** is probably too small to hide the hole: unverified, values left as specified |

Full list and confidence: `INFERENCES.md`.

## Open questions for Max

1. True plate thickness and cap size — CRL "Technical References & CAD Drawings" (page not readable from here).
2. Primary bath glass thickness (3/8 or 1/2) and number of panels/joints — not in the finish database; no clamp is scheduled there yet.
3. Which Belmont material should `Clamp_Material` use (see decision 8)?

## Place in the Belmont model (manual; the script never opens it)

1. Load the RFA (choose the type from the catalog by the actual glass thickness).
2. Place one clamp per panel-to-panel joint, on the joint centreline; rotate so the plates align with the glass faces.
3. Assumed height: three per joint, 6 in from top, mid-height, 6 in from bottom — verify against the job hardware layout.
4. Set instance/type comments `SGC180BBRZ`; add to the hardware schedule (Manufacturer, Model).

## Limitations (not defects)

- No Revit was available: nothing here proves API behaviour. Risk points, each measured natively by a gate: EQ dimensions, bound sketch plane, `Sketch.Profile` alignment in elevation views, visibility property names, `GetUnusedElements`, built-in `Type Comments`.
- 500 KB is a spec limit; an empty compacted Generic Model family may already sit near it. G20 reports the measured size.
- FBX export was not run (not requested); G27 checks only the structure it depends on.
- Visual review of `exports\*.png` is a human gate: `visual_verdict` stays `PENDING REVIEWER`.
- Drive: the RFA does not exist yet, so nothing is uploaded (AGENTS.md: upload after a technical + visual pass, verify `fileSize` through the API).

## Files

`run_glass_clamp.ps1` · `source\clamp_geometry.py` (shared numbers) · `source\build_glass_clamp.py` · `source\verify_glass_clamp.py` · `source\mock_revit_dryrun.py` (`python mock_revit_dryrun.py`, temp dir only) · `source\preview_geometry.py` · `preview\PREVIEW_geometry_offline.png` (analytic drawing, **not** a Revit render) · `pyrevit\GlassClamp.extension` · `INFERENCES.md`
