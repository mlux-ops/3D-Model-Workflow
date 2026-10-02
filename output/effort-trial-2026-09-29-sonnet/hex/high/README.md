# ELM Formed Hexagon Tile, Sand: colour + bump atlas (high-effort arm, 2026-09-29)

## What was built

A seamless 8 x 7 atlas of 56 flat-top hexagons at 64 px/in.

| File | Format | Content |
|---|---|---|
| `textures/Color.png` | 4489 x 4536, 8-bit RGB | Colour |
| `textures/Bump16.png` | 4489 x 4536, 16-bit grey | Height. Joints at 0, face plane at 43690 |
| `textures/face_ids.png` | 4489 x 4536, 16-bit grey | Joints 0, faces 1..56 |
| `textures/report.json` | | Per-face type, rotation, mirrored, source patches, and every measurement below |

Bit depths were read from the PNG header bytes (`report.json`: `png_headers`).

Geometry: 10.000 in across flats, 1/8 in joint (8 px, drawn as 4 px on each outer edge of a face), 10.125 in module.

## Revit settings

- **Sample Size 70.148 x 70.875 in** (`5'-10.148in x 5'-10.875in`), as the brief specifies. The pixels give exactly 4489/64 = 70.1406 in by 4536/64 = 70.875 in, so the 70.148 figure is 0.0074 in (0.01 %) larger. Neither dimension is an exact quarter-inch multiple (70.875 in is 70 7/8 in), so Revit may round them in a 1/4 in project and shift the texture by up to 1/8 in over the atlas. This was not tested here.
- **Bump amount: start at 100** on the editor scale (stored 1.0). Basis: the repo calibration for a full-range dimensional map (2.6 mm full scale, 1.6 mm joint) was 100. This map is 2.4 mm full scale with the same joint, so 100 is about 8 % weaker per unit. This is an inference from that calibration and was not tested in Revit.

## Size assumption

The tile is taken as 10 in across flats with flat-top orientation. If the product is really 10 in point to point, scale everything by 0.866 (the across-flats size becomes 8.66 in).

## Joint colour

(208, 200, 186), the 10th percentile of the joint-line centre in the render. The render median is (215, 206, 192). The render joint is only 0.048 in wide, so this measure is uncertain. The joint is drawn at 1/8 in.

## Method

1. The lattice was fitted to the render (31.09 px/in) and each visible hexagon classified into matte, raw or chiseled by high-pass std and structure-tensor coherence. Mix measured: 26 / 9 / 10 of 45 visible hexes (57.8 / 20.0 / 22.2 %).
2. **Matte, raw:** image quilting from render pixels with a minimum-error cut, random flips and transposes, and a reuse penalty shared across all faces of a type. Raw height comes from Wiener-regularised shape-from-shading (light axis -31.5 degrees) blended with band-passed luminance.
3. **Chiseled:** the groove pattern is rebuilt at the measured period (0.199 in) and second-harmonic ratio. The groove amplitude and phase fields come from complex demodulation of the render, so the natural wander in the render is preserved. The residual and albedo come from render pixels.
4. **Layout:** simulated annealing on a wrap-aware adjacency (32 matte, 11 raw, 13 chiseled) so textured faces do not clump. Chiseled directions are 30, 90 and 150 degrees.
5. **Assembly:** each pixel takes the face with the largest hex-metric value. Joints are blended over 1.5 px in height and 0.75 px in colour. Faces are written with modular indexing, so both axes wrap.

`source/run_all.py` lists the run order (lattice, classification, grooves, light axis, joint colour, layout, atlas, review, verify). The final maps came from running the steps one by one. `run_all.py` has not been run end to end. Seed 20260929.

## Gate results

- **Wrap seams:** luminance step across the x wrap 1.15 levels against an interior 1.05 (ratio 1.09). Bump x wrap 0.029 mm against 0.024 mm interior (1.19). The y wrap gives 0.15 levels and 0.002 mm, but that is small by construction because rows 0 and H-1 both lie on a joint centre line. See `_REVIEW_wrap_seam.jpg` for a four-way corner and a joint crossing.
- **Joints:** 8 px wide (edge-normal median 8.0), joint fraction 2.45 % against 2.44 % expected. All 56 face ids present.
- **Mix used:** 32 / 11 / 13 (57.1 / 19.6 / 23.2 %). No raw-raw or chiseled-chiseled neighbours. Largest textured cluster 7 faces. 1 textured face has no textured neighbour.
- **Fidelity to the render:** mean colour within about 1.5 levels for each type. Texture energy at render scale: matte 0.97 vs 0.87, raw 2.40 vs 2.28, chiseled 3.15 vs 3.26.
- **Non-repetition:** 112 px patch NCC (1.75 in, 8 rotations and mirrors) against all other faces of the same type. Raw: max 0.495, median 0.372. Matte: max 0.723, median 0.425. A copied patch would score above 0.9. Raw face pairs, whole-face peak NCC: worst 0.149. Chiseled same-direction envelope NCC: max 0.354.

## Relief (design values scaled from the render, in mm)

Pattern depth and joint depth are separate terms. The joint floor is 1.6 mm below the face plane. Clearance is the joint floor minus the deepest point of the pattern.

| Type | rms | p1..p99 span | Deepest below face plane | Clearance to joint floor | Median / p99 slope |
|---|---|---|---|---|---|
| Matte | 0.014 | 0.079 | 0.21 | 1.39 | 0.7 / 4.7 degrees |
| Raw | 0.167 | 0.804 | 0.86 | 0.74 | 4.7 / 14.3 degrees |
| Chiseled | 0.185 | 0.682 | 0.55 | 1.05 | 11.1 / 25.1 degrees |

Chiseled groove peak-to-valley is 0.50 mm of design amplitude. The 16-bit encoding is mm = v/65535 x 2.4 - 1.6 (0.000037 mm per step). Clearance is positive for every type, so the pattern never reaches the joint floor. Relief was judged under grazing light (az 200 degrees, el 15 degrees, `_PREVIEW_grazing_light.jpg`).

## Review images (`textures/`)

`_PREVIEW_atlas_full.jpg`, `_PREVIEW_wrap_2x2.jpg`, `_REVIEW_wrap_seam.jpg`, `_REVIEW_face_types.jpg` (labelled by index and type), `_PREVIEW_grazing_light.jpg`, `_REVIEW_crops_1to1.jpg` (per type: ours, ours under grazing light, render at the same physical scale).

## Limitations

- The render is about 2x lower resolution than the atlas (2.06x upsample). Fine detail is reconstructed, not observed, and looks softer than the lifestyle photo.
- Relief amplitudes are not measurable from a 2D image. The figures above are design values scaled from the render's shading and the lifestyle photo, not product measurements.
- The matte source has WebP block artefacts of 1 to 2 levels. They are invisible at normal contrast but are present.
- Matte faces occasionally reuse the same speckle cluster (max patch NCC 0.723). Only 26 matte hexes are available, covering about half the needed output area.
- Raw ripples are isotropic, while the lifestyle photo shows some elongated structure. Lifestyle ridges are more ragged than the chiseled grooves here.
- Face-to-face colour variation of textured types is lower than in the render: raw 0.93 vs 2.06, chiseled 0.72 vs 1.62 (luminance std). Matte matches (2.03 vs 2.21).
- Chiseled texture energy is 3.5 % below the render (3.15 vs 3.26), and raw and matte are 4 to 11 % above it (matte 0.97 vs 0.87).
- Quilt patches use flips and transposes at patch level, so per-face `mirrored` is reported as false.
- Sample Size 70.148 in was used as specified. Pixel-exact is 70.1406 in.
- The size assumption (10 in across flats) is unverified, and the Revit bump value has not been tested in Revit.
