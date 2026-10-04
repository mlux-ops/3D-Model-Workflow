<!-- worker5 completion -->
# Plumbing fixture row 2316077269450628

**Final status: BUILT_WITH_LIMITATIONS**

## Identity and scope

- Row ID: `2316077269450628`; item key: `27458003__2316077269450628`.
- Scheduled product: Hansgrohe / 27458003.
- Scheduled description: Hansgrohe FixFit Wall Supply Elbow with Check Valve.
- Scheduled finish: -; unit: Penthouse; room: Bath 3.
- Original agent_ignore: `false`. Coverage does not reinstate an ignored or descoped product.

Original source note: None recorded.

## Source and last verified stage

Shared product group: `27458003`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [27458003/Hansgrohe_27458003_R2025.rfa](<../27458003/Hansgrohe_27458003_R2025.rfa>).
RFA SHA-256: `da71053abd4e47b4c8a306a2bdd25fe26dedb50bc040606ffc961e0bd68d1ea4`.
Validation: [validation.json](<../27458003/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T14:48:44.207000Z.
Source RFA input version: Native custom build.
RFA search result: No acceptable no-account RFA recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"result": "No acceptable no-account RFA recovered", "evidence": "_research/27458003/sources.json"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- Hansgrohe 2026 US Price Book: https://assets.hansgrohe.com/celum/emailmarketing/hansgrohe_2026_Price_Book_en_US.pdf; page 272.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 63.5 | 63.5 | 0 | PASS |
| Y | 72.898 | 72.898 | 0 | PASS |
| Z | 47.625 | 47.625 | 0 | PASS |

All overall dimensions have manufacturer authority: **false**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- Body diameter 2.5 in; projection 1.875 in.
- Native anchor/path: Flange diameter, measured 63.5 mm; nominal 63.5 mm; PASS.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: 27458003 - chrome; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3690", "host_kind": "wall", "hostface_present": true, "instance_host_id": "3690", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Finish | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [27458003/source/build.py](<../27458003/source/build.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [Hansgrohe_27458003_R2025_Isolated - 3D View - Native Front.png](<../27458003/evidence/Hansgrohe_27458003_R2025_Isolated - 3D View - Native Front.png>)
- [Hansgrohe_27458003_R2025_Isolated - 3D View - Native Material.png](<../27458003/evidence/Hansgrohe_27458003_R2025_Isolated - 3D View - Native Material.png>)
- [Hansgrohe_27458003_R2025_Isolated - 3D View - Native Oblique.png](<../27458003/evidence/Hansgrohe_27458003_R2025_Isolated - 3D View - Native Oblique.png>)
- [Hansgrohe_27458003_R2025_Isolated - 3D View - Native Side.png](<../27458003/evidence/Hansgrohe_27458003_R2025_Isolated - 3D View - Native Side.png>)

## Assumptions and limitations

- Underside threaded connection extends below the dimensioned body; its 0.37 in exposed extension is drawing-derived.
- Rounded shell and concealed check valve are simplified.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.

## Blockers and release

No additional identity-specific NEEDS_USER hold is recorded. Inferred geometry/finish fidelity still requires orchestrator review.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
