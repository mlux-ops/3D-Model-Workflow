# ELM Jute Vein-Cut 24x48 (stack bond): colour, bump and model pattern

ELM Surfaces ElmStone Jute Vein-Cut 24x48, matte porcelain, 8 mm. The same product is sold as MILE stone EcoStone
Vein-Cut Jute, SKU 1104304. Project 25-012 651 W. Belmont. The deliverable is the maps and the pattern only: no ADSKLIB,
RVT or V-Ray.

## Files (Belmont Revit Material Maps folder)

| file | what |
|---|---|
| `ELM Jute Vein-Cut 24x48 - 11'-10.000in x 11'-10.500in.png` | colour map, 8-bit sRGB, 5112 x 5130 px |
| `ELM Jute Vein-Cut 24x48 - 11'-10.000in x 11'-10.500in - Bump 60.png` | bump map, 16-bit grey, same pixels |
| `ELM Jute Vein-Cut 24x48 - Model Pattern - 11'-10.000in x 11'-10.500in.pat` | Revit model fill patterns |

## Revit settings

- **Sample Size, Image and Bump: 11'-10" x 11'-10 1/2"** (142.00 x 142.50 in). Both values are exact quarter inches.
- **Bump Amount: 60** (editor value).
- Layout of the maps: stack bond, long side horizontal, veins horizontal. 3 tiles across, 6 down.
- Model pattern `ELM Jute Vein-Cut 24x48 - Stack Horizontal` matches the maps.
- `... - Stack Vertical` is for tiles laid long side vertical; rotate both maps 90° to match it.
- Pattern origin = the maps' top-left corner, which is a joint-centre crossing. The first tile face starts 1/16 in right of and 1/16 in below the origin.

## Geometry

- Actual size is not published by ELM or MILE. Used 600 x 1200 mm = 23.622 x 47.244 in (Florim metric rectified convention). This is an assumption.
- Drawn tile 47.2083 x 23.625 in, to reach quarter-inch Sample Sizes: -0.91 mm / +0.08 mm against actual (-0.08 % / +0.01 %).
- Joint 1/8 in (assumption; no manufacturer recommendation is published). Module 47.3333 x 23.75 in.
- 36 px/in. Joint centrelines at x = k·1704 px and y = k·855 px, so a half joint lies on every image edge and the maps wrap exactly.
- Grout: warm light neutral, sRGB 208/198/180.

## Colour

The colour is 100 % real photo pixels: no synthesised veins or mottle. Six distinct printed faces were used
(see `SOURCE_SELECTION.md`):

- A: the ELM/MILE 24x48 swatch (u09).
- B: the second 24x48 face (old 05), re-toned to Jute from the MILE panel.
- W1 to W4: the four corners of the MILE 48x110 slab photo, re-toned to the swatch.

Each face is used 3 times, in different orientation-preserving flips (r0, flipH, flipV, r180; veins stay horizontal). Rows
0/2/4 and rows 1/3/5 use disjoint face groups, so no face touches itself, including across the wrap. Treatment:

- Only a first-order lighting gradient was removed from each face.
- Per-tile tone jitter sd 2 % (MILE: shade variation V3, moderate).
- Face mean 218/206/188, within 0.5 % of the swatch.

**Limitation:**

- Every real face appears three times per atlas, mirrored differently.
- The W faces share a 12 to 17 % corner area with face A.
- No further independent faces are published: all other MILE/ELM images are copies or crops of these, or low-res mock-ups.

## Bump (mm above the grout floor; full scale 1.600 mm)

| term | value |
|---|---|
| joint depth (face above grout floor) | 1.50 mm |
| eased edge | quarter-round, r = 1.0 mm |
| face micro-relief | photo-derived luminance band-pass, sd 0.027 mm, bounded ±0.10 mm (face 1.40 to 1.595 mm) |
| clearance (face minimum above the grout floor) | 1.40 mm |

The face is flat matte. The vein-cut face shows no ridges: spectral peak prominence 1.07 to 1.09, against 75.8 on the ridged
cross-cut. The bump amount of 60 follows the owner's calibration (100 for 2.6 mm), scaled to 1.6 mm, as for MSI Soreno.

## Rebuild or grout variant

```
python source/a07_faces.py
python source/b01_build_24x48.py
python source/e01_model_pattern.py veincut_24x48
python source/b03_verify.py veincut_24x48
python source/b01_build_24x48.py <suffix> R,G,B
```

The last command writes the colour map only, as `Color_<suffix>.png`, with the same seed. It raises if the bump would change.

## Verification

`validation.json`, written by `source/b03_verify.py`, re-derives every gate from the files; all 10 pass:

- ihdr, aspect, quarter_inch;
- joints: centre error 0, fitted width 4.500 px;
- wrap;
- distinct: 6 face clusters of 3, none touching, same-orientation NCC ≤ 0.13;
- veins: all cells within 1.1° of horizontal;
- clearance, colour_bump;
- model_pattern: 425 joint runs per pattern, max offset 0.0 px.

Not tested: a render inside Revit. Previews are `_PREVIEW_*.jpg` in this folder.
