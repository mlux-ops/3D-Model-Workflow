# Miele KWT 6722 iS - custom replacement R1

Status: **BUILT_WITH_LIMITATIONS**. Native round-1 gates: **PASS**. Orchestrator review/release: pending.

Smartsheet row IDs: 7384660666023812.
Working RFA: `miele_kwt6722is/miele_kwt6722is_Custom_R1_R2025.rfa`. SHA-256: `85206dca8b02262eed2c77b675ff8938157b1241ad7caf648a708bfc878836ee`.

## Why this is custom
Orchestrator round 1: exact-identity manufacturer working family fails the <=1 mm complete overall dimension gate. New native custom geometry replaces the working selection; OEM originals and prior working RFA remain preserved.

The prior working RFA remains at `miele_kwt6722is/miele_kwt6722is_R2025.rfa` with unchanged SHA-256 `b6d424fe8d51979c0b5f753df9e4485767182ab63fa86aba7f7677e7bd500318`. Its historical measurements are retained in `../rework_round1/history_before/miele_kwt6722is/validation.json`. Manufacturer originals remain in `source/original/`; their original hashes are preserved in source_manifest.json. No source RFA was rescaled or overwritten.

## Dimension authority and native evidence
Appliance body dimensions; installation flanges/projections may enlarge native envelope.

Authoritative axes: X = width, Y = front-to-back depth, Z = height.
Target W x D x H: **557.000 x 553.000 x 1770.000 mm**.
Actual complete placed-solid bounds: **557.000 x 553.000 x 1770.000 mm**.
Delta W, D, H: -0.000005198, +0.000002766, -0.000044632 mm.
The same complete geometry was measured after native reopen and again after placement. All components, including modeled handles, feet, grates and trim, are included; no selected-body filter or artificial envelope object was used.
Revit format: 2025. Category: Specialty Equipment. Placement: WorkPlaneBased; actual native host: Floors.
Native geometry: 133 FreeFormElements, zero imported CAD instances, zero nested manufacturer family instances.
Material substitutions and restoration: 6/6 in the reopened family and 6/6 in the placed instance. Every used finish has a native appearance and a verified bound companion bitmap.
Fixed manufacturer size: Overall Width/Depth/Height are formula-locked. Variable dimensional flex is not advertised; editable finish controls were tested.
Warnings: zero in both family and disposable placement project.

## Visual inspection
The tall right-hinged wine cabinet shows eight beech-colored shelf assemblies, two separated storage regions, a glazed door and lower ventilation. Sommelier accessories, shelf mechanisms and detailed optical response remain simplified.

Fresh native views:
- `miele_kwt6722is/views/rework_r1/oblique - 3D View - oblique.png`
- `miele_kwt6722is/views/rework_r1/front - 3D View - front.png`
- `miele_kwt6722is/views/rework_r1/side - 3D View - side.png`

## Sources and retained evidence
Manufacturer specification: `source/product_sheet.pdf`, SHA-256 `01d2d6d736c7bc01b7bbbd99ba7abca1605664ff86ccf49bb1819951510192e8`.
Dimension authority page: 2.
- https://www.mieleusa.com/product/11329860/24-built-in-wine-refrigerator-kwt-6722-is
- https://media.miele.com/downloads/a5/52/05_70A8A51285B71FE1ABFA89BF1ABCA552.zip
- https://media.miele.com/downloads/n-/us/FS_11329860_USE_US-en-US.pdf

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
