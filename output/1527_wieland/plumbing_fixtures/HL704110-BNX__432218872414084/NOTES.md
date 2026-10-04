<!-- worker5 completion -->
# Plumbing fixture row 432218872414084

**Final status: BUILT_WITH_LIMITATIONS**

## Identity and scope

- Row ID: `432218872414084`; item key: `HL704110-BNX__432218872414084`.
- Scheduled product: Brizo / HL704110-BNX.
- Scheduled description: Brizo Two-Handle Wall-Mount Tub Lever Handle Kit.
- Scheduled finish: -; unit: Triplex; room: Primary Bathroom.
- Original agent_ignore: `false`. Coverage does not reinstate an ignored or descoped product.

Original source note: None recorded.

## Source and last verified stage

Shared product group: `HL704110-BNX`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [HL704110-BNX/Brizo_HL704110-BNX_R2025.rfa](<../HL704110-BNX/Brizo_HL704110-BNX_R2025.rfa>).
RFA SHA-256: `8ba47aab617376f011b1109f5a1579a3cd8433f7d3580305c8e6b1c932844e73`.
Validation: [validation.json](<../HL704110-BNX/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T14:49:13.660000Z.
Source RFA input version: Native custom build.
RFA search result: No acceptable no-account RFA recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"result": "No acceptable no-account RFA recovered", "evidence": "_research/HL704110-BNX/sources.json"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- BSP-B-T704110-LHP Rev B: https://bravo.requested-info.com/brands/BRZ/documents/specSheets/T704110-BLLHP_Spec.pdf; page 1.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 361.95 | 361.95 | 0 | PASS |
| Y | 69.85 | 69.85 | 0 | PASS |
| Z | 73.025 | 73.025 | 0 | PASS |

All overall dimensions have manufacturer authority: **false**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- Bases diameter 2.75 in; installed handle projection 2.875 in; lever axis-to-tip reach 3.125 in.
- Native anchor/path: Handle projection, measured 73.025 mm; nominal 73.025 mm; PASS.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: HL704110-BNX - onyx; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3693", "host_kind": "wall", "hostface_present": true, "instance_host_id": "3693", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Finish | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [HL704110-BNX/source/build.py](<../HL704110-BNX/source/build.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [Brizo_HL704110-BNX_R2025_Isolated - 3D View - Native Front.png](<../HL704110-BNX/evidence/Brizo_HL704110-BNX_R2025_Isolated - 3D View - Native Front.png>)
- [Brizo_HL704110-BNX_R2025_Isolated - 3D View - Native Material.png](<../HL704110-BNX/evidence/Brizo_HL704110-BNX_R2025_Isolated - 3D View - Native Material.png>)
- [Brizo_HL704110-BNX_R2025_Isolated - 3D View - Native Oblique.png](<../HL704110-BNX/evidence/Brizo_HL704110-BNX_R2025_Isolated - 3D View - Native Oblique.png>)
- [Brizo_HL704110-BNX_R2025_Isolated - 3D View - Native Side.png](<../HL704110-BNX/evidence/Brizo_HL704110-BNX_R2025_Isolated - 3D View - Native Side.png>)

## Assumptions and limitations

- ASSUMPTION: paired at the companion trim 8 in centers, levers pointing outwards. Fine lever taper is simplified.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.

## Blockers and release

No additional identity-specific NEEDS_USER hold is recorded. Inferred geometry/finish fidelity still requires orchestrator review.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
