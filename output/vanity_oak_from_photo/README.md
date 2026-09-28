# Vanity Oak colour map (from the supplied product photo), 25-012 651 W. Belmont

This is a colour map only: an 8-bit sRGB PNG. There is no bump map, ADSKLIB or .pat, because none was requested and the material is wood, not tile.

| Item | Value |
|---|---|
| Delivered map | `Vanity Oak - 4'-0.000in x 2'-0.000in.png` in `Revit Material Maps - 25-012 651 Belmont` |
| Pixels | 3072 x 1536, 8-bit RGB (PNG colour type 2) |
| Real-world size | 48 in x 24 in, at exactly 64 px/in |
| Grain | Horizontal, along the 48 in width |
| Repeats inside the map | None. Every output pixel is a different source pixel; the provenance check proves it |
| Wrap | Seamless on both axes, so larger surfaces can tile it |

## Revit setup

1. Material Browser: duplicate a wood material, then go to Appearance > Generic > Image and pick the PNG.
2. In the Texture Editor, set Sample Size to Width **4'-0"** and Height **2'-0"**. Both are exact quarter inches, so Revit will not round them. Leave Offset at 0 and 0.
3. Rotation:
   - **0°** for horizontal-grain pieces: drawer fronts, the top apron, the bottom rail, and the 3'-1" x 7 1/2" panel.
   - **90°** for vertical-grain pieces: doors and side panels.
   - Rotation belongs to the material, not the element. For both grain directions you need two materials with the same image, for example `Vanity Oak - Horiz` (0°) and `Vanity Oak - Vert` (90°).
4. Rotated 90°, a vertical-grain piece up to 24 in wide and 48 in tall is covered by one map with no repeat. Horizontally, a piece up to 48 in long and 24 in tall is covered. The largest panel, 37 x 7.5 in, fits with margin.
5. Neighbouring pieces: Revit maps each face from its own origin, so identical drawer fronts will show the same part of the map. If adjacent pieces should look different, duplicate the material and give each copy its own Offset (for example 0/0, 11"/5", 23"/13", 31"/9"). The map has 48 x 24 in of distinct content to draw from.
6. No bump is supplied. The grain in the photo is too fine and too soft to give a trustworthy relief map. If you want some, keep it very low.

## Scale basis and assumptions

- **Vanity width: 48 in, assumed.** A web search did not identify the product. The photo matches the "48 in class" brief.
  - The reveal geometry is internally consistent. With the front fitted as a plane, the door and drawer columns come out symmetric to 0.2 %, and left and right drawer heights agree to 0.05 in.
  - Cross-check that conflicts: at 48 in, the overall height (counter to floor) works out to about 38–40 in, which is tall for a vanity. A standard 34.5–36 in height would imply the vanity is about 42–44 in wide.
  - If you know it is a 42 in unit, the grain in this map is drawn about 14 % too large. You can correct that without a new file by setting Sample Size to **3'-6" x 1'-9"**, which is also exact quarter inches.
- Measured on the front plane at 48 in: front frame 43.02 x 28.33 in inside the reveals, corner posts about 2.5 in each, doors 10.74 x 28.33 in, drawer fronts 10.73 x 9.45 in, apron and bottom rail 43.0 x 2.7 in.
- **Density:**
  - Native on the front panels: 23.1–25.9 px/in (right side lower, because it is farther from the camera).
  - Rectified and assembled at 32 px/in.
  - Delivered at **64 px/in** by one 2x upscale at the end: cubic B-spline interpolation, periodic boundary, in float64 sRGB, then a mild unsharp mask along the across-grain axis only (sigma 1.4 px, amount 0.45).
  - The upscale makes the map smoother under magnification. It adds no detail: the real grain detail is what about 24 px/in of photo holds. No noise or synthetic grain was added.

## How it was built (photo pixels only)

1. **Geometry.** Every reveal line was fitted (rms 0.06–0.5 px) and intersected into panel quads. The front-plane homography was fitted from the frame corners, and each panel rectified to 32 px/in inside the reveals (0.2–0.3 in inset). Doors were rotated 90° so all grain runs horizontally.
2. **De-lighting.** These steps remove shading only:
   - removed a neutral specular veil from `drawer_R1`, `drawer_R2` and the apron (fitted from their chromaticity and confirmed on the second chroma ratio);
   - removed the front-wide lighting plane;
   - removed each crop's quadratic luminance and chroma gradients;
   - flattened the along-grain profile (reveal fall-off);
   - flattened each row along the grain for the two long rails.
   The tone differences between leaves are kept.
3. **Assembly.** Six full-length leaves are stacked across the grain: apron | left door | left-door remainder | bottom rail | right door | right-door remainder. The last leaf wraps onto the first.
   - Each leaf is extended along the grain with real drawer pieces and strips from the same side of the vanity.
   - For every end joint, the candidate is shifted across (and along) the grain to the offset that best continues the grain already placed, then cut on a minimum-error boundary.
   - The loop-closing piece is cut against both neighbours, which is also what makes the horizontal wrap.
   - Leaves meet along the grain on minimum-error cuts in 5 px overlaps. The joint that closes the vertical wrap is cut the same way, and its path closes around the horizontal wrap.
   - Tone: pieces within a leaf are matched to the leaf. Between leaves, 20–40 % of the natural tone difference is kept.
   - Per-piece grain contrast is matched to the leaf (a detail gain of 0.77–1.40, which scales only existing detail).
   - The whole map is matched to the photo's mid-panel oak tone, sRGB (166, 138, 102).
4. **Checks.** See `validation.json`, which `source/b04_verify.py` re-derives from the file on disk:

| Gate | Result |
|---|---|
| IHDR | pass |
| Quarter-inch Sample Size | pass |
| Aspect | pass |
| Wrap x, wrap step / median interior step | 0.92 |
| Wrap y, wrap step / median interior step | 1.18 (limit 1.25) |
| Self-similarity, max NCC | 0.28 < 0.50 (planted-copy self-test 1.00; the source photo's own window-to-window baseline is 0.26) |
| Grain angle | +0.5° over the whole map; blocks −1.8° to +3.5° |
| Tone drift | along-grain 0.5 %, gradient harmonics ≤ 0.6 %, leaf-to-leaf 3.7 % |

## Limitations (disclosed, not failures)

- The source is one 1600 px product photo, so the grain is soft at close range compared with a real veneer scan. The right-hand drawers and the bottom-right drawer are the softest.
- Leaf joints (along the grain) are visible as subtle tone and figure changes, as in real veneer. At 1:1, some end joints show as a slight change in figure character where a drawer piece meets a door leaf. No hard lines, ghosting or repeats were found in the previews.
- A finite bitmap is periodic. Beyond 48 x 24 in, the map repeats by design.
- The rendered look in Revit has not been checked. That is pending your review in the model.

## Package contents

This notes package holds `README.md`, `SOURCE_SELECTION.md`, `ERRORS.md`, `validation.json`, the `_PREVIEW_*` images (all 800 px or smaller), `source/*.py` (guard, measure, rectify, dupes, de-light, build, upscale, previews, verify, package, deliver), the `_work/*.json` records, and the supplied reference photo. The colour map itself is only in the Belmont maps folder.
