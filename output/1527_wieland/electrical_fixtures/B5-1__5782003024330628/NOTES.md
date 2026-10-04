# Electrical Fixtures final row record - worker-4

Row ID: `5782003024330628`

Inventory identity: "Better" option - Duo Pendant; recorded model `AST1561665`.

Location: Triplex / Bath 4. Agent Ignore retained: False.

All package paths below are relative to the Electrical Fixtures section root.

Status: **BUILT_WITH_LIMITATIONS**

Delivered identity: **Astro Lighting 1184057+5048001**.

RFA: `B5-1__5782003024330628/Astro_Duo_1184057_5048001_R2025.rfa`
SHA-256: `a4ad17ff2a9b448172a2e72b020ee812dec7c159f0bc3934123419efac3e7267`

Category/template: Lighting Fixtures; native Revit 2025 Generic Model face-based template recategorized for the fixture. Native ceiling face placement was verified.

Source/spec: https://www.lightology.com/index.php?module=prod_detail&prod_id=1561665.

RFA search: Public product resources inspected; no exact anonymous native RFA located. Prior native shade geometry is the documented rebuild source.

Source evidence: `B3-2__2025454640496516/source/`; definitions `B3-2__2025454640496516/source/build_family.py`.

Terms/version: anonymous public sources only; no account, credentials or license acceptance used. Manufacturer copyright retained. Final family saved and reopened in Revit 2025; original OEM files and older-version upgrade receipts remain in the source folders. This output is a native build/reconstruction, not an unchanged downloaded OEM family.

## Dimensions checked

| Check | Expected, inches | Saved measurement, inches |
|---|---|---|
| Overall native envelope | 8.267717 x 8.267717 x 39.370079 | 8.267717 x 8.26599 x 39.370079 |

Local coordinate order: wall families width / height / projection; overhead families X / Y / total envelope. For fans the static rectangular envelope differs from swept blade diameter; radial checks are retained below.

Native gates: dimensions=PASS, orientation=PASS, cct=PASS, reopened=PASS, materials=PASS, category=PASS, actual_face_host=PASS, saved_bitmaps_resolve=PASS, warnings=PASS, saved_dimensions_within_1mm=PASS, views=PASS.
Warnings: zero in family, reopened file and disposable host project. Finish substitution reached native faces and was restored. Saved bitmap bindings resolve.

Validation: `B5-1__5782003024330628/validation.json`. Canonical evidence: `B3-2__2025454640496516/validation.json` and `B3-2__2025454640496516/evidence/geometry_review.json`.

This row uses a byte-identical RFA copy. Canonical native measurements are reused only after SHA-256 comparison; no separate native run is claimed for this duplicate.

## Assumptions and limitations

ASSUMPTION / modeled limitations: 210 mm diameter/height shade rebuilt from inspected prior native geometry. Canopy corrected from prior 96 mm to current scheduled 4.3-inch diameter. ASSUMPTION: 1-inch canopy height and 1000 mm installed drop; source does not fully dimension those installed details. Finishes matte white and opal; material parameters editable.

Parameter scope: Nominal product dimensions are fixed formulas. Editable material parameters were flexed on hosted native geometry and restored.

Visual review: REVIEWED_WITH_LIMITATIONS. Upper rounded body with central opening and lower opal globe are present. The unlit material view does not reproduce the reference light emission.
Review image: `_review/final/final_06.jpg`; individual front/side/oblique/material and hosted images are retained in this row evidence folder.

Viewport shading is unlit evidence. Accurate photometric output, production-render glass/reflection matching, and final client visual approval are not established by the native gates.

Blockers: No remaining source/build/native gate blocker. The listed modeling assumptions remain for orchestrator acceptance.

Loading: keep the section directory structure and companion textures. Bitmap bindings currently resolve to canonical source/textures folders. When relocating, add the included texture folders to Revit Additional Render Appearance Paths or relink them. Copying only an RFA omits appearance assets.

Original inventory notes: NEEDS REVIEW 2026-10-01: This is explicitly a "Better" lighting option and Client comment remains TBD. Product/pricing is populated for comparison, but selection is not approved; do not treat as awarded scope. | RESOLVED 2026-10-01: dedicated lighting schedule / Lightopia base quote supports a separate base fixture for this location. This Better row is retained as a priced comparison alternate only and is excluded from the base procurement decision total.
