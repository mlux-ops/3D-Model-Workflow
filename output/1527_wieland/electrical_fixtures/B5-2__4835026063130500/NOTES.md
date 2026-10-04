# Electrical Fixtures final row record - worker-4

Row ID: `4835026063130500`

Inventory identity: Rona Bathroom Vanity Light; recorded model `KZC780336`.

Location: Penthouse / Bath 4. Agent Ignore retained: False.

All package paths below are relative to the Electrical Fixtures section root.

Status: **BUILT_WITH_LIMITATIONS**

Delivered identity: **Kuzco Lighting VL17024-CH**.

RFA: `B5-2__4835026063130500/Kuzco_Rona_VL17024_Chrome_R2025.rfa`
SHA-256: `48944d5ceaf0ab47810ad0e582ec0c05a6d90a46848e782b73841c4c2656f163`

Category/template: Lighting Fixtures; native Revit 2025 Generic Model face-based template recategorized for the fixture. Native wall face placement was verified.

Source/spec: https://kuzcolighting.com/products/rona-vl17024-kuzco.

RFA search: Manufacturer RFA publicly downloaded and opened in 2025; inconsistent metadata, missing nested solid evidence and a rendering warning prevented accepting it unchanged.

Source evidence: `B3-2__7654954174709636/source/`; definitions `B3-2__7654954174709636/source/model_definition.json`.

Terms/version: anonymous public sources only; no account, credentials or license acceptance used. Manufacturer copyright retained. Final family saved and reopened in Revit 2025; original OEM files and older-version upgrade receipts remain in the source folders. This output is a native build/reconstruction, not an unchanged downloaded OEM family.

## Dimensions checked

| Check | Expected, inches | Saved measurement, inches |
|---|---|---|
| Overall native envelope | 4.5 x 24 x 2.75 | 4.5 x 24 x 2.75 |

Local coordinate order: wall families width / height / projection; overhead families X / Y / total envelope. For fans the static rectangular envelope differs from swept blade diameter; radial checks are retained below.

Native gates: cct=PASS, materials=PASS, saved_bitmaps_resolve=PASS, reopened=PASS, dimensions=PASS, saved_dimensions_within_1mm=PASS, actual_face_host=PASS, saved_components_within_1mm=PASS, orientation=PASS, warnings=PASS, views=PASS, category=PASS.
Warnings: zero in family, reopened file and disposable host project. Finish substitution reached native faces and was restored. Saved bitmap bindings resolve.

Validation: `B5-2__4835026063130500/validation.json`. Canonical evidence: `B3-2__7654954174709636/validation.json` and `B3-2__7654954174709636/evidence/geometry_review.json`.

This row uses a byte-identical RFA copy. Canonical native measurements are reused only after SHA-256 comparison; no separate native run is claimed for this duplicate.

## Assumptions and limitations

ASSUMPTION / modeled limitations: Current 24-inch Rona, 4.5-inch square backplate x 0.625, 2.75-inch extension. Vertical default; may be rotated on wall. ASSUMPTION: 1.25-inch optic diameter and clamp contours from photograph. Manufacturer 2019 RFA contains model metadata VL10724, an interior-light-source warning and incomplete Fine-detail native geometry; retained as reference.

Parameter scope: Nominal product dimensions are fixed formulas. Editable material parameters were flexed on hosted native geometry and restored.

Visual review: REVIEWED_WITH_LIMITATIONS. Long cylindrical optic, central clamp and square mounting plate are present. Default vertical orientation can be rotated on the wall; fine clamp detail is approximate.
Review image: `_review/final/final_08.jpg`; individual front/side/oblique/material and hosted images are retained in this row evidence folder.

Viewport shading is unlit evidence. Accurate photometric output, production-render glass/reflection matching, and final client visual approval are not established by the native gates.

Blockers: No remaining source/build/native gate blocker. The listed modeling assumptions remain for orchestrator acceptance.

Loading: keep the section directory structure and companion textures. Bitmap bindings currently resolve to canonical source/textures folders. When relocating, add the included texture folders to Revit Additional Render Appearance Paths or relink them. Copying only an RFA omits appearance assets.

Original inventory notes: NEEDS REVIEW 2026-10-01: Fixture row is populated, but Client comment remains TBD. Verify against the final lighting schedule / approved fixture selection before order; existing identity, quantity, and carried price are preserved. | RESOLVED 2026-10-01: Rona Bathroom Vanity Light KZC780336 is supported for B5-2 / Penthouse Bath 4; Lightopia estimate quotes the third Penthouse Rona vanity fixture for the secondary-bath set; the dedicated schedule repeats the B4-2 designation for multiple bathrooms, so the room/product match supports the live B5-2 row. Client TBD text is retained as historical input; this row is treated as the base fixture for procurement comparison.
