# 651 Belmont PH Good | Bolla and Smooth OEM material map

Date: 2026-10-16. Evidence is the native read-only probe recorded at
`E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\qa\inspect_oem_material_parts.json`.
Receipt SHA-256: `2ee88654c081a629fa324681703497a72adff29a2481a676f51b98d03b2213b3`.
No authoring or native Revit execution was performed in this review.

## Kuzco Bolla PD3106-BG

OEM-derived saved RFA: `E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\families\Kuzco_Bolla_PD3106_BG_R2025.rfa`,
SHA-256 `eb5cf17c25531152acc8e51ccb0ad5bd80913ae547f878d9108d059090e6f2f3`.
Exact downloaded OEM original:
`E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\sources\oem\extracted\KZC1353667_PD3106_Bolla_Revit\PD3106 - Bolla.rfa`,
SHA-256 `8d84d0a6842b26ca3b8686f86948172349d1d1aec04a75a2b68af4463ef5c98a`.

| Native element ID | Geometry/material probe | Local Z extent, mm | Decision |
| --- | --- | --- | --- |
| 4435 | Revolution; 6 glass faces; material 1742 `Glass`; horizontal extent 139.72 × 140.65 mm | 3337.68–3476.78 | Preserve clear outer glass |
| 5101 | Revolution; 16 glass faces; material 8722 `Glass Frosted`; horizontal extent 63.39 × 63.52 mm | 3396.50–3475.31 | Preserve inner opal glass |
| 4715 | Revolution; 8 unassigned faces; 14.80 × 17.09 × 25.78 mm | 3464.22–3490.00 | **Brushed Gold research candidate**: small connector/metal neck immediately above glass |
| 7721 | Revolution; 14 unassigned faces; maximum horizontal extent 116.99 × 120 mm; 510 mm tall | 3490.00–4000.00 | **Hold**: canopy plus suspension span; entire-element gold could recolor the manufacturer's black wire |
| 3626 | Light Source category mesh; default light source material 3633 | 2890.83–3500.43 | Exclude from fixture appearance and physical dimensional acceptance |

Native family type `Type 1` has no material type parameters. Source-specific finish proof:
manufacturer [Bolla PD3106 product](https://kuzcolighting.com/products/bolla-pd3106-kuzco)
confirms steel-and-glass construction, Brushed Gold for `BG`, clear glass
with inner opal glass, and **black suspension wire** for Brushed Gold.
The [PD3106 specification PDF](https://kuzcolighting.lightingnewyork.com/on/demandware.static/-/Sites-master-catalog-lny/default/dw1bbe4fb8/brand/kuz/assets/specsheet/pd3106+spec+sheet.pdf)
confirms `BG` versus `BG/OP` variant distinctions, 5.5-inch diameter
by 6-inch high body and 4.75-inch canopy. The native family includes a
20-inch suspension/canopy assembly; that is not part of the 6-inch body.

**Candidate conversion:** `E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\scripts\build_bolla_pd3106_bg_neck_r02.py`.
The script checks the SHA-256 of all three inputs, checks native Revit
element classes/face materials/approximate measured bounds, and uses the
individual material parameter of **element 4715 only**. It does not
recolor element 7721 or the two glass elements. Brushed Gold material RGB
and reflection are provisional estimates, not a manufacturer material map.
When the prime runs it in isolated Revit 2025, its *new* output target is
`E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\candidates\Kuzco_Bolla_PD3106_BG_R2025_R02_PARTIAL_NECK_UNAPPROVED.rfa`
with new native receipt at
`E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\qa\bolla_pd3106_bg_r02_neck_build.json`.
No target RFA has yet been produced by this worker.

**Release status:** research-only partial Brushed Gold neck. Canopy,
black wire and structural hardware boundaries must be separated with
additional face-level evidence before a complete Brushed Gold family is
approved. Native material binding, geometry readback, hosting, photometry
and realistic finish still require prime execution/review.

## Modern Forms Smooth FR-W2502-52L-SB/MB

OEM-derived saved RFA:
`E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\families\ModernForms_Smooth_FR-W2502-52L_SBMB_R2025.rfa`,
SHA-256 `45c76b46fba9daebcf5d0ebbedb7b5592d4eaa50cbbd4b5b59fe44321b7b8e18`.
Manufacturer [Smooth product](https://modernforms.com/product/smooth/)
and [FR-W2502 specification](https://modernforms.com/images/products/SPECSHEET_PDF/FR-W2502_SPSHT.pdf)
specify a **Soft Brass housing** with **Matte Black blades**, plus an
opal luminaire lens, for exact variant `SB/MB`.

The OEM native probe finds an unnamed family type (`" "`) with **no
material family-type parameters**. Thirteen `ImportInstance` elements,
IDs 2977, 2980, 2982, 2985–2989, 2990–2994, expose numeric import
subcategory names `0` through `20` and the same subcategory material ID
`2869`; their visible solid faces are unassigned. Those numeric layer names
cannot distinguish aluminum Soft Brass housing from Matte Black ABS blades.

Three `FreeFormElement` IDs **2997**, **2998**, **2999** have thin radial/
swept envelope sizes of approximately 403 × 590 × 50.9 mm, 405 × 589 × 50.9
mm, and 645 × 129 × 50.9 mm respectively. They are **blade-shaped
candidates**, but unnamed `Generic Models` with unassigned materials;
their geometry alone does not establish authoritative manufacturer
part identities. An 8-foot template/source `Extrusion` at element
**1537** contributes the 96-inch XY overall native probe bounds.
Do not conclude the *actual fan blade sweep* is 96 inches from that
unfiltered all-element AABB. A separate physical fan-only radial
diameter check is required before dimension approval.

**Release status: HOLD.** No Smooth recolor/conversion builder is prepared.
The OEM importer must be inspected for visual element grouping, part
identity, appearance inheritance and actual source geometry before
applying gold/black materials. Any material set at shared import layer
`2869` would change unrelated surfaces across 13 imports.
