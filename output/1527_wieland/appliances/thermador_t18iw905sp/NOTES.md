# Thermador T18IW905SP

Status: **DOWNLOADED**. Recorded 2026-10-02T14:36:37.480895+00:00.

Smartsheet row IDs: 2705397813673860.
RFA: `thermador_t18iw905sp/thermador_t18iw905sp_R2025.rfa`. SHA-256: `96d62d335c78b32e40359a88210d9b5c40214a909fa105c5f81f42c89bee3cbd`.

## Native evidence
Revit 2025 save/reopen: PASS. Category: Specialty Equipment. Placement: WorkPlaneBased; actual test host: Floors.
Actual full placed bounds (W x D x H): **451.000 x 643.510 x 2134.000 mm**.
Comparison target (W x D x H): 450.850 x 609.600 x 2127.250 mm.
Dimension gate: **HOLD**; scope: full native geometry versus published appliance envelope.
Dimension basis: 17 3/4 x 24 x 83 3/4 in; foot setting and handle/panel inclusion need comparison.
Delta against comparison target (W, D, H): +0.150015, +33.910357, +6.749976 mm.
Material parameter substitution with geometry evidence: 4/5. Zero exposed parameters means the manufacturer materials remain nested/fixed, not that editability passed.
Family warnings: 0; placed-project warnings: 0.

Detailed native results: `../thermador_t18iw905sp/validation.json`.
Native previews: `../thermador_t18iw905sp/views/placed_oblique - 3D View - placed_oblique.png`.

## Visual review
Tall wine-column exterior and long handle are visible, but the glass/interior reads opaque in the native source preview. Treat as an exterior proxy until glazing/interior finish is resolved.

## Sources and access
- https://www.thermador.com/us/en/mkt-product/refrigeration/wine-refrigeration/T18IW905SP
- https://media3.bsh-group.com/3D_Asset/16603829_T18IW905SP-Thermador-TradeCAD.zip
- https://media3.bsh-group.com/Documents/16173464_T18IW905SP-18-INCH-FLUSH-CUSTOM-WINE-PRESERVATION-COLUMN-Specifications.pdf

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
- ASSUMPTION: abbreviated T18IW905S link resolves to the official panel-ready T18IW905SP model. The full suffix is a working selection requiring design confirmation.

## Blockers and disposition
No native save/reopen or placement blocker remains. Design identity, dimensional fit and material limitations above remain review holds. The section does not authorize procurement, installation or release for final visualization.
