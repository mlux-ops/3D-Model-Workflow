<!-- worker5 completion -->
# Plumbing fixture row 1518721918631812

**Final status: BUILT_WITH_LIMITATIONS**

## Identity and scope

- Row ID: `1518721918631812`; item key: `R65700__1518721918631812`.
- Scheduled product: Brizo / R65700.
- Scheduled description: Brizo Single-Handle Wall-Mount   Lavatory Faucet Rough-In.
- Scheduled finish: -; unit: Penthouse; room: Powder Room.
- Original agent_ignore: `false`. Coverage does not reinstate an ignored or descoped product.

Original source note: None recorded.

## Source and last verified stage

Shared product group: `R65700`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [R65700/Brizo_R65700_R2025.rfa](<../R65700/Brizo_R65700_R2025.rfa>).
RFA SHA-256: `6320791d2ef7695672c5641218d6d2952703a15c1990a352ceb6079fb86007c9`.
Validation: [validation.json](<../R65700/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T15:55:00.433000Z.
Source RFA input version: Native custom build.
RFA search result: No acceptable no-account RFA recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"result": "No acceptable no-account RFA recovered", "evidence": "_research/R65700/sources.json"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- Brizo BSP-L-R65700 Rev B: https://media.brizo.com/SpecSheet/BSP-L-R65700%20Rev%20B.pdf; page 1.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 90.4875 | 90.4875 | 0 | PASS |
| Y | 50.8 | 50.8 | 0 | PASS |
| Z | 101.6 | 101.6 | 0 | PASS |

All overall dimensions have manufacturer authority: **true**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- Overall mounting plate 3.5625 x 2 in; full rough projection 4 in; fixing centers 3.0625 x 1.5 in.
- Native anchor/path: Mounting plate width, measured 90.4875 mm; nominal 90.4875 mm; PASS.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: R65700 - brass; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3696", "host_kind": "wall", "hostface_present": true, "instance_host_id": "3696", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Brass | True | True |
| Detail | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [R65700/source/build.py](<../R65700/source/build.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [Brizo_R65700_R2025_Isolated - 3D View - Native Front.png](<../R65700/evidence/Brizo_R65700_R2025_Isolated - 3D View - Native Front.png>)
- [Brizo_R65700_R2025_Isolated - 3D View - Native Material.png](<../R65700/evidence/Brizo_R65700_R2025_Isolated - 3D View - Native Material.png>)
- [Brizo_R65700_R2025_Isolated - 3D View - Native Oblique.png](<../R65700/evidence/Brizo_R65700_R2025_Isolated - 3D View - Native Oblique.png>)
- [Brizo_R65700_R2025_Isolated - 3D View - Native Side.png](<../R65700/evidence/Brizo_R65700_R2025_Isolated - 3D View - Native Side.png>)

## Assumptions and limitations

- Hidden valve passages, stop screws and plaster-guard lettering are not modeled.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.

## Blockers and release

No additional identity-specific NEEDS_USER hold is recorded. Inferred geometry/finish fidelity still requires orchestrator review.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
