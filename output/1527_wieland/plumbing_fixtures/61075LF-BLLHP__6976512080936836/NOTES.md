<!-- worker5 completion -->
# Plumbing fixture row 6976512080936836

**Final status: BUILT_WITH_LIMITATIONS**

## Identity and scope

- Row ID: `6976512080936836`; item key: `61075LF-BLLHP__6976512080936836`.
- Scheduled product: Brizo / 61075LF-BLLHP.
- Scheduled description: Brizo Odin Bar Faucet with Arc   Spout, Less Handle - Matte Black.
- Scheduled finish: Matte Black; Black; unit: Triplex; room: Kitchen.
- Original agent_ignore: `false`. Coverage does not reinstate an ignored or descoped product.

Original source note: None recorded.

## Source and last verified stage

Shared product group: `61075LF-BLLHP`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [61075LF-BLLHP/Brizo_61075LF-BLLHP_R2025.rfa](<../61075LF-BLLHP/Brizo_61075LF-BLLHP_R2025.rfa>).
RFA SHA-256: `0752fefd550bce6ae7bbb45f7bc2e341c2f57d5507385336d17b3b5a173de305`.
Validation: [validation.json](<../61075LF-BLLHP/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T15:43:17.478000Z.
Source RFA input version: Native custom build.
RFA search result: No acceptable no-account RFA recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"result": "No acceptable no-account RFA recovered", "evidence": "_research/61075LF-BLLHP/sources.json"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- Brizo BSP-K-61075LF-LHP Rev C: https://assets.specbooks.cloud/brand/brizo/spec/7646847/document/spec-sb-sccscf.pdf; page 1.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 93.6625 | 93.6625 | 0 | PASS |
| Y | 193.5043 | 193.675 | -0.1707 | PASS |
| Z | 295.2323 | 295.275 | -0.0427 | PASS |

All overall dimensions have manufacturer authority: **false**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- Overall height 11.625 in, nominal spout reach 6 in, outlet center height 8.375 in, base diameter 2.375 in.
- Native anchor/path: Faucet height, measured 295.2323 mm; nominal 295.275 mm; PASS.
- Native anchor/path: Base diameter, measured 60.325 mm; nominal 60.325 mm; PASS.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: 61075LF-BLLHP - Matte Black -  Black; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3703", "host_kind": "floor", "hostface_present": true, "instance_host_id": "3703", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Brass | True | True |
| Detail | True | True |
| Finish | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [61075LF-BLLHP/source/build.py](<../61075LF-BLLHP/source/build.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [Brizo_61075LF-BLLHP_R2025_Isolated - 3D View - Native Front.png](<../61075LF-BLLHP/evidence/Brizo_61075LF-BLLHP_R2025_Isolated - 3D View - Native Front.png>)
- [Brizo_61075LF-BLLHP_R2025_Isolated - 3D View - Native Material.png](<../61075LF-BLLHP/evidence/Brizo_61075LF-BLLHP_R2025_Isolated - 3D View - Native Material.png>)
- [Brizo_61075LF-BLLHP_R2025_Isolated - 3D View - Native Oblique.png](<../61075LF-BLLHP/evidence/Brizo_61075LF-BLLHP_R2025_Isolated - 3D View - Native Oblique.png>)
- [Brizo_61075LF-BLLHP_R2025_Isolated - 3D View - Native Side.png](<../61075LF-BLLHP/evidence/Brizo_61075LF-BLLHP_R2025_Isolated - 3D View - Native Side.png>)

## Assumptions and limitations

- Below-deck shank and supply tubing are omitted.
- Body and tube diameters are drawing-derived; spout endpoint follows the printed outlet height with a continuous tangent arc.
- The separate HLB175 handle is intentionally absent from this less-handle SKU.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.

## Blockers and release

No additional identity-specific NEEDS_USER hold is recorded. Inferred geometry/finish fidelity still requires orchestrator review.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
