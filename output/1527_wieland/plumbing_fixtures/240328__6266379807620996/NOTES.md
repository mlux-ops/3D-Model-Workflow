<!-- worker5 completion -->
# Plumbing fixture row 6266379807620996

**Final status: BUILT_WITH_LIMITATIONS**

## Identity and scope

- Row ID: `6266379807620996`; item key: `240328__6266379807620996`.
- Scheduled product: Blanco / 240328.
- Scheduled description: BLANCO   Decorative Metal Garbage Disposal Flange - Black.
- Scheduled finish: Black; unit: Penthouse; room: Kitchen.
- Original agent_ignore: `false`. Coverage does not reinstate an ignored or descoped product.

Original source note: None recorded.

## Source and last verified stage

Shared product group: `240328`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [240328/Blanco_240328_R2025.rfa](<../240328/Blanco_240328_R2025.rfa>).
RFA SHA-256: `322921047f6bc77f25bb76ee4675671785a3dfcc2c8164d58e6cf4d132f91ee4`.
Validation: [validation.json](<../240328/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T15:55:06.198000Z.
Source RFA input version: Native custom build.
RFA search result: No acceptable no-account RFA recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"result": "No acceptable no-account RFA recovered", "evidence": "_research/240328/sources.json"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- BLANCO strainer and flange identities: https://www.blanco.com/us/sinks/sink-accessories/strainers-and-drain-covers/; page 1.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 109.22 | 109.22 | 0 | PASS |
| Y | 109.22 | 109.22 | 0 | PASS |
| Z | 25.4 | 25.4 | 0 | PASS |

All overall dimensions have manufacturer authority: **false**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- Manufacturer identifies compatibility with nominal 3.5-inch disposal openings.
- Native anchor/path: Opening collar nominal OD, measured 88.9 mm; nominal 88.9 mm; PASS.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: 240328 - Black; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3696", "host_kind": "floor", "hostface_present": true, "instance_host_id": "3696", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Detail | True | True |
| Finish | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [240328/source/build.py](<../240328/source/build.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [Blanco_240328_R2025_Isolated - 3D View - Native Front.png](<../240328/evidence/Blanco_240328_R2025_Isolated - 3D View - Native Front.png>)
- [Blanco_240328_R2025_Isolated - 3D View - Native Material.png](<../240328/evidence/Blanco_240328_R2025_Isolated - 3D View - Native Material.png>)
- [Blanco_240328_R2025_Isolated - 3D View - Native Oblique.png](<../240328/evidence/Blanco_240328_R2025_Isolated - 3D View - Native Oblique.png>)
- [Blanco_240328_R2025_Isolated - 3D View - Native Side.png](<../240328/evidence/Blanco_240328_R2025_Isolated - 3D View - Native Side.png>)

## Assumptions and limitations

- IDENTITY HOLD: 240328 is a White SKU, while the schedule requests Black. Black geometry is a visual variant only.
- ASSUMPTION: outer rim 4.3 in, collar length 0.9 in and rim thickness 0.18 in are photo-derived; no exact dimensional cut sheet was recovered.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.

## Blockers and release

- NEEDS_USER_BLANCO_240328_FINISH: Exact manufacturer SKU 240328 is White; the inventory requests Black. The saved Black flange is an explicitly unresolved visual variant with inferred secondary dimensions. Confirm finish/SKU before release.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
