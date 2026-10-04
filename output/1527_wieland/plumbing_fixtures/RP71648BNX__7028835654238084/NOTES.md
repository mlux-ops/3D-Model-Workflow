<!-- worker5 completion -->
# Plumbing fixture row 7028835654238084

**Final status: BUILT_WITH_LIMITATIONS**

## Identity and scope

- Row ID: `7028835654238084`; item key: `RP71648BNX__7028835654238084`.
- Scheduled product: Brizo / RP71648BNX.
- Scheduled description: Brizo 16" Linear Round   Wall-Mount Shower Arm and Flange - Brilliance Black Onyx.
- Scheduled finish: Brilliance Black Onyx; Black; unit: Penthouse; room: Bath 4.
- Original agent_ignore: `false`. Coverage does not reinstate an ignored or descoped product.

Original source note: None recorded.

## Source and last verified stage

Shared product group: `RP71648BNX`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [RP71648BNX/Brizo_RP71648BNX_R2025.rfa](<../RP71648BNX/Brizo_RP71648BNX_R2025.rfa>).
RFA SHA-256: `40bf67daba52c1076a5a1159e00417039b94986dfc64ab688c4a8745ca4d9101`.
Validation: [validation.json](<../RP71648BNX/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T15:43:11.261000Z.
Source RFA input version: Native custom build.
RFA search result: No acceptable no-account RFA recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"result": "No acceptable no-account RFA recovered", "evidence": "_research/RP71648BNX/sources.json"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- Brizo BSP-B-RP71648 Rev D: https://media.brizo.com/SpecSheet/BSP-B-RP71648%20Rev%20D.pdf; page 1.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 63.5 | 63.5 | 0 | PASS |
| Y | 95.25 | 95.25 | 0 | PASS |
| Z | 406.4 | 406.4 | 0 | PASS |

All overall dimensions have manufacturer authority: **true**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- Projection 16 in, flange diameter 2.5 in, and centerline-to-outlet drop 2.5 in: manufacturer drawing.
- Native anchor/path: Arm projection, measured 406.4 mm; nominal 406.4 mm; PASS.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: RP71648BNX - Brilliance Black Onyx -  Black; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3694", "host_kind": "wall", "hostface_present": true, "instance_host_id": "3694", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Detail | True | True |
| Finish | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [RP71648BNX/source/build.py](<../RP71648BNX/source/build.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [Brizo_RP71648BNX_R2025_Isolated - 3D View - Native Front.png](<../RP71648BNX/evidence/Brizo_RP71648BNX_R2025_Isolated - 3D View - Native Front.png>)
- [Brizo_RP71648BNX_R2025_Isolated - 3D View - Native Material.png](<../RP71648BNX/evidence/Brizo_RP71648BNX_R2025_Isolated - 3D View - Native Material.png>)
- [Brizo_RP71648BNX_R2025_Isolated - 3D View - Native Oblique.png](<../RP71648BNX/evidence/Brizo_RP71648BNX_R2025_Isolated - 3D View - Native Oblique.png>)
- [Brizo_RP71648BNX_R2025_Isolated - 3D View - Native Side.png](<../RP71648BNX/evidence/Brizo_RP71648BNX_R2025_Isolated - 3D View - Native Side.png>)

## Assumptions and limitations

- Pipe diameter 0.75 in, bend radius 1.375 in and flange thickness 0.20 in are drawing-derived.
- Thread grooves are omitted; open outlet is represented by a recessed dark face.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.

## Blockers and release

No additional identity-specific NEEDS_USER hold is recorded. Inferred geometry/finish fidelity still requires orchestrator review.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
