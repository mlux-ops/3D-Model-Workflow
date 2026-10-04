<!-- worker5 completion -->
# Plumbing fixture row 6153607807827844

**Final status: BUILT_WITH_LIMITATIONS**

## Identity and scope

- Row ID: `6153607807827844`; item key: `873111-BNX-2.5__6153607807827844`.
- Scheduled product: Brizo / 873111-BNX-2.5.
- Scheduled description: Brizo   Roccesco Multi-Function Sconce Wall-Mount Shower Head with Jointed Arm, 2.5   GPM - Brilliance Black Onyx.
- Scheduled finish: Brilliance Black Onyx; Black; unit: Penthouse; room: Primary Bathroom.
- Original agent_ignore: `false`. Coverage does not reinstate an ignored or descoped product.

Original source note: None recorded.

## Source and last verified stage

Shared product group: `873111-BNX-2.5`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [873111-BNX-2.5/Brizo_873111-BNX-2.5_R2025.rfa](<../873111-BNX-2.5/Brizo_873111-BNX-2.5_R2025.rfa>).
RFA SHA-256: `bc1de8b753cda547c51055bac5ec7fc40afa53e70cece5b5e2a6cad78e3513be`.
Validation: [validation.json](<../873111-BNX-2.5/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T16:07:29.641000Z.
Source RFA input version: Native custom build.
RFA search result: No acceptable no-account RFA recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"evidence": "_research/873111-BNX-2.5/sources.json", "result": "No acceptable no-account RFA recovered"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- Brizo Roccesco jointed shower head BSP-B-873111 Rev A: https://media.brizo.com/SpecSheet/BSP-B-873111%20Rev%20A.pdf; page 1.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 120.65 | 120.65 | 0 | PASS |
| Y | 242.6812 | 242.6812 | 0 | PASS |
| Z | 406.4 | 406.4 | 0 | PASS |

All overall dimensions have manufacturer authority: **false**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- Shower cylinder diameter 4.75 in and axial length 7.75 in; wall flange diameter 4.75 in; full shown thread-to-head projection 16 in.
- Native anchor/path: Head diameter, measured 120.65 mm; nominal 120.65 mm; PASS.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: 873111-BNX-2.5 - Brilliance Black Onyx -  Black; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3755", "host_kind": "wall", "hostface_present": true, "instance_host_id": "3755", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Brass | True | True |
| Detail | True | True |
| Finish | True | True |
| Gray | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [873111-BNX-2.5/source/build.py](<../873111-BNX-2.5/source/build.py>).
Visual review: NATIVE_OBLIQUE_AND_SIDE_INSPECTED_WITH_LIMITATIONS. Final release is pending orchestrator review.

- [Brizo_873111-BNX-2_5_R2025_Isolated - 3D View - Native Front.png](<../873111-BNX-2.5/evidence/Brizo_873111-BNX-2_5_R2025_Isolated - 3D View - Native Front.png>)
- [Brizo_873111-BNX-2_5_R2025_Isolated - 3D View - Native Material.png](<../873111-BNX-2.5/evidence/Brizo_873111-BNX-2_5_R2025_Isolated - 3D View - Native Material.png>)
- [Brizo_873111-BNX-2_5_R2025_Isolated - 3D View - Native Oblique.png](<../873111-BNX-2.5/evidence/Brizo_873111-BNX-2_5_R2025_Isolated - 3D View - Native Oblique.png>)
- [Brizo_873111-BNX-2_5_R2025_Isolated - 3D View - Native Side.png](<../873111-BNX-2.5/evidence/Brizo_873111-BNX-2_5_R2025_Isolated - 3D View - Native Side.png>)

Native oblique and side images inspected: round wall flange, asymmetric pivot/arm, inclined cylinder and recessed nozzle disk are present. Fixed 45-degree pose and simplified hardware remain disclosed.

Manufacturer BSP-B-873111 Rev A page 1 screenshot inspected. Cylinder/flange diameter 4.75 inches, cylinder length 7.75 inches and full thread-to-head envelope 16 inches are the selected drawing authority.

## Assumptions and limitations

- ASSUMPTION: neutral 45-degree cylinder angle and 1.5-inch concealed stub; final finished-wall projection therefore depends on mounting depth.
- Jointed arm plate, nozzle distribution and small pivots are drawing-derived.
- Printed standard-specification body text names 873110, while this sheet title and model field explicitly identify 873111; the 873111 drawing is used.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.
- ASSUMPTION: use the explicit 873111 title/model drawing even though standard-specification body text names 873110. The 16-inch total includes the assumed 1.5-inch concealed stub; it is not a finished-wall projection.

## Blockers and release

No additional identity-specific NEEDS_USER hold is recorded. Inferred geometry/finish fidelity still requires orchestrator review.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
