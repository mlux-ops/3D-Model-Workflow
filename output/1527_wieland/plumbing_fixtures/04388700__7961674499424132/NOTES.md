<!-- worker5 completion -->
# Plumbing fixture row 7961674499424132

**Final status: BUILT_WITH_LIMITATIONS**

## Identity and scope

- Row ID: `7961674499424132`; item key: `04388700__7961674499424132`.
- Scheduled product: Hansgrohe / 04388700.
- Scheduled description: Hansgrohe Croma Select S 180   2-Jet Shower Head, 1.8 GPM - Matte White.
- Scheduled finish: White; unit: Triplex; room: Bath 4.
- Original agent_ignore: `false`. Coverage does not reinstate an ignored or descoped product.

Original source note: None recorded.

## Source and last verified stage

Shared product group: `04388700`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [04388700/Hansgrohe_04388700_R2025.rfa](<../04388700/Hansgrohe_04388700_R2025.rfa>).
RFA SHA-256: `b2fcd69b5482402fdb769117e3b4817af0c88c593cc6bf67ce54ce4cc9934e6c`.
Validation: [validation.json](<../04388700/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T14:37:27.314000Z.
Source RFA input version: Native custom build.
RFA search result: No acceptable no-account RFA recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"evidence": "_research/04388700/sources.json", "result": "No acceptable no-account RFA recovered"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- Hansgrohe 2026 US Price Book: https://assets.hansgrohe.com/celum/emailmarketing/hansgrohe_2026_Price_Book_en_US.pdf; page 189.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 187.325 | 187.325 | 0 | PASS |
| Y | 187.325 | 187.325 | 0 | PASS |
| Z | 85.725 | 85.725 | 0 | PASS |

All overall dimensions have manufacturer authority: **true**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- Width and depth 7.375 in; total head height 3.375 in; 147 spray nozzles.
- Native anchor/path: Head overall width, measured 187.325 mm; nominal 187.325 mm; PASS.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: 04388700 - White; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3848", "host_kind": "ceiling", "hostface_present": true, "instance_host_id": "3848", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Detail | True | True |
| Finish | True | True |
| Gray | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [04388700/source/build.py](<../04388700/source/build.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [Hansgrohe_04388700_R2025_Isolated - 3D View - Native Front.png](<../04388700/evidence/Hansgrohe_04388700_R2025_Isolated - 3D View - Native Front.png>)
- [Hansgrohe_04388700_R2025_Isolated - 3D View - Native Material.png](<../04388700/evidence/Hansgrohe_04388700_R2025_Isolated - 3D View - Native Material.png>)
- [Hansgrohe_04388700_R2025_Isolated - 3D View - Native Oblique.png](<../04388700/evidence/Hansgrohe_04388700_R2025_Isolated - 3D View - Native Oblique.png>)
- [Hansgrohe_04388700_R2025_Isolated - 3D View - Native Side.png](<../04388700/evidence/Hansgrohe_04388700_R2025_Isolated - 3D View - Native Side.png>)

## Assumptions and limitations

- Ball joint shown in the neutral vertical position. Nozzle distribution and shoulder profile follow the drawing approximately.
- Scheduled matte-white finish retained; the current catalog omits this legacy all-white SKU.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.

## Blockers and release

No additional identity-specific NEEDS_USER hold is recorded. Inferred geometry/finish fidelity still requires orchestrator review.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
