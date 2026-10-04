# LG WM4000HBA

Status: **BUILT_WITH_LIMITATIONS**. Recorded 2026-10-02T14:36:37.480895+00:00.

Smartsheet row IDs: 3292695531945860, 4443914724376452.
RFA: `lg_wm4000hba/lg_wm4000hba_R2025.rfa`. SHA-256: `506f2a58ee6630d16b9049b7041a1c51bd9c29518931bab5832ca09385e68721`.

## Native evidence
Revit 2025 save/reopen: PASS. Category: Specialty Equipment. Placement: WorkPlaneBased; actual test host: Floors.
Actual full placed bounds (W x D x H): **685.800 x 768.350 x 990.600 mm**.
Comparison target (W x D x H): 685.800 x 768.350 x 990.600 mm.
Dimension gate: **PASS**; scope: overall.
Dimension basis: 27 x 39 x 30 1/4 in, W x H x D; LG builder specification page 2.
Delta against comparison target (W, D, H): +0.000000, -0.000024, +0.000000 mm.
Material parameter substitution with geometry evidence: 5/5. Zero exposed parameters means the manufacturer materials remain nested/fixed, not that editability passed.
Family warnings: 0; placed-project warnings: 0.

Detailed native results: `../lg_wm4000hba/validation.json`.
Native previews: `../lg_wm4000hba/views/oblique - 3D View - oblique.png`, `../lg_wm4000hba/views/front - 3D View - front.png`.

## Visual review
Black Steel body, left detergent drawer/service panel, closed dark round door and right display are visible. Control legends, glass optics and local molded profiles remain simplified.

## Sources and access
- https://media.us.lg.com/m/1c4e8c8e7a284ef2/original/WM4000H_A-LG-Builder-Spec-Sheet.pdf

Manufacturer media were accessed through public product/download pages without a sign-in, new account, payment or acceptance interaction. No new redistribution license was inferred. Manufacturer copyright/terms remain applicable; this is an internal project working copy.
Original RFA hashes and source records are in `source_manifest.json`. An older download manifest can describe an overwritten ZIP filename; actual retained original RFA hashes, rather than a historical ZIP pathname, establish the source artifacts.

## Build and material dependencies
Entry point: `source/build.py`; shared implementation: `../build_custom.py` and `../family_common.py`. Always invoke the entry point by absolute path through the repository serialized Revit runner.
Manufacturer dimensions are fixed. Finish parameters are intended to flex. Companion uniform diffuse PNG files in `source/` are bound to appearance assets and checked after reopen. Revit stores their workstation paths; retain the source folder and relink/search that folder when relocating the family.

## Assumptions and limitations
- Black Steel selected by B suffix. Washer left hinge; closed-door visualization. Pedestal and stacking kit excluded.
- Visualization geometry; no MEP connectors, operating mechanisms or fabrication tolerances.
- Overall dimensions are manufacturer dimensions. Undimensioned seams, controls, edge radii and optical properties are inferred from product imagery.
- Fixed product dimensions; editable finish parameters are the intended flex controls.

## Row identity decisions
- One row is a washer/dryer pair: both separate native families are provided. Black Steel follows the B model suffix.
- One row is a washer/dryer pair. The stated WM4000HBA model controls the conflicting 5.0-cu-ft wording; no alternate washer was substituted.

## Blockers and disposition
No native save/reopen or placement blocker remains. Design identity, dimensional fit and material limitations above remain review holds. The section does not authorize procurement, installation or release for final visualization.
