<!-- worker5 completion -->
# Plumbing fixture row 4091393569652612

**Final status: BUILT_WITH_LIMITATIONS**

## Identity and scope

- Row ID: `4091393569652612`; item key: `T704110-BNXLHP__4091393569652612`.
- Scheduled product: Brizo / T704110-BNXLHP.
- Scheduled description: Brizo Roccesco Two-Handle Wall-Mount Tub Filler Trim, Less Handles and Rough-In - Brilliance Black Onyx.
- Scheduled finish: Brilliance Black Onyx; Black; unit: Triplex; room: Primary Bathroom.
- Original agent_ignore: `false`. Coverage does not reinstate an ignored or descoped product.

Original source note: None recorded.

## Source and last verified stage

Shared product group: `T704110-BNXLHP`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [T704110-BNXLHP/Brizo_T704110-BNXLHP_R2025.rfa](<../T704110-BNXLHP/Brizo_T704110-BNXLHP_R2025.rfa>).
RFA SHA-256: `7449532041a175a88952cb2d7352abaf4c8eede47907333f8adf1186e1026fe7`.
Validation: [validation.json](<../T704110-BNXLHP/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T15:12:41.206000Z.
Source RFA input version: Native custom build.
RFA search result: No acceptable no-account RFA recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"evidence": "_research/T704110-BNXLHP/sources.json", "result": "No acceptable no-account RFA recovered"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- BSP-B-T704110-LHP Rev B: https://bravo.requested-info.com/brands/BRZ/documents/specSheets/T704110-BLLHP_Spec.pdf; page 1.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 210.312 | 210.312 | 0 | PASS |
| Y | 80.9308 | 80.9307 | 0 | PASS |
| Z | 319.0875 | 319.0875 | 0 | PASS |

All overall dimensions have manufacturer authority: **false**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- Projection 12.5625 in; nominal outlet reach 11.875 in; flange diameter 2.8125 in; stem centers 8 in.
- Native anchor/path: Flange diameter, measured 71.4375 mm; nominal 71.4375 mm; PASS.
- Native anchor/path: Projection, measured 319.0875 mm; nominal 319.0875 mm; PASS.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: T704110-BNXLHP - Brilliance Black Onyx -  Black; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3695", "host_kind": "wall", "hostface_present": true, "instance_host_id": "3695", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Brass | True | True |
| Finish | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [T704110-BNXLHP/source/build.py](<../T704110-BNXLHP/source/build.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [Brizo_T704110-BNXLHP_R2025_Isolated - 3D View - Native Front.png](<../T704110-BNXLHP/evidence/Brizo_T704110-BNXLHP_R2025_Isolated - 3D View - Native Front.png>)
- [Brizo_T704110-BNXLHP_R2025_Isolated - 3D View - Native Material.png](<../T704110-BNXLHP/evidence/Brizo_T704110-BNXLHP_R2025_Isolated - 3D View - Native Material.png>)
- [Brizo_T704110-BNXLHP_R2025_Isolated - 3D View - Native Oblique.png](<../T704110-BNXLHP/evidence/Brizo_T704110-BNXLHP_R2025_Isolated - 3D View - Native Oblique.png>)
- [Brizo_T704110-BNXLHP_R2025_Isolated - 3D View - Native Side.png](<../T704110-BNXLHP/evidence/Brizo_T704110-BNXLHP_R2025_Isolated - 3D View - Native Side.png>)

## Assumptions and limitations

- Rounded spout side profile, underside arch and vertical outlet position are drawing-derived.
- LHP handles and R70400 rough are separate inventory items.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.

## Blockers and release

No additional identity-specific NEEDS_USER hold is recorded. Inferred geometry/finish fidelity still requires orchestrator review.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
