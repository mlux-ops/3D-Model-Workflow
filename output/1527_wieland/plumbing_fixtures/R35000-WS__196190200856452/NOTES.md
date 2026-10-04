<!-- worker5 completion -->
# Plumbing fixture row 196190200856452

**Final status: BUILT_WITH_LIMITATIONS**

## Identity and scope

- Row ID: `196190200856452`; item key: `R35000-WS__196190200856452`.
- Scheduled product: Brizo / R35000-WS.
- Scheduled description: Brizo Thermostatic Rough In Valve Body with Stops from the Sensori Collection.
- Scheduled finish: -; unit: Triplex; room: Primary Bathroom.
- Original agent_ignore: `true`. Coverage does not reinstate an ignored or descoped product.

Original source note: None recorded.

## Source and last verified stage

Shared product group: `R35000-WS`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [R35000-WS/Brizo_R35000-WS_R2025.rfa](<../R35000-WS/Brizo_R35000-WS_R2025.rfa>).
RFA SHA-256: `1b45728c7384871318f713081031b027ca6a15092c154a69116e2e3b21f3f86c`.
Validation: [validation.json](<../R35000-WS/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T14:49:35.175000Z.
Source RFA input version: Native custom build.
RFA search result: No acceptable no-account RFA recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"result": "No acceptable no-account RFA recovered", "evidence": "_research/R35000-WS/sources.json"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- BSP-B-R35000-WS Rev C: https://media.brizo.com/SpecSheet/BSP-B-R35000-WS%20Rev%20C.pdf; page 1.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 177.8 | 177.8 | 0 | PASS |
| Y | 125.4125 | 125.4125 | 0 | PASS |
| Z | 89.408 | 88.9 | 0.508 | PASS |

All overall dimensions have manufacturer authority: **false**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- Inlet-to-inlet width 7 in; plaster guard height 4.9375 in and width 5.625 in.
- Native anchor/path: Plaster guard width, measured 142.875 mm; nominal 142.875 mm; PASS.
- Native anchor/path: Plaster guard height, measured 125.4125 mm; nominal 125.4125 mm; PASS.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: R35000-WS - brass; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3698", "host_kind": "wall", "hostface_present": true, "instance_host_id": "3698", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Brass | True | True |
| Detail | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [R35000-WS/source/build.py](<../R35000-WS/source/build.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [Brizo_R35000-WS_R2025_Isolated - 3D View - Native Front.png](<../R35000-WS/evidence/Brizo_R35000-WS_R2025_Isolated - 3D View - Native Front.png>)
- [Brizo_R35000-WS_R2025_Isolated - 3D View - Native Material.png](<../R35000-WS/evidence/Brizo_R35000-WS_R2025_Isolated - 3D View - Native Material.png>)
- [Brizo_R35000-WS_R2025_Isolated - 3D View - Native Oblique.png](<../R35000-WS/evidence/Brizo_R35000-WS_R2025_Isolated - 3D View - Native Oblique.png>)
- [Brizo_R35000-WS_R2025_Isolated - 3D View - Native Side.png](<../R35000-WS/evidence/Brizo_R35000-WS_R2025_Isolated - 3D View - Native Side.png>)

## Assumptions and limitations

- ASSUMPTION: overall body depth 3.5 in includes the protruding test stem; source gives only stringer-to-finish-wall 3.25 in.
- Internal flow paths, service stops and guard lettering are simplified.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.

## Blockers and release

No additional identity-specific NEEDS_USER hold is recorded. Inferred geometry/finish fidelity still requires orchestrator review.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
