# SHB_Glass Clamp 180 Square — sources, assumptions and inferences

Recorded 2026-09-29. Task file: `Glass_Clamp_180_Family_Build.md`. Rule: never present ASSUMED or INFERRED values as manufacturer data.

## Dimensions

| Value | Number | Class | Source / reason | Confidence |
|---|---|---|---|---|
| Overall height | 2 in | VERIFIED | task file ("verified"); web-search snippet of the CRL page: "Height 2 inches (51 mm)" | high |
| Overall width | 5 in | VERIFIED | same | high |
| Glass range | 3/8–1/2 in | VERIFIED | same; types 3-8 and 1-2 | high |
| Plate thickness | 1/8 in | ASSUMED | task file: "check CRL drawing" | low |
| Joint gap | 1/8 in | ASSUMED | task file: "check job glass detail"; informational only | low |
| Cap Ø | 3/4 in | ASSUMED | task file; snippet says CRL needs **3/4 in glass holes**, so a cap of the same size cannot hide the hole | low, likely too small |
| Cap height | 1/8 in | ASSUMED | task file | low |
| Caps per side | 2, spacing = width − 2 in (3 in) | ASSUMED | task file formula | low |
| Plate corner fillet | none | omitted | optional and cosmetic per task | — |
| Cap shape | cylinder, built as a 360° revolve | INFERRED method | identical solid to an extruded circle; constrainable through the API | — |

Web-search snippet also says "Solid Brass". Not used by the model (no thickness or material data beyond the finish). The CRL page itself returned HTTP 403 to this session; the "Technical References & CAD Drawings" section was not read.

## Appearance (family-embedded, numeric only)

| Value | Number | Class | Reason |
|---|---|---|---|
| Base colour | RGB 110/86/62 | task file | given |
| Roughness → glossiness | 0.35 → 0.65 | mapped | Revit Generic uses glossiness = 1 − roughness |
| Metallic | 1.0 → `generic_is_metal` on | mapped | Generic exposes a metal flag, not a scalar |
| Reflectivity 0° / 90° | 0.40 / 0.80 | INFERRED | between the brass values of the House of Troy build (0.36/0.75) and Cassia gold (0.30/0.80); not measured |
| Brushed grain | not modelled | — | task defines no bitmap; texture-free fixture convention; the ADSKLIB bound-bitmap rule does not apply to family-embedded finishes |
| Surface pattern | none | task file | G29 (soft) reads it back |

## Finish name (Smartsheet FINISH DATABASE, id 6391628162879364, read-only, 2026-09-29)

- 864 rows searched for "bronze", "clamp", "SGC180". The Primary Bath bronze is **Kohler Vibrant Brushed Bronze (BV)** (fixtures, drains, accessories); QM drains use "Satin Bronze (BZ)", recorded there as a distinct finish; MrSteam uses "Brushed Bronze".
- No glass-clamp row and no `SGC180` SKU exist; "clamp" hits are QM clamp-down drain bodies.
- Consequence: the family material is `Brushed Bronze` (task default = CRL's finish name). It is not claimed to match Kohler BV. No prices or notes from the sheet are copied here.

## Modelling conventions

| Item | Choice | Reason |
|---|---|---|
| Front | +Y (toward the room) | task file; opposite Revit's template "Front" elevation; the clamp is symmetric |
| Origin | centre of joint gap, mid-height | task file: `Joint CL` X=0, `Glass Mid` Z=0, template `Center (Front/Back)` Y=0 |
| "Mirror about Glass Mid-plane Y=0" | read as the Y=0 plane | `Glass Mid` is defined as horizontal (Z=0); mirroring about it would flip the plate top-to-bottom |
| Plate Y extents | formula-driven START/END offsets | planes are dimension-driven only (task rule); helper parameters listed in README decision 2 |
| Identity parameters | Revit built-ins (`Manufacturer`, `Model`, `Description`, `Type Comments`) | adding parameters of those names is refused |
| `Cap_Spacing` formula text | `Clamp_Width - 2 in` | the `<number> in` spelling built the House of Troy family natively; `Clamp_Width - 2"` is the fallback |

## Not verified by this session

Revit API behaviour of: EQ dimensions (`AreSegmentsEqual`), `SketchPlane.Create(Document, Reference)`, `Sketch.Profile` alignment in elevation views, `FamilyElementVisibility` property names, `Document.GetUnusedElements`, the built-in `Type Comments` parameter, `SaveAsOptions.Compact`, and the resulting file size. The builder probes and records each; the gates decide.
