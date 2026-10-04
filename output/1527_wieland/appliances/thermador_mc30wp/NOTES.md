# Thermador MC30WP

Status: **DOWNLOADED**. Recorded 2026-10-02T14:36:37.480895+00:00.

Smartsheet row IDs: 2018080639745924.
RFA: `thermador_mc30wp/thermador_mc30wp_R2025.rfa`. SHA-256: `1ef4c23faddae67bf049bd9d27e05410ac714ddfc5e9a04ff0ac924ad3b83816`.

## Native evidence
Revit 2025 save/reopen: PASS. Category: Specialty Equipment. Placement: WorkPlaneBased; actual test host: Floors.
Actual full placed bounds (W x D x H): **755.650 x 549.383 x 498.475 mm**.
Comparison target (W x D x H): 755.650 x 568.325 x 498.475 mm.
Dimension gate: **HOLD**; scope: full native geometry versus published appliance envelope.
Dimension basis: 29 3/4 x 22 3/8 x 19 5/8 in; verify cut-sheet depth convention.
Delta against comparison target (W, D, H): +0.000024, -18.941528, -0.000012 mm.
Material parameter substitution with geometry evidence: 6/6. Zero exposed parameters means the manufacturer materials remain nested/fixed, not that editability passed.
Family warnings: 0; placed-project warnings: 0.

Detailed native results: `../thermador_mc30wp/validation.json`.
Native previews: `../thermador_mc30wp/views/placed_oblique - 3D View - placed_oblique.png`.

## Visual review
Compact oven, two control knobs and horizontal pull match the manufacturer type. Source depth is shorter than the published overall reference; do not accept the fit silently.

## Sources and access
- https://www.thermador.com/us/en/mkt-product/ovens/speed-ovens/MC30WP
- https://media3.bsh-group.com/3D_Asset/15803255_MC30WP-Thermador-TradeCAD.zip
- https://media3.bsh-group.com/3D_Asset/29278877_MC30WP_TradeCAD.zip
- https://media3.bsh-group.com/Documents/MCDOC02760739_MC30WP-30-INCH-SPEED-OVEN-PROFESSIONAL-SERIES-Specifications.pdf

Manufacturer media were accessed through public product/download pages without a sign-in, new account, payment or acceptance interaction. No new redistribution license was inferred. Manufacturer copyright/terms remain applicable; this is an internal project working copy.
Original RFA hashes and source records are in `source_manifest.json`. An older download manifest can describe an overwritten ZIP filename; actual retained original RFA hashes, rather than a historical ZIP pathname, establish the source artifacts.

## Assumptions and limitations
- DOWNLOADED means a manufacturer model was recovered and a working Revit 2025 copy was saved/reopened. It does not mean all dimension, finish or design-identity gates passed.
- Native source geometry is preserved. Some projections can be handles, panels, flanges, feet or accessories. The recorded dimensional mismatch is unresolved unless a specific component comparison proves otherwise; do not scale the model silently.
- Category and hosting were normalized to Specialty Equipment / work plane placement. Missing source appearance assets were repaired from existing source colors where possible; optical fidelity is not established by that repair.
- Manufacturer materials can be nested/imported. Only the material substitutions explicitly evidenced in validation.json are verified.
- Full native geometry differs by more than 1 mm from at least one published envelope dimension. Do not treat as dimensional acceptance; compare handles, flanges, panels, feet and original source geometry.

## Row identity decisions
- ASSUMPTION: MC30WP is the manufacturer Professional-series 30-inch 1.6-cu-ft speed oven matching the description. The row has no exact SKU or URL.

## Blockers and disposition
No native save/reopen or placement blocker remains. Design identity, dimensional fit and material limitations above remain review holds. The section does not authorize procurement, installation or release for final visualization.
