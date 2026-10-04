<!-- worker5 completion -->
# Plumbing fixture row 4063171309010820

**Final status: BUILT_WITH_LIMITATIONS**

## Identity and scope

- Row ID: `4063171309010820`; item key: `62820LF-BL__4063171309010820`.
- Scheduled product: Brizo / 62820LF-BL.
- Scheduled description: Brizo   European Wall-Mount Pot Filler Faucet - Matte Black.
- Scheduled finish: Matte Black; Black; unit: Penthouse; room: Kitchen.
- Original agent_ignore: `false`. Coverage does not reinstate an ignored or descoped product.

Original source note: None recorded.

## Source and last verified stage

Shared product group: `62820LF-BL`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [62820LF-BL/Brizo_62820LF-BL_R2025.rfa](<../62820LF-BL/Brizo_62820LF-BL_R2025.rfa>).
RFA SHA-256: `950c2a3a5513e08169bcddb43ad928eed452667ab3625c592f3c678aba947987`.
Validation: [validation.json](<../62820LF-BL/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T16:07:21.046000Z.
Source RFA input version: Native custom build.
RFA search result: No acceptable no-account RFA recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"evidence": "_research/62820LF-BL/sources.json", "result": "No acceptable no-account RFA recovered"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- Brizo shared pot-filler drawing, exact 62820 handle detail, Rev N: https://media.brizo.com/SpecSheet/BSP-K-62810LF%20Rev%20N.pdf; page 1.
- Worker-5 source cross-check: https://www.brizo.com/kitchen/product/62820LF-BL.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 73.025 | 73.025 | 0 | PASS |
| Y | 234.95 | 234.95 | 0 | PASS |
| Z | 517.525 | 517.525 | 0 | PASS |

All overall dimensions have manufacturer authority: **false**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- Wall-to-front 20.375 in; outlet axis 19.25 in from wall; swivel axes at 3.5 and 11.25 in; flange diameter 2.875 in.
- 6.5 in in the source is the top hinge height above the wall inlet axis, not the complete vertical envelope.
- Native anchor/path: Full projection, measured 517.525 mm; nominal 517.525 mm; PASS.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: 62820LF-BL - Matte Black -  Black; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3703", "host_kind": "wall", "hostface_present": true, "instance_host_id": "3703", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Detail | True | True |
| Finish | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [62820LF-BL/source/build.py](<../62820LF-BL/source/build.py>).
Visual review: NATIVE_OBLIQUE_AND_SIDE_INSPECTED_WITH_LIMITATIONS. Final release is pending orchestrator review.

- [Brizo_62820LF-BL_R2025_Isolated - 3D View - Native Front.png](<../62820LF-BL/evidence/Brizo_62820LF-BL_R2025_Isolated - 3D View - Native Front.png>)
- [Brizo_62820LF-BL_R2025_Isolated - 3D View - Native Material.png](<../62820LF-BL/evidence/Brizo_62820LF-BL_R2025_Isolated - 3D View - Native Material.png>)
- [Brizo_62820LF-BL_R2025_Isolated - 3D View - Native Oblique.png](<../62820LF-BL/evidence/Brizo_62820LF-BL_R2025_Isolated - 3D View - Native Oblique.png>)
- [Brizo_62820LF-BL_R2025_Isolated - 3D View - Native Side.png](<../62820LF-BL/evidence/Brizo_62820LF-BL_R2025_Isolated - 3D View - Native Side.png>)

Native oblique and side images inspected: wall flange, two swivel stages, two downward paddles and downward outlet are visible. Simplified collars and paddles remain disclosed.

Manufacturer BSP-K-62810LF Rev N page 1 screenshot inspected, including the 62820 lever detail. The dimensioned drawing is the chosen authority for 20.375-inch full projection and 19.25-inch outlet reach.

## Assumptions and limitations

- ASSUMPTION: lower handle extends 2.75 in below the inlet axis, creating a 9.25 in full posed envelope.
- Arms are fully extended; swivel, paddle rotation and minor collars are fixed and drawing-derived.
- No operational joint flex is claimed; materials are the editable parameters.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.
- ASSUMPTION: use the explicit Rev N drawing rather than the undifferentiated 22-inch reach on the current product page. The 9.25-inch posed height includes a drawing-derived downward handle; it is not the product-page 6.5-inch body-height value.

## Blockers and release

No additional identity-specific NEEDS_USER hold is recorded. Inferred geometry/finish fidelity still requires orchestrator review.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
