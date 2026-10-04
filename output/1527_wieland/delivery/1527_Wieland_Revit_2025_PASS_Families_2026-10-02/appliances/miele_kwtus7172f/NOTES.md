# Miele KWTUS 7172 F - custom replacement R1

Status: **BUILT_WITH_LIMITATIONS**. Native round-1 gates: **PASS**. Orchestrator review/release: pending.

Smartsheet row IDs: 4666245805309828.
Working RFA: `miele_kwtus7172f/miele_kwtus7172f_Custom_R1_R2025.rfa`. SHA-256: `f8864b4b909c4b7a83a8d4d01712957ebfaa3a1d1e4d9a6f05c20818e7885d32`.

## Why this is custom
Orchestrator round 1: exact-identity manufacturer working family fails the <=1 mm complete overall dimension gate. New native custom geometry replaces the working selection; OEM originals and prior working RFA remain preserved.

The prior working RFA remains at `miele_kwtus7172f/miele_kwtus7172f_R2025.rfa` with unchanged SHA-256 `19baf18cecc8a74a0cdc28196b8e1d2627a1afc51da2ea294d6d2d18cf95fb24`. Its historical measurements are retained in `../rework_round1/history_before/miele_kwtus7172f/validation.json`. Manufacturer originals remain in `source/original/`; their original hashes are preserved in source_manifest.json. No source RFA was rescaled or overwritten.

## Dimension authority and native evidence
Appliance body dimensions; installed door projections are reported separately.

Authoritative axes: X = width, Y = front-to-back depth, Z = height.
Target W x D x H: **597.000 x 563.000 x 859.000 mm**.
Actual complete placed-solid bounds: **597.000 x 563.000 x 859.000 mm**.
Delta W, D, H: +0.000006008, +0.000010109, -0.000034142 mm.
The same complete geometry was measured after native reopen and again after placement. All components, including modeled handles, feet, grates and trim, are included; no selected-body filter or artificial envelope object was used.
Revit format: 2025. Category: Specialty Equipment. Placement: WorkPlaneBased; actual native host: Floors.
Native geometry: 98 FreeFormElements, zero imported CAD instances, zero nested manufacturer family instances.
Material substitutions and restoration: 6/6 in the reopened family and 6/6 in the placed instance. Every used finish has a native appearance and a verified bound companion bitmap.
Fixed manufacturer size: Overall Width/Depth/Height are formula-locked. Variable dimensional flex is not advertised; editable finish controls were tested.
Warnings: zero in both family and disposable placement project.

## Visual inspection
The under-counter wine cabinet shows five shelf assemblies, a single storage region, glazed door, right-side hinges and lower ventilation. Crosswise-storage hardware is simplified; shelf material and count are represented without claiming fabrication detail.

Fresh native views:
- `miele_kwtus7172f/views/rework_r1/oblique - 3D View - oblique.png`
- `miele_kwtus7172f/views/rework_r1/front - 3D View - front.png`
- `miele_kwtus7172f/views/rework_r1/side - 3D View - side.png`

## Sources and retained evidence
Manufacturer specification: `source/product_sheet.pdf`, SHA-256 `c0c6e9f559d3576688afd2d4c92e64ea1da985819f8b0624878406acbaaf6f17`.
Dimension authority page: 2.
- https://www.mieleusa.com/product/12519520/24-built-under-wine-refrigerator-kwtus-7172-f
- https://media.miele.com/downloads/e5/64/05_70A8A51285B71FE1AC82B3099AE9E564.zip
- https://media.miele.com/downloads/n-/us/FS_12519520_USE_US-en-US.pdf

## Assumptions and limitations
- Fixed manufacturer model size; exposed finish parameters are flex-tested.
- Internal partitions, edge radii, controls and concealed mechanisms are reference-derived visualization approximations.
- Default envelope represents the factory appliance without separately supplied customer overlay panels or handles. Panel Finish changes the represented factory front; it does not certify an overlay thickness or panel shop drawing.

The default factory-front material is editable where present. Uniform companion bitmaps do not claim a selected cabinetry species, optical calibration or manufacturer-certified surface shader.

## Files and reproducibility
Current validation: `validation.json`; unchanged native-run record: `source/rework_r1/validation.json`. Build checkpoint and input dimensions: `source/rework_r1/build_result.json` and `source/rework_r1/config.json`.
Entry script: `source/build.py`. Shared code: `../rework_round1/native_rebuild.py`, `../rework_round1/validate_native.py` and `../family_common.py`. Run Revit operations only through the repository shared revit_run.py/revit.lock. The builder refuses to overwrite an existing replacement RFA.
Companion finish maps: `source/rework_r1/*_Finish.png`. Native texture paths are recorded in validation.json and must remain resolvable if a package is relocated.

## Blockers
No native build, dimension, category, placement, material or preview blocker remains for round 1. Detailed installation clearances and the explicitly stated inferred local geometry are not certified by the overall dimension pass. Final delivery is controlled by the orchestrator.
