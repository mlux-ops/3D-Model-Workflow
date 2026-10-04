<!-- worker5 completion -->
# Plumbing fixture row 4021024825474948

**Final status: BUILT_WITH_LIMITATIONS**

## Identity and scope

- Row ID: `4021024825474948`; item key: `75033701__4021024825474948`.
- Scheduled product: Hansgrohe / 75033701.
- Scheduled description: Hansgrohe Vivenis Widespread Bathroom Faucet 90 with Pop-Up Drain, 1.2 GPM - Matte White.
- Scheduled finish: White; unit: Triplex; room: Bath 4.
- Original agent_ignore: `false`. Coverage does not reinstate an ignored or descoped product.

Original source note: None recorded.

## Source and last verified stage

Shared product group: `75033701`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [75033701/Hansgrohe_75033701_R2025.rfa](<../75033701/Hansgrohe_75033701_R2025.rfa>).
RFA SHA-256: `aad6f9b54f273d7dfa283c1a7f189130aaaa258a60a39db3205ca189e59fe5ff`.
Validation: [validation.json](<../75033701/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T14:48:50.750000Z.
Source RFA input version: Native custom build.
RFA search result: No acceptable no-account RFA recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"result": "No acceptable no-account RFA recovered", "evidence": "_research/75033701/sources.json"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- Hansgrohe 2026 US Price Book: https://assets.hansgrohe.com/celum/emailmarketing/hansgrohe_2026_Price_Book_en_US.pdf; page 86.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 361.95 | 361.95 | 0 | PASS |
| Y | 184.15 | 184.15 | 0 | PASS |
| Z | 117.475 | 117.475 | 0 | PASS |

All overall dimensions have manufacturer authority: **false**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- 8 in valve centers; height 4.625 in; reach 5.875 in; spout base diameter 2 in.
- Handle length 3.125 in and height 2.500 in from the manufacturer diagram.
- Native anchor/path: Height, measured 117.475 mm; nominal 117.475 mm; PASS.
- Native anchor/path: Base diameter, measured 50.8 mm; nominal 50.8 mm; PASS.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: 75033701 - White; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3697", "host_kind": "floor", "hostface_present": true, "instance_host_id": "3697", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Finish | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [75033701/source/build.py](<../75033701/source/build.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [Hansgrohe_75033701_R2025_Isolated - 3D View - Native Front.png](<../75033701/evidence/Hansgrohe_75033701_R2025_Isolated - 3D View - Native Front.png>)
- [Hansgrohe_75033701_R2025_Isolated - 3D View - Native Material.png](<../75033701/evidence/Hansgrohe_75033701_R2025_Isolated - 3D View - Native Material.png>)
- [Hansgrohe_75033701_R2025_Isolated - 3D View - Native Oblique.png](<../75033701/evidence/Hansgrohe_75033701_R2025_Isolated - 3D View - Native Oblique.png>)
- [Hansgrohe_75033701_R2025_Isolated - 3D View - Native Side.png](<../75033701/evidence/Hansgrohe_75033701_R2025_Isolated - 3D View - Native Side.png>)

## Assumptions and limitations

- Fixed 8 in installation spacing; levers shown pointing outwards.
- Above-counter set only; drain, supply hoses, cast underside and detailed aerator are omitted.
- Waterfall/spout shoulders are traced approximately from the catalog side drawing.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.

## Blockers and release

No additional identity-specific NEEDS_USER hold is recorded. Inferred geometry/finish fidelity still requires orchestrator review.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
