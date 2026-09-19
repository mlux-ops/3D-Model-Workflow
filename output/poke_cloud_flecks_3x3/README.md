# Poke — Cloud Flecks, Straight Joint 3x3 Matte (Terrazzo-look mosaic)

Scope: minimal Revit texture-map deliverable only — ONE color map, ONE bump map, and a
Sample Size. No ADSKLIB, RVT, V-Ray material, ZIP, or Drive upload was produced or attempted
(explicitly out of scope for this task). No Revit validation was performed.

## Source

- Product page: https://www.daltile.com/products/terrazzo-look/poke/cloud-flecks-straight-joint-3x3-matte
- **Accepted** reference image: `references/poke_cloud_flecks_3x3_DAL_PK20_3x3_Msc_CloudFlecks_MT_Silo_01.jpg`
  (`DAL_PK20_3x3_Msc_CloudFlecks_MT_Silo_01`, flat, straight-on 4x4 chip mosaic sheet, no
  scene, no perspective, no baked lighting), 3000 x 3000 px.
- Rejected candidates and reasons: see `SOURCE_SELECTION.md`. Built only from the flat
  straight-on Silo swatch, per WORKFLOW.md line 30 and the visual acceptance gate.
- `textures/_REVIEW_source_poke_cloud.jpg` — the exact swatch crop used.

## Product facts (sourced from the page, 2026-09-19)

- Nominal chip size: 3 x 3 in; Grout Joint Recommendation: 1/8 in -> actual chip
  2.875 x 2.875 in.
- Nominal Mounted Sheet Size: 12 x 12 in, Mount Method: Dot Mount — a 4 x 4 grid of 3 in
  chips per sheet, directly visible in the accepted Silo swatch.
- Mosaic Pattern: Straight Joint; Finish: Matte; Color: Cloud Flecks (white terrazzo-look
  field with black/grey/taupe flecks); Body Type: Glazed Mosaics.

## Sample Size rule (mandatory)

**The Sample Size equals the real-world extent of every chip shown in the image.** An 8x8
chip atlas of the 3 in nominal installed module (module = 2.875 in actual chip + 0.125 in
joint, matching the page's stated 1/8 in grout joint) was built — 8x8 is the minimum atlas
size specified for non-repetition. Image pixel aspect is 1:1, matching the 1:1 physical
aspect of an 8x8 square grid.

- Chips: **8 across x 8 down**, grid/stack bond, straight joint.
- Module (nominal, installed): 3 x 3 in = actual chip 2.875 x 2.875 in + joint 0.125 in.
- Sample Size = 8 x 3 in = 8 x 3 in = **24 x 24 in = 2'-0" x 2'-0"**.
- Image pixels: 2000 x 2000 (250 px per chip module), aspect 1:1 = matches 24:24 exactly.

## Deliverables (`textures/`)

- `poke_cloud_flecks_3x3_Color.png` — 2000x2000, 8-bit sRGB PNG (verified via PNG header:
  bit depth 8, colour type 2 / RGB).
- `poke_cloud_flecks_3x3_Bump16.png` — 2000x2000, 16-bit grayscale PNG (verified via PNG
  header: bit depth 16, colour type 0 / grayscale).
- `_PREVIEW_tiling_poke_cloud.jpg` — ILLUSTRATIVE 2x2 wrap/seam check of the whole 8x8 atlas.
- `_PREVIEW_grazing_light_poke_cloud.jpg` — ILLUSTRATIVE raking-light shaded preview.
- `_REVIEW_source_poke_cloud.jpg` — the accepted source swatch, for visual confirmation.
- `_REVIEW_chip_interiors.jpg` — contact sheet of the 16 extracted, joint-free chip
  interiors used to build the atlas.

The Silo swatch was cropped to its tile-face bounding box (removing the white photography
margin), then its own 4x4 chip grid was located precisely from per-row/per-column MEDIAN
luminance profiles (median is robust to individual dark/light flecks; only a true joint band
pulls a row/column's median down to the joint's flat grey level). The 16 chip interiors were
extracted with a safety margin inside each detected joint, so none of them contains any
fragment of the source sheet's own joint lines -- see `textures/_REVIEW_chip_interiors.jpg`,
a contact sheet of all 16 extracted interiors. The delivered 8x8 atlas is built only from
random-choice, random 90-degree rotation/flip, mild-tone-jitter copies of those 16
joint-free interiors, so no delivered chip can ever show a source joint fragment, and the
atlas is non-repeating (AGENTS.md 2026-09-17 seamless/non-repeating instruction) while every
chip still shows the same real product colourway. The delivered 1/8 in joint is drawn
procedurally, never copied from the photo. Tile is FLAT (matte terrazzo-look mosaic chip):
the bump map carries only subtle photo-derived surface micro-variation (+/- 0.06 of the 0..1
range) plus the grout-joint recess. No sculpted pattern/relief was added, since this product
has none.

## 2026-09-19 correction

The first build pass cropped random square regions from anywhere in the Silo swatch, so many
atlas chips accidentally straddled the source sheet's own 4x4 grid and showed faint fragments
of its joint lines inside a constructed chip face -- caught on review of
`_PREVIEW_tiling_poke_cloud.jpg`. Fixed as described above: detect the source grid precisely,
extract only joint-free chip interiors, and build the delivered atlas from those. See
`source/build_maps.py` (`find_joint_bands` / `segments_between_bands`) and
`source/build_report.json` (`grid_detection`) for the exact detected joint band pixel ranges.

## Bump amplitude / depth

- Working precision: float64 throughout; quantized only at final 16-bit export.
- Height full range: 0.35 mm (subtle, appropriate to a flat matte tile — same figure used
  for the same-line Poke Confetti Flecks 24x24 build).
- Grout floor: 0.10 of the 0..1 normalized range -> grout recess depth approx 0.315 mm.
- No pattern/flute component (not applicable to this flat product).

## What was inferred vs. sourced

- Sourced directly: nominal 3x3 in chip module, 12x12 in nominal mounted sheet (4x4 chips),
  Dot Mount, matte finish, straight-joint mosaic pattern, Cloud Flecks terrazzo-look
  coloring, 1/8 in grout joint recommendation — all from the product page.
- Inferred: exact micro-surface roughness/relief amplitude (0.35 mm range) is an estimate,
  not a measured value, since no manufacturer height spec or scan was available; the
  specific 64 crop regions used for the atlas chips are arbitrary (chosen for visual variety
  only).

## Limitations

- Built from a single marketing swatch photo; no orthographic reference or physical scan.
- No Revit validation was performed (out of scope for this task).
- The tiling/grazing previews are illustrative only, not rendered/native application checks.
