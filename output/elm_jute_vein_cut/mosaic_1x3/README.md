# ELM Jute Vein-Cut 1x3 mosaic (straight stack): colour, bump and model pattern

ELM Surfaces ElmStone Jute Vein-Cut 1x3 mosaic on a 12x12 sheet, matte porcelain, 8 mm. The same product is sold as MILE
stone EcoStone 1x3 Vein-Cut Jute, SKU 1104340. Project 25-012 651 W. Belmont. The deliverable is the maps and the pattern
only.

## Files (Belmont Revit Material Maps folder)

| file | what |
|---|---|
| `ELM Jute Vein-Cut 1x3 Mosaic - 4'-0.000in x 4'-0.000in.png` | colour map, 8-bit sRGB, 2304 x 2304 px |
| `ELM Jute Vein-Cut 1x3 Mosaic - 4'-0.000in x 4'-0.000in - Bump 50.png` | bump map, 16-bit grey, same pixels |
| `ELM Jute Vein-Cut 1x3 Mosaic - Model Pattern - 4'-0.000in x 4'-0.000in.pat` | Revit model fill patterns |

## Revit settings

- **Sample Size, Image and Bump: 4'-0" x 4'-0"** (48.00 x 48.00 in).
- **Bump Amount: 50** (editor value).
- Layout: straight stack, chips long side horizontal, columns aligned, veins horizontal. The MILE sheet photo, the MILE wall render and the user's photo u11 all show this.
- Model pattern `ELM Jute Vein-Cut 1x3 Mosaic - Stack Horizontal` matches the maps.
- `... - Stack Vertical` is the 90° layout; rotate both maps to match it.
- Origin = the maps' top-left corner, a joint-centre crossing. The first chip face starts 1/32 in right of and 1/32 in below the origin.

## Geometry

- Chip pitch 3 x 1 in: 4 x 12 chips on the nominal 12 x 12 sheet. The pitch ratio measured on the MILE sheet is 2.99.
- Joint 1/16 in, measured at about 0.06 in on the MILE sheet (FWHM 2.07 px at 34.5 px/in) and at 0.076 in on u11.
- Actual chip size and joint are not published. Chip drawn 2.9375 x 0.9375 in (assumption from the measurements).
- The joints between sheets are the same 1/16 in as the joints between chips, so sheet boundaries are invisible.
- Atlas: 16 x 48 chips = 4 x 4 sheets = 48 x 48 in, at 48 px/in. Module 144 x 48 px, joint 3 px. Joints lie on the image edges, so the map wraps exactly.
- Grout sRGB 208/198/180, the same as the 24x48.

## Colour

The colour is 100 % real photo pixels.

- **Chips:** 768 distinct, non-overlapping crops of real vein-cut faces, checked with occupancy masks: 137 from A (u09), 137 from B (old 05, re-toned), and 494 from the MILE 48x110 slab, whose copy of A is excluded.
- **Orientation:** each crop in one of 4 orientation-preserving flips, so the veins stay horizontal.
- **Chip tone:** per-chip jitter is calibrated to the user's photo. u11 has a local chip-tone sd of 0.087 (log); the crops themselves carry 0.038; the jitter adds sd 0.078, giving 0.088 in total.
- **Arrangement:** chips are re-ordered on the grid, which halves the low-frequency light/dark clustering, so no landmark blob repeats with the atlas.
- **Verification:** the largest chip-to-chip NCC is 0.51 (median 0.13, 4 orientations, ±1 px shifts). No chip crop is reused.

## Bump (mm above the grout floor; full scale 1.300 mm)

| term | value |
|---|---|
| joint depth (face above grout floor) | 1.20 mm |
| eased edge | quarter-round, r = 0.6 mm |
| face micro-relief | photo-derived luminance band-pass, sd 0.027 mm, bounded ±0.10 mm (face 1.10 to 1.298 mm) |
| clearance | 1.10 mm |

The face is flat matte, with no ridges (see SOURCE_SELECTION.md). The bump amount of 50 = the owner's 100-per-2.6 mm
calibration scaled to 1.3 mm full scale.

## Rebuild or grout variant

```
python source/a08_mosaic_sources.py
python source/b11_build_mosaic.py
python source/e01_model_pattern.py mosaic_1x3
python source/b03_verify.py mosaic_1x3
python source/b11_build_mosaic.py <suffix> R,G,B
```

The last command writes the colour map only; the bump must stay byte-identical.

## Verification

`validation.json`: all 10 gates pass.

- joints: fitted width 3.000 px on all 16 + 48 lines; the sheet-boundary joints are the same.
- wrap: passes.
- distinct: passes.
- veins: within 2.4° of horizontal.
- model_pattern: 3720 runs per pattern, max offset 0.0 px.

Not tested: a render inside Revit.
