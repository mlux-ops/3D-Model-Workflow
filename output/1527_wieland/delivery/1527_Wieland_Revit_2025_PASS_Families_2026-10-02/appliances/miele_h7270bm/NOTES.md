# Miele H 7270 BM - custom replacement R1

Status: **BUILT_WITH_LIMITATIONS**. Native round-1 gates: **PASS**. Orchestrator review/release: pending.

Smartsheet row IDs: 8816514970877828, 6403663455649668.
Working RFA: `miele_h7270bm/miele_h7270bm_Custom_R1_R2025.rfa`. SHA-256: `f06e96380ec5059cc529b918c2ce34a8ba242cbe9fc3f8f35b77bb5d4e3d654b`.

## Why this is custom
Orchestrator round 1: exact-identity manufacturer working family fails the <=1 mm complete overall dimension gate. New native custom geometry replaces the working selection; OEM originals and prior working RFA remain preserved.

The prior working RFA remains at `miele_h7270bm/miele_h7270bm_R2025.rfa` with unchanged SHA-256 `4f9956271a11bf762ba499664915314ce8b19d790dd946eaf7e8a36ea5f50ac7`. Its historical measurements are retained in `../rework_round1/history_before/miele_h7270bm/validation.json`. Manufacturer originals remain in `source/original/`; their original hashes are preserved in source_manifest.json. No source RFA was rescaled or overwritten.

## Dimension authority and native evidence
Current product-sheet page 2 explicitly states 757 W x 479 H x 573 D mm. Native projections are measured separately.

Authoritative axes: X = width, Y = front-to-back depth, Z = height.
Target W x D x H: **757.000 x 573.000 x 479.000 mm**.
Actual complete placed-solid bounds: **757.000 x 573.000 x 479.000 mm**.
Delta W, D, H: +0.000014496, +0.000017452, +0.000013828 mm.
The same complete geometry was measured after native reopen and again after placement. All components, including modeled handles, feet, grates and trim, are included; no selected-body filter or artificial envelope object was used.
Revit format: 2025. Category: Specialty Equipment. Placement: WorkPlaneBased; actual native host: Floors.
Native geometry: 29 FreeFormElements, zero imported CAD instances, zero nested manufacturer family instances.
Material substitutions and restoration: 5/5 in the reopened family and 5/5 in the placed instance. Every used finish has a native appearance and a verified bound companion bitmap.
Fixed manufacturer size: Overall Width/Depth/Height are formula-locked. Variable dimensional flex is not advertised; editable finish controls were tested.
Warnings: zero in both family and disposable placement project.

## Visual inspection
The compact speed-oven proportions, black control band, door glazing and horizontal handle are visible in all three views. The complete 573 mm depth includes modeled handle geometry; concealed case depth is reconstructed for the requested nominal envelope.

Fresh native views:
- `miele_h7270bm/views/rework_r1/oblique - 3D View - oblique.png`
- `miele_h7270bm/views/rework_r1/front - 3D View - front.png`
- `miele_h7270bm/views/rework_r1/side - 3D View - side.png`

## Sources and retained evidence
Manufacturer specification: `source/product_sheet.pdf`, SHA-256 `66d7053796d55dd0f4bc3b0657de0bdee1952f7b83a9604adb94b2b99f06bb29`.
Dimension authority page: 2.
- https://www.mieleusa.com/product/11968190/30-speed-oven-h-7270-bm-obsidian-black
- https://media.miele.com/downloads/8b/20/02_C7F138387FFA1FD189C793AEE9B58B20.zip
- https://media.miele.com/downloads/n-/us/FS_11968190_USE_US-en-US.pdf

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
