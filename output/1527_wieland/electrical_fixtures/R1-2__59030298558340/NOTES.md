# Electrical Fixtures final row record - worker-4

Row ID: `59030298558340`

Inventory identity: Zephyr Smart 3-Blade Fan with Color-Select Light; recorded model `MFR918914`.

Location: Penthouse / Roof Deck. Agent Ignore retained: False.

All package paths below are relative to the Electrical Fixtures section root.

Status: **BUILT_WITH_LIMITATIONS**

Delivered identity: **Modern Forms FR-W2006-52L-MB**.

RFA: `R1-2__59030298558340/Modern_Forms_Zephyr_FR_W2006_52L_MB_R2025.rfa`
SHA-256: `b70e4dd0f9ac9067e95d630aaefb1ab535f56c148b6d236b499104076537ef35`

Category/template: Lighting Fixtures; native Revit 2025 Generic Model face-based template recategorized for the fixture. Native ceiling face placement was verified.

Source/spec: https://modernforms.com/images/products/SPECSHEET_PDF/FR-W2006-52_SPSHT.pdf.

RFA search: Public manufacturer and reputable BIM resource searches retained. No exact acceptable anonymous native RFA accepted; see acquisition evidence.

Source evidence: `R1-2__1154902149234564/source/`; definitions `R1-2__1154902149234564/source/remaining_definition.json`.

Terms/version: anonymous public sources only; no account, credentials or license acceptance used. Manufacturer copyright retained. Final family saved and reopened in Revit 2025; original OEM files and older-version upgrade receipts remain in the source folders. This output is a native build/reconstruction, not an unchanged downloaded OEM family.

## Dimensions checked

| Check | Expected, inches | Saved measurement, inches |
|---|---|---|
| Overall native envelope | 42.810762 x 46.498344 x 18.125 | 42.810762 x 46.498344 x 18.125 |
| Luminaire diameter | 5.625 x 5.625 x n/a | 5.625 x 5.62152 x 1.099999 |
| Canopy diameter | 7 x 7 x n/a | 7 x 7 x 1.35 |

Local coordinate order: wall families width / height / projection; overhead families X / Y / total envelope. For fans the static rectangular envelope differs from swept blade diameter; radial checks are retained below.

Radial checks: `[{"element_ids": ["3219", "3220", "3221"], "label": "Swept blade diameter", "expected_diameter_in": 52.0, "center_in": [0, 0], "measured_diameter_in": 51.99999828926829, "error_mm": 4.3452585413206175e-05, "pass": true, "source": "Manufacturer nominal blade sweep"}]`

Native gates: views=PASS, warnings=PASS, reopened=PASS, saved_bitmaps_resolve=PASS, saved_radial_dimensions_within_1mm=PASS, actual_face_host=PASS, dimensions=PASS, saved_components_within_1mm=PASS, category=PASS, cct=PASS, saved_dimensions_within_1mm=PASS, orientation=PASS, materials=PASS.
Warnings: zero in family, reopened file and disposable host project. Finish substitution reached native faces and was restored. Saved bitmap bindings resolve.

Validation: `R1-2__59030298558340/validation.json`. Canonical evidence: `R1-2__1154902149234564/validation.json` and `R1-2__1154902149234564/evidence/geometry_review.json`.

This row uses a byte-identical RFA copy. Canonical native measurements are reused only after SHA-256 comparison; no separate native run is claimed for this duplicate.

## Assumptions and limitations

ASSUMPTION / modeled limitations: Manufacturer 52-inch blade sweep, 7-inch canopy and 5.625-inch lower luminaire diameter. ASSUMPTION: use the right-hand 18.125-inch overall-drop drawing with its longer included downrod. The left drawing and current retailer values differ; this edition explicitly follows the right-hand factory diagram. Blade twist/sweep and housing contours are reconstructed, not factory CAD. The public manufacturer RFA ZIP is truncated and cannot be extracted. Fixed three-blade position; swept diameter is measured separately from its rectangular bounds.

Parameter scope: Nominal product dimensions are fixed formulas. Editable material parameters were flexed on hosted native geometry and restored.

Visual review: REVIEWED_WITH_LIMITATIONS. Three blades, rounded motor, lower luminaire and downrod are present. Blade tips, twist and body contours are visibly simplified relative to the reference. The 52-inch sweep passes its separate radial gate; unusable OEM ZIP is retained.
Review image: `_review/final/final_09.jpg`; individual front/side/oblique/material and hosted images are retained in this row evidence folder.

Viewport shading is unlit evidence. Accurate photometric output, production-render glass/reflection matching, and final client visual approval are not established by the native gates.

Blockers: No remaining source/build/native gate blocker. The listed modeling assumptions remain for orchestrator acceptance.

Loading: keep the section directory structure and companion textures. Bitmap bindings currently resolve to canonical source/textures folders. When relocating, add the included texture folders to Revit Additional Render Appearance Paths or relink them. Copying only an RFA omits appearance assets.

Original inventory notes: None.
