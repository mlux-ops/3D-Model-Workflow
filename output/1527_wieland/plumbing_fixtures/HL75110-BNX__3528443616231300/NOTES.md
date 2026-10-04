<!-- worker5 completion -->
# Plumbing fixture row 3528443616231300

**Final status: BUILT_WITH_LIMITATIONS**

## Identity and scope

- Row ID: `3528443616231300`; item key: `HL75110-BNX__3528443616231300`.
- Scheduled product: Brizo / HL75110-BNX.
- Scheduled description: Brizo   Roccesco Integrated Diverter Lever Handle Kit - Brilliance Black Onyx.
- Scheduled finish: Brilliance Black Onyx; Black; unit: Triplex; room: Primary Bathroom.
- Original agent_ignore: `false`. Coverage does not reinstate an ignored or descoped product.

Original source note: None recorded.

## Source and last verified stage

Shared product group: `HL75110-BNX`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [HL75110-BNX/Brizo_HL75110-BNX_R2025.rfa](<../HL75110-BNX/Brizo_HL75110-BNX_R2025.rfa>).
RFA SHA-256: `57bb276b7a70bddf4bf97f23bdf4b3ea7ad636ceb11a1e2789254d2c31899816`.
Validation: [validation.json](<../HL75110-BNX/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T15:27:38.095000Z.
Source RFA input version: Native custom build.
RFA search result: No acceptable no-account RFA recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"result": "No acceptable no-account RFA recovered", "evidence": "_research/HL75110-BNX/sources.json"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- Brizo BSP-B-T755110-LHP Rev A: https://bravo.requested-info.com/brands/BRZ/documents/specSheets/T755110-BLLHP_Spec.pdf; page 1.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 88.9 | 88.9 | 0 | PASS |
| Y | 122.2375 | 122.2375 | 0 | PASS |
| Z | 104.775 | 104.775 | 0 | PASS |

All overall dimensions have manufacturer authority: **false**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- Lower handle projection 4.125 in; upper handle projection 2.4375 in; lever length 3.5 in; upper sleeve diameter 1.375 in.
- Native anchor/path: Lower handle projection, measured 104.775 mm; nominal 104.775 mm; PASS.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: HL75110-BNX - Brilliance Black Onyx -  Black; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3694", "host_kind": "wall", "hostface_present": true, "instance_host_id": "3694", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Finish | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [HL75110-BNX/source/build.py](<../HL75110-BNX/source/build.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [Brizo_HL75110-BNX_R2025_Isolated - 3D View - Native Front.png](<../HL75110-BNX/evidence/Brizo_HL75110-BNX_R2025_Isolated - 3D View - Native Front.png>)
- [Brizo_HL75110-BNX_R2025_Isolated - 3D View - Native Material.png](<../HL75110-BNX/evidence/Brizo_HL75110-BNX_R2025_Isolated - 3D View - Native Material.png>)
- [Brizo_HL75110-BNX_R2025_Isolated - 3D View - Native Oblique.png](<../HL75110-BNX/evidence/Brizo_HL75110-BNX_R2025_Isolated - 3D View - Native Oblique.png>)
- [Brizo_HL75110-BNX_R2025_Isolated - 3D View - Native Side.png](<../HL75110-BNX/evidence/Brizo_HL75110-BNX_R2025_Isolated - 3D View - Native Side.png>)

## Assumptions and limitations

- ASSUMPTION: control center spacing 2.875 in follows the companion trim drawing.
- Kit origins are representative and require alignment with the installed trim; concealed mating surfaces are not fabrication geometry.
- Secondary temperature lever depth and sleeve diameters are drawing-derived.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.

## Blockers and release

No additional identity-specific NEEDS_USER hold is recorded. Inferred geometry/finish fidelity still requires orchestrator review.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
