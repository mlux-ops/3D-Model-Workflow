<!-- worker5 completion -->
# Plumbing fixture row 2525236026867588

**Final status: BUILT_WITH_LIMITATIONS**

## Identity and scope

- Row ID: `2525236026867588`; item key: `81392-BNX-2.5__2525236026867588`.
- Scheduled product: Brizo / 81392-BNX-2.5.
- Scheduled description: Brizo 12" Linear Round   Single-Function Raincan Shower Head, 2.5 GPM - Brilliance Black Onyx.
- Scheduled finish: Brilliance Black Onyx; Black; unit: Penthouse; room: Bath 4.
- Original agent_ignore: `false`. Coverage does not reinstate an ignored or descoped product.

Original source note: None recorded.

## Source and last verified stage

Shared product group: `81392-BNX-2.5`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [81392-BNX-2.5/Brizo_81392-BNX-2.5_R2025.rfa](<../81392-BNX-2.5/Brizo_81392-BNX-2.5_R2025.rfa>).
RFA SHA-256: `1d9d57a2569404d2b058ed34070afec47e354d393725755801f443dfced4c506`.
Validation: [validation.json](<../81392-BNX-2.5/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T14:49:31.725000Z.
Source RFA input version: Native custom build.
RFA search result: No acceptable no-account RFA recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"result": "No acceptable no-account RFA recovered", "evidence": "_research/81392-BNX-2.5/sources.json"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- BSP-B-81392 Rev B: https://media.brizo.com/SpecSheet/BSP-B-81392%20Rev%20B.pdf; page 1.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 298.45 | 298.45 | 0 | PASS |
| Y | 298.45 | 298.45 | 0 | PASS |
| Z | 60.325 | 60.325 | 0 | PASS |

All overall dimensions have manufacturer authority: **true**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- Actual plate diameter 11.75 in, plate thickness .5 in, total depth 2.375 in.
- Native anchor/path: Plate diameter, measured 298.45 mm; nominal 298.45 mm; PASS.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: 81392-BNX-2.5 - Brilliance Black Onyx -  Black; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3888", "host_kind": "ceiling", "hostface_present": true, "instance_host_id": "3888", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Detail | True | True |
| Finish | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [81392-BNX-2.5/source/build.py](<../81392-BNX-2.5/source/build.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [Brizo_81392-BNX-2_5_R2025_Isolated - 3D View - Native Front.png](<../81392-BNX-2.5/evidence/Brizo_81392-BNX-2_5_R2025_Isolated - 3D View - Native Front.png>)
- [Brizo_81392-BNX-2_5_R2025_Isolated - 3D View - Native Material.png](<../81392-BNX-2.5/evidence/Brizo_81392-BNX-2_5_R2025_Isolated - 3D View - Native Material.png>)
- [Brizo_81392-BNX-2_5_R2025_Isolated - 3D View - Native Oblique.png](<../81392-BNX-2.5/evidence/Brizo_81392-BNX-2_5_R2025_Isolated - 3D View - Native Oblique.png>)
- [Brizo_81392-BNX-2_5_R2025_Isolated - 3D View - Native Side.png](<../81392-BNX-2.5/evidence/Brizo_81392-BNX-2_5_R2025_Isolated - 3D View - Native Side.png>)

## Assumptions and limitations

- Catalog market name is 12 in; model uses its dimensioned 11.75 in diameter.
- Dense spray array follows the 2.5 GPM variant; individual nozzle positions are approximate.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.

## Blockers and release

No additional identity-specific NEEDS_USER hold is recorded. Inferred geometry/finish fidelity still requires orchestrator review.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
