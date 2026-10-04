# Summit SDHWC98PNR

Status: **BUILT_WITH_LIMITATIONS**. Recorded 2026-10-02T14:36:37.480895+00:00.

Smartsheet row IDs: 6521680267116420.
RFA: `summit_sdhwc98pnr/summit_sdhwc98pnr_R2025.rfa`. SHA-256: `dd76bf969af45350272b23ba17cc9c5b74566027149c5f0ee2e63f0b38016eeb`.

## Native evidence
Revit 2025 save/reopen: PASS. Category: Specialty Equipment. Placement: WorkPlaneBased; actual test host: Floors.
Actual full placed bounds (W x D x H): **596.900 x 457.200 x 1822.450 mm**.
Comparison target (W x D x H): 596.900 x 457.200 x 1822.450 mm.
Dimension gate: **PASS**; scope: overall.
Dimension basis: 23.5 x 71.75 x 18 in, W x H x D, factory appliance envelope without optional customer panel.
Delta against comparison target (W, D, H): +0.000012, +0.000000, -0.000048 mm.
Material parameter substitution with geometry evidence: 5/5. Zero exposed parameters means the manufacturer materials remain nested/fixed, not that editability passed.
Family warnings: 0; placed-project warnings: 0.

Detailed native results: `../summit_sdhwc98pnr/validation.json`.
Native previews: `../summit_sdhwc98pnr/views/oblique - 3D View - oblique.png`, `../summit_sdhwc98pnr/views/front - 3D View - front.png`.

## Visual review
Revised native view shows two zones, sixteen wire shelves, metallic shelf fronts, transparent door and vertical lower grille. Customer overlay and pull remain absent; exact interior spacing and optical appearance are inferred.

## Sources and access
- https://www.summitappliance.com/catalog/model/SDHWC98PNR
- https://www.summitappliance.com/brochure/8799.pdf
- https://drtr5fjqqz6ee.cloudfront.net/uploads/fsi/drawing/file/16133/SDHWC98PNR-Assembly.pdf
- https://drtr5fjqqz6ee.cloudfront.net/uploads/fsi/product_image/image/89059/SDHWC98PNR_Front_PR.jpg

Manufacturer media were accessed through public product/download pages without a sign-in, new account, payment or acceptance interaction. No new redistribution license was inferred. Manufacturer copyright/terms remain applicable; this is an internal project working copy.
Original RFA hashes and source records are in `source_manifest.json`. An older download manifest can describe an overwritten ZIP filename; actual retained original RFA hashes, rather than a historical ZIP pathname, establish the source artifacts.

## Build and material dependencies
Entry point: `source/build.py`; shared implementation: `../build_custom.py` and `../family_common.py`. Always invoke the entry point by absolute path through the repository serialized Revit runner.
Manufacturer dimensions are fixed. Finish parameters are intended to flex. Companion uniform diffuse PNG files in `source/` are bound to appearance assets and checked after reopen. Revit stores their workstation paths; retain the source folder and relink/search that folder when relocating the family.

## Assumptions and limitations
- Panel-ready appliance represented before customer panel/pull installation; no cabinet finish has been selected.
- Two temperature zones and 16 shelves represented; exact shelf spacing, internal clearances and glass tint inferred.
- Visualization geometry; no MEP connectors, operating mechanisms or fabrication tolerances.
- Overall dimensions are manufacturer dimensions. Undimensioned seams, controls, edge radii and optical properties are inferred from product imagery.
- Fixed product dimensions; editable finish parameters are the intended flex controls.
- Customer overlay panel and pull excluded; their thickness and projections would change installed envelope.

## Blockers and disposition
No native save/reopen or placement blocker remains. Design identity, dimensional fit and material limitations above remain review holds. The section does not authorize procurement, installation or release for final visualization.
