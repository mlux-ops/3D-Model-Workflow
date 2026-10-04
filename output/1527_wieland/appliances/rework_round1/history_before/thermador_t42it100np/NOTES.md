# Thermador T42IT100NP

Status: **DOWNLOADED**. Recorded 2026-10-02T14:36:37.480895+00:00.

Smartsheet row IDs: 7829128394243972.
RFA: `thermador_t42it100np/thermador_t42it100np_R2025.rfa`. SHA-256: `41a0d65b3a5640a1b23f6b3e0fc1787e0d60b708caa0cd3a625e85b980ce06f1`.

## Native evidence
Revit 2025 save/reopen: PASS. Category: Specialty Equipment. Placement: WorkPlaneBased; actual test host: Floors.
Actual full placed bounds (W x D x H): **1110.430 x 684.136 x 2145.254 mm**.
Comparison target (W x D x H): 1048.000 x 608.000 x 2123.000 mm.
Dimension gate: **HOLD**; scope: full native geometry versus published appliance envelope.
Dimension basis: Published metric appliance dimensions, excluding customer panels.
Delta against comparison target (W, D, H): +62.429604, +76.136293, +22.253504 mm.
Material parameter substitution with geometry evidence: 0/2. Zero exposed parameters means the manufacturer materials remain nested/fixed, not that editability passed.
Family warnings: 0; placed-project warnings: 0.

Detailed native results: `../thermador_t42it100np/validation.json`.
Native previews: `../thermador_t42it100np/views/placed_oblique - 3D View - placed_oblique.png`.

## Visual review
After the category-filter correction, imported French doors, two freezer drawers and assembly edges are visible. Black imported shading and oversized full envelope remain fit/finish holds.

## Sources and access
- https://www.thermador.com/us/en/mkt-product/refrigeration/bottom-freezer-refrigerators/T42IT100NP
- https://media3.bsh-group.com/3D_Asset/22537542_T42IT100NP_TradeCADs.zip
- https://media3.bsh-group.com/Documents/25549017_T42IT100NP-42-INCH-BUILT-IN-FRENCH-DOOR_REFRIGERATOR-2-DRAWER-PANEL-READY-Specifications.pdf

Manufacturer media were accessed through public product/download pages without a sign-in, new account, payment or acceptance interaction. No new redistribution license was inferred. Manufacturer copyright/terms remain applicable; this is an internal project working copy.
Original RFA hashes and source records are in `source_manifest.json`. An older download manifest can describe an overwritten ZIP filename; actual retained original RFA hashes, rather than a historical ZIP pathname, establish the source artifacts.

## Assumptions and limitations
- DOWNLOADED means a manufacturer model was recovered and a working Revit 2025 copy was saved/reopened. It does not mean all dimension, finish or design-identity gates passed.
- Native source geometry is preserved. Some projections can be handles, panels, flanges, feet or accessories. The recorded dimensional mismatch is unresolved unless a specific component comparison proves otherwise; do not scale the model silently.
- Category and hosting were normalized to Specialty Equipment / work plane placement. Missing source appearance assets were repaired from existing source colors where possible; optical fidelity is not established by that repair.
- Manufacturer materials can be nested/imported. Only the material substitutions explicitly evidenced in validation.json are verified.
- Full native geometry differs by more than 1 mm from at least one published envelope dimension. Do not treat as dimensional acceptance; compare handles, flanges, panels, feet and original source geometry.
- Some manufacturer materials are fixed/nested/imported or lack a confirmed top-level geometry binding; editable-material acceptance is limited.

## Blockers and disposition
No native save/reopen or placement blocker remains. Design identity, dimensional fit and material limitations above remain review holds. The section does not authorize procurement, installation or release for final visualization.
