<!-- worker5 completion -->
# Plumbing fixture row 2994239780028292

**Final status: BUILT_WITH_LIMITATIONS**

## Identity and scope

- Row ID: `2994239780028292`; item key: `72411701__2994239780028292`.
- Scheduled product: Hansgrohe / 72411701.
- Scheduled description: Hansgrohe Talis S Tub Spout with   Diverter - Matte White.
- Scheduled finish: White; unit: Penthouse; room: Bath 2.
- Original agent_ignore: `false`. Coverage does not reinstate an ignored or descoped product.

Original source note: None recorded.

## Source and last verified stage

Shared product group: `72411701`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [72411701/Hansgrohe_72411701_R2025.rfa](<../72411701/Hansgrohe_72411701_R2025.rfa>).
RFA SHA-256: `24ce688b623bd85d6309be0c97f6a24cca8a4eb146faeecd3f39fbbe8c822c41`.
Validation: [validation.json](<../72411701/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T14:37:52.325000Z.
Source RFA input version: Native custom build.
RFA search result: No acceptable no-account RFA recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"evidence": "_research/72411701/sources.json", "result": "No acceptable no-account RFA recovered"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- Hansgrohe 2026 US Price Book: https://assets.hansgrohe.com/celum/emailmarketing/hansgrohe_2026_Price_Book_en_US.pdf; page 282.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 69.85 | 69.85 | 0 | PASS |
| Y | 73.025 | 73.025 | 0 | PASS |
| Z | 165.1 | 165.1 | 0 | PASS |

All overall dimensions have manufacturer authority: **false**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- Overall spout projection 6.5 in; flange diameter 2.75 in; front diverter diameter 1.625 in.
- Native anchor/path: Flange diameter, measured 69.85 mm; nominal 69.85 mm; PASS.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: 72411701 - White; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3696", "host_kind": "wall", "hostface_present": true, "instance_host_id": "3696", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Detail | True | True |
| Finish | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [72411701/source/build.py](<../72411701/source/build.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [Hansgrohe_72411701_R2025_Isolated - 3D View - Native Front.png](<../72411701/evidence/Hansgrohe_72411701_R2025_Isolated - 3D View - Native Front.png>)
- [Hansgrohe_72411701_R2025_Isolated - 3D View - Native Material.png](<../72411701/evidence/Hansgrohe_72411701_R2025_Isolated - 3D View - Native Material.png>)
- [Hansgrohe_72411701_R2025_Isolated - 3D View - Native Oblique.png](<../72411701/evidence/Hansgrohe_72411701_R2025_Isolated - 3D View - Native Oblique.png>)
- [Hansgrohe_72411701_R2025_Isolated - 3D View - Native Side.png](<../72411701/evidence/Hansgrohe_72411701_R2025_Isolated - 3D View - Native Side.png>)

## Assumptions and limitations

- Tip reach is nominally 5.625 in; the terminal cylinder is placed at 5.6875 in to match the separately printed projection.
- Top lift height is inferred from the drawing; markings and hidden fittings omitted.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.

## Blockers and release

No additional identity-specific NEEDS_USER hold is recorded. Inferred geometry/finish fidelity still requires orchestrator review.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
