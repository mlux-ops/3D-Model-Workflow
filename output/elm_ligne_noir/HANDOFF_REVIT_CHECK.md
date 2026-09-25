# ELM Vivid Ligne Noir 3x10: handoff for native Revit checks

Written 2026-09-25 by the cloud session (Linux container, no Revit, no Drive mount).
Branch `claude/light-fixture-rfa-yw6npk`. The maps are in commit `759c168`.
**Status: maps built and verified offline (`source/verify_maps.py` PASS). Native Revit check NOT RUN (BLOCKED, not failed). Drive upload PENDING.**

## 0. Start

```powershell
Set-Location 'C:\Users\mlux\Documents\GitHub\3D-Model-Workflow'   # confirm root: AGENTS.md present
git fetch origin; git checkout claude/light-fixture-rfa-yw6npk; git pull
& 'C:\Users\mlux\AppData\Local\Programs\Python\Python312\python.exe' output\elm_ligne_noir\source\verify_maps.py   # must print PASS, exit 0
```

Read `AGENTS.md`, `PROJECT_MEMORY.md` (section "ELM Vivid Ligne Noir 3x10 colour + bump -- 2026-09-25") and `output/elm_ligne_noir/README.md` first.

## 1. Inputs

| Item | Value |
|---|---|
| Colour | `output/elm_ligne_noir/textures/ELM_Ligne_Noir_3x10_Color.png` (8-bit sRGB, 3600 x 4000) |
| Bump | `output/elm_ligne_noir/textures/ELM_Ligne_Noir_3x10_Bump16.png` (16-bit grey, same layout; white = rib tops, black = grout floor) |
| Sample Size | 36 in W x 40 in H (3'-0" x 3'-4"), both maps, scale lock on |
| Layout | 12 x 4 tiles, 3 x 10 in module, flutes vertical, straight stack, 1/16 in joint |
| Bump amount | 0.4 (0.3 to 0.5) |
| Finish | matte (low glossiness); record the value used |

## 2. Revit 2025 check (disposable project only)

- Never open or modify a user project. Do not close a Revit session this run did not launch.
- Write only under `output/elm_ligne_noir/revit_check/` through an `out_path()` guard that raises outside it.
- Adapt `output/model-transfer-tests/candidate-20260918-01/material/build_revit.py`: reuse `connect_bitmap`, `read_bitmap`, `paint_test_face`, and keep its rules (JSON report written first, then re-raise; no Transfer Project Standards).
- Set up the material:
  - Generic appearance.
  - `generic_diffuse` = Colour, `generic_bump_map` = Bump.
  - `texture_RealWorldScaleX/Y` = 36 / 40 in on both maps.
  - `generic_bump_amount` = 0.4.
- Write `revit_check/validation.json`. It must record these gates, each with a measured value:

| Gate | Pass condition |
|---|---|
| Material saved and reopened | material present after the project is saved and reopened |
| Both bitmaps connected | diffuse and bump are UnifiedBitmap with the paths above |
| Paths resolve | `os.path.isfile` true for both bound paths |
| Scale | X = 36, Y = 40 in, +/- 0.0005 |
| Painted face | wall face painted and `GetPaintedMaterial` equals the material |

- Exports go to `revit_check/`:
  - An 8 x 8 ft wall in a Realistic view, frontal.
  - The same wall rendered with light at a grazing angle (about 10 to 20 degrees to the face).
- Pass the exports only after a reviewer has looked at them. The script never self-certifies the visual verdict.

| Visual check | Accept |
|---|---|
| Scale | 4 tiles per foot across, 4 tiles per 40 in up; flutes vertical, 10 per tile |
| Seams | no visible line at the 36 in / 40 in repeat boundaries |
| Relief (grazing) | ribs raised, channels read; grout sits deeper than the channels; the face does not look punctured |
| Bump sign | ribs raised, not sunken (inverted = the bump was read as a depth map) |
| Colour | warm near-black charcoal face; light grey grout; no blown highlights |

## 3. After the checks

- **Any failure:** fix it in `source/build_ligne_noir.py`, rebuild, re-run `verify_maps.py`, then re-run the Revit check.
  - Never tune the bump by raising a global multiplier: the flute relief and the grout depth are separate terms.
  - Keep the clearance above the grout floor greater than 0.
- **Deliverable:** the colour PNG, the bump PNG and the Sample Size.
  - No RVT, no V-Ray.
  - An ADSKLIB only if the user asks for a material package.
  - The disposable project is not a deliverable.
- **Drive** (standing authorisation):
  - Deduplicate first.
  - Zip the two maps, `README.md`, `SOURCE_SELECTION.md` and `textures/ligne_noir_build_report.json` as `ELM_Ligne_Noir_3x10_Color_Bump_Maps.zip`.
  - Copy it to `F:\My Drive\3D Model Workflow\Material Packages`.
  - Confirm through the Drive connector that the file appears with a matching `fileSize`, and report the link. A file in the sync folder alone is not evidence.
- **Memory:**
  - Log every error and its fix in `PROJECT_MEMORY.md` during the same task.
  - Update the Ligne Noir entry's Revit and Drive status with new lines only; never alter historical entries.
- **Commit:** on a branch; offer `git merge --ff-only`.

## 4. Also pending on the workstation (separate task)

Cassia SF549315AGOP RFA: the native build has not been run. See `output/cassia/README.md` (`run_cassia.ps1`, verifier exit code = result).
