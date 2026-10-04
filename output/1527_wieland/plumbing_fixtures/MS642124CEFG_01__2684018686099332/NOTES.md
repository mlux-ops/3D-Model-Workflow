<!-- worker5 completion -->
# Plumbing fixture row 2684018686099332

**Final status: DOWNLOADED**

## Identity and scope

- Row ID: `2684018686099332`; item key: `MS642124CEFG_01__2684018686099332`.
- Scheduled product: TOTO / MS642124CEFG#01.
- Scheduled description: TOTO   Nexus One-Piece Elongated Toilet with SoftClose Seat, 1.28 GPF - Cotton.
- Scheduled finish: -; unit: Triplex; room: Primary Bathroom.
- Original agent_ignore: `false`. Coverage does not reinstate an ignored or descoped product.

Original source note: None recorded.

## Source and last verified stage

Shared product group: `MS642124CEFG_01`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [MS642124CEFG_01/Manufacturer_MS642124CEFG_01_R2025.rfa](<../MS642124CEFG_01/Manufacturer_MS642124CEFG_01_R2025.rfa>).
RFA SHA-256: `34ae1bba989da333e19bb837d4a4ec903216879200e89938791c27bd24f223cc`.
Validation: [validation.json](<../MS642124CEFG_01/validation.json>); last verified stage: `manufacturer_review_complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T15:34:48.036000Z.
Source RFA input version: 2019.
RFA search result: Public manufacturer family recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"result": "Public manufacturer family recovered", "url": "https://www.totousa.com/filemanager_uploads/product_assets/REVITModels/BM-00593_MS642124CEFG_MS642124CUFG.rfa"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- Public manufacturer RFA: https://www.totousa.com/filemanager_uploads/product_assets/REVITModels/BM-00593_MS642124CEFG_MS642124CUFG.rfa.
- Manufacturer dimensional reference: https://www.totousa.com/filemanager_uploads/product_assets/SpecSheet/SS-01451_MS642124CEFG.pdf.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 451.3477 | 444.5 | 6.8477 | FAIL |
| Y | 726.0167 | 725.4875 | 0.5292 | PASS |
| Z | 685.8 | 685.8 | 0 | PASS |

All overall dimensions have manufacturer authority: **true**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.


## Native gates and parameters

Native gate result: **HOLD**. Category: Plumbing Fixtures; selected type: MS642124CEFG; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "dimensions": false, "materials": false, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_kind": "floor", "hostface_present": true, "instance_host_id": "6025"}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Flush Lever Finish | True | False |
| Product Material | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [_harness/inspect_downloaded_families.py](<../_harness/inspect_downloaded_families.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [Manufacturer_MS642124CEFG_01 - 3D View - Manufacturer Front.png](<../MS642124CEFG_01/evidence/Manufacturer_MS642124CEFG_01 - 3D View - Manufacturer Front.png>)
- [Manufacturer_MS642124CEFG_01 - 3D View - Manufacturer Oblique.png](<../MS642124CEFG_01/evidence/Manufacturer_MS642124CEFG_01 - 3D View - Manufacturer Oblique.png>)
- [Manufacturer_MS642124CEFG_01 - 3D View - Manufacturer Side.png](<../MS642124CEFG_01/evidence/Manufacturer_MS642124CEFG_01 - 3D View - Manufacturer Side.png>)

## Assumptions and limitations

- Original manufacturer geometry retained in its separate Revit 2025 copy; documented failed source gates remain holds. No source geometry was scaled to force agreement.

## Blockers and release

- NEEDS_USER_TOTO_NEXUS_DIMENSION_AND_LEVER: Manufacturer width is 451.348 mm versus 444.500 mm (+6.848 mm). Flush Lever Finish is writable but its substitution does not reach faces. Dimension and material gates remain false; source geometry has not been scaled.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
