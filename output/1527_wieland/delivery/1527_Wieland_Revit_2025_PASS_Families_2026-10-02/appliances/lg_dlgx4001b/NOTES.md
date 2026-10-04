# LG DLGX4001B

Status: **BUILT_WITH_LIMITATIONS**. Recorded 2026-10-02T14:36:37.480895+00:00.

Smartsheet row IDs: 3292695531945860, 4443914724376452.
RFA: `lg_dlgx4001b/lg_dlgx4001b_R2025.rfa`. SHA-256: `17406675cb26e611a8150e987985228ec68f1bf1abfc3ea11f5235d29420f911`.

## Native evidence
Revit 2025 save/reopen: PASS. Category: Specialty Equipment. Placement: WorkPlaneBased; actual test host: Floors.
Actual full placed bounds (W x D x H): **685.800 x 765.175 x 990.600 mm**.
Comparison target (W x D x H): 685.800 x 765.175 x 990.600 mm.
Dimension gate: **PASS**; scope: overall.
Dimension basis: 27 x 39 x 30 1/8 in, W x H x D; LG manufacturer specification, gas section.
Delta against comparison target (W, D, H): +0.000000, +0.000024, +0.000000 mm.
Material parameter substitution with geometry evidence: 5/5. Zero exposed parameters means the manufacturer materials remain nested/fixed, not that editability passed.
Family warnings: 0; placed-project warnings: 0.

Detailed native results: `../lg_dlgx4001b/validation.json`.
Native previews: `../lg_dlgx4001b/views/oblique - 3D View - oblique.png`, `../lg_dlgx4001b/views/front - 3D View - front.png`.

## Visual review
Black Steel dryer has the round dark door and right display without a washer detergent/service panel. Reversible door is depicted with the documented right hinge assumption.

## Sources and access
- https://content.abt.com/documents/129668/SpecificationSheet-DLXX400X-1.pdf

Manufacturer media were accessed through public product/download pages without a sign-in, new account, payment or acceptance interaction. No new redistribution license was inferred. Manufacturer copyright/terms remain applicable; this is an internal project working copy.
Original RFA hashes and source records are in `source_manifest.json`. An older download manifest can describe an overwritten ZIP filename; actual retained original RFA hashes, rather than a historical ZIP pathname, establish the source artifacts.

## Build and material dependencies
Entry point: `source/build.py`; shared implementation: `../build_custom.py` and `../family_common.py`. Always invoke the entry point by absolute path through the repository serialized Revit runner.
Manufacturer dimensions are fixed. Finish parameters are intended to flex. Companion uniform diffuse PNG files in `source/` are bound to appearance assets and checked after reopen. Revit stores their workstation paths; retain the source folder and relink/search that folder when relocating the family.

## Assumptions and limitations
- Black Steel selected by B suffix. Reversible dryer door depicted right-hinged; no pedestal.
- Visualization geometry; no MEP connectors, operating mechanisms or fabrication tolerances.
- Overall dimensions are manufacturer dimensions. Undimensioned seams, controls, edge radii and optical properties are inferred from product imagery.
- Fixed product dimensions; editable finish parameters are the intended flex controls.

## Row identity decisions
- One row is a washer/dryer pair: both separate native families are provided. Black Steel follows the B model suffix.
- One row is a washer/dryer pair. The stated WM4000HBA model controls the conflicting 5.0-cu-ft wording; no alternate washer was substituted.

## Blockers and disposition
No native save/reopen or placement blocker remains. Design identity, dimensional fit and material limitations above remain review holds. The section does not authorize procurement, installation or release for final visualization.
