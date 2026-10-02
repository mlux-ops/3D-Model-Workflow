# Source selection

Two inputs, both in `../inputs/`:

- `elm_formed_hex_sand_layout_render.webp`, 2000 x 1888 (the layout render)
- `elm_formed_hex_sand_lifestyle_angled.webp`, 1414 x 2000 (the angled lifestyle photo)

## Layout render: the texture source

Fitted lattice: module 314.815 px per 10.125 in, so 31.094 px/in in the render and a 2.058 x upsample to the atlas's 64 px/in. The render carries fine surface grain on each face, distinct grooves on Chiseled faces, and all three finishes on one wall.

**Used**

| Use | What was taken | Where |
|---|---|---|
| Lattice | Hexagon centres and module size from an edge-point fit | `s02` |
| Face types | 39 complete faces classified by high-frequency luminance std, groove coherence and visible fraction: 22 Matte, 8 Raw, 9 Chiseled | `s03`, `s04`, `s07`, `s09`, `s10` |
| Mix | Measured ratios 56.4 / 20.5 / 23.1 % and Chiseled wave angles 0 / 60 / 120 = 3 / 2 / 4 | `s14_qa.py` |
| Matte texture | Luminance and chroma residuals (plane removed, band-passed) of 22 complete faces plus 6 half-visible faces, restricted to their visible mask: 28 windows | `s10`, quilted in `s12` |
| Raw texture | Same residuals from 8 complete faces plus 1 half-visible face: 9 windows. The luminance residual was equalised in angular spectrum (gain clipped at 1.8) to remove the render's directional light before it was used as relief; std 3.19 to 3.12 render levels | `s10`, quilted in `s12` |
| Chiseled grooves | Pitch 0.19893 in, 16-bin profile, phase wobble structure function (from two vertical-groove faces), stroke continuity | `s04`, `s05` |
| Chiseled amplitude and grain | Per-face amplitude and grain maps from all 9 complete Chiseled faces, rotated into a canonical frame and quilted | `s06`, `s10`, `s12` |
| Tone | Per-type mean and covariance of face colour (Matte 243.7, 231.1, 206.9; Raw 243.9, 232.1, 207.7; Chiseled 243.4, 232.0, 207.7) | `s10` |
| Joint colour | Median along the joint centrelines: (218.2, 209.0, 195.0), rounded to (218, 209, 195) | `s08` |
| Copy check | Confirmation that the render's own Matte and Raw faces are not copies of each other (max whole-face NCC 0.03) | `s09` |
| Repeat-search reference | The same NCC search run on the render's unique faces (max 0.684) as the null for gate 4 | `s16` |

**Rejected**

- **Partial edge faces for Chiseled, and for Raw beyond one face:** Chiseled needs a complete face to measure groove phase and amplitude. Partial faces were used only for Matte (6 faces, 13 to 50 % visible) and Raw (1 face, 50 % visible), and only inside their visible mask.
- **Copying Chiseled faces directly:** their grooves and phase are fixed by the render, and a 13-face layout would repeat the same nine faces, with visibly repeated groove wobble. Grooves were rebuilt from measured geometry, and only the amplitude and grain came from source pixels.
- **A single quilt with no reuse tracking:** Matte and Raw need about 1.4 x the source area available, so a reuse penalty was added rather than tiling.
- **Using the render's luminance directly for Raw relief:** the render's light direction shows up as a bias (angular energy spans 0.023 to 0.154), so the residual was equalised first.
- **Render joint pixels for joint texture:** the joint is about 2 px wide and anti-aliased into the face colour, so only its colour was used, not its pixels.

## Lifestyle photo: sanity check only

**Used**

- **Colour sanity check.** Its Matte tone reads 4 to 5 % darker and warmer than the render-derived tone. The atlas follows the render.
- **Relief calibration.** Band-pass luminance std over mean at three physical scales (sigma 1-3, 3-9, 9-27 lifestyle px; about 41.2 px/in across the flats, a hand estimate from a 566 px-wide view of the photo, so the physical band edges are approximate), measured in five hand-drawn boxes (1 Chiseled, 2 Raw, 2 Matte) and compared with the raking-light preview of the atlas at the same physical bands (`work/contrast_lifestyle_vs_preview.txt`). This set the height constants (`K_RAW_H`, `CHIS_DEPTH_MM`, `K_GRAIN_H`) so the relief is not several times stronger than the photo. It is still 2.1 to 2.3 x stronger at the finest band for Raw and Chiseled; see the README.
- **Finish appearance check.** That Matte is close to flat, Raw is visibly textured and Chiseled shows fine parallel grooves.

**Rejected as a texture source**

- **Oblique view:** the wall is seen at a slight angle, so the hexagons are not regular in the frame and would need rectifying without a known homography.
- **Baked-in lighting:** directional light and soft shadows (plant, mirror) are part of the pixels; one photo gives no way to separate albedo from relief.
- **Mixed content:** the frame includes a mirror, faucet, plant, accessories and counter; several tiles are partly occluded or in shadow.
- **Coverage:** at most one or two clean faces of each finish, so it would not give a non-repeating library.

Nothing in the atlas was copied from the lifestyle photo.
