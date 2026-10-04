# Miele H 7280 BP - custom replacement R1

Status: **BUILT_WITH_LIMITATIONS**. Native round-1 gates: **PASS**. Orchestrator review/release: pending.

Smartsheet row IDs: 4418595438788484, 3025963735121796.
Working RFA: `miele_h7280bp/miele_h7280bp_Custom_R1_R2025.rfa`. SHA-256: `f720de18bf6d88581b58b63ef3430d7ab04d954a404960fc7312d076ae4c0ded`.

## Why this is custom
Orchestrator round 1: exact-identity manufacturer working family fails the <=1 mm complete overall dimension gate. New native custom geometry replaces the working selection; OEM originals and prior working RFA remain preserved.

The prior working RFA remains at `miele_h7280bp/miele_h7280bp_R2025.rfa` with unchanged SHA-256 `8ee511e3f74f0c28239cc513154e56fb8a5a1868dfad5a52637a0f95ccf196ea`. Its historical measurements are retained in `../rework_round1/history_before/miele_h7280bp/validation.json`. Manufacturer originals remain in `source/original/`; their original hashes are preserved in source_manifest.json. No source RFA was rescaled or overwritten.

## Dimension authority and native evidence
Official exact-model Miele product page, Technical data: W757 x H727 x D626 mm, checked 2026-10-02; retained two-page fact sheet omits this overall row.

Authoritative axes: X = width, Y = front-to-back depth, Z = height.
Target W x D x H: **757.000 x 626.000 x 727.000 mm**.
Actual complete placed-solid bounds: **757.000 x 626.000 x 727.000 mm**.
Delta W, D, H: +0.000014496, +0.000016403, +0.000028801 mm.
The same complete geometry was measured after native reopen and again after placement. All components, including modeled handles, feet, grates and trim, are included; no selected-body filter or artificial envelope object was used.
Revit format: 2025. Category: Specialty Equipment. Placement: WorkPlaneBased; actual native host: Floors.
Native geometry: 33 FreeFormElements, zero imported CAD instances, zero nested manufacturer family instances.
Material substitutions and restoration: 5/5 in the reopened family and 5/5 in the placed instance. Every used finish has a native appearance and a verified bound companion bitmap.
Fixed manufacturer size: Overall Width/Depth/Height are formula-locked. Variable dimensional flex is not advertised; editable finish controls were tested.
Warnings: zero in both family and disposable placement project.

## Visual inspection
Front, side and oblique views show the full-height black oven fascia, recessed glazing, touch-control band, horizontal handle and metal case. The complete case-to-handle extent is measured. Concealed case partition and cavity detailing are approximations.

Fresh native views:
- `miele_h7280bp/views/rework_r1/oblique - 3D View - oblique.png`
- `miele_h7280bp/views/rework_r1/front - 3D View - front.png`
- `miele_h7280bp/views/rework_r1/side - 3D View - side.png`

## Sources and retained evidence
Manufacturer specification: `source/product_sheet.pdf`, SHA-256 `caacad6a120468ecd42757ad43314d70fb3de9f26208cbd1c4e367c5bf31679e`.
- https://www.mieleusa.com/product/11968200/30-inch-convection-oven-h-7280-bp-obsidian-black
- https://media.miele.com/downloads/1d/33/01_C7F12828C0C31FE182DC54A63F5A1D33.zip
- https://media.miele.com/downloads/n-/us/FS_11968200_USE_US-en-US.pdf
- https://www.mieleusa.com/product/11968200/30-oven-h-7280-bp-obsidian-black

## Assumptions and limitations
- Fixed manufacturer model size; exposed finish parameters are flex-tested.
- Internal partitions, edge radii, controls and concealed mechanisms are reference-derived visualization approximations.
- Published nominal appliance W/D/H is the requested complete coordination envelope. Handles are included inside this envelope; the concealed case-depth partition is reconstructed rather than certified to the separate installation section. This family is not a cabinet-cutout or manufacturing authority.

The default factory-front material is editable where present. Uniform companion bitmaps do not claim a selected cabinetry species, optical calibration or manufacturer-certified surface shader.

## Files and reproducibility
Current validation: `validation.json`; unchanged native-run record: `source/rework_r1/validation.json`. Build checkpoint and input dimensions: `source/rework_r1/build_result.json` and `source/rework_r1/config.json`.
Entry script: `source/build.py`. Shared code: `../rework_round1/native_rebuild.py`, `../rework_round1/validate_native.py` and `../family_common.py`. Run Revit operations only through the repository shared revit_run.py/revit.lock. The builder refuses to overwrite an existing replacement RFA.
Companion finish maps: `source/rework_r1/*_Finish.png`. Native texture paths are recorded in validation.json and must remain resolvable if a package is relocated.

## Blockers
No native build, dimension, category, placement, material or preview blocker remains for round 1. Detailed installation clearances and the explicitly stated inferred local geometry are not certified by the overall dimension pass. Final delivery is controlled by the orchestrator.
