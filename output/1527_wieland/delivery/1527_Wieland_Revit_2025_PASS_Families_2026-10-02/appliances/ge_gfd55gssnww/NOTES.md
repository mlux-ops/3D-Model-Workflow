# GE GFD55GSSNWW

Status: **BUILT_WITH_LIMITATIONS**. Recorded 2026-10-02T14:36:37.480895+00:00.

Smartsheet row IDs: 5407997394747268.
RFA: `ge_gfd55gssnww/ge_gfd55gssnww_R2025.rfa`. SHA-256: `9563e29835dca39d9745dabac1787b6d576bd582b1643fd7ab70a4637f947747`.

## Native evidence
Revit 2025 save/reopen: PASS. Category: Specialty Equipment. Placement: WorkPlaneBased; actual test host: Floors.
Actual full placed bounds (W x D x H): **711.200 x 812.800 x 1009.650 mm**.
Comparison target (W x D x H): 711.200 x 812.800 x 1009.650 mm.
Dimension gate: **PASS**; scope: overall.
Dimension basis: 28 x 39 3/4 x 32 in, W x H x D; official GE product dimensions.
Delta against comparison target (W, D, H): -0.000024, +0.000024, +0.000000 mm.
Material parameter substitution with geometry evidence: 5/5. Zero exposed parameters means the manufacturer materials remain nested/fixed, not that editability passed.
Family warnings: 0; placed-project warnings: 0.

Detailed native results: `../ge_gfd55gssnww/validation.json`.
Native previews: `../ge_gfd55gssnww/views/oblique - 3D View - oblique.png`, `../ge_gfd55gssnww/views/front - 3D View - front.png`.

## Visual review
White dryer body and dark round door are visible; detergent/service drawer is absent. Fixed published size is verified, while molded fascia details remain image-derived.

## Sources and access
- https://www.geappliances.com/appliance/GE-ENERGY-STAR-7-8-cu-ft-Capacity-Smart-Front-Load-Gas-Dryer-with-Sanitize-Cycle-GFD55GSSNWW
- https://images.salsify.com/image/upload/s--VBxQtwSo--/5bb2a02635c02de483dad44b5d164513c2baf6de.pdf
- https://images.salsify.com/raw/upload/s--Ghj2_qby--/o7ndvfxdcod1hde4qmaf.dwg
- https://cdn11.bigcommerce.com/s-pacto3wrn2/products/137096/images/1017453/5679f1fe5c4b18b59ba9fa7c79c67269dcf5d9e9__18687.1776494511.386.513.jpg?c=2

Manufacturer media were accessed through public product/download pages without a sign-in, new account, payment or acceptance interaction. No new redistribution license was inferred. Manufacturer copyright/terms remain applicable; this is an internal project working copy.
Original RFA hashes and source records are in `source_manifest.json`. An older download manifest can describe an overwritten ZIP filename; actual retained original RFA hashes, rather than a historical ZIP pathname, establish the source artifacts.

## Build and material dependencies
Entry point: `source/build.py`; shared implementation: `../build_custom.py` and `../family_common.py`. Always invoke the entry point by absolute path through the repository serialized Revit runner.
Manufacturer dimensions are fixed. Finish parameters are intended to flex. Companion uniform diffuse PNG files in `source/` are bound to appearance assets and checked after reopen. Revit stores their workstation paths; retain the source folder and relink/search that folder when relocating the family.

## Assumptions and limitations
- Corrected gas dryer GFD55GSSNWW governs; obsolete electric-model row text is not the model authority. Reversible door depicted right-hinged.
- Visualization geometry; no MEP connectors, operating mechanisms or fabrication tolerances.
- Overall dimensions are manufacturer dimensions. Undimensioned seams, controls, edge radii and optical properties are inferred from product imagery.
- Fixed product dimensions; editable finish parameters are the intended flex controls.
- The official 3D DWG is retained under `source/` as reference. Its audit candidate is not the delivered RFA: washer geometry is mesh-only and has a deeper envelope; dryer default units were inconsistent. The native editable family uses the published overall dimensions and image-derived face details.
- Control legends and exact molded/vent profiles are simplified; no close-up photographic equivalence is claimed.

## Row identity decisions
- The supplied correction GFD55GSSNWW gas dryer governs the obsolete electric-model wording.

## Blockers and disposition
No native save/reopen or placement blocker remains. Design identity, dimensional fit and material limitations above remain review holds. The section does not authorize procurement, installation or release for final visualization.
