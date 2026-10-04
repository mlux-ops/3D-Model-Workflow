<!-- worker5 completion -->
# Plumbing fixture row 924800081657732

**Final status: BUILT_WITH_LIMITATIONS**

## Identity and scope

- Row ID: `924800081657732`; item key: `CT446CEFGNT40_01__924800081657732`.
- Scheduled product: TOTO / CT446CEFGNT40#01.
- Scheduled description: TOTO   Aquia IV WASHLET+ Elongated Toilet Bowl - Cotton.
- Scheduled finish: -; unit: Triplex; room: Bath 3.
- Original agent_ignore: `false`. Coverage does not reinstate an ignored or descoped product.

Original source note: None recorded.

## Source and last verified stage

Shared product group: `CT446CEFGNT40_01`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [CT446CEFGNT40_01/TOTO_CT446CEFGNT40_01_R2025.rfa](<../CT446CEFGNT40_01/TOTO_CT446CEFGNT40_01_R2025.rfa>).
RFA SHA-256: `1e7cbd6a3fe1946e8f479980ed053105768f4d0ca2c777b8bb3ce19ab2d94f85`.
Validation: [validation.json](<../CT446CEFGNT40_01/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T15:43:40.762000Z.
Source RFA input version: Native custom build.
RFA search result: No acceptable no-account RFA recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"result": "No acceptable no-account RFA recovered", "evidence": "_research/CT446CEFGNT40_01/sources.json"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- TOTO Aquia IV SS-02062: https://www.totousa.com/filemanager_uploads/product_assets/SpecSheet/SS-02062_MS446124CEMF(G)N.pdf; page 2.
- TOTO Aquia IV PD-01451 parts: https://www.totousa.com/filemanager_uploads/product_assets/PartsManual/PD-01451_446EN.pdf; page 1.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 368.6043 | 368.3 | 0.3043 | PASS |
| Y | 700.9539 | 700.0875 | 0.8664 | PASS |
| Z | 409.575 | 409.575 | 0 | PASS |

All overall dimensions have manufacturer authority: **false**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- Floor-to-rim 16.125 in and full set depth 27.5625 in from manufacturer drawing; exact component number confirmed in parts manual.
- Native anchor/path: Rim height, measured 409.575 mm; nominal 409.575 mm; PASS.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: CT446CEFGNT40#01 - ceramic; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3690", "host_kind": "floor", "hostface_present": true, "instance_host_id": "3690", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Finish | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [CT446CEFGNT40_01/source/build.py](<../CT446CEFGNT40_01/source/build.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [TOTO_CT446CEFGNT40_01_R2025_Isolated - 3D View - Native Front.png](<../CT446CEFGNT40_01/evidence/TOTO_CT446CEFGNT40_01_R2025_Isolated - 3D View - Native Front.png>)
- [TOTO_CT446CEFGNT40_01_R2025_Isolated - 3D View - Native Material.png](<../CT446CEFGNT40_01/evidence/TOTO_CT446CEFGNT40_01_R2025_Isolated - 3D View - Native Material.png>)
- [TOTO_CT446CEFGNT40_01_R2025_Isolated - 3D View - Native Oblique.png](<../CT446CEFGNT40_01/evidence/TOTO_CT446CEFGNT40_01_R2025_Isolated - 3D View - Native Oblique.png>)
- [TOTO_CT446CEFGNT40_01_R2025_Isolated - 3D View - Native Side.png](<../CT446CEFGNT40_01/evidence/TOTO_CT446CEFGNT40_01_R2025_Isolated - 3D View - Native Side.png>)

## Assumptions and limitations

- Bowl-only width 14.5 in, underside footprint, bowl interior and shell curvature are drawing-derived; no separate bowl fabrication sheet was found.
- The tank, seat and push-button are separate scheduled components. This family has an open bowl and rear mounting deck.
- Internal trapway, WASHLET connection pocket and fixture-specific anchor recesses are omitted.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.

## Blockers and release

No additional identity-specific NEEDS_USER hold is recorded. Inferred geometry/finish fidelity still requires orchestrator review.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
