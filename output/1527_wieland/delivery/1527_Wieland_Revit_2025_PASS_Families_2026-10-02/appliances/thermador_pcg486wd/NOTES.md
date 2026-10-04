# Thermador PCG486WD - custom replacement R1

Status: **BUILT_WITH_LIMITATIONS**. Native round-1 gates: **PASS**. Orchestrator review/release: pending.

Smartsheet row IDs: 8955028301086596.
Working RFA: `thermador_pcg486wd/thermador_pcg486wd_Custom_R1_R2025.rfa`. SHA-256: `bd01ca911e2a6dffe9731c667046a839dad2e897d27a37daacf533381cf41dcf`.

## Why this is custom
Orchestrator round 1: exact-identity manufacturer working family fails the <=1 mm complete overall dimension gate. New native custom geometry replaces the working selection; OEM originals and prior working RFA remain preserved.

The prior working RFA remains at `thermador_pcg486wd/thermador_pcg486wd_R2025.rfa` with unchanged SHA-256 `356457f2f43ca992a3c733ae59c551261e8d6ff28701e31d4947a7fc7d78f0aa`. Its historical measurements are retained in `../rework_round1/history_before/thermador_pcg486wd/validation.json`. Manufacturer originals remain in `source/original/`; their original hashes are preserved in source_manifest.json. No source RFA was rescaled or overwritten.

## Dimension authority and native evidence
47 15/16 x 25 13/16 x 8 1/8 in published appliance dimensions; native grate/knob configuration is compared explicitly.

Authoritative axes: X = width, Y = front-to-back depth, Z = height.
Target W x D x H: **1217.612 x 655.638 x 206.375 mm**.
Actual complete placed-solid bounds: **1217.613 x 655.638 x 206.375 mm**.
Delta W, D, H: +0.000024223, +0.000024223, -0.000006056 mm.
The same complete geometry was measured after native reopen and again after placement. All components, including modeled handles, feet, grates and trim, are included; no selected-body filter or artificial envelope object was used.
Revit format: 2025. Category: Specialty Equipment. Placement: WorkPlaneBased; actual native host: Floors.
Native geometry: 105 FreeFormElements, zero imported CAD instances, zero nested manufacturer family instances.
Material substitutions and restoration: 4/4 in the reopened family and 4/4 in the placed instance. Every used finish has a native appearance and a verified bound companion bitmap.
Fixed manufacturer size: Overall Width/Depth/Height are formula-locked. Variable dimensional flex is not advertised; editable finish controls were tested.
Warnings: zero in both family and disposable placement project.

## Visual inspection
Six star-shaped burner assemblies are arranged as four on the left and two on the right, with a griddle between them, seven front controls and a rounded bolster. Grate tops and knob projections are included in the complete measured envelope. Local grate/crown profiles remain simplified.

Fresh native views:
- `thermador_pcg486wd/views/rework_r1/oblique - 3D View - oblique.png`
- `thermador_pcg486wd/views/rework_r1/front - 3D View - front.png`
- `thermador_pcg486wd/views/rework_r1/side - 3D View - side.png`

## Sources and retained evidence
Manufacturer specification: `source/product_sheet.pdf`, SHA-256 `b32a34ccbae59e9466010bb2dcbc58f609bd2bc723354372d677d20bf5b2fc22`.
Dimension authority page: 1.
- https://www.thermador.com/us/en/mkt-product/cooktops-rangetops/rangetops/PCG486WD
- https://media3.bsh-group.com/3D_Asset/15802529_PCG486WD-Thermador-TradeCAD.zip
- https://media3.bsh-group.com/3D_Asset/29485643_PCG486WD_TradeCAD.zip
- https://media3.bsh-group.com/Documents/MCDOC02690629_PCG486WD-48-INCH-GAS-RANGETOP-WITH-GRIDDLE-Specifications.pdf

## Assumptions and limitations
- Fixed manufacturer model size; exposed finish parameters are flex-tested.
- Internal partitions, edge radii, controls and concealed mechanisms are reference-derived visualization approximations.

The default factory-front material is editable where present. Uniform companion bitmaps do not claim a selected cabinetry species, optical calibration or manufacturer-certified surface shader.

## Files and reproducibility
Current validation: `validation.json`; unchanged native-run record: `source/rework_r1/validation.json`. Build checkpoint and input dimensions: `source/rework_r1/build_result.json` and `source/rework_r1/config.json`.
Entry script: `source/build.py`. Shared code: `../rework_round1/native_rebuild.py`, `../rework_round1/validate_native.py` and `../family_common.py`. Run Revit operations only through the repository shared revit_run.py/revit.lock. The builder refuses to overwrite an existing replacement RFA.
Companion finish maps: `source/rework_r1/*_Finish.png`. Native texture paths are recorded in validation.json and must remain resolvable if a package is relocated.

## Blockers
No native build, dimension, category, placement, material or preview blocker remains for round 1. Detailed installation clearances and the explicitly stated inferred local geometry are not certified by the overall dimension pass. Final delivery is controlled by the orchestrator.
