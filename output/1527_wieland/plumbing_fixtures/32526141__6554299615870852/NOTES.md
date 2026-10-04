<!-- worker5 completion -->
# Plumbing fixture row 6554299615870852

**Final status: BUILT_WITH_LIMITATIONS**

## Identity and scope

- Row ID: `6554299615870852`; item key: `32526141__6554299615870852`.
- Scheduled product: Hansgrohe / 32526141.
- Scheduled description: Hansgrohe Rough-In Valve for 2 Hole Wall Mounted Faucets - ALREADY PROCURED IN SHOWROOM.
- Scheduled finish: -; unit: Triplex; room: Powder Room.
- Original agent_ignore: `false`. Coverage does not reinstate an ignored or descoped product.

Original source note: None recorded.

## Source and last verified stage

Shared product group: `32526141`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [32526141/Hansgrohe_32526141_R2025.rfa](<../32526141/Hansgrohe_32526141_R2025.rfa>).
RFA SHA-256: `35e325b21148c1e263bf6aa72298bd654ddb7e6aafdf8a6a9a9c0a3dfa41c32f`.
Validation: [validation.json](<../32526141/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T14:48:53.787000Z.
Source RFA input version: Native custom build.
RFA search result: No acceptable no-account RFA recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"result": "No acceptable no-account RFA recovered", "evidence": "_research/32526141/sources.json"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- Hansgrohe 2026 US Price Book: https://assets.hansgrohe.com/celum/emailmarketing/hansgrohe_2026_Price_Book_en_US.pdf; page 128.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 319.0875 | 319.0875 | 0 | PASS |
| Y | 66.675 | 66.675 | 0 | PASS |
| Z | 241.3 | 241.3 | 0 | PASS |

All overall dimensions have manufacturer authority: **false**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- Two square plates 2.625 in; plate thickness .375 in; total projection 9.5 in; nominal reach 8.875 in.
- Native anchor/path: Plate width, measured 66.675 mm; nominal 66.675 mm; PASS.
- Native anchor/path: Projection, measured 241.3 mm; nominal 241.3 mm; PASS.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: 32526141 - bronze; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3697", "host_kind": "wall", "hostface_present": true, "instance_host_id": "3697", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Detail | True | True |
| Finish | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [32526141/source/build.py](<../32526141/source/build.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [Hansgrohe_32526141_R2025_Isolated - 3D View - Native Front.png](<../32526141/evidence/Hansgrohe_32526141_R2025_Isolated - 3D View - Native Front.png>)
- [Hansgrohe_32526141_R2025_Isolated - 3D View - Native Material.png](<../32526141/evidence/Hansgrohe_32526141_R2025_Isolated - 3D View - Native Material.png>)
- [Hansgrohe_32526141_R2025_Isolated - 3D View - Native Oblique.png](<../32526141/evidence/Hansgrohe_32526141_R2025_Isolated - 3D View - Native Oblique.png>)
- [Hansgrohe_32526141_R2025_Isolated - 3D View - Native Side.png](<../32526141/evidence/Hansgrohe_32526141_R2025_Isolated - 3D View - Native Side.png>)

## Assumptions and limitations

- ASSUMPTION: 8 in spout-to-control centers because the catalog does not specify spacing.
- Inventory calls this SKU a rough-in; the exact SKU is faucet trim. Required rough 13622181 is not included.
- Rectangular section thicknesses and control geometry are drawing-derived.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.

## Blockers and release

- NEEDS_USER_32526141_IDENTITY_SCOPE: Exact SKU 32526141 is Metropol wall faucet trim, although the inventory describes a rough-in. The saved family represents trim; required rough 13622181 is not included. Confirm row identity/scope and the inferred 8-inch centers.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
