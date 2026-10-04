<!-- worker5 completion -->
# Plumbing fixture row 2050699988500356

**Final status: BUILT_WITH_LIMITATIONS**

## Identity and scope

- Row ID: `2050699988500356`; item key: `48140991__2050699988500356`.
- Scheduled product: AXOR / 48140991.
- Scheduled description: Wall-Mounted Widespread Faucet 220-Cross Handles, 1.2 GPM.
- Scheduled finish: -; unit: Triplex; room: Powder Room.
- Original agent_ignore: `false`. Coverage does not reinstate an ignored or descoped product.

Original source note: None recorded.

## Source and last verified stage

Shared product group: `48140991`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [48140991/AXOR_48140991_R2025.rfa](<../48140991/AXOR_48140991_R2025.rfa>).
RFA SHA-256: `4a42bea9cdadbda24e6adcd17dbe19337137518f27e66d430d82ca094de77664`.
Validation: [validation.json](<../48140991/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T15:47:28.261000Z.
Source RFA input version: Native custom build.
RFA search result: No acceptable no-account RFA recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"evidence": "_research/48140991/sources.json", "result": "No acceptable no-account RFA recovered"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- AXOR ONE 48140991 dimension drawing: https://assets.hansgrohe.com/mam/celum/celum_assets/153__amu01065_eps.jpg?format=HBW7; page 1.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 273.05 | 273.05 | 0 | PASS |
| Y | 76.8257 | 76.8257 | 0 | PASS |
| Z | 229.5173 | 229.5173 | 0 | PASS |

All overall dimensions have manufacturer authority: **false**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- 8 in centers; escutcheons diameter 2.375 in; cross handle axis-to-tip 1.375 in; tube diameter 0.875 in; outlet center reach 8.625 in; nominal projection 9 in.
- Native anchor/path: Escutcheon diameter, measured 60.325 mm; nominal 60.325 mm; PASS.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: 48140991 - gold; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3702", "host_kind": "wall", "hostface_present": true, "instance_host_id": "3702", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Detail | True | True |
| Finish | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [48140991/source/build.py](<../48140991/source/build.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [AXOR_48140991_R2025_Isolated - 3D View - Native Front.png](<../48140991/evidence/AXOR_48140991_R2025_Isolated - 3D View - Native Front.png>)
- [AXOR_48140991_R2025_Isolated - 3D View - Native Material.png](<../48140991/evidence/AXOR_48140991_R2025_Isolated - 3D View - Native Material.png>)
- [AXOR_48140991_R2025_Isolated - 3D View - Native Oblique.png](<../48140991/evidence/AXOR_48140991_R2025_Isolated - 3D View - Native Oblique.png>)
- [AXOR_48140991_R2025_Isolated - 3D View - Native Side.png](<../48140991/evidence/AXOR_48140991_R2025_Isolated - 3D View - Native Side.png>)

## Assumptions and limitations

- Finish 991 verified as Polished Gold Optic on the exact manufacturer product page.
- Cross junction fillets, handle neck and coating response are inferred.
- Outlet bend is a circular reconstruction from the 1.5 in drop and 20 degree outlet axis; its calculated outer projection is 9.036 in, within 1 mm of nominal 9 in.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.

## Blockers and release

No additional identity-specific NEEDS_USER hold is recorded. Inferred geometry/finish fidelity still requires orchestrator review.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
