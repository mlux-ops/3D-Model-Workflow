<!-- worker5 completion -->
# Plumbing fixture row 2895124918632324

**Final status: BUILT_WITH_LIMITATIONS**

## Identity and scope

- Row ID: `2895124918632324`; item key: `26866701__2895124918632324`.
- Scheduled product: Hansgrohe / 26866701.
- Scheduled description: Hansgrohe   Rainfinity Baton 100 Single-Jet Hand Shower, 2.5 GPM - Matte White.
- Scheduled finish: White; unit: Triplex; room: Bath 4.
- Original agent_ignore: `false`. Coverage does not reinstate an ignored or descoped product.

Original source note: None recorded.

## Source and last verified stage

Shared product group: `26866701`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [26866701/Hansgrohe_26866701_R2025.rfa](<../26866701/Hansgrohe_26866701_R2025.rfa>).
RFA SHA-256: `1e9159abe1bc7e7d46e940ad5f156462283a68c4cb9110a70e380eae54f0e7fd`.
Validation: [validation.json](<../26866701/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T14:48:35.551000Z.
Source RFA input version: Native custom build.
RFA search result: No acceptable no-account RFA recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"result": "No acceptable no-account RFA recovered", "evidence": "_research/26866701/sources.json"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- Hansgrohe 2026 US Price Book: https://assets.hansgrohe.com/celum/emailmarketing/hansgrohe_2026_Price_Book_en_US.pdf; page 229.
- Manufacturer reference: https://www.bimobject.com/en-us/hansgrohe/product/26866001.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 38.1 | 38.1 | 0 | PASS |
| Y | 25.3048 | 25 | 0.3048 | PASS |
| Z | 228.6 | 228.6 | 0 | PASS |

All overall dimensions have manufacturer authority: **false**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- Width 1.5 in and overall length 9 in: catalog drawing.
- 25 mm body depth is a dimensional reference from the manufacturer BIM listing; its conflicting width is not used.
- Native anchor/path: Overall length, measured 228.6 mm; nominal 228.6 mm; PASS.
- Native anchor/path: Body width, measured 38.1 mm; nominal 38.1 mm; PASS.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: 26866701 - White; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3815", "host_kind": "floor", "hostface_present": true, "instance_host_id": "3815", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Detail | True | True |
| Finish | True | True |
| Graphite | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [26866701/source/build.py](<../26866701/source/build.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [Hansgrohe_26866701_R2025_Isolated - 3D View - Native Front.png](<../26866701/evidence/Hansgrohe_26866701_R2025_Isolated - 3D View - Native Front.png>)
- [Hansgrohe_26866701_R2025_Isolated - 3D View - Native Material.png](<../26866701/evidence/Hansgrohe_26866701_R2025_Isolated - 3D View - Native Material.png>)
- [Hansgrohe_26866701_R2025_Isolated - 3D View - Native Oblique.png](<../26866701/evidence/Hansgrohe_26866701_R2025_Isolated - 3D View - Native Oblique.png>)
- [Hansgrohe_26866701_R2025_Isolated - 3D View - Native Side.png](<../26866701/evidence/Hansgrohe_26866701_R2025_Isolated - 3D View - Native Side.png>)

## Assumptions and limitations

- Matte white is retained from the exact inventory SKU and manufacturer BIM finish list; the 2026 main catalog omits that finish.
- Nozzle count and undimensioned body taper are approximate.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.

## Blockers and release

No additional identity-specific NEEDS_USER hold is recorded. Inferred geometry/finish fidelity still requires orchestrator review.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
