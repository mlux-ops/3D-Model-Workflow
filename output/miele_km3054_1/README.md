# Miele KM 3054-1 gas cooktop: Revit 2025 face-based family

Status: **NATIVE TECHNICAL PASS, visual verdict PENDING REVIEWER.** Not packaged and not
uploaded to Drive. Both wait for the reviewer's verdict in `REVIEW.md`.

- Branch: `docs/rfa-family-skill-2026-10-22`. Checkout used: `C:\Users\found\Documents\3\3D-Model-Workflow`.
- RFA: `output/miele_km3054_1/Miele_KM3054-1_Gas_Cooktop_R2025.rfa` (618,496 bytes,
  SHA-256 `d7de5a70ed082fa0022f9593fcad16ea42bd736e9282e07ae3005f074f75f34a`), a Git LFS object.
- Product resolved: Miele **KM 3054-1**, material number 11766750, EAN 4002516451501, marketing
  class Platinum, 37 1/8 in (942 mm) gas cooktop on black ceramic glass (SCHOTT CERAN), 5
  burners incl. 1 dual wok, matte black enamelled cast-iron grates, 5 rotary knobs. The page
  offers only this one variant. The user called it a "rangetop"; the page and drawings show a
  drop-in cooktop, which is what is modelled.
- Type: `KM 3054-1 - 37 1/8 in - Black Ceramic Glass`.
- Sources and hashes: `references/miele_km3054_1/SOURCE_MANIFEST.md`.

## Category and hosting

- **Specialty Equipment** (`OST_SpecialityEquipment`). It is an appliance, not a light or
  plumbing fixture, and nothing in the references points to another category. The Miele
  G 5051 SCVi dishwasher kit on `origin/docs/agents-memory-2026-09-26` also used Specialty Equipment.
- Template `Generic Model face based.rft`; `FAMILY_ALWAYS_VERTICAL = 0`; placement WorkPlaneBased.
- Mounts on the **top face of the countertop**. Local +Z follows the face normal (up). The
  glass and frame sit 0-7 mm above the face, the grates reach 37 mm above it, and the casing
  hangs 46 mm below it, with the electronics housing reaching 71 mm below it (78 mm built-in
  height from the glass top). The family does not cut the countertop; cut it 916 x 490-500 mm.

## Parameters

Type parameters, locked by constant formulas: Overall Width 942, Overall Depth 526, Overall
Height 53, Height Above Counter 7, Casing Depth 46, Built-in Height 78, Cutout Width 916,
Cutout Depth 500 (mm). Identity: Manufacturer Miele, Model KM 3054-1, URL, Miele Material
Number 11766750, Model Accuracy Notes.

Material type parameters (GenericSchema appearance clones, no bitmaps, nothing
self-illuminated; colours sampled from the product top view, metals below the pixel median):

| Parameter | RGB | Gloss | Applies to |
|---|---|---|---|
| Top Finish | 0, 0, 0 | 1.00 | pitch black polished ceramic glass (user direction 2026-10-22; photo median was blue-tinted) |
| Frame Finish | 120, 122, 125 | 0.50 | stainless edge band |
| Grate Finish | 73, 72, 77 | 0.25 | 5 cast-iron grates |
| Burner Finish | 78, 74, 75 | 0.30 | caps, bowls, wok outer cap |
| Burner Ring Finish | 183, 180, 188 | 0.40 | aluminium burner heads |
| Knob Finish | 184, 185, 187 | 0.50 | 5 knobs |
| Housing Finish | 150, 152, 155 | 0.30 | below-counter casing, electronics housing, gas stub |

## Geometry

32 FreeFormElements, one subcategory per finish (Cooktop Glass, Cooktop Frame, Grates,
Burner Caps, Burner Heads, Control Knobs, Housing). Each grate is one cast piece: ring, pan
fingers, outer bars and diagonals unioned into one solid, with real openings between the
bars (gate `grate_opening_is_open`). Burners: bowl, aluminium head and cap per burner; the
dual wok burner adds an outer flame ring and cap. Positions and sizes come from the
orthographic product photo at 0.3395 mm/px (overlay `evidence/COMPARE_top_overlay_50pct.png`).
Dimension provenance is tagged per constant in `source/km3054_geometry.py`; unprinted values
are listed in `INFERENCES.md`.

## Run it

Route A (used for this build):

    powershell -ExecutionPolicy Bypass -File "<checkout>\output\miele_km3054_1\run_km3054.ps1"

It prints the checkout and the RFA path, preflights every path (exit 2 BLOCKED if missing),
writes `logs/run-start.txt`, moves an earlier RFA to `logs/attempt-rfas/`, runs
`pyrevit run "<absolute builder>" --revit=2025`, ignores pyRevit's exit code, runs
`source/verify_km3054.py`, and ends with `RFA written:` or `NO RFA was written`. Its exit code is the verifier's.

Route B (if `pyrevit run` cannot start Revit, e.g. `0xe06d7363`): register
`pyrevit extensions paths add "<checkout>\output\miele_km3054_1\pyrevit"`, Reload, press
KM3054 > Build > Build KM 3054-1, then run the verifier with pyRevit's CPython.

Then `C:\Python314\python.exe source\compare_km3054.py` rebuilds the comparison sheets.
After the reviewer writes `Visual verdict: ACCEPTED` in `REVIEW.md`:
`"C:\Program Files\pyRevit-Master\bin\cengines\CPY3123\python.exe" source\package_km3054.py`,
then upload to Drive > 3D Model Workflow > 3D Models and verify by file id.

## Native attempts

1. 2026-10-22 23:27 UTC: all builder gates true, verifier exit 0, but the family-document
   exports showed the template host slab (grey) and the Underside view showed only the host.
   The verifier had trusted a recorded "hidden" flag. Kept in `logs/attempt1/` and
   `logs/attempt-rfas/`.
2. 2026-10-22 23:30 UTC (repair cycle 1): evidence views now come from the project with the
   disposable floor host hidden and the crop from the fixture's measured bounds; the verifier
   decodes each export and requires >= 97% background on the crop border. Pass, verifier exit 0.
   Family-document views still show the template host; they are kept out of `evidence/`
   (`logs/family-doc-views/`) and are not used as evidence.

## Kit

`source/build_km3054.py` (IronPython builder), `source/km3054_geometry.py` (stdlib spec,
provenance, rays; `python km3054_geometry.py` runs the offline profile check),
`source/verify_km3054.py` (CPython stdlib verifier, exit 0/1/2, stale-report guard),
`source/package_km3054.py` (allow-list ZIP, refuses without the verdict line),
`source/compare_km3054.py` (comparison sheets, pillow), `run_km3054.ps1`, the pushbutton,
`INFERENCES.md`, `PATH_AUDIT.md`, `REVIEW.md`, `validation.json`, `logs/`, `evidence/`.
