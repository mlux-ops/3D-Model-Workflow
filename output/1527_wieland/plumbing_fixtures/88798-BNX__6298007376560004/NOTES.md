<!-- worker5 completion -->
# Plumbing fixture row 6298007376560004

**Final status: BUILT_WITH_LIMITATIONS**

## Identity and scope

- Row ID: `6298007376560004`; item key: `88798-BNX__6298007376560004`.
- Scheduled product: Brizo / 88798-BNX.
- Scheduled description: Brizo   Levoir H2Okinetic Multi-Function Slide Bar Hand Shower - Brilliance Black   Onyx.
- Scheduled finish: Black; unit: Penthouse; room: Bath 4.
- Original agent_ignore: `false`. Coverage does not reinstate an ignored or descoped product.

Original source note: None recorded.

## Source and last verified stage

Shared product group: `88798-BNX`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [88798-BNX/Brizo_88798-BNX_R2025.rfa](<../88798-BNX/Brizo_88798-BNX_R2025.rfa>).
RFA SHA-256: `4b376456e11a15214c7cc1681b0f78aa3717706c34a249dab4d541e505df7432`.
Validation: [validation.json](<../88798-BNX/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T15:27:44.652000Z.
Source RFA input version: Native custom build.
RFA search result: No acceptable no-account RFA recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"result": "No acceptable no-account RFA recovered", "evidence": "_research/88798-BNX/sources.json"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- Brizo BSP-B-88798 Rev D: https://media.brizo.com/SpecSheet/BSP-B-88798%20Rev%20D.pdf; page 1.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 180.1812 | 180.1812 | 0 | PASS |
| Y | 1281.7489 | 1281.7489 | 0 | PASS |
| Z | 116.078 | 116.078 | 0 | PASS |

All overall dimensions have manufacturer authority: **false**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- Bar height 26.6875 in; bar width 1.75 in; projection 3.75 in; head diameter 3.9375 in; handshower length 11.375 in.
- Native anchor/path: Bar height, measured 677.8625 mm; nominal 677.8625 mm; PASS.
- Native anchor/path: Head diameter, measured 100.0125 mm; nominal 100.0125 mm; PASS.
- Native anchor/path: 60 inch hose, measured 1524 mm; nominal 1524 mm; PASS.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: 88798-BNX - Black; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3726", "host_kind": "wall", "hostface_present": true, "instance_host_id": "3726", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Detail | True | True |
| Finish | True | True |
| Gray | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [88798-BNX/source/build.py](<../88798-BNX/source/build.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [Brizo_88798-BNX_R2025_Isolated - 3D View - Native Front.png](<../88798-BNX/evidence/Brizo_88798-BNX_R2025_Isolated - 3D View - Native Front.png>)
- [Brizo_88798-BNX_R2025_Isolated - 3D View - Native Material.png](<../88798-BNX/evidence/Brizo_88798-BNX_R2025_Isolated - 3D View - Native Material.png>)
- [Brizo_88798-BNX_R2025_Isolated - 3D View - Native Oblique.png](<../88798-BNX/evidence/Brizo_88798-BNX_R2025_Isolated - 3D View - Native Oblique.png>)
- [Brizo_88798-BNX_R2025_Isolated - 3D View - Native Side.png](<../88798-BNX/evidence/Brizo_88798-BNX_R2025_Isolated - 3D View - Native Side.png>)

## Assumptions and limitations

- ASSUMPTION: handshower upright pose and 60 in hanging hose shape are fixed. The complete posed envelope is not a factory rigid-body dimension.
- Bar end bends, slider fittings and nozzle layout are simplified; hose is smooth rather than corrugated.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.

## Blockers and release

No additional identity-specific NEEDS_USER hold is recorded. Inferred geometry/finish fidelity still requires orchestrator review.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
