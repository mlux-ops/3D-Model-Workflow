<!-- worker5 completion -->
# Plumbing fixture row 1769225011789700

**Final status: BUILT_WITH_LIMITATIONS**

## Identity and scope

- Row ID: `1769225011789700`; item key: `28276703__1769225011789700`.
- Scheduled product: Hansgrohe / 28276703.
- Scheduled description: Hansgrohe Isiflex 63" Hand Shower Hose - Matte White.
- Scheduled finish: White; unit: Triplex; room: Bath 4.
- Original agent_ignore: `false`. Coverage does not reinstate an ignored or descoped product.

Original source note: None recorded.

## Source and last verified stage

Shared product group: `28276703`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [28276703/Hansgrohe_28276703_R2025.rfa](<../28276703/Hansgrohe_28276703_R2025.rfa>).
RFA SHA-256: `4e1fd64385defcf595c934d6654a5a401a48850600e7b55d7109ef2a16996700`.
Validation: [validation.json](<../28276703/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T14:37:45.404000Z.
Source RFA input version: Native custom build.
RFA search result: No acceptable no-account RFA recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"evidence": "_research/28276703/sources.json", "result": "No acceptable no-account RFA recovered"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- Hansgrohe 2026 US Price Book: https://assets.hansgrohe.com/celum/emailmarketing/hansgrohe_2026_Price_Book_en_US.pdf; page 277.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 174.752 | 174.752 | 0 | PASS |
| Y | 771.8453 | 771.8453 | -0 | PASS |
| Z | 22.352 | 22.352 | 0 | PASS |

All overall dimensions have manufacturer authority: **false**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- Manufacturer nominal flexible hose length 63 in. U-pose centerline consists of two equal legs and a 3 in radius semicircle.
- Native anchor/path: 63 inch hose, measured 1600.2 mm; nominal 1600.2 mm; PASS.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: 28276703 - White; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3690", "host_kind": "wall", "hostface_present": true, "instance_host_id": "3690", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Finish | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [28276703/source/build.py](<../28276703/source/build.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [Hansgrohe_28276703_R2025_Isolated - 3D View - Native Front.png](<../28276703/evidence/Hansgrohe_28276703_R2025_Isolated - 3D View - Native Front.png>)
- [Hansgrohe_28276703_R2025_Isolated - 3D View - Native Material.png](<../28276703/evidence/Hansgrohe_28276703_R2025_Isolated - 3D View - Native Material.png>)
- [Hansgrohe_28276703_R2025_Isolated - 3D View - Native Oblique.png](<../28276703/evidence/Hansgrohe_28276703_R2025_Isolated - 3D View - Native Oblique.png>)
- [Hansgrohe_28276703_R2025_Isolated - 3D View - Native Side.png](<../28276703/evidence/Hansgrohe_28276703_R2025_Isolated - 3D View - Native Side.png>)

## Assumptions and limitations

- Fixed hanging pose is an installation assumption; its bounding box is not a manufacturer product envelope.
- Connector dimensions and hose outside diameter are drawing-derived. Matte-white legacy finish retained.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.

## Blockers and release

No additional identity-specific NEEDS_USER hold is recorded. Inferred geometry/finish fidelity still requires orchestrator review.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
