# ElmStone Jute cross-cut: non-repeating colour atlas (xhigh run)

A seamless 3 × 3 panel colour atlas for Revit, built only from the two supplied photos. It is a test run: there are no bump, normal or roughness maps, no ADSKLIB, no V-Ray output and no Drive upload.

## Deliverables

| File | What it is |
|---|---|
| `textures/Color.png` | 9228 × 4620 px, 8-bit RGB PNG (sRGB ICC embedded), 64 px/in. 3 × 3 panels of 24 × 48 in tile laid long side horizontal, with a 1/16 in joint in sRGB (209, 209, 209). |
| `textures/report.json` | Gate measurements (format, joints, wrap steps, internal seams, cross-cell similarity, repetition), perspective validation, and every block's source and transform, per cell. |
| `textures/_provenance.json` | The raw build record that `report.json` summarises. |
| `textures/_PREVIEW_atlas_full.jpg` | The whole atlas at 1/3 scale. |
| `textures/_PREVIEW_wrap_2x2.jpg` | A 2 × 2 repeat at 1/6 scale. |
| `textures/_REVIEW_wrap_seam.jpg` | The four-way wrap corner: 1:1 on the left, 8× magnified on the right. |
| `textures/_REVIEW_cell_grid.jpg` | All 9 cells, labelled with how many blocks each takes from each source. |
| `textures/_REVIEW_floor_rectified.jpg`, `textures/_floor_validation.json` | Evidence for the perspective correction. |
| `source/` | Build scripts (below). |
| `ERRORS.md` | Every error and failed check hit during the run, with fix and status. |

## Revit setup

- **Sample Size: 144.1875 in wide × 72.1875 in high** (12′-0 3/16″ × 6′-0 3/16″). Keep aspect locked.
- Each panel repeat is 48.0625 × 24.0625 in: 3076 × 1540 px, 3072 × 1536 px of stone plus a 4 px joint.
- The image edges fall on joint centre lines, with 2 px of joint on each edge. When the texture tiles, the wrap joint is a full 4 px, like every interior joint. To register the texture joints to modelled tile edges, offset the texture origin to a joint centre line.

## Scale assumptions

- **Swatch** (`crosscut_swatch.webp`, 2000 × 875 px): taken to span the full 48 in panel length, as the brief says. That gives **41.667 px/in**, so the swatch covers 48 × 21 in. It was Lanczos-resampled once by ×1.536 to 3072 × 1344 px (64 px/in).
- **Floor photo** (`crosscut_floor_angled.jpg`, 2000 × 349 px): tiles are laid long side into the depth. The across-floor joint pitch is 24.0625 in: 24 in tile plus 1/16 in joint, measured to joint centres. The floor content is resampled straight from the photo pixels onto the floor plane at 64 px/in, in one interpolation step.
- **Real resolution of the floor photo** once projected onto the floor: 16.4–22.1 px/in across the floor and only **5.3–9.7 px/in into the depth**. At 64 px/in the floor content is therefore up-sampled 3–4× across and 7–12× in depth. See the limitations section.

## Perspective correction: method and validation

The floor photo is a pure-pitch view:

- The five depth joints fit straight lines with 0.15–0.34 px RMS and no measurable curvature, so there is no lens distortion to correct.
- All five lines meet at one vanishing point, (1142.6, −934.7) px, within 0.5 px.
- Joint spacing divided by distance from the horizon is constant to 0.2 %, so there is no yaw.
- The only cross joint is level at y = 260.5 px, measured on both halves of the image, so there is no roll.

For that geometry the plane mapping is `X = K·(x − x_vp)/u` and `Z = α·(1/u − 1/u_joint)`, with `u = y − y_vp`:

- **K = 58.02 in** is fixed by the joint pitch.
- **α** is the camera height ÷ focal length term. It can't be read from joints, because only one cross joint is in frame. It was measured from texture isotropy instead. Cross-cut stone has no directional veining; the swatch's band-passed gradient-energy ratio gy²/gx² is 1.03. α was solved so the rectified floor texture has the same ratio, over 2 bands × 6 independent regions (far row, near row, 4 tile columns) × 2 targets (the swatch ratio and 1.0): 24 estimates. The median is **α = 169,046**, with a spread of 146,922–202,928.

Validation, all of it measured (`_floor_validation.json`):

1. **Joint spacing.** Rectified depth joints measured in 1 in bands sit 24.026, 24.123, 24.026 and 24.094 in apart. The worst error against 24.0625 in is 0.060 in.
2. **Straightness.** The joints are straight and parallel to 0.007 in (the largest per-joint standard deviation over the full depth).
3. **Cross joint.** It lands at Z = −0.02 to −0.05 in in all four columns.
4. **Depth.** The visible far-row depth comes out at 39.4 in. That is less than the 48 in tile length, which fits the fact that no second cross joint is in frame. This check is independent of the isotropy calibration.
5. **Camera.** The implied camera is plausible: a focal length of about 2,910 px, which is about a 38° horizontal field of view over the 2000 px frame, and a camera height of about 58 in × cos(pitch).
6. **Visual.** `_REVIEW_floor_rectified.jpg` shows the ideal 24.0625 in grid and Z = 0 line landing on the photographed joints. The stone reads isotropic.

## Method (`source/`)

Run `python calibrate_floor.py`, then `python build_atlas.py`, then `python validate_floor.py` and `python review_atlas.py`. `floor_geom.py` holds the plane geometry. The build is deterministic (seed 20260925): re-running `build_atlas.py` reproduces `Color.png` byte-for-byte (the hash check is recorded in the final section).

1. **Tone normalisation** (gentle tone and warmth adjustment only):
   - Lighting is flattened at a 10 in scale. On the swatch this is a no-op (its lighting field varies by ±0.6 levels). On the floor photo it removes a 29-level lighting gradient.
   - Floor contrast is scaled per channel by 0.61 / 0.68 / 0.72 (R/G/B), so that its 0.15–1.5 in band contrast matches the manufacturer swatch.
   - The target mean colour is the swatch mean, sRGB (243.9, 238.8, 225.2).
2. **Floor preparation.** A 0.7 px pre-filter suppresses JPEG 8×8 block edges before they are magnified. A row-dependent horizontal blur of 0.5·√(r² − 1) source px (r = across/depth resolution ratio) halves the resolution anisotropy, so floor content doesn't read as streaked. Joints (with 0.4 in clearance), the two cast shadows and the frame are masked out.
3. **Quilting.** Each 48 × 24 in face is 5 × 3 blocks of 10.75 × 8.75 in, overlapping by 1.44 in and 1.13 in. Blocks are chosen at 8 px/in by overlap SSD plus penalties for:
   - reuse (linear and convex, weighted by how distinctive the source area is),
   - area already shared with each earlier face (convex, which spreads sharing across face pairs),
   - reusing an orientation,
   - switching source,
   - far-row softness.

   Hard rules: no source area twice in one face, no reuse in the same orientation, and no reuse that would sit within 10 in of a flip-mirror of its earlier copy. That last rule prevents book-matched repeats and keeps whole-cell correlation low. All 8 quarter-turn and flip orientations are allowed, because cross-cut has no direction. Of the 135 blocks, 27 are swatch and 108 are floor; 14 of the swatch blocks are quarter-turned.
4. **Compositing at 64 px/in.** Minimum-error dynamic-programming seams run through each overlap, with a 3 px feather. There is no wide cross-fade, so no ghosting or double exposure.
5. **Grain band.** Floor blocks, and swatch blocks that are quarter-turned, keep their own structure above about 0.06 in (σ = 3.8 px). Their sub-0.06 in grain band comes from a bland swatch window (low crack-edge energy, 30th percentile), flipped at random. The floor photo resolves nothing that fine, and the swatch's own grain carries a horizontal striation (below) that must not be turned.
6. **Striation.** The swatch carries a perfectly periodic horizontal line pattern: period 3.77 px native, 5.79 px (0.090 in) at 64 px/in, amplitude about 3 levels, and the same phase across the whole photo. It was kept as-is, because removing it is not an allowed operation, and phase-aligned inside each block row so it runs continuously across vertical seams. Each block row takes its own phase, and the phase changes only inside horizontal seams, where the lines run parallel to the seam. A 174° jump is invisible at 1:1 and 3×. The 27 row phases were optimised so the grating shared by every cell doesn't correlate whole cells: worst stripe correlation 0.365, against 0.96 with one phase per cell.
7. **Joints.** 4 px of exact (209, 209, 209) between faces; the atlas edges are joint centre lines.

## Gate results (measured, `textures/report.json`)

| Gate | Result |
|---|---|
| 1. Photographic only | Every stone pixel is resampled, flipped or rotated content from the two photos, or a narrow seam blend of such content. Tone changes are per-channel gain and offset plus low-frequency lighting flattening. No noise, vein, cloud or pattern generator is used anywhere. The disclosed exception is the band-limited grain transfer in step 5. |
| 2. Perspective | Pass. Rectified joint spacing error ≤ 0.060 in; joint straightness ≤ 0.007 in; cross joint at Z ≤ 0.05 in. The depth scale comes from isotropy with a ±15 % spread (see limitations). |
| 3. Seamless | Pass. Wrap steps **L/R 0.00** and **T/B 0.00** (mean abs RGB, edge column/row against opposite edge; both are joint centre line), against typical interior neighbour steps of median 2.16 (x) and 2.94 (y). Stone across the wrap joint differs by 5.8 (L/R) and 6.2 (T/B), against 5.9–6.3 across interior joints. Stone-to-joint contrast is 27.6 at the wrap and 26.4 inside. Overlap bands where the DP seams run carry 1.00× (x) and 0.98× (y) the step energy of the rest of each face. |
| 4. Non-repeating | Max whole-cell NCC (36 pairs × {none, flipH, flipV, rot180}): **0.124** at full resolution, 0.202 including the identical joint frame, 0.138 at ¼ resolution, 0.165 at 8 px/in. No same-orientation, same-face or flip-aligned reuse. Visual review of the cell grid, full preview, 2 × 2 repeat and 1:1 crops found no recognisable repeated block or landmark, no ghosting, and no visible seam. |
| 5. Scale | Pass. 64 px/in. Swatch ×1.536 from 41.667 px/in; floor resampled from its measured plane geometry. No native pixels tiled unscaled. |
| 6. Format | Pass. 9228 × 4620, 8-bit, colour type 2 (RGB), no alpha. All 166,032 joint pixels exactly (209, 209, 209); joints 4 px wide everywhere in a 2× tiling; no stone pixel equals the joint colour. |

## Limitations (honest)

- **Source area is short, so content is reused.** The two photos hold about 4.6 faces of usable real stone: the 48 × 21 in swatch plus about 4,300 in² of floor. The atlas needs 9 faces. On average every used source pixel appears **2.5 times** (at most 6), each time in a different orientation and position. On average a face pair shares 326 in² of source footprint, at most 494 in² (43 % of a face). Local 6 in windows reappear in another cell, rotated or flipped, at NCC up to 0.92. Hard rules keep reuse out of the same orientation, the same face and flip-aligned positions. It is still reuse: a finite 12 ft × 6 ft atlas of this product is not non-repeating in a mathematical sense, and the whole atlas repeats every 144.1875 × 72.1875 in.
- **Floor-derived content is softer than the swatch.** 108 of 135 blocks come from the floor photo, which resolves only 5–10 px/in into the depth and 16–22 across. Its crack edges and plate outlines are visibly softer at 1:1 than swatch-derived areas. At the full-atlas preview scale (about 21 px/in) the difference is slight.
- **The grain is borrowed.** In floor-derived and quarter-turned swatch pixels, the sub-0.06 in grain band is real swatch grain taken from a different location. That makes those pixels a band-limited blend of two real photo regions. It is not generated, but it is not literally that spot's own grain either.
- **The depth scale is estimated.** Across-floor scale is fixed by the joints to within 0.06 in per tile. Depth scale comes from texture isotropy and spans ±15 % across estimates, so floor features may be up to about 15 % stretched or squashed in one direction.
- **The striation may be an artifact.** Its perfect periodicity and constant phase suggest it may come from the manufacturer's imaging, not the tile surface. It was preserved and phase-managed, not removed. At the atlas's full-res scale it adds a fixed 0.09 in line texture.
- **Tone has been evened out.** Lighting was flattened at 10 in and floor contrast was reduced by about 30–40 % to match the swatch. All nine faces have the same mean colour, so any real tile-to-tile shade variation (V-rating) is not represented. A mild shared large-scale pattern remains (face edges about 0.4 levels rms darker on average). It is the main reason whole-cell NCC rises to 0.165 at 8 px/in.
- **The joint is flat.** It is a 4 px flat 209-grey line, with no bevel, shadow or highlight.
- **Not tested in Revit.** No Revit or rendered check was run (out of scope for this trial). The visual review was done on the preview images and 1:1 crops only.

## Reproducibility

The atlas was rebuilt from scratch with `python build_atlas.py` and compared by hash: identical. `Color.png` SHA-256 is `1427c95b5e515a7a5d1f132222c7cca88bbe79f22b77b02fdc3bc55da31d8827` before and after. The build takes about 3 minutes on this machine and needs Python 3 with numpy, scipy and Pillow.
