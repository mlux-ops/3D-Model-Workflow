# ElmStone Jute Cross-Cut: non-repeating colour atlas (effort trial, high arm)

## What was built

- `textures/Color.png`: 9228 × 4620 px, 8-bit sRGB RGB PNG (no alpha, no ICC chunk). It holds 3 × 3 stacked 24 × 48 in tile faces at 64 px/in with 1/16 in (4 px) joints in sRGB (209, 209, 209).
- `textures/report.json` has every measurement quoted below, plus the source rectangle and transform for each of the 189 patches, listed per cell.
- Review images: `_PREVIEW_atlas_full.jpg`, `_PREVIEW_wrap_2x2.jpg`, `_REVIEW_wrap_seam.jpg` (the four-way wrap corner at 4× nearest-neighbour) and `_REVIEW_cell_grid.jpg`. I opened and inspected all of them, along with 1:1 and contrast-stretched crops of the atlas.
- `source/`: `run_all.py` runs `prep_sources.py`, then `validate_floor.py`, `build_atlas.py` and `review_atlas.py`. A full rebuild reproduced `Color.png` byte for byte (SHA-256 `b17c0be5…59ff3a`, same hash on both runs). Intermediates go to `_work/`.

## Revit

- **Sample Size: 144.1875 in × 72.1875 in** (12′-0 3/16″ × 6′-0 3/16″), which is 3 × (48 + 1/16) by 3 × (24 + 1/16).
- Offset 0/0. The atlas edge bisects a joint (2 px of joint on each edge), so every tile boundary, including the wrap, gets a full 4 px joint.

## Scale assumptions

- **Swatch:** per the brief, I took it to span 48 in, so 2000 px / 48 in = 41.67 px/in, and assumed the same scale vertically (875 px ≈ 21 in of the 24 in face). It was resampled by ×1.536 with Lanczos to 3072 × 1344 px at 64 px/in. I did not tile any native pixels unscaled.
- **Floor photo:** the across scale comes from the measured 24 in tile width, and the forward scale from texture isotropy (see below).
- **Cross-check, not fully consistent:** the autocorrelation half-width of the stone mottle is 1.31 in on the rectified floor and 1.44–1.56 in on the swatch at 41.67 px/in. Taken at face value, the swatch detail may sit about 10–19 % larger than on the installed floor. That is within the uncertainty of the method, so I kept the brief's assumption. It is recorded as an open scale uncertainty.

## Method

1. **Swatch clean-up.** The swatch carries a strictly periodic horizontal line pattern: period 3.77 px, amplitude about 2.1 code values on row means. That pattern is not stone. I removed it with a narrow Gaussian notch at 0.2651 cycles/px vertical, which cut the row-mean oscillation from 2.14 to 0.39. After resampling I removed a least-squares linear illumination plane per channel. No other tone change was made to the swatch.
2. **Floor perspective correction** (`prep_sources.py`, `validate_floor.py`):
   - I fitted the five vertical joints by a line search for minimum darkness, and the horizontal joint at y = 261.
   - All joint lines meet at one vanishing point, (1142.5, −935.4) ±1 px. The joint spacing is linear in the row (387.75 + 0.4145·y), which gives the horizon.
   - Model: a ground-plane mapping with X = (x − x_v)·H/(y − y_h), where H = 24/0.4145 comes from the 24 in tile width, and Z = F/(y − y_h) + const.
   - I chose F = 160 000 px·in so the stone's spectral energy is isotropic (Ex/Ey = 0.98; 0.79 at F = 120k, 1.11 at F = 180k). Cross-cut stone has no direction.
   - **Validation:**
     - Re-detected joints in the rectified image are straight and vertical: 0.000 in deviation across 10 bands of 4 in each, at 1/16 in sampling.
     - Joint spacings are 23.94, 24.06 and 23.94 in.
     - The visible depth above the horizontal joint comes out at 34.8 in, which is less than the 48 in tile length. That fits the fact that no second joint is visible.
     - The rectified image (`_work/floor_rectified_check.jpg`) shows square, straight joints.
   - F carries roughly ±20 % uncertainty.
3. **Decision on the floor photo:**
   - After rectification, its native resolution is only 16–22 px/in across and 5.6–10.3 px/in forward. At 64 px/in it needs 3–11× anisotropic upsampling, and a 1:1 comparison (`_work/cmp_64ppi.png`) showed obvious smearing.
   - Using its pixels would fail the no-smearing/stretching gate, so **Color.png contains swatch pixels only**. The floor photo was used for the perspective and scale validation above.
   - A tone-matched version of it is prepared (`src_floor*.npy`) but not used.
4. **Quilting** (`build_atlas.py`):
   - Each of the 9 faces is built independently from 21 patches: 640 px (10 in) square, with 160 px overlaps.
   - Patches are cut from the 64 px/in swatch under the 8 dihedral transforms. This is valid because cross-cut has no direction, and the striation removal means rotated patches do not give themselves away.
   - Candidates are scored by overlap SSD, computed with FFT at ¼ scale. On top of that are three penalties:
     - global usage of that source region;
     - heavier usage within the same cell;
     - extra weight on rare flakes (more than 3σ from their surroundings).
   - A seeded random pick is made from the best 4 candidates.
   - Patches are joined along minimum-error boundary cuts with a σ = 1.5 px feather. No pixel is synthesized, and no two regions are cross-faded beyond that feather.
5. Joints are drawn as exact (209, 209, 209). The faces are independent tiles, so the wrap lands joint to joint.

## Gate measurements (from `report.json`)

| Gate | Result |
|---|---|
| Format | 9228 × 4620, RGB, 8-bit PNG |
| Joint | 166 032 joint pixels, all exactly (209, 209, 209); 4 px wide (2 + 2 at the wrap); 0 face pixels equal to the joint colour |
| Wrap step, L/R and T/B (last column/row vs first) | 0.00 / 0.00. Interior face neighbour step: 2.38 horizontal, 2.39 vertical |
| Face-to-face step across the wrap joint vs across interior joints | L/R 5.66 vs 6.15; T/B 5.93 vs 6.16 |
| Face mean values | 235.9–236.3 across all 9 cells, so no tonal jump in the repeat |
| Cross-cell similarity (whole-face NCC, including flips and 180°) | max 0.125 (r0c2 vs r1c2) |
| 5 in block repeat search (54 random blocks, 8 variants, all other faces) | median best match 0.77; 15/54 above 0.90 |

## Honest limitations

- **Small-scale reuse is unavoidable with one swatch.** One face (1152 in²) is larger than the whole swatch (≈1008 in²), and the atlas needs about 9–10× the swatch area. Every source region therefore appears several times, in different orientations and with different neighbours.
  - Whole cells do not correlate (max NCC 0.125), and I found no repeated block at preview scale.
  - A 5 in block search does find exact local matches in other cells (15/54 above 0.9).
  - A few distinctive small bright flakes recur about 9–12 times across the 9 faces, never in the same orientation next to each other. A viewer hunting for them can find them.
- **Large-scale structure:** 10 in patches make the faces slightly busier and more even-toned than the original swatch, which has larger calm cloud areas.
- **Floor pixels are not used** because of their resolution (see Method 3). The atlas therefore reflects only the swatch's colour, which is warmer and lighter than the floor photo's lighting.
- **Swatch assumptions:** the 48 in span is the brief's assumption. The floor cross-check suggests the swatch features may be 10–19 % large, and this is unresolved. The notch filter attenuates stone content within ±0.0035 cycles/px of the artifact frequency. That is negligible visually, but it is a modification.
- **Not validated:** I did not validate in Revit or any renderer (out of scope for this trial). I made no bump, roughness, ADSKLIB or V-Ray files and did no Drive upload, per the brief.
