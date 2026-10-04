<!-- worker5 completion -->
# Plumbing fixture row 7469093290180484

**Final status: BUILT_WITH_LIMITATIONS**

## Identity and scope

- Row ID: `7469093290180484`; item key: `653110LF-BNXLHP__7469093290180484`.
- Scheduled product: Brizo / 653110LF-BNXLHP.
- Scheduled description: Brizo Roccesco Widespread   Bathroom Faucet with Arc Spout, Less Handles - Brilliance Black Onyx.
- Scheduled finish: Brilliance Black Onyx; Black; unit: Triplex; room: Primary Bathroom.
- Original agent_ignore: `false`. Coverage does not reinstate an ignored or descoped product.

Original source note: None recorded.

## Source and last verified stage

Shared product group: `653110LF-BNXLHP`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [653110LF-BNXLHP/Brizo_653110LF-BNXLHP_R2025.rfa](<../653110LF-BNXLHP/Brizo_653110LF-BNXLHP_R2025.rfa>).
RFA SHA-256: `dd7b02728a6d6d9c534bfb20991316602eb4153dcbdd82fad566c83b520dc64a`.
Validation: [validation.json](<../653110LF-BNXLHP/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T14:49:06.692000Z.
Source RFA input version: Native custom build.
RFA search result: No acceptable no-account RFA recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"result": "No acceptable no-account RFA recovered", "evidence": "_research/653110LF-BNXLHP/sources.json"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- BSP-L-653110LF-LHP Rev A: https://bravo.requested-info.com/brands/BRZ/documents/specSheets/653110LF-BLLHP_Spec.pdf; page 1.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 250.825 | 250.825 | 0 | PASS |
| Y | 184.126 | 184.15 | -0.024 | PASS |
| Z | 236.5374 | 236.5375 | -0.0001 | PASS |

All overall dimensions have manufacturer authority: **false**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- Height 9.3125 in; outlet height 6.3125 in; reach 6 in; bases 2 in and 1.875 in.
- Native anchor/path: Height, measured 236.5374 mm; nominal 236.5375 mm; PASS.
- Native anchor/path: Spout base diameter, measured 50.8 mm; nominal 50.8 mm; PASS.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: 653110LF-BNXLHP - Brilliance Black Onyx -  Black; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3699", "host_kind": "floor", "hostface_present": true, "instance_host_id": "3699", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Brass | True | True |
| Finish | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [653110LF-BNXLHP/source/build.py](<../653110LF-BNXLHP/source/build.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [Brizo_653110LF-BNXLHP_R2025_Isolated - 3D View - Native Front.png](<../653110LF-BNXLHP/evidence/Brizo_653110LF-BNXLHP_R2025_Isolated - 3D View - Native Front.png>)
- [Brizo_653110LF-BNXLHP_R2025_Isolated - 3D View - Native Material.png](<../653110LF-BNXLHP/evidence/Brizo_653110LF-BNXLHP_R2025_Isolated - 3D View - Native Material.png>)
- [Brizo_653110LF-BNXLHP_R2025_Isolated - 3D View - Native Oblique.png](<../653110LF-BNXLHP/evidence/Brizo_653110LF-BNXLHP_R2025_Isolated - 3D View - Native Oblique.png>)
- [Brizo_653110LF-BNXLHP_R2025_Isolated - 3D View - Native Side.png](<../653110LF-BNXLHP/evidence/Brizo_653110LF-BNXLHP_R2025_Isolated - 3D View - Native Side.png>)

## Assumptions and limitations

- ASSUMPTION: 8 in valve centers selected within the published 4-16 in range.
- Above-deck scope only; handles supplied separately. Oval section and arc shoulders are drawing-derived.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.

## Blockers and release

No additional identity-specific NEEDS_USER hold is recorded. Inferred geometry/finish fidelity still requires orchestrator review.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
