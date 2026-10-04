# Thermador PRD48WISGU

Status: **DOWNLOADED**. Recorded 2026-10-02T14:36:37.480895+00:00.

Smartsheet row IDs: 7647580173959044.
RFA: `thermador_prd48wisgu/thermador_prd48wisgu_R2025.rfa`. SHA-256: `e4311b255150c9aa0b701fa377a4b09237ba5c93e441d04fe16acc282ef29429`.

## Native evidence
Revit 2025 save/reopen: PASS. Category: Specialty Equipment. Placement: WorkPlaneBased; actual test host: Floors.
Actual full placed bounds (W x D x H): **1217.613 x 777.955 x 1035.050 mm**.
Comparison target (W x D x H): 1217.612 x 708.025 x 908.050 mm.
Dimension gate: **HOLD**; scope: full native geometry versus published appliance envelope.
Dimension basis: 47 15/16 x 27 7/8 x 35 3/4 in minimum height; adjustable to 36 3/4 in. Current 9/26 cut sheet.
Delta against comparison target (W, D, H): +0.000024, +69.930058, +126.999976 mm.
Material parameter substitution with geometry evidence: 6/6. Zero exposed parameters means the manufacturer materials remain nested/fixed, not that editability passed.
Family warnings: 0; placed-project warnings: 0.

Detailed native results: `../thermador_prd48wisgu/validation.json`.
Native previews: `../thermador_prd48wisgu/views/placed_oblique - 3D View - placed_oblique.png`.

## Visual review
Six gas burners plus the far-right induction surface and three lower compartments agree with the current manufacturer sheet. Native overall height/depth still exceed the specified appliance reference.

## Sources and access
- https://www.thermador.com/us/en/mkt-product/ranges/48-ranges/PRD48WISGU
- https://media3.bsh-group.com/3D_Asset/15842904_PRD48WISGU-Thermador-TradeCAD.zip
- https://media3.bsh-group.com/3D_Asset/29476114_PRD48WISGU_TradeCAD.zip
- https://media3.bsh-group.com/Documents/MCDOC02915579_PRD48WISGU-48-INCH-DUAL-FUEL-PRO-GRAND-RANGE-WITH-STEAM-AND-INDUCTION-Specifications.pdf

Manufacturer media were accessed through public product/download pages without a sign-in, new account, payment or acceptance interaction. No new redistribution license was inferred. Manufacturer copyright/terms remain applicable; this is an internal project working copy.
Original RFA hashes and source records are in `source_manifest.json`. An older download manifest can describe an overwritten ZIP filename; actual retained original RFA hashes, rather than a historical ZIP pathname, establish the source artifacts.

## Assumptions and limitations
- DOWNLOADED means a manufacturer model was recovered and a working Revit 2025 copy was saved/reopened. It does not mean all dimension, finish or design-identity gates passed.
- Native source geometry is preserved. Some projections can be handles, panels, flanges, feet or accessories. The recorded dimensional mismatch is unresolved unless a specific component comparison proves otherwise; do not scale the model silently.
- Category and hosting were normalized to Specialty Equipment / work plane placement. Missing source appearance assets were repaired from existing source colors where possible; optical fidelity is not established by that repair.
- Manufacturer materials can be nested/imported. Only the material substitutions explicitly evidenced in validation.json are verified.
- Full native geometry differs by more than 1 mm from at least one published envelope dimension. Do not treat as dimensional acceptance; compare handles, flanges, panels, feet and original source geometry.

## Row identity decisions
- ASSUMPTION / IDENTITY HOLD: exact URL model PRD48WISGU governs the working family. It is a 48-inch range with steam and induction; the row describes a 30-inch double/triple oven.

## Blockers and disposition
No native save/reopen or placement blocker remains. Design identity, dimensional fit and material limitations above remain review holds. The section does not authorize procurement, installation or release for final visualization.
