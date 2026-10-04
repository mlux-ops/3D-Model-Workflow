# Electrical Fixtures final row record - worker-4

Row ID: `1809170063490948`

Inventory identity: Sky Dome Wall Sconce; recorded model `PBL1129156`.

Location: Common / Lobby. Agent Ignore retained: False.

Status: **BUILT_WITH_LIMITATIONS**

Delivered identity: **Pablo SKY FSH 18 DOM BLK-3000K**.

RFA: `L2-0__1809170063490948/Pablo_Sky_Dome_18_Wall_Black_Aluminum_R2025.rfa`
SHA-256: `5bbfceacf990a20599e5709dd00a0b67fa4bd4d60c08e94fad834f796b0a1288`

Category/template: Lighting Fixtures; native Revit 2025 Generic Model face-based template recategorized for the fixture. Native wall face placement was verified.

Source/spec: https://pablodesigns.com/product/sky-flush.

RFA search: Public primary product resources and the retained exact product page were inspected; no direct, exact native RFA was available in those resources. This does not assert that no RFA exists elsewhere.

Source evidence: `L2-0__1809170063490948/source/`; definitions `L2-0__1809170063490948/source/model_definition.json`.

Terms/version: anonymous public sources only; no account, credentials or license acceptance used. Manufacturer copyright retained. Final family saved and reopened in Revit 2025; original OEM files and older-version upgrade receipts remain in the source folders. This output is a native build/reconstruction, not an unchanged downloaded OEM family.

## Dimensions checked

| Check | Expected, inches | Saved measurement, inches |
|---|---|---|
| Overall native envelope | 18 x 18 x 4 | 18.004539 x 18.003925 x 4 |

Local coordinate order: wall families width / height / projection; overhead families X / Y / total envelope. For fans the static rectangular envelope differs from swept blade diameter; radial checks are retained below.

Native gates: cct=PASS, materials=PASS, saved_bitmaps_resolve=PASS, reopened=PASS, dimensions=PASS, saved_dimensions_within_1mm=PASS, actual_face_host=PASS, saved_components_within_1mm=PASS, orientation=PASS, warnings=PASS, views=PASS, category=PASS.
Warnings: zero in family, reopened file and disposable host project. Finish substitution reached native faces and was restored. Saved bitmap bindings resolve.

Validation: `L2-0__1809170063490948/validation.json`. Canonical evidence: `L2-0__1809170063490948/validation.json` and `L2-0__1809170063490948/evidence/geometry_review.json`.

This canonical family was measured in saved-file native checks and independently reopened for the final geometry review.

## Assumptions and limitations

ASSUMPTION / modeled limitations: 18-inch shade diameter and 4-inch projection; 6.5-inch rear mount. Wall host follows the scheduled wall-sconce use. Matte-black reflector with polished-aluminum lamp rim and opal diffuser. ASSUMPTION: shallow reflector curve and central optic dimensions; manufacturer offers STEP geometry rather than a direct RFA in inspected resources.

Parameter scope: Nominal product dimensions are fixed formulas. Editable material parameters were flexed on hosted native geometry and restored.

Visual review: REVIEWED_WITH_LIMITATIONS. Broad shallow black reflector with central optic and rear mount matches the main source silhouette. Unlit viewport shading is not a lumen or appearance match.
Review image: `_review/final/final_01.jpg`; individual front/side/oblique/material and hosted images are retained in this row evidence folder.

Viewport shading is unlit evidence. Accurate photometric output, production-render glass/reflection matching, and final client visual approval are not established by the native gates.

Blockers: No remaining source/build/native gate blocker. The listed modeling assumptions remain for orchestrator acceptance..

Loading: keep the section directory structure and companion textures. Bitmap bindings currently resolve to canonical source/textures folders. When relocating, add the included texture folders to Revit Additional Render Appearance Paths or relink them. Copying only an RFA omits appearance assets.

Original inventory notes: None.
