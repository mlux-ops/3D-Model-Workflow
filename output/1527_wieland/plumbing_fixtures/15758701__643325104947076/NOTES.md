<!-- worker5 completion -->
# Plumbing fixture row 643325104947076

**Final status: BUILT_WITH_LIMITATIONS**

## Identity and scope

- Row ID: `643325104947076`; item key: `15758701__643325104947076`.
- Scheduled product: Hansgrohe / 15758701.
- Scheduled description: Hansgrohe   Ecostat S Thermostatic Trim with Volume Control and Diverter - Matte White.
- Scheduled finish: White; unit: Triplex; room: Bath 4.
- Original agent_ignore: `false`. Coverage does not reinstate an ignored or descoped product.

Original source note: None recorded.

## Source and last verified stage

Shared product group: `15758701`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [15758701/Hansgrohe_15758701_R2025.rfa](<../15758701/Hansgrohe_15758701_R2025.rfa>).
RFA SHA-256: `c06d25df6f23ace9b6e819d0a3eae8367564f861a803620ec20234c2869859ea`.
Validation: [validation.json](<../15758701/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T14:27:07.466000Z.
Source RFA input version: Native custom build.
RFA search result: No acceptable no-account RFA recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"result": "No acceptable no-account RFA recovered", "evidence": "_research/15758701/sources.json"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- Hansgrohe 2026 US Price Book: https://assets.hansgrohe.com/celum/emailmarketing/hansgrohe_2026_Price_Book_en_US.pdf; page 302.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 149.225 | 149.225 | 0 | PASS |
| Y | 174.625 | 174.625 | 0 | PASS |
| Z | 79.375 | 79.375 | 0 | PASS |

All overall dimensions have manufacturer authority: **false**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- Escutcheon diameter 5.875 in; centers 2.875 in; lower control diameter 1.75 in; lower lever reach 2.5 in.
- Projection configured at the published 3.125 in maximum; overall height derives from the down-pointing lower lever and plate.
- Native anchor/path: Escutcheon diameter, measured 149.225 mm; nominal 149.225 mm; PASS.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: 15758701 - White; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3699", "host_kind": "wall", "hostface_present": true, "instance_host_id": "3699", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Finish | True | True |
| Graphite | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [15758701/source/build.py](<../15758701/source/build.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [Hansgrohe_15758701_R2025_Isolated - 3D View - Native Front.png](<../15758701/evidence/Hansgrohe_15758701_R2025_Isolated - 3D View - Native Front.png>)
- [Hansgrohe_15758701_R2025_Isolated - 3D View - Native Material.png](<../15758701/evidence/Hansgrohe_15758701_R2025_Isolated - 3D View - Native Material.png>)
- [Hansgrohe_15758701_R2025_Isolated - 3D View - Native Oblique.png](<../15758701/evidence/Hansgrohe_15758701_R2025_Isolated - 3D View - Native Oblique.png>)
- [Hansgrohe_15758701_R2025_Isolated - 3D View - Native Side.png](<../15758701/evidence/Hansgrohe_15758701_R2025_Isolated - 3D View - Native Side.png>)

## Assumptions and limitations

- Installation-depth range is fixed at its outer limit for this visualization.
- Temperature markings and small internal collars are simplified.
- Matte white identity comes from scheduled 15758701 and its manufacturer instruction listing; current family drawing is the same 15758 body.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.

## Blockers and release

No additional identity-specific NEEDS_USER hold is recorded. Inferred geometry/finish fidelity still requires orchestrator review.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
