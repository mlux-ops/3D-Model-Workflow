# Electrical Fixtures final row record - worker-4

Row ID: `604904094171012`

Inventory identity: Juno QC4 J6 new-construction housing - REQUIRED SCOPE / COUNT HOLD; recorded model `QC4 J6`.

Location: Triplex / General. Agent Ignore retained: False.

All package paths below are relative to the Electrical Fixtures section root.

Status: **BUILT_WITH_LIMITATIONS**

Delivered identity: **Juno / Acuity Brands QC4 J6**.

RFA: `D2__604904094171012/Juno_QC4_J6_Housing_R2025.rfa`
SHA-256: `8067608b45dc67d4d0222c11fd94e4073eb5cfcc3e00e2964d6ec9d730d97638`

Category/template: Lighting Fixtures; native Revit 2025 Generic Model face-based template recategorized for the fixture. Native ceiling face placement was verified.

Source/spec: https://pdmassets.azureedge.net/library/JL/documents/specsheets/QC4.pdf.

RFA search: Official product resources and verified BIM listings searched; no exact, usable anonymous RFA accepted. See retained source resources and manufacturer acquisition/inspection receipts.

Source evidence: `D2__7923253488648068/source/`; definitions `D2__7923253488648068/source/completion_definition.json`.

Terms/version: anonymous public sources only; no account, credentials or license acceptance used. Manufacturer copyright retained. Final family saved and reopened in Revit 2025; original OEM files and older-version upgrade receipts remain in the source folders. This output is a native build/reconstruction, not an unchanged downloaded OEM family.

## Dimensions checked

| Check | Expected, inches | Saved measurement, inches |
|---|---|---|
| Overall native envelope | 9 x 13.5 x 5.375 | 9 x 13.5 x 5.375 |
| Housing height and can mouth | 4.5 x 4.5 x 5.375 | 4.5 x 4.5 x 5.375 |

Local coordinate order: wall families width / height / projection; overhead families X / Y / total envelope. For fans the static rectangular envelope differs from swept blade diameter; radial checks are retained below.

Native gates: dimensions=PASS, materials=PASS, views=PASS, reopened=PASS, saved_dimensions_within_1mm=PASS, orientation=PASS, actual_face_host=PASS, category=PASS, saved_components_within_1mm=PASS, warnings=PASS, cct=PASS, saved_bitmaps_resolve=PASS.
Warnings: zero in family, reopened file and disposable host project. Finish substitution reached native faces and was restored. Saved bitmap bindings resolve.

Validation: `D2__604904094171012/validation.json`. Canonical evidence: `D2__7923253488648068/validation.json` and `D2__7923253488648068/evidence/geometry_review.json`.

This row uses a byte-identical RFA copy. Canonical native measurements are reused only after SHA-256 comparison; no separate native run is claimed for this duplicate.

## Assumptions and limitations

ASSUMPTION / modeled limitations: Manufacturer drawing: 5.375-inch housing height, 4.5-inch ceiling cutout, and 13.5-inch supplied bar-hanger length. J6 denotes packaging of six, not a different shape. ASSUMPTION: 9-inch transverse assembly envelope, can wall thickness and junction-box dimensions are drawing-derived. Bars are shown at the supplied length; extension and wiring are not modeled. Housing sits above its ceiling mounting plane.

Parameter scope: Nominal product dimensions are fixed formulas. Editable material parameters were flexed on hosted native geometry and restored.

Visual review: REVIEWED_WITH_LIMITATIONS. Housing can, aperture, support plate and hanger rails are present. Rear engineering detail and adjustable hanger behavior are intentionally simplified.
Review image: `_review/final/final_03.jpg`; individual front/side/oblique/material and hosted images are retained in this row evidence folder.

Viewport shading is unlit evidence. Accurate photometric output, production-render glass/reflection matching, and final client visual approval are not established by the native gates.

Blockers: No remaining source/build/native gate blocker. The listed modeling assumptions remain for orchestrator acceptance.

Loading: keep the section directory structure and companion textures. Bitmap bindings currently resolve to canonical source/textures folders. When relocating, add the included texture folders to Revit Additional Render Appearance Paths or relink them. Copying only an RFA omits appearance assets.

Original inventory notes: SCHEDULE SCOPE ADDED 2026-10-01: D2/QC4 J6 housing is required, but dedicated schedule Qty 8/12 conflicts with the 4/28 recessed BOM, which pairs QC4 J6 one-for-one with D1 trims. Qty/AUC intentionally blank until 20-vs-169 count basis is reconciled. Do not treat as zero scope. | QUANTITY RESOLVED 2026-10-01: governing 1527 Wieland Lighting Fixture Schedule explicitly assigns D2 QC4 J6 Qty 12 per Triplex unit. Acuity/Juno confirms QC4 as the compatible quick-connect new-construction housing; current retailer evidence lists QC4 J6 at $27.84/EA. Treat that only as a planning benchmark pending awarded-supplier quote.
