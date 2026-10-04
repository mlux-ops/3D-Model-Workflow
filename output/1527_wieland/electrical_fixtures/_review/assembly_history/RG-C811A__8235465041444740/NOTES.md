# Electrical Fixtures final row record - worker-4

Row ID: `8235465041444740`

Inventory identity: Whisper Choice DC Pick-A-Flow 80/110 CFM Ceiling Bathroom Exhaust Fan with Flex-Z Fast Bracket; recorded model `RG-C811A`.

Location: Triplex / Primary Bathroom. Agent Ignore retained: False.

Status: **BUILT_WITH_LIMITATIONS**

Delivered identity: **Panasonic RG-C811A**.

RFA: `RG-C811A__8235465041444740/Panasonic_WhisperChoice_RG_C811A_R2025.rfa`
SHA-256: `964037726335371d1af9c007f723ec7ac951ce97af68fd526a22fa36ee97df87`

Category/template: Mechanical Equipment; native Revit 2025 Generic Model face-based template recategorized for the fixture. Native ceiling face placement was verified.

Source/spec: https://ftp.panasonic.com/ventilationfan/installation/rg-c811a_rg-c811ha_eng.pdf.

RFA search: Public primary product resources and the retained exact product page were inspected; no direct, exact native RFA was available in those resources. This does not assert that no RFA exists elsewhere.

Source evidence: `RG-C811A__240438544629636/source/`; definitions `RG-C811A__240438544629636/source/model_definition.json`.

Terms/version: anonymous public sources only; no account, credentials or license acceptance used. Manufacturer copyright retained. Final family saved and reopened in Revit 2025; original OEM files and older-version upgrade receipts remain in the source folders. This output is a native build/reconstruction, not an unchanged downloaded OEM family.

## Dimensions checked

| Check | Expected, inches | Saved measurement, inches |
|---|---|---|
| Overall native envelope | 15.5 x 13 x 8.375 | 15.5 x 13 x 8.375 |
| Main housing | 10.25 x 10.25 x 7.5 | 10.25 x 10.25 x 7.5 |
| Grille | 13 x 13 x 0.875 | 13 x 13 x 0.875 |

Local coordinate order: wall families width / height / projection; overhead families X / Y / total envelope. For fans the static rectangular envelope differs from swept blade diameter; radial checks are retained below.

Native gates: cct=PASS, saved_dimensions_within_1mm=PASS, warnings=PASS, reopened=PASS, materials=PASS, actual_face_host=PASS, views=PASS, saved_components_within_1mm=PASS, saved_bitmaps_resolve=PASS, dimensions=PASS, category=PASS, orientation=PASS.
Warnings: zero in family, reopened file and disposable host project. Finish substitution reached native faces and was restored. Saved bitmap bindings resolve.

Validation: `RG-C811A__8235465041444740/validation.json`. Canonical evidence: `RG-C811A__240438544629636/validation.json` and `RG-C811A__240438544629636/evidence/geometry_review.json`.

This row uses a byte-identical RFA copy. Canonical native measurements are reused only after SHA-256 comparison; no separate native run is claimed for this duplicate.

## Assumptions and limitations

ASSUMPTION / modeled limitations: Manufacturer manual page 4: 13-inch grille, 10.25-inch housing plan, 7.5-inch housing height, 3.875-inch adapter extension and 0.875-inch grille projection. Component checks distinguish these from the derived combined envelope. ASSUMPTION: hole pitch, bezel section, internal impeller and junction box detail; perforations are real native holes. Adjustable joist bracket, wiring and duct connector engineering are excluded. Mechanical Equipment face-based visualization family.

Parameter scope: Nominal product dimensions are fixed formulas. Editable material parameters were flexed on hosted native geometry and restored.

Visual review: REVIEWED_WITH_LIMITATIONS. Square housing, real perforated grille and side duct-adapter geometry are present. No paired product photograph is included; prior manufacturer drawing dimensions and native component checks support this visualization. Engineering bracket/connector behavior is excluded.
Review image: `_review/final/final_09.jpg`; individual front/side/oblique/material and hosted images are retained in this row evidence folder.

Viewport shading is unlit evidence. Accurate photometric output, production-render glass/reflection matching, and final client visual approval are not established by the native gates.

Blockers: No remaining source/build/native gate blocker. The listed modeling assumptions remain for orchestrator acceptance..

Loading: keep the section directory structure and companion textures. Bitmap bindings currently resolve to canonical source/textures folders. When relocating, add the included texture folders to Revit Additional Render Appearance Paths or relink them. Copying only an RFA omits appearance assets.

Original inventory notes: None.
