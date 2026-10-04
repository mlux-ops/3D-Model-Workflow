<!-- worker5 completion -->
# Plumbing fixture row 4935818499784580

**Final status: BUILT_WITH_LIMITATIONS**

## Identity and scope

- Row ID: `4935818499784580`; item key: `K-70-PVC__4935818499784580`.
- Scheduled product: - / K-70-PVC.
- Scheduled description: Victoria + Albert K-70 Freestanding Bathtub Island Drain for Sub-Floor Installation Box - PVC.
- Scheduled finish: -; unit: Triplex; room: Primary Bathroom.
- Original agent_ignore: `false`. Coverage does not reinstate an ignored or descoped product.

Original source note: REPLACED 2026-08-04. Was Westbrass ITD910P PVC island tub drain rough-in. Victoria + Albert specifies its own K-51 waste/overflow plus K-70 island drain box for the Terrassa; the Westbrass body is not the manufacturer-specified rough-in and its use put the tub warranty at risk. K-70 is also offered as K-70-ABS - switch if the building DWV is ABS rather than PVC.

## Source and last verified stage

Shared product group: `K-70-PVC`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [K-70-PVC/Fixture_K-70-PVC_R2025.rfa](<../K-70-PVC/Fixture_K-70-PVC_R2025.rfa>).
RFA SHA-256: `11d0e799a972139f173400b42931af4e4b9ab35308a22880c296a1147b7f2e55`.
Validation: [validation.json](<../K-70-PVC/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T15:27:51.925000Z.
Source RFA input version: Native custom build.
RFA search result: No acceptable no-account RFA recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"result": "No acceptable no-account RFA recovered", "evidence": "_research/K-70-PVC/sources.json"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- Victoria + Albert K-70 Rev 05/24: https://assets.fbgpg.com/shared/docs/product-specifications/spc-k-70sp.pdf; page 1.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 177.8 | 177.8 | 0 | PASS |
| Y | 158.75 | 158.75 | 0 | PASS |
| Z | 85.725 | 85.725 | 0 | PASS |

All overall dimensions have manufacturer authority: **true**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- Elliptical flange 7 x 6.25 in; total body height 3.375 in; outlet OD 2.375 in.
- Native anchor/path: Flange width, measured 177.8 mm; nominal 177.8 mm; PASS.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: K-70-PVC - white; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3702", "host_kind": "floor", "hostface_present": true, "instance_host_id": "3702", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Brass | True | True |
| Detail | True | True |
| Finish | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [K-70-PVC/source/build.py](<../K-70-PVC/source/build.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [Fixture_K-70-PVC_R2025_Isolated - 3D View - Native Front.png](<../K-70-PVC/evidence/Fixture_K-70-PVC_R2025_Isolated - 3D View - Native Front.png>)
- [Fixture_K-70-PVC_R2025_Isolated - 3D View - Native Material.png](<../K-70-PVC/evidence/Fixture_K-70-PVC_R2025_Isolated - 3D View - Native Material.png>)
- [Fixture_K-70-PVC_R2025_Isolated - 3D View - Native Oblique.png](<../K-70-PVC/evidence/Fixture_K-70-PVC_R2025_Isolated - 3D View - Native Oblique.png>)
- [Fixture_K-70-PVC_R2025_Isolated - 3D View - Native Side.png](<../K-70-PVC/evidence/Fixture_K-70-PVC_R2025_Isolated - 3D View - Native Side.png>)

## Assumptions and limitations

- Thread ribs, locking tabs and red shipping insert omitted. Perforation distribution is drawing-derived.
- The sub-floor drain is modeled below the face placement plane; no extension pipe is assumed.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.

## Blockers and release

No additional identity-specific NEEDS_USER hold is recorded. Inferred geometry/finish fidelity still requires orchestrator review.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
