<!-- worker5 completion -->
# Plumbing fixture row 1214550655041412

**Final status: BUILT_WITH_LIMITATIONS**

## Identity and scope

- Row ID: `1214550655041412`; item key: `04790000__1214550655041412`.
- Scheduled product: Hansgrohe / 04790000.
- Scheduled description: Hansgrohe Croma Select E 1.8 GPM Multi Function Hand Shower Package with Select Technology - Includes Slide Bar and Hose.
- Scheduled finish: -; unit: Penthouse; room: Bath 3.
- Original agent_ignore: `false`. Coverage does not reinstate an ignored or descoped product.

Original source note: None recorded.

## Source and last verified stage

Shared product group: `04790000`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [04790000/Hansgrohe_04790000_R2025.rfa](<../04790000/Hansgrohe_04790000_R2025.rfa>).
RFA SHA-256: `a80f48ec81e8b8347e6528aa1056304f09a0023f31c69cb0896775da930d2915`.
Validation: [validation.json](<../04790000/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T15:43:33.715000Z.
Source RFA input version: Native custom build.
RFA search result: No acceptable no-account RFA recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"result": "No acceptable no-account RFA recovered", "evidence": "_research/04790000/sources.json"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- Hansgrohe 2026 US Price Book: https://assets.hansgrohe.com/celum/emailmarketing/hansgrohe_2026_Price_Book_en_US.pdf; page 252.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 141.351 | 141.351 | 0 | PASS |
| Y | 1348.445 | 1348.445 | -0 | PASS |
| Z | 105.41 | 105.41 | 0 | PASS |

All overall dimensions have manufacturer authority: **false**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- Bar 28.25 in and diameter 0.875 in; hose 63 in; handset 110 mm nominal spray-face size.
- Native anchor/path: Slide bar length, measured 717.55 mm; nominal 717.55 mm; PASS.
- Native anchor/path: 63 inch hose, measured 1600.2 mm; nominal 1600.2 mm; PASS.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: 04790000 - chrome; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3739", "host_kind": "wall", "hostface_present": true, "instance_host_id": "3739", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Ceramic | True | True |
| Detail | True | True |
| Finish | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [04790000/source/build.py](<../04790000/source/build.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [Hansgrohe_04790000_R2025_Isolated - 3D View - Native Front.png](<../04790000/evidence/Hansgrohe_04790000_R2025_Isolated - 3D View - Native Front.png>)
- [Hansgrohe_04790000_R2025_Isolated - 3D View - Native Material.png](<../04790000/evidence/Hansgrohe_04790000_R2025_Isolated - 3D View - Native Material.png>)
- [Hansgrohe_04790000_R2025_Isolated - 3D View - Native Oblique.png](<../04790000/evidence/Hansgrohe_04790000_R2025_Isolated - 3D View - Native Oblique.png>)
- [Hansgrohe_04790000_R2025_Isolated - 3D View - Native Side.png](<../04790000/evidence/Hansgrohe_04790000_R2025_Isolated - 3D View - Native Side.png>)

## Assumptions and limitations

- ASSUMPTION: upright handset and fixed U hose display pose. The full posed envelope is not a manufacturer rigid overall dimension.
- Handset angle, slider, connection and rounded-square edge details are simplified.
- The current catalog calls this 1.75 GPM, while the schedule describes 1.8 GPM.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.

## Blockers and release

No additional identity-specific NEEDS_USER hold is recorded. Inferred geometry/finish fidelity still requires orchestrator review.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
