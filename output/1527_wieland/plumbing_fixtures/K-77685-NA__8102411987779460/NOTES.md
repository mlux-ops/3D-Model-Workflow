<!-- worker5 completion -->
# Plumbing fixture row 8102411987779460

**Final status: BUILT_WITH_LIMITATIONS**

## Identity and scope

- Row ID: `8102411987779460`; item key: `K-77685-NA__8102411987779460`.
- Scheduled product: Kohler / K-77685-NA.
- Scheduled description: Kohler Aquifer Single-Manifold   Water Filtration System.
- Scheduled finish: -; unit: Triplex; room: Kitchen.
- Original agent_ignore: `false`. Coverage does not reinstate an ignored or descoped product.

Original source note: None recorded.

## Source and last verified stage

Shared product group: `K-77685-NA`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [K-77685-NA/Kohler_K-77685-NA_R2025.rfa](<../K-77685-NA/Kohler_K-77685-NA_R2025.rfa>).
RFA SHA-256: `57f09944faeb97de71af51b7e1de3d7f16ed50ba7c2949d27e446cafd764ef69`.
Validation: [validation.json](<../K-77685-NA/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T15:54:54.421000Z.
Source RFA input version: Native custom build.
RFA search result: No acceptable no-account RFA recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"result": "No acceptable no-account RFA recovered", "evidence": "_research/K-77685-NA/sources.json"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- Kohler K-77685 specification, 2026-10-01: https://techcomm.kohler.com/techcomm/pdf/K-77685_spec_US-CA_Kohler_en.pdf; page 3.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 77.7875 | 77.7875 | 0 | PASS |
| Y | 85.725 | 85.725 | 0 | PASS |
| Z | 307.975 | 307.975 | 0 | PASS |

All overall dimensions have manufacturer authority: **true**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- Body height 12.125 in, front width 3.0625 in, and total bracket depth 3.375 in.
- Native anchor/path: Body height, measured 307.975 mm; nominal 307.975 mm; PASS.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: K-77685-NA - white; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3697", "host_kind": "floor", "hostface_present": true, "instance_host_id": "3697", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Finish | True | True |
| Gray | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [K-77685-NA/source/build.py](<../K-77685-NA/source/build.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [Kohler_K-77685-NA_R2025_Isolated - 3D View - Native Front.png](<../K-77685-NA/evidence/Kohler_K-77685-NA_R2025_Isolated - 3D View - Native Front.png>)
- [Kohler_K-77685-NA_R2025_Isolated - 3D View - Native Material.png](<../K-77685-NA/evidence/Kohler_K-77685-NA_R2025_Isolated - 3D View - Native Material.png>)
- [Kohler_K-77685-NA_R2025_Isolated - 3D View - Native Oblique.png](<../K-77685-NA/evidence/Kohler_K-77685-NA_R2025_Isolated - 3D View - Native Oblique.png>)
- [Kohler_K-77685-NA_R2025_Isolated - 3D View - Native Side.png](<../K-77685-NA/evidence/Kohler_K-77685-NA_R2025_Isolated - 3D View - Native Side.png>)

## Assumptions and limitations

- The two 24-inch connection tubes are installation-dependent and omitted from this rigid-body family.
- Cartridge/manifold split and small corner radii are drawing-derived.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.

## Blockers and release

No additional identity-specific NEEDS_USER hold is recorded. Inferred geometry/finish fidelity still requires orchestrator review.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
