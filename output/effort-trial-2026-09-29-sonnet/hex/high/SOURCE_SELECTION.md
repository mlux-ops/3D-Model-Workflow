# SOURCE_SELECTION.md

## Inputs (read-only)

1. `elm_formed_hex_sand_layout_render.webp`, 2000 x 1888. Flat-top layout render. Fitted lattice scale is 31.09 render px/in, so the module hexagon is 314.8 px across flats. The atlas is 64 px/in, an upsample factor of 2.0585.
2. `elm_formed_hex_sand_lifestyle_angled.webp`, 1414 x 2000. Photo of an installed wall.

## Used

| Source | Role |
|---|---|
| Layout render, matte hexes (26 of 45 visible, labels `iXjY` in `work/render_hexes.json`) | Colour and micro-relief of matte faces, quilted. Per-face patch provenance is in `textures/report.json` (`faces[].source`) |
| Layout render, raw hexes (9 of 45) | Colour by quilting. Height by shape-from-shading (light axis -31.5 degrees) mixed with band-passed luminance (0.6 / 0.4) |
| Layout render, chiseled hexes (10 of 45) | Groove amplitude and phase fields by complex demodulation, plus residual and albedo, quilted. Grooves are rebuilt analytically at the measured period (0.199 in, 5.05 mm) and second-harmonic ratio (0.112) |
| Layout render, face-type mix | 57.8 / 20.0 / 22.2 % (all visible) or 56.4 / 20.5 / 23.1 % (full hexes only). Used 32 / 11 / 13 of 56 |
| Layout render, joint line | Joint colour sampled at the p10 of the line centre: (208, 200, 186) |
| Lifestyle photo | Only to check groove period and character (regular fine ridges, isotropic ripples on raw). No pixels are copied from it |

Only whole, fully visible hexagons were used as pixel sources. Samples come from inside 0.955 of the module hexagon (`INSET_R` in `source/srcs.py`), so the joint line and edge pixels are excluded.

## Rejected

- Lifestyle photo scene items (faucet, plant, mirror, sink), its perspective, lighting and colour cast.
- Partial hexes at the render edge.
- Render joint pixels. The joint is 0.048 in wide in the render, so it is redrawn at 1/8 in.
- Any invented noise. All organic detail comes from render pixels.
