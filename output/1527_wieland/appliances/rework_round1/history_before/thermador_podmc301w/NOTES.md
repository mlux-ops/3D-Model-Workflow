# Thermador PODMC301W

Status: **DOWNLOADED**. Recorded 2026-10-02T14:36:37.480895+00:00.

Smartsheet row IDs: 2199628860030852.
RFA: `thermador_podmc301w/thermador_podmc301w_R2025.rfa`. SHA-256: `2c5c54e83c38b0cdc2619f61ce089b47df09b5f52bf4f7bcf89ca3585b1f0ae5`.

## Native evidence
Revit 2025 save/reopen: PASS. Category: Specialty Equipment. Placement: WorkPlaneBased; actual test host: Floors.
Actual full placed bounds (W x D x H): **755.650 x 684.314 x 1244.600 mm**.
Comparison target (W x D x H): 755.650 x 622.300 x 1244.600 mm.
Dimension gate: **HOLD**; scope: full native geometry versus published appliance envelope.
Dimension basis: 29 3/4 x 24 1/2 x 49 in appliance body; handle projection additional.
Delta against comparison target (W, D, H): +0.000024, +62.014335, +0.000048 mm.
Material parameter substitution with geometry evidence: 4/4. Zero exposed parameters means the manufacturer materials remain nested/fixed, not that editability passed.
Family warnings: 1; placed-project warnings: 0.
- Warning: Extrusion is too thin.

Detailed native results: `../thermador_podmc301w/validation.json`.
Native previews: `../thermador_podmc301w/views/placed_oblique - 3D View - placed_oblique.png`.

## Visual review
Stacked speed and full-size ovens with separate controls/pulls are visible. Native source has one warning and a larger full-depth envelope.

## Sources and access
- https://www.thermador.com/us/en/mkt-product/ovens/double-ovens/PODMC301W
- https://media3.bsh-group.com/3D_Asset/15838407_PODMC301W-Thermador-TradeCAD.zip
- https://media3.bsh-group.com/3D_Asset/29273463_PODMC301W_TradeCAD.zip
- https://media3.bsh-group.com/Documents/MCDOC02802507_PODMC301W-30-INCH-DOUBLE-COMBINATION-BUILT-IN-OVEN-WITH-SPEED-OVEN-Specifications.pdf

Manufacturer media were accessed through public product/download pages without a sign-in, new account, payment or acceptance interaction. No new redistribution license was inferred. Manufacturer copyright/terms remain applicable; this is an internal project working copy.
Original RFA hashes and source records are in `source_manifest.json`. An older download manifest can describe an overwritten ZIP filename; actual retained original RFA hashes, rather than a historical ZIP pathname, establish the source artifacts.

## Assumptions and limitations
- DOWNLOADED means a manufacturer model was recovered and a working Revit 2025 copy was saved/reopened. It does not mean all dimension, finish or design-identity gates passed.
- Native source geometry is preserved. Some projections can be handles, panels, flanges, feet or accessories. The recorded dimensional mismatch is unresolved unless a specific component comparison proves otherwise; do not scale the model silently.
- Category and hosting were normalized to Specialty Equipment / work plane placement. Missing source appearance assets were repaired from existing source colors where possible; optical fidelity is not established by that repair.
- Manufacturer materials can be nested/imported. Only the material substitutions explicitly evidenced in validation.json are verified.
- Full native geometry differs by more than 1 mm from at least one published envelope dimension. Do not treat as dimensional acceptance; compare handles, flanges, panels, feet and original source geometry.

## Blockers and disposition
No native save/reopen or placement blocker remains. Design identity, dimensional fit and material limitations above remain review holds. The section does not authorize procurement, installation or release for final visualization.
