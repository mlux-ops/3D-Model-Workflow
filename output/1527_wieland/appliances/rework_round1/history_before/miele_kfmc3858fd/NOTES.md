# Miele KFMC 3858 FD

Status: **DOWNLOADED**. Recorded 2026-10-02T14:36:37.480895+00:00.

Smartsheet row IDs: 2166795625103236, 1900063828279172.
RFA: `miele_kfmc3858fd/miele_kfmc3858fd_R2025.rfa`. SHA-256: `33f4dda96d550daa71c7e359a83bc4c093ad19caa9514a3c80dd3de418f067de`.

## Native evidence
Revit 2025 save/reopen: PASS. Category: Specialty Equipment. Placement: WorkPlaneBased; actual test host: Floors.
Actual full placed bounds (W x D x H): **1067.000 x 610.636 x 2124.551 mm**.
Comparison target (W x D x H): 1048.000 x 608.000 x 2125.000 mm.
Dimension gate: **HOLD**; scope: full native geometry versus published appliance envelope.
Dimension basis: Appliance body; 1067 mm installation width is not appliance body width.
Delta against comparison target (W, D, H): +18.999988, +2.635538, -0.449012 mm.
Material parameter substitution with geometry evidence: 0/0. Zero exposed parameters means the manufacturer materials remain nested/fixed, not that editability passed.
Family warnings: 0; placed-project warnings: 0.

Detailed native results: `../miele_kfmc3858fd/validation.json`.
Native previews: `../miele_kfmc3858fd/views/placed_oblique - 3D View - placed_oblique.png`.

## Visual review
Closed black factory assembly with mounting hardware is visible. The shaded facade does not clearly show all French-door/freezer seams; customer panels and closed-front configuration require visual confirmation.

## Sources and access
- https://www.mieleusa.com/product/12489440/42-mastercool-frenchdoor-bottom-mount-unit-kfmc-3858-fd-compatible-with-furniture-fronts
- https://media.miele.com/downloads/a5/64/03_70A8A51285B71FE1AC8273C8621BA564.zip
- https://media.miele.com/downloads/n-/us/FS_12489440_USE_US-en-US.pdf

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
