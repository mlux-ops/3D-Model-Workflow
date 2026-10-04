# Electrical Fixtures final row record - worker-4

Row ID: `2521309084581764`

Inventory identity: Stephord Wall Sconce; recorded model `KZC1403797`.

Location: Penthouse / Dining. Agent Ignore retained: False.

Status: **BUILT_WITH_LIMITATIONS**

Delivered identity: **Kuzco Lighting WS97204-BK/CL**.

RFA: `K2-2__2521309084581764/Kuzco_Stephord_WS97204_BK_CL_R2025.rfa`
SHA-256: `8f810878a791beff0c871947c0e3262503cce07907de8125cc4bd689c94a46a4`

Category/template: Lighting Fixtures; native Revit 2025 Generic Model face-based template recategorized for the fixture. Native wall face placement was verified.

Source/spec: https://kuzcolighting.com/products/stephord-ws97204-kuzco.

RFA search: Public manufacturer ZIP downloaded, CRC checked and opened in Revit 2025. Current nominal projection differs by 1.402 mm; native reconstruction follows published current dimensions.

Source evidence: `K2-2__2521309084581764/source/`; definitions `K2-2__2521309084581764/source/model_definition.json`.

Terms/version: anonymous public sources only; no account, credentials or license acceptance used. Manufacturer copyright retained. Final family saved and reopened in Revit 2025; original OEM files and older-version upgrade receipts remain in the source folders. This output is a native build/reconstruction, not an unchanged downloaded OEM family.

## Dimensions checked

| Check | Expected, inches | Saved measurement, inches |
|---|---|---|
| Overall native envelope | 4.75 x 4.75 x 1.63 | 4.75 x 4.75 x 1.64558 |

Local coordinate order: wall families width / height / projection; overhead families X / Y / total envelope. For fans the static rectangular envelope differs from swept blade diameter; radial checks are retained below.

Native gates: cct=PASS, materials=PASS, saved_bitmaps_resolve=PASS, reopened=PASS, dimensions=PASS, saved_dimensions_within_1mm=PASS, actual_face_host=PASS, saved_components_within_1mm=PASS, orientation=PASS, warnings=PASS, views=PASS, category=PASS.
Warnings: zero in family, reopened file and disposable host project. Finish substitution reached native faces and was restored. Saved bitmap bindings resolve.

Validation: `K2-2__2521309084581764/validation.json`. Canonical evidence: `K2-2__2521309084581764/validation.json` and `K2-2__2521309084581764/evidence/geometry_review.json`.

This canonical family was measured in saved-file native checks and independently reopened for the final geometry review.

## Assumptions and limitations

ASSUMPTION / modeled limitations: 4.75-inch diameter, 1.63-inch projection. Separate clear curved glass lens, black central disk and concealed opal ring. ASSUMPTION: internal lens curvature and thickness from photograph. Downloaded 2019 manufacturer RFA measured 4.7244 x 4.7244 x 1.5748 inches; preserved as source, not accepted as a current inch-spec match.

Parameter scope: Nominal product dimensions are fixed formulas. Editable material parameters were flexed on hosted native geometry and restored.

Visual review: REVIEWED_WITH_LIMITATIONS. Curved clear annular lens, central black disk and circular rear body are present. Refraction and internal optical details remain approximate.
Review image: `_review/final/final_08.jpg`; individual front/side/oblique/material and hosted images are retained in this row evidence folder.

Viewport shading is unlit evidence. Accurate photometric output, production-render glass/reflection matching, and final client visual approval are not established by the native gates.

Blockers: No remaining source/build/native gate blocker. The listed modeling assumptions remain for orchestrator acceptance..

Loading: keep the section directory structure and companion textures. Bitmap bindings currently resolve to canonical source/textures folders. When relocating, add the included texture folders to Revit Additional Render Appearance Paths or relink them. Copying only an RFA omits appearance assets.

Original inventory notes: None.
