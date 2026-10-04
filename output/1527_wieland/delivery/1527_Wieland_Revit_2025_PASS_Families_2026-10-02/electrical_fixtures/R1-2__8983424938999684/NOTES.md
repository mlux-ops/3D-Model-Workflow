# Electrical Fixtures final row record - worker-4

Row ID: `8983424938999684`

Inventory identity: "Better" option - Ambit DC Ceiling Fan; recorded model `AMB-MB-56-EB-870-CC`.

Location: Penthouse / Patio. Agent Ignore retained: False.

All package paths below are relative to the Electrical Fixtures section root.

Status: **BUILT_WITH_LIMITATIONS**

Delivered identity: **The Modern Fan Company AMB-MB-56-EB-870-CC**.

RFA: `R1-2__8983424938999684/Modern_Fan_Ambit_MB_56_EB_870_CC_R2025.rfa`
SHA-256: `a0efba516a72180517548d3f0d69806ca7805328b474a3d4774c9925e59cedc9`

Category/template: Lighting Fixtures; native Revit 2025 Generic Model face-based template recategorized for the fixture. Native ceiling face placement was verified.

Source/spec: https://modernfan.com/wp-content/uploads/AMB-Cutsheet.pdf.

RFA search: Public manufacturer and reputable BIM resource searches retained. No exact acceptable anonymous native RFA accepted; see acquisition evidence.

Source evidence: `R1-2__8983424938999684/source/`; definitions `R1-2__8983424938999684/source/remaining_definition.json`.

Terms/version: anonymous public sources only; no account, credentials or license acceptance used. Manufacturer copyright retained. Final family saved and reopened in Revit 2025; original OEM files and older-version upgrade receipts remain in the source folders. This output is a native build/reconstruction, not an unchanged downloaded OEM family.

## Dimensions checked

| Check | Expected, inches | Saved measurement, inches |
|---|---|---|
| Overall native envelope | 44.307004 x 50.862968 x 14.45 | 44.307004 x 50.862968 x 14.45 |
| Motor housing diameter | 7.9 x 7.9 x n/a | 7.9 x 7.9 x 5.049999 |
| Canopy diameter | 5.5 x 5.5 x n/a | 5.5 x 5.5 x 1.25 |

Local coordinate order: wall families width / height / projection; overhead families X / Y / total envelope. For fans the static rectangular envelope differs from swept blade diameter; radial checks are retained below.

Radial checks: `[{"element_ids": ["3221", "3222", "3223"], "label": "Swept blade diameter", "expected_diameter_in": 56.0, "center_in": [0, 0], "measured_diameter_in": 56.00000064535897, "error_mm": 1.6392117923658134e-05, "pass": true, "source": "Manufacturer nominal blade sweep"}]`

Native gates: views=PASS, warnings=PASS, reopened=PASS, saved_bitmaps_resolve=PASS, saved_radial_dimensions_within_1mm=PASS, actual_face_host=PASS, dimensions=PASS, saved_components_within_1mm=PASS, category=PASS, cct=PASS, saved_dimensions_within_1mm=PASS, orientation=PASS, materials=PASS.
Warnings: zero in family, reopened file and disposable host project. Finish substitution reached native faces and was restored. Saved bitmap bindings resolve.

Validation: `R1-2__8983424938999684/validation.json`. Canonical evidence: `R1-2__8983424938999684/validation.json` and `R1-2__8983424938999684/evidence/geometry_review.json`.

This canonical family was measured in saved-file native checks and independently reopened for the final geometry review.

## Assumptions and limitations

ASSUMPTION / modeled limitations: Exact scheduled matte-black / ebony / 870 LED combination. Manufacturer: 56-inch swept blade diameter, 5.5-inch canopy, 7.9-inch housing, 13.7-inch standard drop with 6-inch rod; LED option adds 0.75 inch, giving 14.45 inches. The stationary three-blade rectangular bounds are recorded separately and must not be confused with swept diameter. ASSUMPTION: blade airfoil/twist, housing curves and ebony wood-print optical detail are approximated; the included 16-inch rod alternative is not modeled. Finishes remain editable.

Parameter scope: Nominal product dimensions are fixed formulas. Editable material parameters were flexed on hosted native geometry and restored.

Visual review: REVIEWED_WITH_LIMITATIONS. Three ebony blades, motor body and optional lower light are present. Blade shape, twist and wood appearance are simplified; the 56-inch swept diameter is measured independently of static rectangular bounds.
Review image: `_review/final/final_05.jpg`; individual front/side/oblique/material and hosted images are retained in this row evidence folder.

Viewport shading is unlit evidence. Accurate photometric output, production-render glass/reflection matching, and final client visual approval are not established by the native gates.

Blockers: No remaining source/build/native gate blocker. The listed modeling assumptions remain for orchestrator acceptance.

Loading: keep the section directory structure and companion textures. Bitmap bindings currently resolve to canonical source/textures folders. When relocating, add the included texture folders to Revit Additional Render Appearance Paths or relink them. Copying only an RFA omits appearance assets.

Original inventory notes: None.
