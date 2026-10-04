# Miele KWT 6722 iS

Status: **DOWNLOADED**. Recorded 2026-10-02T14:36:37.480895+00:00.

Smartsheet row IDs: 7384660666023812.
RFA: `miele_kwt6722is/miele_kwt6722is_R2025.rfa`. SHA-256: `b6d424fe8d51979c0b5f753df9e4485767182ab63fa86aba7f7677e7bd500318`.

## Native evidence
Revit 2025 save/reopen: PASS. Category: Specialty Equipment. Placement: WorkPlaneBased; actual test host: Floors.
Actual full placed bounds (W x D x H): **558.500 x 560.000 x 1770.000 mm**.
Comparison target (W x D x H): 557.000 x 553.000 x 1770.000 mm.
Dimension gate: **HOLD**; scope: full native geometry versus published appliance envelope.
Dimension basis: Appliance body dimensions; installation flanges/projections may enlarge native envelope.
Delta against comparison target (W, D, H): +1.500012, +7.000000, -0.000045 mm.
Material parameter substitution with geometry evidence: 0/0. Zero exposed parameters means the manufacturer materials remain nested/fixed, not that editability passed.
Family warnings: 0; placed-project warnings: 0.

Detailed native results: `../miele_kwt6722is/validation.json`.
Native previews: `../miele_kwt6722is/views/placed_oblique - 3D View - placed_oblique.png`.

## Visual review
Tall wine-unit shelves and glazing are visible, but a conspicuous blue internal source component remains. This is a finish-review hold; the manufacturer model is not visually release-ready.

## Sources and access
- https://www.mieleusa.com/product/11329860/24-built-in-wine-refrigerator-kwt-6722-is
- https://media.miele.com/downloads/a5/52/05_70A8A51285B71FE1ABFA89BF1ABCA552.zip
- https://media.miele.com/downloads/n-/us/FS_11329860_USE_US-en-US.pdf

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
