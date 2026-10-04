<!-- worker5 completion -->
# Plumbing fixture row 5735549071130500

**Final status: DOWNLOADED**

## Identity and scope

- Row ID: `5735549071130500`; item key: `SS124_01__5735549071130500`.
- Scheduled product: TOTO / SS124#01.
- Scheduled description: TOTO SoftClose Elongated Toilet Seat - Cotton.
- Scheduled finish: -; unit: Triplex; room: Bath 2.
- Original agent_ignore: `false`. Coverage does not reinstate an ignored or descoped product.

Original source note: ADDED 2026-09-03. Triplex Bath 2 had the Aquia IV bowl and push-button but no tank and no seat. Price and reference copied from the identical item in Triplex Bath 3.

## Source and last verified stage

Shared product group: `SS124_01`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [SS124_01/Manufacturer_SS124_01_R2025.rfa](<../SS124_01/Manufacturer_SS124_01_R2025.rfa>).
RFA SHA-256: `dc2bd56330f6c8c4609666658742eda286dcca858dfd3fbeeb70d5530d9bc0f1`.
Validation: [validation.json](<../SS124_01/validation.json>); last verified stage: `manufacturer_review_complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T15:34:50.639000Z.
Source RFA input version: 2019; extracted nested BM-00561_SS124.
RFA search result: Public manufacturer family recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"result": "Public manufacturer family recovered", "url": "https://www.totousa.com/filemanager_uploads/product_assets/REVITModels/BM-00593_MS642124CEFG_MS642124CUFG.rfa"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- Public manufacturer RFA: https://www.totousa.com/filemanager_uploads/product_assets/REVITModels/BM-00593_MS642124CEFG_MS642124CUFG.rfa.
- Manufacturer dimensional reference: https://www.totousa.com/filemanager_uploads/product_assets/SpecSheet/SS-02062_MS446124CEMF(G)N.pdf.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 355.6583 | 355.6 | 0.0583 | PASS |
| Y | 513.772 | 473.075 | 40.697 | FAIL |
| Z | 122.1045 | 46.0375 | 76.067 | FAIL |

All overall dimensions have manufacturer authority: **true**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.


## Native gates and parameters

Native gate result: **HOLD**. Category: Plumbing Fixtures; selected type: SS124; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "dimensions": false, "materials": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_kind": "floor", "hostface_present": true, "instance_host_id": "3737"}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Material | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [_harness/inspect_downloaded_families.py](<../_harness/inspect_downloaded_families.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [Manufacturer_SS124_01 - 3D View - Manufacturer Front.png](<../SS124_01/evidence/Manufacturer_SS124_01 - 3D View - Manufacturer Front.png>)
- [Manufacturer_SS124_01 - 3D View - Manufacturer Oblique.png](<../SS124_01/evidence/Manufacturer_SS124_01 - 3D View - Manufacturer Oblique.png>)
- [Manufacturer_SS124_01 - 3D View - Manufacturer Side.png](<../SS124_01/evidence/Manufacturer_SS124_01 - 3D View - Manufacturer Side.png>)

## Assumptions and limitations

- Original manufacturer geometry retained in its separate Revit 2025 copy; documented failed source gates remain holds. No source geometry was scaled to force agreement.

## Blockers and release

- NEEDS_USER_TOTO_SS124_ENVELOPE: Manufacturer seat envelope is 355.658 x 513.772 x 122.104 mm versus 355.600 x 473.075 x 46.038 mm. Depth +40.697 mm and height +76.067 mm include hinge/rod extents; reconcile seat-body and accessory scope before release.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
