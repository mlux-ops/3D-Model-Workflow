# Electrical Fixtures final row record - worker-4

Row ID: `1967952628416388`

Inventory identity: "Best" option - Orion Tube Pendant; recorded model `unspecified`.

Location: Penthouse / Powder Room. Agent Ignore retained: False.

Status: **BUILT_WITH_LIMITATIONS**

Delivered identity: **Lee Broom ORI0120 - ASSUMED FINISH / HORIZONTAL**.

RFA: `Best_option_-_Orion_Tube_Pendant__1967952628416388/Lee_Broom_Orion_Tube_ORI0120_Horizontal_Assumed_R2025.rfa`
SHA-256: `e60ed6c59964d49099d36944a839f243c80a6c216572637f8bd3d15867e39ba2`

Category/template: Lighting Fixtures; native Revit 2025 Generic Model face-based template recategorized for the fixture. Native ceiling face placement was verified.

Source/spec: https://leebroom.com/wp-content/uploads/2026/06/Orion-Tube-Light_0626REV21.pdf.

RFA search: Anonymous manufacturer Orion-1.zip passed CRC and source RFA opened/upgraded from 2019. Imported Generic Models geometry has no finish parameters and differs from current dimensional sheet; replaced with native face-based dimensioned geometry. Original source retained.

Source evidence: `Best_option_-_Orion_Tube_Pendant__1967952628416388/source/`; definitions `Best_option_-_Orion_Tube_Pendant__1967952628416388/source/orion_definition.json`.

Terms/version: anonymous public sources only; no account, credentials or license acceptance used. Manufacturer copyright retained. Final family saved and reopened in Revit 2025; original OEM files and older-version upgrade receipts remain in the source folders. This output is a native build/reconstruction, not an unchanged downloaded OEM family.

## Dimensions checked

| Check | Expected, inches | Saved measurement, inches |
|---|---|---|
| Overall native envelope | 36.125 x 5.125 x 48 | 36.125001 x 5.122273 x 48 |
| Current US fixture body | 34.5 x 5.125 x 5.125 | 34.5 x 5.122273 x 5.124999 |
| Polished metal globe | 5.125 x 5.125 x 5.125 | 5.125 x 5.122273 x 5.124999 |
| Mini canopy 1 | 1.625 x 1.625 x 0.625 | 1.625001 x 1.625 x 0.625 |
| Mini canopy 2 | 1.625 x 1.625 x 0.625 | 1.625001 x 1.625 x 0.625 |

Local coordinate order: wall families width / height / projection; overhead families X / Y / total envelope. For fans the static rectangular envelope differs from swept blade diameter; radial checks are retained below.

Native gates: views=PASS, actual_face_host=PASS, dimensions=PASS, saved_radial_dimensions_within_1mm=PASS, category=PASS, saved_bitmaps_resolve=PASS, saved_dimensions_within_1mm=PASS, orientation=PASS, reopened=PASS, warnings=PASS, materials=PASS, cct=PASS, saved_components_within_1mm=PASS.
Warnings: zero in family, reopened file and disposable host project. Finish substitution reached native faces and was restored. Saved bitmap bindings resolve.

Validation: `Best_option_-_Orion_Tube_Pendant__1967952628416388/validation.json`. Canonical evidence: `Best_option_-_Orion_Tube_Pendant__1967952628416388/validation.json` and `Best_option_-_Orion_Tube_Pendant__1967952628416388/evidence/geometry_review.json`.

This canonical family was measured in saved-file native checks and independently reopened for the final geometry review.

## Assumptions and limitations

ASSUMPTION / modeled limitations: Current manufacturer US specification EN 0626rev21 page 2: body 34.5 inches long and 5.125-inch globe; two 1.625-inch diameter by 0.625-inch high mini canopies. US printed inches control; corresponding metric labels are rounded and differ by up to 1.3 mm. These current dimensions supersede legacy 88.5-cm web and 2019 CAD length. Overall mounting envelope is 36.125 inches including mini canopies centered over the body ends; body is checked independently. ASSUMPTION: polished gold ORI0120, single horizontal module, 48-inch installed drop, globe center at one-quarter body length, 30-mm opal tube diameter from manufacturer EU product text, and small end-cap/cable sizes. Inventory names Orion Tube but specifies no finish, code or configuration. This is a reviewable representative family; exact finish, orientation, array and installed drop remain NEEDS_USER_ORION_CONFIGURATION. Remote driver and optional covers are not included. No engineering connectors or photometric source. Editable materials; fixed dimensional geometry.

Parameter scope: Nominal product dimensions are fixed formulas. Editable material parameters were flexed on hosted native geometry and restored.

Visual review: REVIEWED_WITH_LIMITATIONS. Metal globe is off-center on the opal tube, with two separate suspension points and mini canopies. Horizontal gold single-module configuration and 48-inch drop are explicit assumptions. Current US specification controls body dimensions.
Review image: `_review/final/final_04.jpg`; individual front/side/oblique/material and hosted images are retained in this row evidence folder.

Viewport shading is unlit evidence. Accurate photometric output, production-render glass/reflection matching, and final client visual approval are not established by the native gates.

Blockers: NEEDS_USER_ORION_CONFIGURATION.

Loading: keep the section directory structure and companion textures. Bitmap bindings currently resolve to canonical source/textures folders. When relocating, add the included texture folders to Revit Additional Render Appearance Paths or relink them. Copying only an RFA omits appearance assets.

Original inventory notes: None.
