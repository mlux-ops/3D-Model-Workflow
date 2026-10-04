# Miele G 5051 SCVi ADA - custom replacement R1

Status: **BUILT_WITH_LIMITATIONS**. Native round-1 gates: **PASS**. Orchestrator review/release: pending.

Smartsheet row IDs: 3328172767117188, 904397767376772.
Working RFA: `miele_g5051scvi/miele_g5051scvi_Custom_R1_R2025.rfa`. SHA-256: `eb5801a312601166421008c2c045efc77742b8ee0454652f9288750872c90873`.

## Why this is custom
Orchestrator round 1: exact-identity manufacturer working family fails the <=1 mm complete overall dimension gate. New native custom geometry replaces the working selection; OEM originals and prior working RFA remain preserved.

The prior working RFA remains at `miele_g5051scvi/miele_g5051scvi_R2025.rfa` with unchanged SHA-256 `27391211e2833b4185affafe8f8bf49126ed9e20b216479b254294c4227ba10f`. Its historical measurements are retained in `../rework_round1/history_before/miele_g5051scvi/validation.json`. Manufacturer originals remain in `source/original/`; their original hashes are preserved in source_manifest.json. No source RFA was rescaled or overwritten.

## Dimension authority and native evidence
Current product sheet states 598 W x 815 H x 550 D mm. The downloaded ADA model is 805 mm high; this difference is not accepted silently.

Authoritative axes: X = width, Y = front-to-back depth, Z = height.
Target W x D x H: **598.000 x 550.000 x 815.000 mm**.
Actual complete placed-solid bounds: **598.000 x 550.000 x 815.000 mm**.
Delta W, D, H: +0.000017643, +0.000004196, +0.000035286 mm.
The same complete geometry was measured after native reopen and again after placement. All components, including modeled handles, feet, grates and trim, are included; no selected-body filter or artificial envelope object was used.
Revit format: 2025. Category: Specialty Equipment. Placement: WorkPlaneBased; actual native host: Floors.
Native geometry: 20 FreeFormElements, zero imported CAD instances, zero nested manufacturer family instances.
Material substitutions and restoration: 4/4 in the reopened family and 4/4 in the placed instance. Every used finish has a native appearance and a verified bound companion bitmap.
Fixed manufacturer size: Overall Width/Depth/Height are formula-locked. Variable dimensional flex is not advertised; editable finish controls were tested.
Warnings: zero in both family and disposable placement project.

## Visual inspection
The 815 mm high integrated dishwasher shows its top control strip, separate factory door skin, recessed toe region and feet. No detached hardware or connector glyph obscures the preview. The neutral editable front is not an approved customer overlay.

Fresh native views:
- `miele_g5051scvi/views/rework_r1/oblique - 3D View - oblique.png`
- `miele_g5051scvi/views/rework_r1/front - 3D View - front.png`
- `miele_g5051scvi/views/rework_r1/side - 3D View - side.png`

## Sources and retained evidence
Manufacturer specification: `source/product_sheet.pdf`, SHA-256 `9ee6f3dbc23ad9bd205255e96a591e01f32f83dbf0926879be2e2f2b5f0a25f8`.
Dimension authority page: 2.
- https://www.mieleusa.com/product/11636710/fully-integrated-ada-dishwasher-g-5051-scvi-active-stainless-steel
- https://media.miele.com/downloads/a5/52/10_70A8A51285B71FE1ABFC9D443DCBA552.zip
- https://media.miele.com/downloads/n-/us/FS_11636710_USE_US-en-US.pdf
- https://www.mieleusa.com/product/11636710/fully-integrated-dishwasher-g-5051-scvi-active-stainless-steel

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
