<!-- worker5 completion -->
# Plumbing fixture row 6022321546002308

**Final status: BUILT_WITH_LIMITATIONS**

## Identity and scope

- Row ID: `6022321546002308`; item key: `RP72414GL__6022321546002308`.
- Scheduled product: Brizo / RP72414GL.
- Scheduled description: Brizo   Push-Button Pop-Up Lavatory Drain with Overflow - Luxe Gold.
- Scheduled finish: Gold; unit: Penthouse; room: Powder Room.
- Original agent_ignore: `false`. Coverage does not reinstate an ignored or descoped product.

Original source note: None recorded.

## Source and last verified stage

Shared product group: `RP72414GL`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [RP72414GL/Brizo_RP72414GL_R2025.rfa](<../RP72414GL/Brizo_RP72414GL_R2025.rfa>).
RFA SHA-256: `ce98cb84c4ce5f2621efb54b1d4c90f5d8136dfd63f796c161e216011d9dd53c`.
Validation: [validation.json](<../RP72414GL/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T14:49:25.812000Z.
Source RFA input version: Native custom build.
RFA search result: No acceptable no-account RFA recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"result": "No acceptable no-account RFA recovered", "evidence": "_research/RP72414GL/sources.json"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- BSP-L-653110LF-LHP Rev A: https://bravo.requested-info.com/brands/BRZ/documents/specSheets/653110LF-BLLHP_Spec.pdf; page 1.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 69.85 | 69.85 | 0 | PASS |
| Y | 69.85 | 69.85 | 0 | PASS |
| Z | 165.5356 | 165.1 | 0.4356 | PASS |

All overall dimensions have manufacturer authority: **false**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- Cap diameter 2.75 in from the exact RP72414 detail.
- Native anchor/path: Cap diameter, measured 69.85 mm; nominal 69.85 mm; PASS.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: RP72414GL - Gold; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3699", "host_kind": "floor", "hostface_present": true, "instance_host_id": "3699", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Detail | True | True |
| Finish | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [RP72414GL/source/build.py](<../RP72414GL/source/build.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [Brizo_RP72414GL_R2025_Isolated - 3D View - Native Front.png](<../RP72414GL/evidence/Brizo_RP72414GL_R2025_Isolated - 3D View - Native Front.png>)
- [Brizo_RP72414GL_R2025_Isolated - 3D View - Native Material.png](<../RP72414GL/evidence/Brizo_RP72414GL_R2025_Isolated - 3D View - Native Material.png>)
- [Brizo_RP72414GL_R2025_Isolated - 3D View - Native Oblique.png](<../RP72414GL/evidence/Brizo_RP72414GL_R2025_Isolated - 3D View - Native Oblique.png>)
- [Brizo_RP72414GL_R2025_Isolated - 3D View - Native Side.png](<../RP72414GL/evidence/Brizo_RP72414GL_R2025_Isolated - 3D View - Native Side.png>)

## Assumptions and limitations

- ASSUMPTION: fixed 6 in tailpiece cut length, 1.25 in outside diameter and underside stack from the drawing.
- Overflow ports and threaded internals are simplified; cap shown open.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.

## Blockers and release

No additional identity-specific NEEDS_USER hold is recorded. Inferred geometry/finish fidelity still requires orchestrator review.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
