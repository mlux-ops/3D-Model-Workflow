# Miele H 7270 BM

Status: **DOWNLOADED**. Recorded 2026-10-02T14:36:37.480895+00:00.

Smartsheet row IDs: 8816514970877828, 6403663455649668.
RFA: `miele_h7270bm/miele_h7270bm_R2025.rfa`. SHA-256: `4f9956271a11bf762ba499664915314ce8b19d790dd946eaf7e8a36ea5f50ac7`.

## Native evidence
Revit 2025 save/reopen: PASS. Category: Specialty Equipment. Placement: WorkPlaneBased; actual test host: Floors.
Actual full placed bounds (W x D x H): **757.000 x 619.000 x 479.000 mm**.
Comparison target (W x D x H): 757.000 x 573.000 x 479.000 mm.
Dimension gate: **HOLD**; scope: full native geometry versus published appliance envelope.
Dimension basis: Current product-sheet page 2 explicitly states 757 W x 479 H x 573 D mm. Native projections are measured separately.
Delta against comparison target (W, D, H): +0.000014, +46.000003, +0.000014 mm.
Material parameter substitution with geometry evidence: 0/0. Zero exposed parameters means the manufacturer materials remain nested/fixed, not that editability passed.
Family warnings: 0; placed-project warnings: 0.

Detailed native results: `../miele_h7270bm/validation.json`.
Native previews: `../miele_h7270bm/views/placed_oblique - 3D View - placed_oblique.png`.

## Visual review
Black compact oven fascia and handle profile are visible. Nested manufacturer materials and the published-depth discrepancy remain unresolved.

## Sources and access
- https://www.mieleusa.com/product/11968190/30-speed-oven-h-7270-bm-obsidian-black
- https://media.miele.com/downloads/8b/20/02_C7F138387FFA1FD189C793AEE9B58B20.zip
- https://media.miele.com/downloads/n-/us/FS_11968190_USE_US-en-US.pdf

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
