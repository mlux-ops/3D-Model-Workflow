# MSI Soreno Ivory Matte 24x48 (NSORIVO2448): Revit colour, bump and model pattern

Project 25-012 651 Belmont, Primary Bath floor. Built 2026-09-26. Supersedes
`output/belmont_tiles/Soreno_Ivory_24x48/` (half offset, 490 x 240 px faces, V-Ray files).
No ADSKLIB, RVT or V-Ray output for this job (owner's choice).

## Delivered files (Google Drive: `Revit Material Maps - 25-012 651 Belmont`)

| File | Content |
|---|---|
| `MSI Soreno Ivory 24x48 - 11'-10.000in x 11'-10.500in.png` | Colour, 8-bit sRGB, 3408 x 3420 px |
| `MSI Soreno Ivory 24x48 - 11'-10.000in x 11'-10.500in - Bump 60.png` | Bump, 16-bit grey, same size and layout; white = high, 0 = grout floor |
| `MSI Soreno Ivory 24x48 - Model Pattern - 11'-10.000in x 11'-10.500in.pat` | Revit model fill patterns (horizontal = maps, vertical = rotated 90 deg) |

Sources in this package: `textures/Color.png` and `textures/Bump16.png` are the same bytes.

## Revit setup

- Colour: Appearance > Generic > Image. **Sample Size 11'-10" x 11'-10 1/2"** (142.00 x 142.50 in).
  Both are exact 1/4 in values, so the Texture Editor will not round them. Offset 0, rotation 0.
- Bump: Appearance > Bump > Image with the same Sample Size, offset and rotation. **Amount 60**
  (the editor's whole-number scale; stored value 0.60).
- Tiles run long side horizontal (along the image's width). For tiles running the other way, set
  rotation 90 deg on both maps and use the "Vertical" fill pattern.
- Fill pattern: Manage > Additional Settings > Fill Patterns > Model > New > Custom > Import the
  `.pat`, units inches, import scale 1.00. Choose `MSI Soreno Ivory 24x48 - 1-3 Bond Horizontal`
  (or `... Vertical`). The pattern origin is the maps' top-left corner, on a joint crossing.
  Move/align the surface pattern to a real joint once and the maps and pattern will line up.

## Product facts and the size decision

| Item | Value | Source |
|---|---|---|
| Nominal | 24 x 48 in, matte, glazed porcelain, rectified | MSI page, MSI Soreno flyer |
| Thickness | 3/8 in nominal; 0.39 in (10 mm) on dealer tables; 9.90 mm on Home Depot | flyer, villohome, wallandtile, HD |
| Origin | Italy | villohome spec table |
| **Actual face size** | **Not published** by MSI or any of 11 dealers checked | see ERRORS.md #6 |
| Used | **600 x 1200 mm = 23.622 x 47.244 in** | metric rectified convention for an Italian 24x48 with 10 mm body |
| Joint | **1/8 in** | MSI flyer: "1/8" Grout Size is recommended" |
| Layout | **1/3-offset running bond**, each row steps +1/3 module | flyer: "less than 33% staggered brick lay" is strongly recommended; owner accepted |
| Shade variation | flyer V4, MSI web page "Low" (conflict noted) | |

Drawn tile vs actual: **47.2083 x 23.625 in** drawn against 47.2441 x 23.6220 in actual
(-0.91 mm = -0.076 % on the length, +0.08 mm = +0.013 % on the width), joint kept at 1/8 in.
This gives a module of 47.3333 x 23.75 in, so 3 tiles x 6 rows is exactly 142.00 x 142.50 in. With the
actual size, the Sample Size would have been 142.107 x 142.482 in, which Revit would round.

## Atlas

- 3 tiles across x 6 rows = 18 tile faces; the 1/3 bond repeats every 3 rows. 24 px/in; the joint is 3 px.
- Horizontal joints are centred on y = k x 570 px; row r vertical joints on x = r x 378.667 + k x 1136 px.
  Half a joint lies on every image edge where a joint meets it, so both maps wrap in both directions.
- Grout colour **sRGB 200, 194, 184** (light warm grey, about 12 % darker than the tile field, which averages
  sRGB 232, 225, 216). Belmont's grout is unspecified. Rebuild the colour map with another grout:
  `python source/b01_build.py <suffix> R,G,B` writes `textures/Color_<suffix>.png` and asserts that the
  recomputed bump equals the delivered one byte for byte. The `offwhite` (214, 209, 199) variant was built as a test.

## Source faces (see SOURCE_SELECTION.md)

MSI publishes no face variations for Soreno Ivory. The NCC test shows that **every** face in every
published swatch (24x48, 24x24, paver, flyer, dealer copies, the old Belmont reference) is one of **2
independent printed faces**, A and B, some of them mirrored or rotated. A is available at 16.7 px/in
(from the 24x24 swatch halves); B at 16.7 px/in on its right half and 11.2 px/in on its left half.

The 18 atlas faces are **synthesised** from A and B by min-cut patch quilting (8 in patches, 2.5 in
overlap, 8 orientations, random choice among the 12 best-matching candidates, a usage penalty so no
source region is over-used). The 11.2 px/in half of B carries a 1.3x cost penalty. A planar luminance
trend of 0.8 to 9.9 % was removed per source region; clouds and veining were kept. Per-tile tone is
+/-1.5 % (log sigma): A and B differ by 1.0 % in luminance, and the MSI page states "Low" variation.
Measured non-repetition: max NCC between any two built faces **0.112** (median 0.061); max NCC of a built
face against source A or B **0.202**. Seed 2026092611.

## Relief (bump)

| Term | mm |
|---|---|
| Grout floor | 0 |
| Tile face above the grout floor (joint step) | 1.50 |
| Eased edge radius (height at the tile edge = 0.50) | 1.00 |
| Face micro-relief (band-limited noise, not from the print) | sd 0.028, bounded +/-0.10 (measured -0.092 to +0.092) |
| Full scale (65535) | 1.592 |
| Minimum face height outside the eased edge (clearance above the grout floor) | 1.408 |

Bump amount 60: the owner's calibration was 100 for a full-range 16-bit map of about 2.6 mm full scale.
That is about 38 per mm, so this 1.59 mm map at 60 has the same mm-per-unit as the calibrated case. The
1.5 mm joint then reads like the calibrated 1.6 mm joint at 100, which read well. The matte face stays
nearly flat, which suits a flat porcelain. For stronger joints, raise the value; do not go above about 100.

## Gates (textures/validation.json, from `source/b03_verify.py`, all PASS)

| Gate | Measured |
|---|---|
| IHDR | colour 8-bit type 2 RGB; bump 16-bit type 0 grey; both 3408 x 3420 |
| Aspect | pixel 0.996491 = physical 142.00/142.50 |
| Quarter inch | 142.00 and 142.50 in, both exact multiples of 0.25 |
| Joint width | horizontal mean 2.997 px (min 2.875, max 3.132); vertical mean 2.888 px (min 2.809, max 3.120); target 3.0 px = 1/8 in |
| 1/3 offset | row offsets 0 / 378.56 / 757.44 px vs 0 / 378.67 / 757.33 px; max centre error 0.117 px; 3 joints per row |
| Wrap | x edge/interior step ratio 0.97 (colour), 1.00 (bump) on rows where the edge crosses a face; top/bottom rows and row-0 edge columns 100 % grout |
| Distinct faces | max NCC 0.112 (threshold 0.5), 18 faces |
| Clearance | face min 1.408 mm, max 1.592 mm; grout core 0.000 mm |
| Colour/bump registration | 100 % of grout-core pixels carry the grout colour |
| Model pattern | both patterns: 312 joint runs matched, 0 unmatched, max offset 0.167 px, 100 % of the sampled line points on grout |

## Limitations

- The actual size is an evidence-based convention (600 x 1200 mm), not a published figure. If the delivered tile
  measures differently, rebuild with the measured size.
- Only 2 real faces exist in the published imagery. The 18 faces are recombinations of A and B, not new
  photographs, and the native detail is about 16.7 px/in (11.2 px/in in part of B). Delivering at 24 px/in adds no detail.
- The sources are MSI digital swatch renders, not scans.
- The micro-relief is procedural. The printed veining has no relief, as on the real matte tile.
- Not yet checked in Revit: Sample Size entry, bump response at 60, and the fill pattern import. Look at a
  rendered view with grazing light before relying on the bump value.

## Scripts (`source/`)

`a01_fetch.py` CDN probe; `a02_pdf_images.py` flyer images; `a03_thumbs.py` thumbnails; `a04_grid.py` joint grids;
`a05_dupes.py` NCC duplicate test; `a06_master.py` hi-res masters A/B; `b01_build.py` maps; `b02_previews.py`
previews; `b03_verify.py` independent gates; `e01_model_pattern.py` .pat and its analytic check;
`d01_package.py` notes zip; `d02_deliver.py` no-overwrite copy to the Drive mount; `guard.py` write guard.
