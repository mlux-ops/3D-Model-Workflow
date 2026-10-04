<!-- worker5 completion -->
# Plumbing fixture row 8521984937688964

**Final status: DOWNLOADED**

## Identity and scope

- Row ID: `8521984937688964`; item key: `700337000000090__8521984937688964`.
- Scheduled product: Duravit / 700337000000090.
- Scheduled description: Duravit   Starck 67" x 36" Built-In Acrylic Bathtub with Support Frame -   White.
- Scheduled finish: White; unit: Penthouse; room: Primary Bathroom.
- Original agent_ignore: `false`. Coverage does not reinstate an ignored or descoped product.

Original source note: None recorded.

## Source and last verified stage

Shared product group: `700337000000090`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [700337000000090/Manufacturer_700337000000090_R2025.rfa](<../700337000000090/Manufacturer_700337000000090_R2025.rfa>).
RFA SHA-256: `9c5d7f7efe5f22e6493b5ee36ba289677740d0281f92739fc872dc86058b8642`.
Validation: [validation.json](<../700337000000090/validation.json>); last verified stage: `manufacturer_review_complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T15:34:53.879000Z.
Source RFA input version: 2018.
RFA search result: Public manufacturer family recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"result": "Public manufacturer family recovered", "url": "https://pro.duravit.us/pro/zip/sf_getfiles.us-en.zip?nodeId=3169365&ftd=ASSET_TYPE_REVIT"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- Public manufacturer RFA: https://pro.duravit.us/pro/zip/sf_getfiles.us-en.zip?nodeId=3169365&ftd=ASSET_TYPE_REVIT.
- Manufacturer dimensional reference: https://pro.duravit.us/pro/content/homepage/series/series/overview/products~402880943a1b6e1b013a1bd20b39003d.us-en.html?product=3169365.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 1700 | 1700 | 0 | PASS |
| Y | 900 | 900 | 0 | PASS |
| Z | 531.0417 | unresolved | unresolved | UNRESOLVED |

All overall dimensions have manufacturer authority: **false**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.


## Native gates and parameters

Native gate result: **HOLD**. Category: Plumbing Fixtures; selected type: Starck Bathtub, 1700x900 mm - 700337; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "dimensions": false, "materials": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_kind": "floor", "hostface_present": true, "instance_host_id": "4177"}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Details material | True | True |
| Main material | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [_harness/inspect_downloaded_families.py](<../_harness/inspect_downloaded_families.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [Manufacturer_700337000000090 - 3D View - Manufacturer Front.png](<../700337000000090/evidence/Manufacturer_700337000000090 - 3D View - Manufacturer Front.png>)
- [Manufacturer_700337000000090 - 3D View - Manufacturer Oblique.png](<../700337000000090/evidence/Manufacturer_700337000000090 - 3D View - Manufacturer Oblique.png>)
- [Manufacturer_700337000000090 - 3D View - Manufacturer Side.png](<../700337000000090/evidence/Manufacturer_700337000000090 - 3D View - Manufacturer Side.png>)

## Assumptions and limitations

- Original manufacturer geometry retained in its separate Revit 2025 copy; documented failed source gates remain holds. No source geometry was scaled to force agreement.

## Blockers and release

- NEEDS_USER_DURAVIT_700337_HEIGHT_SCOPE: Manufacturer envelope is 1700.000 x 900.000 x 531.042 mm. Length and width pass; authoritative overall height/body-versus-accessory scope is unresolved. Confirm the height convention and exact 700337000000090 suffix scope before release.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
