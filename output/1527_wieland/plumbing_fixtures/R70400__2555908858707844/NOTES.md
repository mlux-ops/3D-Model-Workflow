<!-- worker5 completion -->
# Plumbing fixture row 2555908858707844

**Final status: BUILT_WITH_LIMITATIONS**

## Identity and scope

- Row ID: `2555908858707844`; item key: `R70400__2555908858707844`.
- Scheduled product: Brizo / R70400.
- Scheduled description: Brizo Two-Handle Wall-Mount Tub Filler Rough-In.
- Scheduled finish: -; unit: Triplex; room: Primary Bathroom.
- Original agent_ignore: `false`. Coverage does not reinstate an ignored or descoped product.

Original source note: None recorded.

## Source and last verified stage

Shared product group: `R70400`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [R70400/Brizo_R70400_R2025.rfa](<../R70400/Brizo_R70400_R2025.rfa>).
RFA SHA-256: `0e55209921d372c66c3678f2c9746dd60b03658af38467f04d9c162b5b06fba1`.
Validation: [validation.json](<../R70400/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T15:43:14.152000Z.
Source RFA input version: Native custom build.
RFA search result: No acceptable no-account RFA recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"result": "No acceptable no-account RFA recovered", "evidence": "_research/R70400/sources.json"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- Brizo BSP-L-R70400 Rev C: https://media.brizo.com/SpecSheet/BSP-L-R70400%20Rev%20C.pdf; page 1.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 273.05 | 273.05 | 0 | PASS |
| Y | 61.9125 | 61.9125 | 0 | PASS |
| Z | 88.9 | 88.9 | 0 | PASS |

All overall dimensions have manufacturer authority: **false**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- Valve axes are 8 in apart; mounting-hole centers are 10.25 in apart; nominal mounting-to-wall distance is 2.75 in.
- Native anchor/path: Mounting strap overall, measured 273.05 mm; nominal 273.05 mm; PASS.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: R70400 - brass; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3707", "host_kind": "wall", "hostface_present": true, "instance_host_id": "3707", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Brass | True | True |
| Detail | True | True |
| Gray | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [R70400/source/build.py](<../R70400/source/build.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [Brizo_R70400_R2025_Isolated - 3D View - Native Front.png](<../R70400/evidence/Brizo_R70400_R2025_Isolated - 3D View - Native Front.png>)
- [Brizo_R70400_R2025_Isolated - 3D View - Native Material.png](<../R70400/evidence/Brizo_R70400_R2025_Isolated - 3D View - Native Material.png>)
- [Brizo_R70400_R2025_Isolated - 3D View - Native Oblique.png](<../R70400/evidence/Brizo_R70400_R2025_Isolated - 3D View - Native Oblique.png>)
- [Brizo_R70400_R2025_Isolated - 3D View - Native Side.png](<../R70400/evidence/Brizo_R70400_R2025_Isolated - 3D View - Native Side.png>)

## Assumptions and limitations

- ASSUMPTION: mounting strap projects 0.25 in beyond each dimensioned fixing center.
- Overall height and test-stem projection are inferred from the drawing. Internal valves and thread details are omitted.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.

## Blockers and release

No additional identity-specific NEEDS_USER hold is recorded. Inferred geometry/finish fidelity still requires orchestrator review.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
