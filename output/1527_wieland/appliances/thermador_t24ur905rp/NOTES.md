# Thermador T24UR905RP

Status: **DOWNLOADED**. Recorded 2026-10-02T14:36:37.480895+00:00.

Smartsheet row IDs: 6703228487401348.
RFA: `thermador_t24ur905rp/thermador_t24ur905rp_R2025.rfa`. SHA-256: `55160dd0481f77c496266aafce0b7967b81cf521bfea1dfe62e8d863447a8d24`.

## Native evidence
Revit 2025 save/reopen: PASS. Category: Specialty Equipment. Placement: WorkPlaneBased; actual test host: Floors.
Actual full placed bounds (W x D x H): **607.637 x 668.439 x 871.466 mm**.
Comparison target (W x D x H): 606.425 x 600.075 x 873.125 mm.
Dimension gate: **HOLD**; scope: full native geometry versus published appliance envelope.
Dimension basis: 23 7/8 x 23 5/8 x 34 3/8 in; source handle projection differs from appliance depth.
Delta against comparison target (W, D, H): +1.211580, +68.364087, -1.658638 mm.
Material parameter substitution with geometry evidence: 0/2. Zero exposed parameters means the manufacturer materials remain nested/fixed, not that editability passed.
Family warnings: 0; placed-project warnings: 0.

Detailed native results: `../thermador_t24ur905rp/validation.json`.
Native previews: `../thermador_t24ur905rp/views/placed_oblique - 3D View - placed_oblique.png`.

## Visual review
After the category-filter correction, the undercounter unit and glass-door outline are visible. Brown source panel and blue glazing are placeholder appearances; project finish is unapproved.

## Sources and access
- https://www.thermador.com/us/en/mkt-product/refrigeration/refrigerationrefrigerationcolumns/T24UR905RP
- https://media3.bsh-group.com/3D_Asset/21810566_T24UR905RP_TradeCAD.zip
- https://media3.bsh-group.com/Documents/19472937_T24UR905RP_UNDER_COUNTER_GLASS_DOOR_REFRIGERATOR_CUSTOM_PANEL_RIGHT_HINGED_Specifications.pdf

Manufacturer media were accessed through public product/download pages without a sign-in, new account, payment or acceptance interaction. No new redistribution license was inferred. Manufacturer copyright/terms remain applicable; this is an internal project working copy.
Original RFA hashes and source records are in `source_manifest.json`. An older download manifest can describe an overwritten ZIP filename; actual retained original RFA hashes, rather than a historical ZIP pathname, establish the source artifacts.

## Assumptions and limitations
- DOWNLOADED means a manufacturer model was recovered and a working Revit 2025 copy was saved/reopened. It does not mean all dimension, finish or design-identity gates passed.
- Native source geometry is preserved. Some projections can be handles, panels, flanges, feet or accessories. The recorded dimensional mismatch is unresolved unless a specific component comparison proves otherwise; do not scale the model silently.
- Category and hosting were normalized to Specialty Equipment / work plane placement. Missing source appearance assets were repaired from existing source colors where possible; optical fidelity is not established by that repair.
- Manufacturer materials can be nested/imported. Only the material substitutions explicitly evidenced in validation.json are verified.
- Full native geometry differs by more than 1 mm from at least one published envelope dimension. Do not treat as dimensional acceptance; compare handles, flanges, panels, feet and original source geometry.
- Some manufacturer materials are fixed/nested/imported or lack a confirmed top-level geometry binding; editable-material acceptance is limited.

## Row identity decisions
- ASSUMPTION / IDENTITY HOLD: the exact T24UR905RP product URL governs the working family. It is a 24-inch undercounter refrigerator; the row says 30-inch warming drawer. These are different appliances.

## Blockers and disposition
No native save/reopen or placement blocker remains. Design identity, dimensional fit and material limitations above remain review holds. The section does not authorize procurement, installation or release for final visualization.
