<!-- worker5 completion -->
# Plumbing fixture row 7398724546002820

**Final status: BUILT_WITH_LIMITATIONS**

## Identity and scope

- Row ID: `7398724546002820`; item key: `26843701__7398724546002820`.
- Scheduled product: Hansgrohe / 26843701.
- Scheduled description: Hansgrohe Rainfinity Wall Outlet   500 with Hand Shower Holder and Shelf - Matte White.
- Scheduled finish: White; unit: Triplex; room: Bath 4.
- Original agent_ignore: `false`. Coverage does not reinstate an ignored or descoped product.

Original source note: None recorded.

## Source and last verified stage

Shared product group: `26843701`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [26843701/Hansgrohe_26843701_R2025.rfa](<../26843701/Hansgrohe_26843701_R2025.rfa>).
RFA SHA-256: `71a5edeaf42eb218b4c989a9fb5e9d792765df2484dad413e931941f896fdf5f`.
Validation: [validation.json](<../26843701/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T14:48:56.682000Z.
Source RFA input version: Native custom build.
RFA search result: No acceptable no-account RFA recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"result": "No acceptable no-account RFA recovered", "evidence": "_research/26843701/sources.json"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- Hansgrohe 2026 US Price Book: https://assets.hansgrohe.com/celum/emailmarketing/hansgrohe_2026_Price_Book_en_US.pdf; page 266.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 501.65 | 501.65 | 0 | PASS |
| Y | 62.23 | 62.23 | 0 | PASS |
| Z | 97.79 | 97.79 | 0 | PASS |

All overall dimensions have manufacturer authority: **false**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- Body span 19.625 in; glass span 19.75 in interpreted from the two separately annotated widths; fixing centers 15.75 in.
- Native anchor/path: Body span, measured 498.475 mm; nominal 498.475 mm; PASS.
- Native anchor/path: Glass span, measured 501.65 mm; nominal 501.65 mm; PASS.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: 26843701 - White; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3696", "host_kind": "wall", "hostface_present": true, "instance_host_id": "3696", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Finish | True | True |
| Graphite | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [26843701/source/build.py](<../26843701/source/build.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [Hansgrohe_26843701_R2025_Isolated - 3D View - Native Front.png](<../26843701/evidence/Hansgrohe_26843701_R2025_Isolated - 3D View - Native Front.png>)
- [Hansgrohe_26843701_R2025_Isolated - 3D View - Native Material.png](<../26843701/evidence/Hansgrohe_26843701_R2025_Isolated - 3D View - Native Material.png>)
- [Hansgrohe_26843701_R2025_Isolated - 3D View - Native Oblique.png](<../26843701/evidence/Hansgrohe_26843701_R2025_Isolated - 3D View - Native Oblique.png>)
- [Hansgrohe_26843701_R2025_Isolated - 3D View - Native Side.png](<../26843701/evidence/Hansgrohe_26843701_R2025_Isolated - 3D View - Native Side.png>)

## Assumptions and limitations

- ASSUMPTION: shelf depth 3.75 in and holder projection 3.85 in from proportions; no explicit side dimension was recovered.
- Left holder slot is represented by separate cheeks; the body, glass and outlet remain separate materials.
- White legacy SKU is retained although omitted from the current main catalog.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.

## Blockers and release

No additional identity-specific NEEDS_USER hold is recorded. Inferred geometry/finish fidelity still requires orchestrator review.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
