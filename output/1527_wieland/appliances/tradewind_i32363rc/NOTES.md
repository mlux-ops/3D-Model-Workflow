# Trade-Wind I32363RC

Status: **BUILT_WITH_LIMITATIONS**. Recorded 2026-10-02T14:36:37.480895+00:00.

Smartsheet row IDs: 7796295159316356, 162646177939332.
RFA: `tradewind_i32363rc/tradewind_i32363rc_R2025.rfa`. SHA-256: `46516fd5c3b343401fc349301975758c85c1d97e5892c807b790b660b3d81f2d`.

## Native evidence
Revit 2025 save/reopen: PASS. Category: Specialty Equipment. Placement: WorkPlaneBased; actual test host: Floors.
Actual full placed bounds (W x D x H): **873.125 x 266.700 x 355.600 mm**.
Comparison target (W x D x H): 873.125 x 266.700 x 330.200 mm.
Dimension gate: **PASS**; scope: body.
Dimension basis: 34 3/8 x 13 x 10 1/2 in body W x H x D; I3236-model drawing page 2; 7-inch round collar for I32363RC.
Delta against comparison target (W, D, H): -0.000024, +0.000000, +0.000012 mm.
Material parameter substitution with geometry evidence: 3/3. Zero exposed parameters means the manufacturer materials remain nested/fixed, not that editability passed.
Family warnings: 0; placed-project warnings: 0.

Detailed native results: `../tradewind_i32363rc/validation.json`.
Native previews: `../tradewind_i32363rc/views/oblique - 3D View - oblique.png`, `../tradewind_i32363rc/views/front - 3D View - front.png`.

## Visual review
Underside view shows two baffle filters and controls/light in a stainless insert body. Collar extension and small filter/control details are inferred.

## Sources and access
- https://linqcdn.avbportal.com/documents/3512c644-ff49-413e-aaf5-5805aa9aad84.pdf

Manufacturer media were accessed through public product/download pages without a sign-in, new account, payment or acceptance interaction. No new redistribution license was inferred. Manufacturer copyright/terms remain applicable; this is an internal project working copy.
Original RFA hashes and source records are in `source_manifest.json`. An older download manifest can describe an overwritten ZIP filename; actual retained original RFA hashes, rather than a historical ZIP pathname, establish the source artifacts.

## Build and material dependencies
Entry point: `source/build.py`; shared implementation: `../build_custom.py` and `../family_common.py`. Always invoke the entry point by absolute path through the repository serialized Revit runner.
Manufacturer dimensions are fixed. Finish parameters are intended to flex. Companion uniform diffuse PNG files in `source/` are bound to appearance assets and checked after reopen. Revit stores their workstation paths; retain the source folder and relink/search that folder when relocating the family.

## Assumptions and limitations
- Specified Trade-Wind model governs conflicting Zephyr vendor text. Two filters and one LED light.
- Duct collar extension is inferred as 25.4 mm above the 13-inch body. Filter blade pitch and light/control recess details are image-derived.
- Visualization geometry; no MEP connectors, operating mechanisms or fabrication tolerances.
- Overall dimensions are manufacturer dimensions. Undimensioned seams, controls, edge radii and optical properties are inferred from product imagery.
- Fixed product dimensions; editable finish parameters are the intended flex controls.
- Overall height with collar is reported separately; the manufacturer body-height dimension does not establish collar extension.

## Row identity decisions
- The explicit Trade-Wind I32363RC model governs the conflicting Zephyr vendor/description text.
- The explicit Trade-Wind I32363RC model governs the conflicting Zephyr vendor/description text.

## Blockers and disposition
No native save/reopen or placement blocker remains. Design identity, dimensional fit and material limitations above remain review holds. The section does not authorize procurement, installation or release for final visualization.
