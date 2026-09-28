# Source selection — ELM Formed Hexagon Tile in Sand

Only two images of this tile exist, both supplied in `../inputs/`. The atlas's colour and relief pixels come from the layout render alone. The lifestyle image was used for measurements, cross-checks and calibration only. None of its pixels are in any map.

| File | Pixels | View | Decision |
|---|---|---|---|
| `elm_formed_hex_sand_layout_render.webp` | 2000 x 1888 | Manufacturer CG layout render, straight-on, orthographic | **Accepted.** The source of all geometry, the face-type mix, the joint colour and every organic pixel in the atlas |
| `elm_formed_hex_sand_lifestyle_angled.webp` | 1414 x 2000 | Manufacturer lifestyle image, angled wall with raking light, bathroom props | **Accepted for measurement only.** Rejected as a pixel source |

## Layout render — what was used

- **Hex lattice.** A 2D fit against the joint lines (`fit_lattice.py`) found regular flat-top hexagons: aspect ratio 1.0005 vs regular. Module across flats is 314.68 px, column pitch 272.67 px, origin (454.4, 156.8). Under the 10.125 in module assumption that is **31.08 px/in**. An earlier 1D estimate had the column phase 8.6 px off, which caused ghost joints (ERRORS.md #4).
- **Face types.** 45 cells were classified by high-pass energy and structure-tensor coherence, and the three groups separate cleanly:
  - Matte: hp 1.2–2.2, coherence < 0.06.
  - Raw: hp 3.5–4.9, coherence 0.32–0.38.
  - Chiseled: hp 6.9–9.9, coherence 0.76–0.84.

  Fully visible faces: **22 Matte, 8 Raw, 9 Chiseled** (56.4 / 20.5 / 23.1 %).
- **Chiseled geometry**, from the 2D spectrum peak of each fully visible Chiseled face:
  - Angles 90.2–90.35°, 29.6–30.3° and 150.3–150.5° (image coords). That is one groove pattern at hexagon rotations of 0 / 60 / 300°.
  - Orientation counts: 3 + one half face at 90°, 4 at 30°, 2 at 150°.
  - Pitch 6.16–6.19 render px, mean **5.052 mm**. Quadrant phases are stable, so the grooves are straight and evenly spaced.
  - Channel profile from the phase-folded luminance: exponent 1.65 (see README).
  - These are real designed grooves. They were measured and rebuilt, never filtered out as noise.
- **Chiseled surface texture.** The render's Chiseled faces with the groove harmonics notched out give the non-groove roughness and mottling (2.7x Matte) and the along-ridge amplitude modulation (cv 0.29, ~8 render px). These were quilted into the atlas's Chiseled faces. The render's groove pixels themselves were not copied; the grooves are rebuilt.
- **Joint colour.** The median of the darkest 20 % of pixels on the joint centreline gives **RGB (208, 200, 186)**, a warm light grey slightly darker than the face.
- **Organic pixels.** Quilting pools come from face interiors more than 5 px from the joint centreline:
  - Matte: 1.93 M px (≈ 25 faces).
  - Raw: 0.68 M px (≈ 8.7 faces).
  - Chiseled: 9 faces, rotated per orientation class.
- **Tone.** Type mean colours are about RGB (243, 231, 207) for all three types. Per-face tone offsets measured on the render (std ≈ 1 level) were reused as tile-to-tile variation.

## Layout render — what was rejected or corrected

- **Global illumination trend.** The render gets darker toward the bottom by 8–11 levels per channel. A quadratic trend with per-type offsets was fitted to the face means (residual std 0.9–1.05) and removed.
- **Pixels within 5 px of the joint centreline.** These hold the joint line and its anti-aliasing. The edge colour profile of the refit lattice is flat from 1.5 px outward.
- **The render's visible joint width** is a thin line of about 1/16 in. It was not used; the joint is fixed at 1/8 in by the brief.
- **The render's Chiseled groove pixels** were not copied. They carry baked shading and are near the render's Nyquist limit (6.2 px period).
- **Kept, with its limitation:** the render's baked directional shading on Raw faces stays in the Raw colour. Quilting is translation-only, so that light direction is consistent across all Raw faces.

## Lifestyle image — what was used (measurements only)

- **Cross-checks.** The Chiseled face at the upper right is also flat-top, with grooves perpendicular to its top edge, as in the render. Its pitch is about 20 grooves per 4 in, about 5.1 mm at about 49 px/in, which agrees with the render's 5.05 mm.
- **Relief character under raking light.** Raw is a dense, crisp, pitted relief. Chiseled ridges are chipped and broken with narrow dark channels. Matte is flat with fine speckle. This informed the choices below.
- **Calibration.** Boxes were placed fully inside faces, clear of joints, props and cast shadows (full-resolution px):
  - Vertical Chiseled (650, 200)–(890, 600).
  - Raw (110–330, 360–620).
  - Matte (380–600, 100–400).
  - Diagonal Chiseled (660–880, 700–900).

  Two measures were taken:
  - The band-passed contrast ratio, vertical Chiseled / Raw = 1.50. The atlas gives 1.36–1.46.
  - The spectral centroid of the relief shading: Raw 0.305 and Matte 0.270 cyc/mm. The atlas gives 0.264 and 0.279.

## Lifestyle image — what was rejected

- **All pixels as texture.** The view is angled, so foreshortening varies across the wall. The light rakes strongly with falloff, and there is a warm colour cast. The only view that is orthographic and at true scale everywhere is the render.
- **Non-tile content:** plant and its cast shadow, mirror, faucet, towel, countertop, sink, soap, bottles, diffuser and toothbrush cup. Shadowed wall regions were also excluded from the calibration boxes.
- **Its colour.** The deeper beige comes from the warm scene lighting. The Sand tone is taken from the render (see README limitations).
