# Electrical Fixtures final row record - worker-4

Row ID: `4412813598064516`

Inventory identity: Motif Slim Pendant; recorded model `KZC1009577`.

Location: Triplex / Dining. Agent Ignore retained: False.

Status: **BUILT_WITH_LIMITATIONS**

Delivered identity: **Kuzco Lighting PD75027-BK**.

RFA: `T1-1__4412813598064516/Kuzco_Motif_PD75027_Black_R2025.rfa`
SHA-256: `0ade2e81187d29614b390607cdffaf74501ba9d8e0c2828b836e44b6d1e6dc93`

Category/template: Lighting Fixtures; native Revit 2025 Generic Model face-based template recategorized for the fixture. Native ceiling face placement was verified.

Source/spec: https://kuzcolighting.com/products/motif-pd75027-kuzco.

RFA search: Manufacturer public RFA downloaded/opened in 2025; measured native body/canopy differ from current published dimensions, so unchanged RFA was not accepted.

Source evidence: `T1-1__4412813598064516/source/`; definitions `T1-1__4412813598064516/source/model_definition.json`.

Terms/version: anonymous public sources only; no account, credentials or license acceptance used. Manufacturer copyright retained. Final family saved and reopened in Revit 2025; original OEM files and older-version upgrade receipts remain in the source folders. This output is a native build/reconstruction, not an unchanged downloaded OEM family.

## Dimensions checked

| Check | Expected, inches | Saved measurement, inches |
|---|---|---|
| Overall native envelope | 4.625 x 4.625 x 48 | 4.625 x 4.625 x 48 |
| Canopy | 4.625 x 4.625 x 0.5 | 4.625 x 4.625 x 0.5 |
| Pendant body | 0.75 x 0.75 x 26.75 | 0.75 x 0.75 x 26.75 |

Local coordinate order: wall families width / height / projection; overhead families X / Y / total envelope. For fans the static rectangular envelope differs from swept blade diameter; radial checks are retained below.

Native gates: cct=PASS, materials=PASS, saved_bitmaps_resolve=PASS, reopened=PASS, dimensions=PASS, saved_dimensions_within_1mm=PASS, actual_face_host=PASS, saved_components_within_1mm=PASS, orientation=PASS, warnings=PASS, views=PASS, category=PASS.
Warnings: zero in family, reopened file and disposable host project. Finish substitution reached native faces and was restored. Saved bitmap bindings resolve.

Validation: `T1-1__4412813598064516/validation.json`. Canonical evidence: `T1-1__4412813598064516/validation.json` and `T1-1__4412813598064516/evidence/geometry_review.json`.

This canonical family was measured in saved-file native checks and independently reopened for the final geometry review.

## Assumptions and limitations

ASSUMPTION / modeled limitations: 0.75-inch x 26.75-inch body, 4.625-inch x 0.5-inch canopy. ASSUMPTION: 48-inch drop and fine internal filament/cap proportions. Public 2019 OEM body measures about 18 mm diameter against the current 19.05 mm nominal; canopy is also undersized. Current native reconstruction preserves the referenced clear cylinder and end caps.

Parameter scope: Nominal product dimensions are fixed formulas. Editable material parameters were flexed on hosted native geometry and restored.

Visual review: REVIEWED_WITH_LIMITATIONS. Long clear tubular body with dark end caps and separate canopy is present. Current nominal dimensions replace the undersized legacy OEM source.
Review image: `_review/final/final_10.jpg`; individual front/side/oblique/material and hosted images are retained in this row evidence folder.

Viewport shading is unlit evidence. Accurate photometric output, production-render glass/reflection matching, and final client visual approval are not established by the native gates.

Blockers: No remaining source/build/native gate blocker. The listed modeling assumptions remain for orchestrator acceptance..

Loading: keep the section directory structure and companion textures. Bitmap bindings currently resolve to canonical source/textures folders. When relocating, add the included texture folders to Revit Additional Render Appearance Paths or relink them. Copying only an RFA omits appearance assets.

Original inventory notes: None.
