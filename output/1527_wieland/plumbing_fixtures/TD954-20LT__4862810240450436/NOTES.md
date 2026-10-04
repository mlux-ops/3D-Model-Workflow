<!-- worker5 completion -->
# Plumbing fixture row 4862810240450436

**Final status: BUILT_WITH_LIMITATIONS**

## Identity and scope

- Row ID: `4862810240450436`; item key: `TD954-20LT__4862810240450436`.
- Scheduled product: Westbrass / TD954-20LT.
- Scheduled description: Westbrass   PVC Bathtub Waste and Overflow Rough-In, Less Trim.
- Scheduled finish: -; unit: Penthouse; room: Primary Bathroom.
- Original agent_ignore: `false`. Coverage does not reinstate an ignored or descoped product.

Original source note: None recorded.

## Source and last verified stage

Shared product group: `TD954-20LT`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [TD954-20LT/Westbrass_TD954-20LT_R2025.rfa](<../TD954-20LT/Westbrass_TD954-20LT_R2025.rfa>).
RFA SHA-256: `74020f1541e7f2fa6c700ef692ca15331f82534b62975746a3b6a3d813ea7970`.
Validation: [validation.json](<../TD954-20LT/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T15:55:19.374000Z.
Source RFA input version: Native custom build.
RFA search result: No acceptable no-account RFA recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"result": "No acceptable no-account RFA recovered", "evidence": "_research/TD954-20LT/sources.json"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- Westbrass TD954 manufacturer product: https://westbrass.com/product/12-4-bath-waste-overflow-assembly-with-tip-toe-drain-plug-and-illusionary-faceplate-sch-40-pvc-pipe/; page 1.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 60.96 | 60.96 | 0 | PASS |
| Y | 160.02 | 160.02 | 0 | PASS |
| Z | 368.3 | 368.3 | 0 | PASS |

All overall dimensions have manufacturer authority: **false**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- Official TD954 description specifies 12-inch and 4-inch pipe lengths and nominal 1.5-inch Sch.40 PVC.
- Native anchor/path: Overflow pipe length, measured 304.8 mm; nominal 304.8 mm; PASS.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: TD954-20LT - white; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3694", "host_kind": "floor", "hostface_present": true, "instance_host_id": "3694", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Finish | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [TD954-20LT/source/build.py](<../TD954-20LT/source/build.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [Westbrass_TD954-20LT_R2025_Isolated - 3D View - Native Front.png](<../TD954-20LT/evidence/Westbrass_TD954-20LT_R2025_Isolated - 3D View - Native Front.png>)
- [Westbrass_TD954-20LT_R2025_Isolated - 3D View - Native Material.png](<../TD954-20LT/evidence/Westbrass_TD954-20LT_R2025_Isolated - 3D View - Native Material.png>)
- [Westbrass_TD954-20LT_R2025_Isolated - 3D View - Native Oblique.png](<../TD954-20LT/evidence/Westbrass_TD954-20LT_R2025_Isolated - 3D View - Native Oblique.png>)
- [Westbrass_TD954-20LT_R2025_Isolated - 3D View - Native Side.png](<../TD954-20LT/evidence/Westbrass_TD954-20LT_R2025_Isolated - 3D View - Native Side.png>)

## Assumptions and limitations

- IDENTITY HOLD: base TD954 is manufacturer-verified; the -20LT exact suffix was not independently verified.
- ASSUMPTION: less-trim interpretation follows the schedule; visible stopper/overflow cover are omitted.
- Pipe assembled positions, sockets and elbow envelopes are approximate; supplied pipes are field-cut to the selected tub.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.

## Blockers and release

- NEEDS_USER_TD954_20LT_SUFFIX: Base TD954 is verified in the preserved manufacturer evidence; the exact -20LT suffix was not independently established. Confirm the scheduled package identity before release.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
