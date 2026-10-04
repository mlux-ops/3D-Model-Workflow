<!-- worker5 completion -->
# Plumbing fixture row 387032865636228

**Final status: BUILT_WITH_LIMITATIONS**

## Identity and scope

- Row ID: `387032865636228`; item key: `R75000-WS__387032865636228`.
- Scheduled product: Brizo / R75000-WS.
- Scheduled description: Brizo MultiChoice Universal   Integrated Shower Diverter Rough-In Valve with Stops.
- Scheduled finish: -; unit: Penthouse; room: Bath 4.
- Original agent_ignore: `false`. Coverage does not reinstate an ignored or descoped product.

Original source note: None recorded.

## Source and last verified stage

Shared product group: `R75000-WS`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [R75000-WS/Brizo_R75000-WS_R2025.rfa](<../R75000-WS/Brizo_R75000-WS_R2025.rfa>).
RFA SHA-256: `fc6e3d119f023c573f879bad018081c56b403ce6c9fe428ed5de786fd5bd8153`.
Validation: [validation.json](<../R75000-WS/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T14:49:39.110000Z.
Source RFA input version: Native custom build.
RFA search result: No acceptable no-account RFA recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"result": "No acceptable no-account RFA recovered", "evidence": "_research/R75000-WS/sources.json"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- BSP-B-R75000 Rev F: https://media.brizo.com/SpecSheet/BSP-B-R75000%20Rev%20F.pdf; page 1.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 128.5875 | 128.5875 | 0 | PASS |
| Y | 156.3687 | 156.3687 | 0 | PASS |
| Z | 122.2375 | 122.2375 | 0 | PASS |

All overall dimensions have manufacturer authority: **false**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- With-stops inlet width 5.0625 in; plaster guard 4.0625 x 5.5625 in.
- Overall front-stem projection 4.8125 in equals nominal stringer-to-wall 2.5625 in plus wall-to-stem 2.25 in.
- Native anchor/path: Guard height, measured 141.2875 mm; nominal 141.2875 mm; PASS.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: R75000-WS - brass; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3707", "host_kind": "wall", "hostface_present": true, "instance_host_id": "3707", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Brass | True | True |
| Detail | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [R75000-WS/source/build.py](<../R75000-WS/source/build.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [Brizo_R75000-WS_R2025_Isolated - 3D View - Native Front.png](<../R75000-WS/evidence/Brizo_R75000-WS_R2025_Isolated - 3D View - Native Front.png>)
- [Brizo_R75000-WS_R2025_Isolated - 3D View - Native Material.png](<../R75000-WS/evidence/Brizo_R75000-WS_R2025_Isolated - 3D View - Native Material.png>)
- [Brizo_R75000-WS_R2025_Isolated - 3D View - Native Oblique.png](<../R75000-WS/evidence/Brizo_R75000-WS_R2025_Isolated - 3D View - Native Oblique.png>)
- [Brizo_R75000-WS_R2025_Isolated - 3D View - Native Side.png](<../R75000-WS/evidence/Brizo_R75000-WS_R2025_Isolated - 3D View - Native Side.png>)

## Assumptions and limitations

- ASSUMPTION: upper outlet extension and upper test-stem projection are drawing-derived.
- Test caps, guard and principal ports represented; internal seats and molded details simplified.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.

## Blockers and release

No additional identity-specific NEEDS_USER hold is recorded. Inferred geometry/finish fidelity still requires orchestrator review.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
