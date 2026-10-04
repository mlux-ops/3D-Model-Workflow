<!-- worker5 completion -->
# Plumbing fixture row 7187618313469828

**Final status: BUILT_WITH_LIMITATIONS**

## Identity and scope

- Row ID: `7187618313469828`; item key: `TER-N-SW-OF__7187618313469828`.
- Scheduled product: - / TER-N-SW-OF.
- Scheduled description: Victoria + Albert Terrassa 67" x 32" Freestanding Soaking Bathtub - Volcanic Limestone, Standard Gloss White, with Overflow.
- Scheduled finish: White; unit: Triplex; room: Primary Bathroom.
- Original agent_ignore: `false`. Coverage does not reinstate an ignored or descoped product.

Original source note: Original cell value was "Fullerton Tub" (no SKU, no link). Resolved 2026-08-04 from 23-008 513 W Fullerton, sheet FINISH DATABASE -Fullerton, Unit Type "Duplex Down" / Room Type "Primary Bathroom" (rows 5480997068705668 and 7270009266769796). Specs: 67 x 31-1/4 x 20-3/4 in, 80 gal, 163 lb empty, centre drain, volcanic limestone. Drain sold separately - see K-51-WH row. Confirm before ordering. | NEEDS REVIEW 2026-10-01: identity is resolved as Victoria + Albert Terrassa TER-N-SW-OF, but live unit cost is still $0. Obtain a current vendor quote before award. | RESOLVED 2026-10-01: current 1529 fixture deck and multiple current retailers list TER-N-SW-OF at $5,931.00; unit cost set to $5,931 and COGS to $6,538.9275 at the sheet 1.1025 factor. Drain remains separate.

## Source and last verified stage

Shared product group: `TER-N-SW-OF`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [TER-N-SW-OF/Fixture_TER-N-SW-OF_R2025.rfa](<../TER-N-SW-OF/Fixture_TER-N-SW-OF_R2025.rfa>).
RFA SHA-256: `ac0d8e4f8c22ba97f1e798b8fdbcb7b4b0d146c15101f1592a9efab96d78b8ca`.
Validation: [validation.json](<../TER-N-SW-OF/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T15:27:48.410000Z.
Source RFA input version: Native custom build.
RFA search result: No acceptable no-account RFA recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"result": "No acceptable no-account RFA recovered", "evidence": "_research/TER-N-SW-OF/sources.json"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- Victoria + Albert Terrassa Rev 09/23: https://assets.fbgpg.com/shared/docs/product-specifications/spc-ter-n-sw_ofsp.pdf; page 1.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 1701.8 | 1701.8 | 0 | PASS |
| Y | 793.75 | 793.75 | 0 | PASS |
| Z | 527.05 | 527.05 | 0 | PASS |

All overall dimensions have manufacturer authority: **true**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- Overall 67 x 31.25 x 20.75 in; base 43.75 x 19.5 in; drain diameter 2 in.
- Native anchor/path: Overall length, measured 1701.8 mm; nominal 1701.8 mm; PASS.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: TER-N-SW-OF - White; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3690", "host_kind": "floor", "hostface_present": true, "instance_host_id": "3690", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Finish | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [TER-N-SW-OF/source/build.py](<../TER-N-SW-OF/source/build.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [Fixture_TER-N-SW-OF_R2025_Isolated - 3D View - Native Front.png](<../TER-N-SW-OF/evidence/Fixture_TER-N-SW-OF_R2025_Isolated - 3D View - Native Front.png>)
- [Fixture_TER-N-SW-OF_R2025_Isolated - 3D View - Native Material.png](<../TER-N-SW-OF/evidence/Fixture_TER-N-SW-OF_R2025_Isolated - 3D View - Native Material.png>)
- [Fixture_TER-N-SW-OF_R2025_Isolated - 3D View - Native Oblique.png](<../TER-N-SW-OF/evidence/Fixture_TER-N-SW-OF_R2025_Isolated - 3D View - Native Oblique.png>)
- [Fixture_TER-N-SW-OF_R2025_Isolated - 3D View - Native Side.png](<../TER-N-SW-OF/evidence/Fixture_TER-N-SW-OF_R2025_Isolated - 3D View - Native Side.png>)

## Assumptions and limitations

- Undimensioned shell sections and curvature reconstructed from the orthographic drawing.
- No K-51 waste assembly is included; the actual drain and overflow openings remain open.
- Original manufacturer download was a 3DS mesh, not RFA, and is preserved as source evidence.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.

## Blockers and release

No additional identity-specific NEEDS_USER hold is recorded. Inferred geometry/finish fidelity still requires orchestrator review.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
