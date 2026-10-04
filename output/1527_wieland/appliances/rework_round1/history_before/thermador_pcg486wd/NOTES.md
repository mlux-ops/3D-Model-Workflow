# Thermador PCG486WD

Status: **DOWNLOADED**. Recorded 2026-10-02T14:36:37.480895+00:00.

Smartsheet row IDs: 8955028301086596.
RFA: `thermador_pcg486wd/thermador_pcg486wd_R2025.rfa`. SHA-256: `356457f2f43ca992a3c733ae59c551261e8d6ff28701e31d4947a7fc7d78f0aa`.

## Native evidence
Revit 2025 save/reopen: PASS. Category: Specialty Equipment. Placement: WorkPlaneBased; actual test host: Floors.
Actual full placed bounds (W x D x H): **1219.250 x 685.875 x 223.535 mm**.
Comparison target (W x D x H): 1217.612 x 655.638 x 206.375 mm.
Dimension gate: **HOLD**; scope: full native geometry versus published appliance envelope.
Dimension basis: 47 15/16 x 25 13/16 x 8 1/8 in published appliance dimensions; native grate/knob configuration is compared explicitly.
Delta against comparison target (W, D, H): +1.637497, +30.237495, +17.159739 mm.
Material parameter substitution with geometry evidence: 3/3. Zero exposed parameters means the manufacturer materials remain nested/fixed, not that editability passed.
Family warnings: 0; placed-project warnings: 0.

Detailed native results: `../thermador_pcg486wd/validation.json`.
Native previews: `../thermador_pcg486wd/views/placed_oblique - 3D View - placed_oblique.png`.

## Visual review
Six burners and the central griddle are visible. Source dimensions differ from the current cut sheet; grates/controls are manufacturer model geometry rather than accepted fabrication dimensions.

## Sources and access
- https://www.thermador.com/us/en/mkt-product/cooktops-rangetops/rangetops/PCG486WD
- https://media3.bsh-group.com/3D_Asset/15802529_PCG486WD-Thermador-TradeCAD.zip
- https://media3.bsh-group.com/3D_Asset/29485643_PCG486WD_TradeCAD.zip
- https://media3.bsh-group.com/Documents/MCDOC02690629_PCG486WD-48-INCH-GAS-RANGETOP-WITH-GRIDDLE-Specifications.pdf

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
