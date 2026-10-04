<!-- worker5 completion -->
# Plumbing fixture row 2472912453566340

**Final status: BUILT_WITH_LIMITATIONS**

## Identity and scope

- Row ID: `2472912453566340`; item key: `61320LF-C-BL__2472912453566340`.
- Scheduled product: Brizo / 61320LF-C-BL.
- Scheduled description: Brizo   Solna Cold-Only Beverage Faucet with Arc Spout - Matte Black.
- Scheduled finish: Matte Black; Black; unit: Triplex; room: Kitchen.
- Original agent_ignore: `false`. Coverage does not reinstate an ignored or descoped product.

Original source note: None recorded.

## Source and last verified stage

Shared product group: `61320LF-C-BL`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [61320LF-C-BL/Brizo_61320LF-C-BL_R2025.rfa](<../61320LF-C-BL/Brizo_61320LF-C-BL_R2025.rfa>).
RFA SHA-256: `981b298ff2a6fd5b3a7aed6b112f829ba53ba5d15168bfdd4af94b1daaa34063`.
Validation: [validation.json](<../61320LF-C-BL/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T15:27:34.689000Z.
Source RFA input version: Native custom build.
RFA search result: No acceptable no-account RFA recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"result": "No acceptable no-account RFA recovered", "evidence": "_research/61320LF-C-BL/sources.json"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- Brizo BSP-K-61320LF-C Rev B: https://media.brizo.com/SpecSheet/BSP-K-61320LF-C%20Rev%20B.pdf; page 1.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 88.9 | 88.9 | 0 | PASS |
| Y | 163.5125 | 163.5125 | 0 | PASS |
| Z | 241.3 | 241.3 | 0 | PASS |

All overall dimensions have manufacturer authority: **false**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- Overall height 9.5 in, base diameter 2 in, outlet height 6.0625 in and reach 5.0625 in.
- Native anchor/path: Height, measured 241.3 mm; nominal 241.3 mm; PASS.
- Native anchor/path: Base diameter, measured 50.8 mm; nominal 50.8 mm; PASS.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: 61320LF-C-BL - Matte Black -  Black; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3699", "host_kind": "floor", "hostface_present": true, "instance_host_id": "3699", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Detail | True | True |
| Finish | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [61320LF-C-BL/source/build.py](<../61320LF-C-BL/source/build.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [Brizo_61320LF-C-BL_R2025_Isolated - 3D View - Native Front.png](<../61320LF-C-BL/evidence/Brizo_61320LF-C-BL_R2025_Isolated - 3D View - Native Front.png>)
- [Brizo_61320LF-C-BL_R2025_Isolated - 3D View - Native Material.png](<../61320LF-C-BL/evidence/Brizo_61320LF-C-BL_R2025_Isolated - 3D View - Native Material.png>)
- [Brizo_61320LF-C-BL_R2025_Isolated - 3D View - Native Oblique.png](<../61320LF-C-BL/evidence/Brizo_61320LF-C-BL_R2025_Isolated - 3D View - Native Oblique.png>)
- [Brizo_61320LF-C-BL_R2025_Isolated - 3D View - Native Side.png](<../61320LF-C-BL/evidence/Brizo_61320LF-C-BL_R2025_Isolated - 3D View - Native Side.png>)

## Assumptions and limitations

- Above-counter scope only. Side lever envelope, body diameter and spout tube section are drawing-derived.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.

## Blockers and release

No additional identity-specific NEEDS_USER hold is recorded. Inferred geometry/finish fidelity still requires orchestrator review.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
