<!-- worker5 completion -->
# Plumbing fixture row 161681487036292

**Final status: BUILT_WITH_LIMITATIONS**

## Identity and scope

- Row ID: `161681487036292`; item key: `HLK175-BL__161681487036292`.
- Scheduled product: Brizo / HLK175-BL.
- Scheduled description: Brizo Odin Pull-Down Kitchen   Faucet Lever Handle - Matte Black.
- Scheduled finish: Matte Black; Black; unit: Triplex; room: Kitchen.
- Original agent_ignore: `false`. Coverage does not reinstate an ignored or descoped product.

Original source note: None recorded.

## Source and last verified stage

Shared product group: `HLK175-BL`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [HLK175-BL/Brizo_HLK175-BL_R2025.rfa](<../HLK175-BL/Brizo_HLK175-BL_R2025.rfa>).
RFA SHA-256: `3c3be4f2713c8f541226016de2bb5eb47cf0aad23a2d2df6962cbca7771dff03`.
Validation: [validation.json](<../HLK175-BL/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T15:43:26.539000Z.
Source RFA input version: Native custom build.
RFA search result: No acceptable no-account RFA recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"result": "No acceptable no-account RFA recovered", "evidence": "_research/HLK175-BL/sources.json"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- Brizo BSP-K-63121LF-LHP Rev B: https://media.brizo.com/SpecSheet/BSP-K-63121LF-LHP%20Rev%20B.pdf; page 1.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 22.225 | 22.225 | 0 | PASS |
| Y | 93.6625 | 93.6625 | 0 | PASS |
| Z | 27.94 | 27.94 | 0 | PASS |

All overall dimensions have manufacturer authority: **false**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- Socket nominal diameter 0.875 in and axis-to-lever-tip distance 3.25 in: manufacturer handle detail.
- Native anchor/path: Socket diameter, measured 22.225 mm; nominal 22.225 mm; PASS.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: HLK175-BL - Matte Black -  Black; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3690", "host_kind": "wall", "hostface_present": true, "instance_host_id": "3690", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Finish | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [HLK175-BL/source/build.py](<../HLK175-BL/source/build.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [Brizo_HLK175-BL_R2025_Isolated - 3D View - Native Front.png](<../HLK175-BL/evidence/Brizo_HLK175-BL_R2025_Isolated - 3D View - Native Front.png>)
- [Brizo_HLK175-BL_R2025_Isolated - 3D View - Native Material.png](<../HLK175-BL/evidence/Brizo_HLK175-BL_R2025_Isolated - 3D View - Native Material.png>)
- [Brizo_HLK175-BL_R2025_Isolated - 3D View - Native Oblique.png](<../HLK175-BL/evidence/Brizo_HLK175-BL_R2025_Isolated - 3D View - Native Oblique.png>)
- [Brizo_HLK175-BL_R2025_Isolated - 3D View - Native Side.png](<../HLK175-BL/evidence/Brizo_HLK175-BL_R2025_Isolated - 3D View - Native Side.png>)

## Assumptions and limitations

- Socket depth and lever section are drawing-derived. Handle supplied in an upright neutral pose.
- HLB175 and HLK175 have separate product identities and must be aligned to their respective valve stems.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.

## Blockers and release

No additional identity-specific NEEDS_USER hold is recorded. Inferred geometry/finish fidelity still requires orchestrator review.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
