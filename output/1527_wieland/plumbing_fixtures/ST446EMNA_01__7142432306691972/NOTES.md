<!-- worker5 completion -->
# Plumbing fixture row 7142432306691972

**Final status: BUILT_WITH_LIMITATIONS**

## Identity and scope

- Row ID: `7142432306691972`; item key: `ST446EMNA_01__7142432306691972`.
- Scheduled product: TOTO / ST446EMNA#01.
- Scheduled description: TOTO   Aquia IV Dual-Flush Toilet Tank, 1.28/0.9 GPF - Cotton.
- Scheduled finish: -; unit: Penthouse; room: Bath 4.
- Original agent_ignore: `false`. Coverage does not reinstate an ignored or descoped product.

Original source note: None recorded.

## Source and last verified stage

Shared product group: `ST446EMNA_01`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [ST446EMNA_01/TOTO_ST446EMNA_01_R2025.rfa](<../ST446EMNA_01/TOTO_ST446EMNA_01_R2025.rfa>).
RFA SHA-256: `1998925a4c423081301d94f74a6a85a50c667ca5c24aef977e5c51172c109a19`.
Validation: [validation.json](<../ST446EMNA_01/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T15:47:31.840000Z.
Source RFA input version: Native custom build.
RFA search result: No acceptable no-account RFA recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"evidence": "_research/ST446EMNA_01/sources.json", "result": "No acceptable no-account RFA recovered"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- TOTO Aquia IV SS-02062: https://www.totousa.com/filemanager_uploads/product_assets/SpecSheet/SS-02062_MS446124CEMF(G)N.pdf; page 2.
- TOTO Aquia IV PD-01451 parts: https://www.totousa.com/filemanager_uploads/product_assets/PartsManual/PD-01451_446EN.pdf; page 1.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 393.7 | 393.7 | 0 | PASS |
| Y | 161.925 | 161.925 | 0 | PASS |
| Z | 358.775 | 358.775 | 0 | PASS |

All overall dimensions have manufacturer authority: **false**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- Tank width 15.5 in and depth 6.375 in from the complete-set drawing.
- Tank height 14.125 in is derived from 30.25 in total minus 16.125 in rim-height datum.
- Native anchor/path: Tank width, measured 393.7 mm; nominal 393.7 mm; PASS.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: ST446EMNA#01 - ceramic; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3696", "host_kind": "floor", "hostface_present": true, "instance_host_id": "3696", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Finish | True | True |
| Gray | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [ST446EMNA_01/source/build.py](<../ST446EMNA_01/source/build.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [TOTO_ST446EMNA_01_R2025_Isolated - 3D View - Native Front.png](<../ST446EMNA_01/evidence/TOTO_ST446EMNA_01_R2025_Isolated - 3D View - Native Front.png>)
- [TOTO_ST446EMNA_01_R2025_Isolated - 3D View - Native Material.png](<../ST446EMNA_01/evidence/TOTO_ST446EMNA_01_R2025_Isolated - 3D View - Native Material.png>)
- [TOTO_ST446EMNA_01_R2025_Isolated - 3D View - Native Oblique.png](<../ST446EMNA_01/evidence/TOTO_ST446EMNA_01_R2025_Isolated - 3D View - Native Oblique.png>)
- [TOTO_ST446EMNA_01_R2025_Isolated - 3D View - Native Side.png](<../ST446EMNA_01/evidence/TOTO_ST446EMNA_01_R2025_Isolated - 3D View - Native Side.png>)

## Assumptions and limitations

- ASSUMPTION: tank mounting base aligns with the complete-set rim-height datum. Independent tank-height dimension is not published in this reference.
- The ceramic body and lid are represented; internal flushing hardware, screws and gaskets are omitted.
- THU842 button remains a separately scheduled component; lid opening diameter is drawing-derived.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.

## Blockers and release

No additional identity-specific NEEDS_USER hold is recorded. Inferred geometry/finish fidelity still requires orchestrator review.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
