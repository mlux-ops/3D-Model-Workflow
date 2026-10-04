# Miele KFMC 3858 FD - custom replacement R1

Status: **BUILT_WITH_LIMITATIONS**. Native round-1 gates: **PASS**. Orchestrator review/release: pending.

Smartsheet row IDs: 2166795625103236, 1900063828279172.
Working RFA: `miele_kfmc3858fd/miele_kfmc3858fd_Custom_R1_R2025.rfa`. SHA-256: `b6bb3f3629dfc04b9851a521d78d7ffa16b6bfb90464e2c8d8ca30394aafc0ad`.

## Why this is custom
Orchestrator round 1: exact-identity manufacturer working family fails the <=1 mm complete overall dimension gate. New native custom geometry replaces the working selection; OEM originals and prior working RFA remain preserved.

The prior working RFA remains at `miele_kfmc3858fd/miele_kfmc3858fd_R2025.rfa` with unchanged SHA-256 `33f4dda96d550daa71c7e359a83bc4c093ad19caa9514a3c80dd3de418f067de`. Its historical measurements are retained in `../rework_round1/history_before/miele_kfmc3858fd/validation.json`. Manufacturer originals remain in `source/original/`; their original hashes are preserved in source_manifest.json. No source RFA was rescaled or overwritten.

## Dimension authority and native evidence
Appliance body; 1067 mm installation width is not appliance body width.

Authoritative axes: X = width, Y = front-to-back depth, Z = height.
Target W x D x H: **1048.000 x 608.000 x 2125.000 mm**.
Actual complete placed-solid bounds: **1048.000 x 608.000 x 2125.000 mm**.
Delta W, D, H: -0.000015259, -0.000011349, -0.000056458 mm.
The same complete geometry was measured after native reopen and again after placement. All components, including modeled handles, feet, grates and trim, are included; no selected-body filter or artificial envelope object was used.
Revit format: 2025. Category: Specialty Equipment. Placement: WorkPlaneBased; actual native host: Floors.
Native geometry: 77 FreeFormElements, zero imported CAD instances, zero nested manufacturer family instances.
Material substitutions and restoration: 3/3 in the reopened family and 3/3 in the placed instance. Every used finish has a native appearance and a verified bound companion bitmap.
Fixed manufacturer size: Overall Width/Depth/Height are formula-locked. Variable dimensional flex is not advertised; editable finish controls were tested.
Warnings: zero in both family and disposable placement project.

## Visual inspection
Two upper French-door fronts, one smaller convertible drawer, one larger lower drawer and the recessed toe grille are visible. The 1048 mm appliance body width replaces the oversized prior working family. No unselected customer pulls or applied furniture overlay is included.

Fresh native views:
- `miele_kfmc3858fd/views/rework_r1/oblique - 3D View - oblique.png`
- `miele_kfmc3858fd/views/rework_r1/front - 3D View - front.png`
- `miele_kfmc3858fd/views/rework_r1/side - 3D View - side.png`

## Sources and retained evidence
Manufacturer specification: `source/product_sheet.pdf`, SHA-256 `eab5869ceba00358a77db46cf342a80023fb8d7b8cfbd54f9ceb7dedad13db4d`.
Dimension authority page: 2.
- https://www.mieleusa.com/product/12489440/42-mastercool-frenchdoor-bottom-mount-unit-kfmc-3858-fd-compatible-with-furniture-fronts
- https://media.miele.com/downloads/a5/64/03_70A8A51285B71FE1AC8273C8621BA564.zip
- https://media.miele.com/downloads/n-/us/FS_12489440_USE_US-en-US.pdf

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
