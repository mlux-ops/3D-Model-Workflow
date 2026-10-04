<!-- worker5 completion -->
# Plumbing fixture row 3338858040721284

**Final status: BUILT_WITH_LIMITATIONS**

## Identity and scope

- Row ID: `3338858040721284`; item key: `BT0734816-BNX__3338858040721284`.
- Scheduled product: Brizo / BT0734816-BNX.
- Scheduled description: Brizo 48" Reversible Linear   Shower Drain - Brilliance Black Onyx.
- Scheduled finish: Brilliance Black Onyx; Black; unit: Penthouse; room: Primary Bathroom.
- Original agent_ignore: `false`. Coverage does not reinstate an ignored or descoped product.

Original source note: None recorded.

## Source and last verified stage

Shared product group: `BT0734816-BNX`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [BT0734816-BNX/Brizo_BT0734816-BNX_R2025.rfa](<../BT0734816-BNX/Brizo_BT0734816-BNX_R2025.rfa>).
RFA SHA-256: `4a07e6c8b2a384b67c41917039f7c3297aa75aadb440a3fe5eec57d5c0a31029`.
Validation: [validation.json](<../BT0734816-BNX/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T15:55:15.303000Z.
Source RFA input version: Native custom build.
RFA search result: No acceptable no-account RFA recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"result": "No acceptable no-account RFA recovered", "evidence": "_research/BT0734816-BNX/sources.json"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- Brizo reversible linear drain dimensions, BSP-B-BT0732416 Rev B: https://media.brizo.com/SpecSheet/BSP-B-BT0732416%20Rev%20B.pdf; page 1.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 1158.875 | 1158.875 | 0 | PASS |
| Y | 68.2625 | 68.2625 | 0 | PASS |
| Z | 26.9875 | 26.9875 | 0 | PASS |

All overall dimensions have manufacturer authority: **true**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- Actual trim 45.625 x 2.6875 in; minimum height 1.0625 in; maximum adjustable height 1.375 in.
- Native anchor/path: Trim length, measured 1158.875 mm; nominal 1158.875 mm; PASS.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: BT0734816-BNX - Brilliance Black Onyx -  Black; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3697", "host_kind": "floor", "hostface_present": true, "instance_host_id": "3697", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Finish | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [BT0734816-BNX/source/build.py](<../BT0734816-BNX/source/build.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [Brizo_BT0734816-BNX_R2025_Isolated - 3D View - Native Front.png](<../BT0734816-BNX/evidence/Brizo_BT0734816-BNX_R2025_Isolated - 3D View - Native Front.png>)
- [Brizo_BT0734816-BNX_R2025_Isolated - 3D View - Native Material.png](<../BT0734816-BNX/evidence/Brizo_BT0734816-BNX_R2025_Isolated - 3D View - Native Material.png>)
- [Brizo_BT0734816-BNX_R2025_Isolated - 3D View - Native Oblique.png](<../BT0734816-BNX/evidence/Brizo_BT0734816-BNX_R2025_Isolated - 3D View - Native Oblique.png>)
- [Brizo_BT0734816-BNX_R2025_Isolated - 3D View - Native Side.png](<../BT0734816-BNX/evidence/Brizo_BT0734816-BNX_R2025_Isolated - 3D View - Native Side.png>)

## Assumptions and limitations

- Solid metal side is shown; the reversible tile insert option is not populated with a tile.
- Minimum-height fixed pose; frame spacers and small drain removal tool omitted.
- The separate rough BR73480 and optional wall edge are not part of this trim family.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.

## Blockers and release

No additional identity-specific NEEDS_USER hold is recorded. Inferred geometry/finish fidelity still requires orchestrator review.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
