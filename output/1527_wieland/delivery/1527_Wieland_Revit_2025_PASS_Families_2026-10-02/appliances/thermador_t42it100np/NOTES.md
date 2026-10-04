# Thermador T42IT100NP - custom replacement R1

Status: **BUILT_WITH_LIMITATIONS**. Native round-1 gates: **PASS**. Orchestrator review/release: pending.

Smartsheet row IDs: 7829128394243972.
Working RFA: `thermador_t42it100np/thermador_t42it100np_Custom_R1_R2025.rfa`. SHA-256: `2031192ec11e938be2c0d36e8e149919182866dc7af186aadf253e5146fa2be2`.

## Why this is custom
Orchestrator round 1: exact-identity manufacturer working family fails the <=1 mm complete overall dimension gate. New native custom geometry replaces the working selection; OEM originals and prior working RFA remain preserved.

The prior working RFA remains at `thermador_t42it100np/thermador_t42it100np_R2025.rfa` with unchanged SHA-256 `41a0d65b3a5640a1b23f6b3e0fc1787e0d60b708caa0cd3a625e85b980ce06f1`. Its historical measurements are retained in `../rework_round1/history_before/thermador_t42it100np/validation.json`. Manufacturer originals remain in `source/original/`; their original hashes are preserved in source_manifest.json. No source RFA was rescaled or overwritten.

## Dimension authority and native evidence
Retained September 2026 manufacturer drawing, page 4: explicit metric W1048 x D608 x H2123 mm with leveling feet at minimum. Drawing metric values govern inconsistent rounded inch equivalents.

Authoritative axes: X = width, Y = front-to-back depth, Z = height.
Target W x D x H: **1048.000 x 608.000 x 2123.000 mm**.
Actual complete placed-solid bounds: **1048.000 x 608.000 x 2123.000 mm**.
Delta W, D, H: -0.000015259, -0.000011349, +0.000065613 mm.
The same complete geometry was measured after native reopen and again after placement. All components, including modeled handles, feet, grates and trim, are included; no selected-body filter or artificial envelope object was used.
Revit format: 2025. Category: Specialty Equipment. Placement: WorkPlaneBased; actual native host: Floors.
Native geometry: 77 FreeFormElements, zero imported CAD instances, zero nested manufacturer family instances.
Material substitutions and restoration: 3/3 in the reopened family and 3/3 in the placed instance. Every used finish has a native appearance and a verified bound companion bitmap.
Fixed manufacturer size: Overall Width/Depth/Height are formula-locked. Variable dimensional flex is not advertised; editable finish controls were tested.
Warnings: zero in both family and disposable placement project.

## Visual inspection
The complete factory appliance is visible with two upper French doors, two lower drawer faces and toe grille at the documented minimum 2123 mm height. Customer panels, pulls, cutout framing and accessory frame kits are not part of this default envelope.

Fresh native views:
- `thermador_t42it100np/views/rework_r1/oblique - 3D View - oblique.png`
- `thermador_t42it100np/views/rework_r1/front - 3D View - front.png`
- `thermador_t42it100np/views/rework_r1/side - 3D View - side.png`

## Sources and retained evidence
Manufacturer specification: `source/product_sheet.pdf`, SHA-256 `b5571a589d7f07bb8107b4738a8a74eeba0a33337bf2bcd76134309913e2b709`.
Dimension authority page: 4.
- https://www.thermador.com/us/en/mkt-product/refrigeration/bottom-freezer-refrigerators/T42IT100NP
- https://media3.bsh-group.com/3D_Asset/22537542_T42IT100NP_TradeCADs.zip
- https://media3.bsh-group.com/Documents/25549017_T42IT100NP-42-INCH-BUILT-IN-FRENCH-DOOR_REFRIGERATOR-2-DRAWER-PANEL-READY-Specifications.pdf

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
