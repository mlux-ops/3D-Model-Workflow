<!-- worker5 completion -->
# Plumbing fixture row 6906143336759172

**Final status: BUILT_WITH_LIMITATIONS**

## Identity and scope

- Row ID: `6906143336759172`; item key: `813110-BNX-2.5__6906143336759172`.
- Scheduled product: Brizo / 813110-BNX-2.5.
- Scheduled description: Brizo Roccesco 12"   Single-Function Halo Raincan Shower Head, 2.5 GPM - Brilliance Black Onyx.
- Scheduled finish: Brilliance Black Onyx; Black; unit: Triplex; room: Primary Bathroom.
- Original agent_ignore: `false`. Coverage does not reinstate an ignored or descoped product.

Original source note: None recorded.

## Source and last verified stage

Shared product group: `813110-BNX-2.5`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [813110-BNX-2.5/Brizo_813110-BNX-2.5_R2025.rfa](<../813110-BNX-2.5/Brizo_813110-BNX-2.5_R2025.rfa>).
RFA SHA-256: `3e73c8e34305420b4a866bc8bf10b09772eac88b966f398999ef51dfdf931603`.
Validation: [validation.json](<../813110-BNX-2.5/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T14:48:40.147000Z.
Source RFA input version: Native custom build.
RFA search result: No acceptable no-account RFA recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"result": "No acceptable no-account RFA recovered", "evidence": "_research/813110-BNX-2.5/sources.json"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- Brizo BSP-B-813110 Rev A: https://assets.specbooks.cloud/brand/brizo/spec/22628776/document/spec-sb-eli3kf.pdf; page 1.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 311.15 | 311.15 | 0 | PASS |
| Y | 311.15 | 311.15 | 0 | PASS |
| Z | 88.9 | 88.9 | 0 | PASS |

All overall dimensions have manufacturer authority: **true**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- Diameter 12.25 in and total head depth 3.5 in: manufacturer drawing.
- Radial spoke width 1.75 in: manufacturer drawing.
- Native anchor/path: Halo diameter, measured 311.15 mm; nominal 311.15 mm; PASS.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: 813110-BNX-2.5 - Brilliance Black Onyx -  Black; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3769", "host_kind": "ceiling", "hostface_present": true, "instance_host_id": "3769", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Detail | True | True |
| Finish | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [813110-BNX-2.5/source/build.py](<../813110-BNX-2.5/source/build.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [Brizo_813110-BNX-2_5_R2025_Isolated - 3D View - Native Front.png](<../813110-BNX-2.5/evidence/Brizo_813110-BNX-2_5_R2025_Isolated - 3D View - Native Front.png>)
- [Brizo_813110-BNX-2_5_R2025_Isolated - 3D View - Native Material.png](<../813110-BNX-2.5/evidence/Brizo_813110-BNX-2_5_R2025_Isolated - 3D View - Native Material.png>)
- [Brizo_813110-BNX-2_5_R2025_Isolated - 3D View - Native Oblique.png](<../813110-BNX-2.5/evidence/Brizo_813110-BNX-2_5_R2025_Isolated - 3D View - Native Oblique.png>)
- [Brizo_813110-BNX-2_5_R2025_Isolated - 3D View - Native Side.png](<../813110-BNX-2.5/evidence/Brizo_813110-BNX-2_5_R2025_Isolated - 3D View - Native Side.png>)

## Assumptions and limitations

- Open annulus and radial spoke are retained; internal waterway and fine edge radii are simplified.
- Arm is supplied as its separate 899110-12-BNX family.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.

## Blockers and release

No additional identity-specific NEEDS_USER hold is recorded. Inferred geometry/finish fidelity still requires orchestrator review.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
