# Miele G 5051 SCVi ADA

Status: **DOWNLOADED**. Recorded 2026-10-02T14:36:37.480895+00:00.

Smartsheet row IDs: 3328172767117188, 904397767376772.
RFA: `miele_g5051scvi/miele_g5051scvi_R2025.rfa`. SHA-256: `27391211e2833b4185affafe8f8bf49126ed9e20b216479b254294c4227ba10f`.

## Native evidence
Revit 2025 save/reopen: PASS. Category: Specialty Equipment. Placement: WorkPlaneBased; actual test host: Floors.
Actual full placed bounds (W x D x H): **598.000 x 551.000 x 805.000 mm**.
Comparison target (W x D x H): 598.000 x 550.000 x 815.000 mm.
Dimension gate: **HOLD**; scope: full native geometry versus published appliance envelope.
Dimension basis: Current product sheet states 598 W x 815 H x 550 D mm. The downloaded ADA model is 805 mm high; this difference is not accepted silently.
Delta against comparison target (W, D, H): +0.000018, +1.000007, -10.000008 mm.
Material parameter substitution with geometry evidence: 0/0. Zero exposed parameters means the manufacturer materials remain nested/fixed, not that editability passed.
Family warnings: 0; placed-project warnings: 0.

Detailed native results: `../miele_g5051scvi/validation.json`.
Native previews: `../miele_g5051scvi/views/placed_oblique - 3D View - placed_oblique.png`.

## Visual review
Closed integrated dishwasher body, top control edge and toe recess are visible. Customer overlay finish is not selected; native 805 mm height differs from the current 815 mm specification.

## Sources and access
- https://www.mieleusa.com/product/11636710/fully-integrated-ada-dishwasher-g-5051-scvi-active-stainless-steel
- https://media.miele.com/downloads/a5/52/10_70A8A51285B71FE1ABFC9D443DCBA552.zip
- https://media.miele.com/downloads/n-/us/FS_11636710_USE_US-en-US.pdf
- https://www.mieleusa.com/product/11636710/fully-integrated-dishwasher-g-5051-scvi-active-stainless-steel

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
