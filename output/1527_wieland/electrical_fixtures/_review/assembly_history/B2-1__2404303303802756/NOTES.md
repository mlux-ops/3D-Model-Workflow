# Electrical Fixtures final row record - worker-4

Row ID: `2404303303802756`

Inventory identity: "Better" option - Dimple Wall Sconce; recorded model `DP-WS-S1-AA04-30-10_TRIAC_120V-IP65`.

Location: Triplex / Primary Bathroom. Agent Ignore retained: False.

Status: **BUILT_WITH_LIMITATIONS**

Delivered identity: **RBW DP-WS-S1-AA04-30-10_TRIAC_120V-IP65**.

RFA: `B2-1__2404303303802756/RBW_Dimple_S1_AA04_White_Interior_R2025.rfa`
SHA-256: `ade1d78f8a0178f0063119a6193659f4a079fccf8d03b96df48ea2048e9c2c15`

Category/template: Lighting Fixtures; native Revit 2025 Generic Model face-based template recategorized for the fixture. Native wall face placement was verified.

Source/spec: https://rbw.com/products/dimple-sconce/dimple-sconce.

RFA search: Manufacturer public RFA downloaded; old SKU/dimensions and missing Fine-detail lens solids prevented exact-current release. Independent native reconstruction used.

Source evidence: `B2-2__5960925969973124/source/`; definitions .

Terms/version: anonymous public sources only; no account, credentials or license acceptance used. Manufacturer copyright retained. Final family saved and reopened in Revit 2025; original OEM files and older-version upgrade receipts remain in the source folders. This output is a native build/reconstruction, not an unchanged downloaded OEM family.

## Dimensions checked

| Check | Expected, inches | Saved measurement, inches |
|---|---|---|
| Overall native envelope | 5 x 5 x 3.3 | 5 x 5 x 3.3 |

Local coordinate order: wall families width / height / projection; overhead families X / Y / total envelope. For fans the static rectangular envelope differs from swept blade diameter; radial checks are retained below.

Native gates: warnings=PASS, materials=PASS, actual_face_host=PASS, category=PASS, reopened=PASS, orientation=PASS, saved_dimensions_within_1mm=PASS, cct=PASS, views=PASS, dimensions=PASS, saved_bitmaps_resolve=PASS.
Warnings: zero in family, reopened file and disposable host project. Finish substitution reached native faces and was restored. Saved bitmap bindings resolve.

Validation: `B2-1__2404303303802756/validation.json`. Canonical evidence: `B2-2__5960925969973124/validation.json` and `B2-2__5960925969973124/evidence/geometry_review.json`.

This row uses a byte-identical RFA copy. Canonical native measurements are reused only after SHA-256 comparison; no separate native run is claimed for this duplicate.

## Assumptions and limitations

ASSUMPTION / modeled limitations: Current S1 black anodized/white interior SKU; 5-inch diameter x 3.3-inch projection. Concave front, rolled rim and separate interior follow saved product photos and the prior native Dimple profile builder. ASSUMPTION: glass thickness, backplate diameter, internal optics and exact dimple curvature. Older public manufacturer 305-D-FM RFA was rejected as an exact match and retained in source. Fixed product geometry; three editable material finishes.

Parameter scope: Nominal product dimensions are fixed formulas. Editable material parameters were flexed on hosted native geometry and restored.

Visual review: REVIEWED_WITH_LIMITATIONS. Current deep annular lens and rear mount are present. This corrects the shallow outdated OEM source; glowing optical appearance is not asserted.
Review image: `_review/final/final_05.jpg`; individual front/side/oblique/material and hosted images are retained in this row evidence folder.

Viewport shading is unlit evidence. Accurate photometric output, production-render glass/reflection matching, and final client visual approval are not established by the native gates.

Blockers: No remaining source/build/native gate blocker. The listed modeling assumptions remain for orchestrator acceptance..

Loading: keep the section directory structure and companion textures. Bitmap bindings currently resolve to canonical source/textures folders. When relocating, add the included texture folders to Revit Additional Render Appearance Paths or relink them. Copying only an RFA omits appearance assets.

Original inventory notes: NEEDS REVIEW 2026-10-01: This is explicitly a "Better" lighting option and Client comment remains TBD. Product/pricing is populated for comparison, but selection is not approved; do not treat as awarded scope. | RESOLVED 2026-10-01: dedicated lighting schedule / Lightopia base quote supports a separate base fixture for this location. This Better row is retained as a priced comparison alternate only and is excluded from the base procurement decision total.
