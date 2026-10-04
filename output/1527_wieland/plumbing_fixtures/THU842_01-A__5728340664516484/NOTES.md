<!-- worker5 completion -->
# Plumbing fixture row 5728340664516484

**Final status: BUILT_WITH_LIMITATIONS**

## Identity and scope

- Row ID: `5728340664516484`; item key: `THU842_01-A__5728340664516484`.
- Scheduled product: TOTO / THU842#01-A.
- Scheduled description: TOTO Aquia Push-Button Assembly   with Rods - Cotton.
- Scheduled finish: -; unit: Penthouse; room: Bath 4.
- Original agent_ignore: `false`. Coverage does not reinstate an ignored or descoped product.

Original source note: None recorded.

## Source and last verified stage

Shared product group: `THU842_01-A`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [THU842_01-A/TOTO_THU842_01-A_R2025.rfa](<../THU842_01-A/TOTO_THU842_01-A_R2025.rfa>).
RFA SHA-256: `bf928d836546e8bee77ff51e6c6da1216265f973c528a64312bcbc785c05f386`.
Validation: [validation.json](<../THU842_01-A/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T15:55:29.659000Z.
Source RFA input version: Native custom build.
RFA search result: No acceptable no-account RFA recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"result": "No acceptable no-account RFA recovered", "evidence": "_research/THU842_01-A/sources.json"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- TOTO PD-01451 Aquia IV exact component illustration: https://www.totousa.com/filemanager_uploads/product_assets/PartsManual/PD-01451_446EN.pdf; page 1.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 47.244 | 47.244 | 0 | PASS |
| Y | 47.244 | 47.244 | 0 | PASS |
| Z | 144.272 | 144.272 | 0 | PASS |

All overall dimensions have manufacturer authority: **false**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- Exact part identity is verified in the manufacturer component illustration; no independent numeric component dimensions are published there.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: THU842#01-A - white; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3698", "host_kind": "floor", "hostface_present": true, "instance_host_id": "3698", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Finish | True | True |
| Gray | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [THU842_01-A/source/build.py](<../THU842_01-A/source/build.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [TOTO_THU842_01-A_R2025_Isolated - 3D View - Native Front.png](<../THU842_01-A/evidence/TOTO_THU842_01-A_R2025_Isolated - 3D View - Native Front.png>)
- [TOTO_THU842_01-A_R2025_Isolated - 3D View - Native Material.png](<../THU842_01-A/evidence/TOTO_THU842_01-A_R2025_Isolated - 3D View - Native Material.png>)
- [TOTO_THU842_01-A_R2025_Isolated - 3D View - Native Oblique.png](<../THU842_01-A/evidence/TOTO_THU842_01-A_R2025_Isolated - 3D View - Native Oblique.png>)
- [TOTO_THU842_01-A_R2025_Isolated - 3D View - Native Side.png](<../THU842_01-A/evidence/TOTO_THU842_01-A_R2025_Isolated - 3D View - Native Side.png>)

## Assumptions and limitations

- DIMENSION HOLD: all button and rod dimensions are inferred from the illustrated relationship to the known tank; they are not manufacturer-verified dimensions.
- Rod length 5.5 in is an illustrative uncut setting. This family is suitable only for approximate visualization until the supplied component is measured.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.

## Blockers and release

- NEEDS_USER_THU842_DIMENSIONS: Button and rod dimensions are inferred from the illustrated relationship to the known tank. Native agreement with configured geometry does not verify manufacturer dimensions. Confirm actual dimensions or approve this limited representation.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
