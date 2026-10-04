<!-- worker5 completion -->
# Plumbing fixture row 5680187871788932

**Final status: BUILT_WITH_LIMITATIONS**

## Identity and scope

- Row ID: `5680187871788932`; item key: `BR73480__5680187871788932`.
- Scheduled product: Brizo / BR73480.
- Scheduled description: Brizo 48" Linear Shower Drain Wall Edge Trim Only.
- Scheduled finish: -; unit: Penthouse; room: Primary Bathroom.
- Original agent_ignore: `false`. Coverage does not reinstate an ignored or descoped product.

Original source note: None recorded.

## Source and last verified stage

Shared product group: `BR73480`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [BR73480/Brizo_BR73480_R2025.rfa](<../BR73480/Brizo_BR73480_R2025.rfa>).
RFA SHA-256: `2f75c41bb72741d614f8afb1b195ba1b214e00c971b76f193c2653fb7b9e9a0f`.
Validation: [validation.json](<../BR73480/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T14:49:43.358000Z.
Source RFA input version: Native custom build.
RFA search result: No acceptable no-account RFA recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"result": "No acceptable no-account RFA recovered", "evidence": "_research/BR73480/sources.json"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- BSP-B-BR73240 Rev B: https://media.brizo.com/SpecSheet/BSP-B-BR73240%20Rev%20B.pdf; page 1.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 1350.9625 | 1350.9625 | 0 | PASS |
| Y | 320.675 | 320.675 | 0 | PASS |
| Z | 138.1125 | 138.1125 | 0 | PASS |

All overall dimensions have manufacturer authority: **true**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- Membrane footprint 53.1875 x 12.625 in; channel length 47.25 in and width 4.4375 in; feet set to published maximum 5.4375 in.
- Native anchor/path: Membrane length, measured 1350.9625 mm; nominal 1350.9625 mm; PASS.
- Native anchor/path: Channel length, measured 1200.15 mm; nominal 1200.15 mm; PASS.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: BR73480 - chrome; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3711", "host_kind": "floor", "hostface_present": true, "instance_host_id": "3711", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Detail | True | True |
| Finish | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [BR73480/source/build.py](<../BR73480/source/build.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [Brizo_BR73480_R2025_Isolated - 3D View - Native Front.png](<../BR73480/evidence/Brizo_BR73480_R2025_Isolated - 3D View - Native Front.png>)
- [Brizo_BR73480_R2025_Isolated - 3D View - Native Material.png](<../BR73480/evidence/Brizo_BR73480_R2025_Isolated - 3D View - Native Material.png>)
- [Brizo_BR73480_R2025_Isolated - 3D View - Native Oblique.png](<../BR73480/evidence/Brizo_BR73480_R2025_Isolated - 3D View - Native Oblique.png>)
- [Brizo_BR73480_R2025_Isolated - 3D View - Native Side.png](<../BR73480/evidence/Brizo_BR73480_R2025_Isolated - 3D View - Native Side.png>)

## Assumptions and limitations

- Channel floor is simplified level geometry; hydraulic slope and hidden membrane seams are not modeled.
- Visible drain trim is a separate inventory item.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.

## Blockers and release

No additional identity-specific NEEDS_USER hold is recorded. Inferred geometry/finish fidelity still requires orchestrator review.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
