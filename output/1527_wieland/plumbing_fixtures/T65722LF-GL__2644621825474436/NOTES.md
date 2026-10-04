<!-- worker5 completion -->
# Plumbing fixture row 2644621825474436

**Final status: BUILT_WITH_LIMITATIONS**

## Identity and scope

- Row ID: `2644621825474436`; item key: `T65722LF-GL__2644621825474436`.
- Scheduled product: Brizo / T65722LF-GL.
- Scheduled description: Brizo Frank Lloyd Wright   Wall-Mount Single-Handle Bathroom Faucet Trim, 1.2 GPM - Luxe Gold.
- Scheduled finish: Gold; unit: Penthouse; room: Powder Room.
- Original agent_ignore: `false`. Coverage does not reinstate an ignored or descoped product.

Original source note: None recorded.

## Source and last verified stage

Shared product group: `T65722LF-GL`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [T65722LF-GL/Brizo_T65722LF-GL_R2025.rfa](<../T65722LF-GL/Brizo_T65722LF-GL_R2025.rfa>).
RFA SHA-256: `4f6b8688da7c5c2101a2a791f4783e52260d077d5541333ad5eb5a75c5a7cb2b`.
Validation: [validation.json](<../T65722LF-GL/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T14:49:16.973000Z.
Source RFA input version: Native custom build.
RFA search result: No acceptable no-account RFA recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"result": "No acceptable no-account RFA recovered", "evidence": "_research/T65722LF-GL/sources.json"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- BSP-L-T65722LF Rev D: https://bravo.requested-info.com/brands/BRZ/documents/specSheets/T65722LF-GL_Spec.pdf; page 1.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 58.7375 | 58.7375 | 0 | PASS |
| Y | 88.9 | 88.9 | 0 | PASS |
| Z | 271.4625 | 271.4625 | 0 | PASS |

All overall dimensions have manufacturer authority: **true**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- Overall projection 10.6875 in; overall vertical envelope 3.5 in; escutcheon square 2.3125 in; nominal outlet reach 9.625 in.
- Native anchor/path: Overall projection, measured 271.4625 mm; nominal 271.4625 mm; PASS.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: T65722LF-GL - Gold; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3698", "host_kind": "wall", "hostface_present": true, "instance_host_id": "3698", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Detail | True | True |
| Finish | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [T65722LF-GL/source/build.py](<../T65722LF-GL/source/build.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [Brizo_T65722LF-GL_R2025_Isolated - 3D View - Native Front.png](<../T65722LF-GL/evidence/Brizo_T65722LF-GL_R2025_Isolated - 3D View - Native Front.png>)
- [Brizo_T65722LF-GL_R2025_Isolated - 3D View - Native Material.png](<../T65722LF-GL/evidence/Brizo_T65722LF-GL_R2025_Isolated - 3D View - Native Material.png>)
- [Brizo_T65722LF-GL_R2025_Isolated - 3D View - Native Oblique.png](<../T65722LF-GL/evidence/Brizo_T65722LF-GL_R2025_Isolated - 3D View - Native Oblique.png>)
- [Brizo_T65722LF-GL_R2025_Isolated - 3D View - Native Side.png](<../T65722LF-GL/evidence/Brizo_T65722LF-GL_R2025_Isolated - 3D View - Native Side.png>)

## Assumptions and limitations

- Native model follows the current exact-SKU Frank Lloyd Wright drawing.
- Control fore/aft placement and rectangular sections are drawing-derived; no teak insert is added to the non-TK SKU.
- R65700 rough-in is separate.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.

## Blockers and release

No additional identity-specific NEEDS_USER hold is recorded. Inferred geometry/finish fidelity still requires orchestrator review.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
