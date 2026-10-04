<!-- worker5 completion -->
# Plumbing fixture row 1839593755967364

**Final status: BUILT_WITH_LIMITATIONS**

## Identity and scope

- Row ID: `1839593755967364`; item key: `HL53110-BNX__1839593755967364`.
- Scheduled product: Brizo / HL53110-BNX.
- Scheduled description: Brizo   Roccesco Widespread Lavatory Lever Handle Kit - Brilliance Black Onyx.
- Scheduled finish: Brilliance Black Onyx; Black; unit: Triplex; room: Primary Bathroom.
- Original agent_ignore: `false`. Coverage does not reinstate an ignored or descoped product.

Original source note: None recorded.

## Source and last verified stage

Shared product group: `HL53110-BNX`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [HL53110-BNX/Brizo_HL53110-BNX_R2025.rfa](<../HL53110-BNX/Brizo_HL53110-BNX_R2025.rfa>).
RFA SHA-256: `ee29b03dd04f1fe806b6a8b70b89e60be243b538755015d789bed59248252c80`.
Validation: [validation.json](<../HL53110-BNX/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T14:49:09.856000Z.
Source RFA input version: Native custom build.
RFA search result: No acceptable no-account RFA recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"result": "No acceptable no-account RFA recovered", "evidence": "_research/HL53110-BNX/sources.json"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- BSP-L-653110LF-LHP Rev A: https://bravo.requested-info.com/brands/BRZ/documents/specSheets/653110LF-BLLHP_Spec.pdf; page 1.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 333.375 | 333.375 | 0 | PASS |
| Y | 47.625 | 47.625 | 0 | PASS |
| Z | 58.7375 | 58.7375 | 0 | PASS |

All overall dimensions have manufacturer authority: **false**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- Handle height 2.3125 in; axis-to-tip reach 2.5625 in; base diameter follows the faucet flange 1.875 in.
- Native anchor/path: Handle height, measured 58.7375 mm; nominal 58.7375 mm; PASS.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: HL53110-BNX - Brilliance Black Onyx -  Black; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3695", "host_kind": "floor", "hostface_present": true, "instance_host_id": "3695", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Finish | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [HL53110-BNX/source/build.py](<../HL53110-BNX/source/build.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [Brizo_HL53110-BNX_R2025_Isolated - 3D View - Native Front.png](<../HL53110-BNX/evidence/Brizo_HL53110-BNX_R2025_Isolated - 3D View - Native Front.png>)
- [Brizo_HL53110-BNX_R2025_Isolated - 3D View - Native Material.png](<../HL53110-BNX/evidence/Brizo_HL53110-BNX_R2025_Isolated - 3D View - Native Material.png>)
- [Brizo_HL53110-BNX_R2025_Isolated - 3D View - Native Oblique.png](<../HL53110-BNX/evidence/Brizo_HL53110-BNX_R2025_Isolated - 3D View - Native Oblique.png>)
- [Brizo_HL53110-BNX_R2025_Isolated - 3D View - Native Side.png](<../HL53110-BNX/evidence/Brizo_HL53110-BNX_R2025_Isolated - 3D View - Native Side.png>)

## Assumptions and limitations

- ASSUMPTION: paired at 8 in centers to align with this section faucet; controls point outward.
- Fine lever waisting and edge radii are drawing-derived.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.

## Blockers and release

No additional identity-specific NEEDS_USER hold is recorded. Inferred geometry/finish fidelity still requires orchestrator review.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
