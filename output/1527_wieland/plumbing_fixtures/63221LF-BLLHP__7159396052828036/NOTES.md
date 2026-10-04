<!-- worker5 completion -->
# Plumbing fixture row 7159396052828036

**Final status: BUILT_WITH_LIMITATIONS**

## Identity and scope

- Row ID: `7159396052828036`; item key: `63221LF-BLLHP__7159396052828036`.
- Scheduled product: Brizo / 63221LF-BLLHP.
- Scheduled description: Brizo Odin Articulating Kitchen   Faucet, Less Handle - Matte Black.
- Scheduled finish: Matte Black; Black; unit: Penthouse; room: Kitchen.
- Original agent_ignore: `false`. Coverage does not reinstate an ignored or descoped product.

Original source note: None recorded.

## Source and last verified stage

Shared product group: `63221LF-BLLHP`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [63221LF-BLLHP/Brizo_63221LF-BLLHP_R2025.rfa](<../63221LF-BLLHP/Brizo_63221LF-BLLHP_R2025.rfa>).
RFA SHA-256: `ffdb7eb9d71883556d8df86ddc55066cc88f8b4db8f7a32f5d516ad812162b8a`.
Validation: [validation.json](<../63221LF-BLLHP/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T16:07:25.786000Z.
Source RFA input version: Native custom build.
RFA search result: No acceptable no-account RFA recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"evidence": "_research/63221LF-BLLHP/sources.json", "result": "No acceptable no-account RFA recovered"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- Brizo Odin 63121/63221 less-handle specification Rev B: https://media.brizo.com/SpecSheet/BSP-K-63121LF-LHP%20Rev%20B.pdf; page 1.
- Worker-5 source cross-check: https://media.brizo.com/SpecSheet/BSP-K-63121LF-LHP%20Rev%20A.pdf.
- Worker-5 source cross-check: https://www.brizo.com/kitchen/product/63221LF-BLLHP.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 98.2662 | 98.2662 | 0 | PASS |
| Y | 166.0842 | 166.0842 | -0 | PASS |
| Z | 552.45 | 552.45 | 0 | PASS |

All overall dimensions have manufacturer authority: **false**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- Base diameter 2.4375 in; outlet reach 4.75 in; lower swivel datum 6.75 in; vertical distance to upper swivel 5.875 in; exposed hose 23 in.
- Native anchor/path: Base diameter, measured 61.9125 mm; nominal 61.9125 mm; PASS.
- Native anchor/path: 23 inch exposed hose, measured 584.2 mm; nominal 584.2 mm; PASS.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: 63221LF-BLLHP - Matte Black -  Black; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3709", "host_kind": "floor", "hostface_present": true, "instance_host_id": "3709", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Brass | True | True |
| Detail | True | True |
| Finish | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [63221LF-BLLHP/source/build.py](<../63221LF-BLLHP/source/build.py>).
Visual review: NATIVE_OBLIQUE_AND_SIDE_INSPECTED_WITH_LIMITATIONS. Final release is pending orchestrator review.

- [Brizo_63221LF-BLLHP_R2025_Isolated - 3D View - Native Front.png](<../63221LF-BLLHP/evidence/Brizo_63221LF-BLLHP_R2025_Isolated - 3D View - Native Front.png>)
- [Brizo_63221LF-BLLHP_R2025_Isolated - 3D View - Native Material.png](<../63221LF-BLLHP/evidence/Brizo_63221LF-BLLHP_R2025_Isolated - 3D View - Native Material.png>)
- [Brizo_63221LF-BLLHP_R2025_Isolated - 3D View - Native Oblique.png](<../63221LF-BLLHP/evidence/Brizo_63221LF-BLLHP_R2025_Isolated - 3D View - Native Oblique.png>)
- [Brizo_63221LF-BLLHP_R2025_Isolated - 3D View - Native Side.png](<../63221LF-BLLHP/evidence/Brizo_63221LF-BLLHP_R2025_Isolated - 3D View - Native Side.png>)

Native oblique and side images inspected: two articulated arms, wand, separate hose, base and less-handle spindle are visible. Pose and rigid simplified sections remain limitations.

Current official product page links BSP-K-63121LF-LHP Rev B. Rev B parsed successfully but its screenshot returned cache miss. Manufacturer Rev A, linked by a supplier, was successfully viewed as a PDF screenshot; the relevant 2.4375/6.75/5.875/4.75/21.5-inch and 23-inch hose callouts match Rev B text. Rev A is used only for visual corroboration.

## Assumptions and limitations

- ASSUMPTION: hose is posed with a 21.75-inch outer crown; the manufacturer states overall height varies with arm position and depicts 21.5 in in another pose.
- Above-deck family only; supply tubing and mounting shank omitted. HLK175 handle remains a separate row.
- Rigid arm sections, wand length, pivots and sleeve proportions are drawing-derived. Articulation is represented as a fixed display pose.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.
- ASSUMPTION: retain the documented fixed pose at 21.75-inch outer hose height and exactly 23-inch native hose path. It is not a verified manufacturer overall height. The current product page states 19.875 inches, while its linked drawing depicts 21.5 inches and states height varies with arm position. Resolve pose/clearance convention during visual review.

## Blockers and release

No additional identity-specific NEEDS_USER hold is recorded. Inferred geometry/finish fidelity still requires orchestrator review.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
