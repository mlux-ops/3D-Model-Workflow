# Thermador WD30W

Status: **DOWNLOADED**. Recorded 2026-10-02T14:36:37.480895+00:00.

Smartsheet row IDs: 4451428673716100.
RFA: `thermador_wd30w/thermador_wd30w_R2025.rfa`. SHA-256: `b1a2a7978ac8fe613780eb4be646ae72bf10222c606f9361b1d32b6ab5ba2f80`.

## Native evidence
Revit 2025 save/reopen: PASS. Category: Specialty Equipment. Placement: WorkPlaneBased; actual test host: Floors.
Actual full placed bounds (W x D x H): **755.650 x 681.287 x 239.712 mm**.
Comparison target (W x D x H): 755.650 x 622.300 x 239.713 mm.
Dimension gate: **HOLD**; scope: full native geometry versus published appliance envelope.
Dimension basis: 29 3/4 x 24 1/2 x 9 7/16 in with 3/4-inch customer panel; handle projection additional.
Delta against comparison target (W, D, H): +0.000024, +58.987194, -0.000006 mm.
Material parameter substitution with geometry evidence: 2/2. Zero exposed parameters means the manufacturer materials remain nested/fixed, not that editability passed.
Family warnings: 0; placed-project warnings: 0.

Detailed native results: `../thermador_wd30w/validation.json`.
Native previews: `../thermador_wd30w/views/placed_oblique - 3D View - placed_oblique.png`.

## Visual review
Single warming-drawer front and horizontal pull are visible. This is not the Zephyr hood described in the conflicting row; customer panel/handle configuration remains an assumption.

## Sources and access
- https://www.thermador.com/us/en/mkt-product/ovens/warming-drawers/WD30W
- https://media3.bsh-group.com/3D_Asset/15803179_WD30W-Thermador-TradeCAD.zip
- https://media3.bsh-group.com/Documents/MCDOC02802519_WD30W-30-INCH-CUSTOM-PANEL-WARMING-DRAWER-Specifications.pdf

Manufacturer media were accessed through public product/download pages without a sign-in, new account, payment or acceptance interaction. No new redistribution license was inferred. Manufacturer copyright/terms remain applicable; this is an internal project working copy.
Original RFA hashes and source records are in `source_manifest.json`. An older download manifest can describe an overwritten ZIP filename; actual retained original RFA hashes, rather than a historical ZIP pathname, establish the source artifacts.

## Assumptions and limitations
- DOWNLOADED means a manufacturer model was recovered and a working Revit 2025 copy was saved/reopened. It does not mean all dimension, finish or design-identity gates passed.
- Native source geometry is preserved. Some projections can be handles, panels, flanges, feet or accessories. The recorded dimensional mismatch is unresolved unless a specific component comparison proves otherwise; do not scale the model silently.
- Category and hosting were normalized to Specialty Equipment / work plane placement. Missing source appearance assets were repaired from existing source colors where possible; optical fidelity is not established by that repair.
- Manufacturer materials can be nested/imported. Only the material substitutions explicitly evidenced in validation.json are verified.
- Full native geometry differs by more than 1 mm from at least one published envelope dimension. Do not treat as dimensional acceptance; compare handles, flanges, panels, feet and original source geometry.

## Row identity decisions
- ASSUMPTION / IDENTITY HOLD: exact URL and manufacturer indicate Thermador WD30W warming drawer; the row description instead identifies a Zephyr 47-inch hood. The family is explicitly WD30W, not a hood.

## Blockers and disposition
No native save/reopen or placement blocker remains. Design identity, dimensional fit and material limitations above remain review holds. The section does not authorize procurement, installation or release for final visualization.
