# Thermador PODMC301W - custom replacement R1

Status: **BUILT_WITH_LIMITATIONS**. Native round-1 gates: **PASS**. Orchestrator review/release: pending.

Smartsheet row IDs: 2199628860030852.
Working RFA: `thermador_podmc301w/thermador_podmc301w_Custom_R1_R2025.rfa`. SHA-256: `1b8fb476c8224a90a7651f7968e091c0a0460cf1b1743135b13813e741a6c9d3`.

## Why this is custom
Orchestrator round 1: exact-identity manufacturer working family fails the <=1 mm complete overall dimension gate. New native custom geometry replaces the working selection; OEM originals and prior working RFA remain preserved.

The prior working RFA remains at `thermador_podmc301w/thermador_podmc301w_R2025.rfa` with unchanged SHA-256 `2c5c54e83c38b0cdc2619f61ce089b47df09b5f52bf4f7bcf89ca3585b1f0ae5`. Its historical measurements are retained in `../rework_round1/history_before/thermador_podmc301w/validation.json`. Manufacturer originals remain in `source/original/`; their original hashes are preserved in source_manifest.json. No source RFA was rescaled or overwritten.

## Dimension authority and native evidence
29 3/4 x 24 1/2 x 49 in appliance body; handle projection additional.

Authoritative axes: X = width, Y = front-to-back depth, Z = height.
Target W x D x H: **755.650 x 622.300 x 1244.600 mm**.
Actual complete placed-solid bounds: **755.650 x 622.300 x 1244.600 mm**.
Delta W, D, H: +0.000024223, +0.000024223, +0.000048447 mm.
The same complete geometry was measured after native reopen and again after placement. All components, including modeled handles, feet, grates and trim, are included; no selected-body filter or artificial envelope object was used.
Revit format: 2025. Category: Specialty Equipment. Placement: WorkPlaneBased; actual native host: Floors.
Native geometry: 66 FreeFormElements, zero imported CAD instances, zero nested manufacturer family instances.
Material substitutions and restoration: 5/5 in the reopened family and 5/5 in the placed instance. Every used finish has a native appearance and a verified bound companion bitmap.
Fixed manufacturer size: Overall Width/Depth/Height are formula-locked. Variable dimensional flex is not advertised; editable finish controls were tested.
Warnings: zero in both family and disposable placement project.

## Visual inspection
The smaller upper speed oven and larger lower oven are distinct, each with its control fascia, glazing and round handle. The complete geometry fits the requested nominal 622.3 mm depth. The body/handle partition differs from a fabrication interpretation of the separate installation section and is explicitly documented.

Fresh native views:
- `thermador_podmc301w/views/rework_r1/oblique - 3D View - oblique.png`
- `thermador_podmc301w/views/rework_r1/front - 3D View - front.png`
- `thermador_podmc301w/views/rework_r1/side - 3D View - side.png`

## Sources and retained evidence
Manufacturer specification: `source/product_sheet.pdf`, SHA-256 `994ef34139be60f0169cc5853180d90ad0c0f25d9977824ddb54cf7c164f41b8`.
Dimension authority page: 1.
- https://www.thermador.com/us/en/mkt-product/ovens/double-ovens/PODMC301W
- https://media3.bsh-group.com/3D_Asset/15838407_PODMC301W-Thermador-TradeCAD.zip
- https://media3.bsh-group.com/3D_Asset/29273463_PODMC301W_TradeCAD.zip
- https://media3.bsh-group.com/Documents/MCDOC02802507_PODMC301W-30-INCH-DOUBLE-COMBINATION-BUILT-IN-OVEN-WITH-SPEED-OVEN-Specifications.pdf

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
