# ELM Surfaces Formed Hexagon Tile in Sand: colour + bump atlas (high arm)

This is a seamless, non-repeating 8 × 7 hexagon atlas (56 faces) that mixes the three Formed face treatments: **Matte, Raw and Chiseled**. It was built only from the manufacturer layout render's pixels. The lifestyle image was used as a visual reference only.

| File | Format (checked from the PNG IHDR bytes) |
|---|---|
| `textures/Color.png` | 4489 × 4536, 8-bit RGB (sRGB) |
| `textures/Bump16.png` | 4489 × 4536, 16-bit greyscale; white is high |
| `textures/face_ids.png` | 4489 × 4536, 16-bit greyscale; 0 = joint, 1…56 = face index |
| `textures/report.json` | per-face type, rotation, mirror and source; mix, wrap steps, relief figures, checks |

## Revit setup

- **Sample Size 70.148 × 70.875 in** (5′-10 5/32″ × 5′-10 7/8″). Turn **Repeat on** in both directions.
- Use `Color.png` as the diffuse image and `Bump16.png` as the bump image, with the same sample size and no offset or rotation.
- **Suggested bump amount: 1.0.** This is a starting value only, **not verified in Revit** (this trial has no Revit). The map encodes a physical 1.65 mm range, and the joint is the deepest feature. If Raw and Chiseled read shallow in a render, raise the amount toward 1.5. Don't lower it below the point where the joint still reads.

## Size assumption

"10 × 10 hexagon" was read as **10.000 in across the flats** (11.547 in point to point), as the brief fixes it. A regular hexagon can't be 10 × 10. If ELM means 10 in point to point, every dimension scales by 0.866, and the Sample Size becomes 60.75 × 61.38 in with the same maps.

## Geometry

- Flat-top hexagons at 64 px/in on a torus: every pixel belongs to its nearest centre, so all maps wrap by construction.
- Face: 640 px across the flats. Joint: 1/8 in = **8 px**, measured as 8 px at all 24 sampled crossings on `face_ids.png`.
- The top and bottom image edges run along joint centrelines (4 px of joint on each edge).
- The left and right edges cut through faces, which continue on the opposite edge.
- Column pitch is W/8 = 561.125 px, against 561.18 px for an exact regular module. The resulting 0.05 px/column mismatch is below one pixel across the atlas.
- **Joint colour: RGB (206, 198, 184)**, a light warm grey. It is the darkest 20 % of core pixels on the render's drawn joint line.

## Method (`source/run_all.py` reruns everything; fixed seeds)

1. **Render measurement.**
   - The hex lattice was fitted to the render's grey joint lines: 31.10 px/in.
   - The 39 complete faces were classified as 22 Matte, 8 Raw and 9 Chiseled, confirmed on a contact sheet.
   - Same-type render faces were checked for duplication: the Raw faces are distinct (maximum NCC 0.22).
2. **Chiseled geometry, measured.**
   - One groove design with a **period of 5.05 mm (0.199 in)**, found at **90°, 150° and 30°**: the three hexagon rotations of one vertical groove pattern.
   - The cross-section profile was measured by folding each face over its demodulated phase.
   - The atlas re-evaluates that profile at 64 px/in on each source face's own local phase and amplitude, plus the source residual. The grooves stay crisp, and the chisel irregularity comes from source pixels.
3. **Raw height** comes from the render's own shading. All 8 Raw faces share one light axis. Their band-passed luminance is integrated along it; re-shading correlates with the source at r ≈ 0.70.
4. **Matte:** source colour and cloudiness. The bump carries fine grain only.
5. **Colour** is the render's pixels. High-frequency baked shading is partly reduced on Raw (75 % kept) and Chiseled (70 % kept), so faces can be rotated.
6. **Atlas faces.**
   - Every complete render face is used once as a "pure" face, resampled 31.1 → 64 px/in under one of the 12 hexagon symmetries.
   - The 3 extra Raw and 10 extra Matte faces are **mosaics** of 5 cells, taken from render faces at arbitrary rotations. Four rules apply:
     - no source is shared with the face or its neighbours;
     - each source pixel appears at most twice in the atlas, with a soft penalty;
     - every reuse sits at least 12° from all hexagon symmetries of the source's earlier appearances;
     - tone is cross-faded wide and detail is blended with variance-preserving weights.
   - The 4 extra Chiseled faces reuse sources at a different hexagon rotation, so each reuse shows a different groove orientation.
7. **Layout.** An annealed arrangement penalises same-type Raw and Chiseled neighbours, same-orientation Chiseled neighbours, and unbalanced rows or columns on the torus.

## Mix

| | Matte | Raw | Chiseled |
|---|---|---|---|
| Render, complete faces | 22 (56.4 %) | 8 (20.5 %) | 9 (23.1 %) |
| Atlas | 32 (57.1 %) | 11 (19.6 %) | 13 (23.2 %) |

Chiseled orientations are 90° / 150° / 30° = 3 / 4 / 2 in the render and **4 / 6 / 3** in the atlas.

## Relief (measured from Bump16.png; face plane = 0 mm; separate terms, no global multiplier)

| Term | Design | Measured in the map (face interior) |
|---|---|---|
| Matte grain | std 0.010 mm | std 0.0098 mm, range −0.035…+0.035 mm |
| Raw relief | 1.00 mm | p0.5–p99.5 = 0.99 mm; deepest −1.147 mm |
| Chiseled groove depth | 0.60 mm | p0.5–p99.5 = 0.60 mm; deepest −0.690 mm |
| Joint floor | −1.60 mm | median −1.600 mm (**joint depth 1.60 mm**) |
| **Clearance**, deepest pattern point to joint floor | > 0 | **0.453 mm** (Raw is the deepest) |

- Bump16 encodes −1.60 … +0.05 mm linearly as 0 … 65535, which is 2.52e-5 mm per code.
- An eased edge over the last 3 px of each face drops to the joint floor. It is excluded from the pattern figures.
- The depth values are design choices, because the sources give no absolute depth. They were judged against the lifestyle image's raking-light read, and the 0.60 mm Chiseled depth was reduced from an initial 0.80 mm.

## Seams and repetition

**Wrap.** The step across each image edge is compared with the same step at lattice-equivalent interior lines. A ratio near 1 means no seam.

| Map | Left/right ratio | Top/bottom ratio |
|---|---|---|
| Color.png | 1.066 (1.23 vs 1.15 levels) | 1.156 (0.75 vs 0.65) |
| Bump16.png | 1.049 (1151 vs 1097 codes) | 1.014 (404 vs 398) |

The corner review (`_REVIEW_wrap_seam.jpg`) and the 2 × 2 repeat (`_PREVIEW_wrap_2x2.jpg`) show continuous joints and no seam.

**Repetition** (`source/check_outputs.py`, results under `checks` in report.json):

- **Raw, whole face:** NCC over all 12 hexagon symmetries on the high-passed bump.
  - Maximum **0.041** (faces 25/34); median pair 0.025.
  - There are no repeated Raw faces.
- **Raw, patch search:** 66 random 64 × 64 px windows, FFT-NCC searched in every other Raw face under all 12 symmetries.
  - Maximum **0.797**, median best 0.555, 11 windows above 0.6.
  - All top hits (29↔10, 7↔10, 5↔37) are pure faces from *different* render faces, which the source check showed to be distinct. No shared pixels are involved.
  - For scale: before the symmetry-distance rule, a genuine copy scored 0.986.
  - The residual similarity is most likely the shared anisotropy of the Raw height, which was integrated along one light axis.
- **Matte, low-frequency colour (clouds), whole face:** maximum 0.687 (faces 4/49), median 0.382.
- **Chiseled, whole face:** maximum 0.991 (faces 18/38). This is one of the 4 deliberate reuses at a different hex rotation; the grooves repeat by design.

## Limitations

- **Resolution.** The only orthographic source is 31.1 px/in. Every face is upsampled 2.06× (bicubic), so fine grain in Color.png is soft at 1:1. Chiseled grooves stay crisp in the bump because the measured profile is re-evaluated at 64 px/in. They are softer in the colour map.
- **The source is a CG render,** not a photograph. Its Matte cloudiness, Raw relief and groove irregularity are the manufacturer's artwork. Raw height is inferred from rendered shading along one light axis. Detail running exactly along that axis is weakly recovered, and its sign (bump or pit) is not determinable. Webp compression blocks in the render appear as faint dots in the Matte grain under grazing light.
- **Depth values are not measured.** The Raw relief, Chiseled depth and joint depth are chosen values. Only the clearance and the per-type figures above are measured, from the map itself.
- **Reuse.**
  - Chiseled: 4 of 13 faces reuse a render face at a different hex rotation. The whole-face check over the 12 symmetries finds them, which the brief allows because the grooves repeat by design.
  - Mosaics: Matte and Raw mosaic faces reuse source pixels at non-symmetric rotations. The last few Matte mosaics exceeded the two-appearance target on part of their cell area.
- **Joint.** The render draws the joint thinner than 1/8 in and flat. The 1/8 in width and the 1.6 mm depth are from the brief and a design choice respectively.
- **Grazing preview.** It is Lambert shading plus ambient, with no cast shadows. It is not a Revit render. No Revit, ADSKLIB, V-Ray or Drive step was part of this trial.
- **Colour.** The Sand tone is the render's exposure (mean face RGB 244, 231, 207), with no colour calibration against a physical sample.
