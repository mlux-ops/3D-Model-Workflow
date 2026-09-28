# Source selection — ELM Formed Hexagon Tile in Sand

Only two images of this tile exist (`../inputs/`). Both were inspected through ≤800 px
thumbnails and 1:1 / magnified crops (`_work/`), and measured with the scripts in `source/`.

| Source | Pixels | View | Verdict |
|---|---|---|---|
| `elm_formed_hex_sand_layout_render.webp` | 2000 × 1888 | Flat, orthographic, computer-generated layout render | **Accepted**: the only source of pixels and geometry |
| `elm_formed_hex_sand_lifestyle_angled.webp` | 1414 × 2000 | Angled bathroom scene, strong raking light, props | **Accepted for reference only**: no pixels used |

## Layout render: what was used

- **Lattice.** Flat-top hexagons fitted to the render's joint lines (`a03`, `a03b`). Row pitch
  314.79 px, column pitch 272.65 px, anisotropy 1.00014, rotation −0.0002°. The overlay
  matches every joint in the image. Scale: (314.79 − 1.5 px line) / 10 in = **31.33 px/in**.
- **Face types and mix** (`a04`). Every face was classified from its fine-texture energy and
  gradient coherence. The three classes separate cleanly: Chiseled coherence 0.78–0.82;
  Raw 0.34–0.43 with a high-pass standard deviation of 3.3–4.9; Matte ≤ 0.06 and 1.1–2.1.
  Of the 39 complete faces, 22 are Matte, 8 Raw and 9 Chiseled (56.4 / 20.5 / 23.1 %).
  Area-weighted with the partial faces the split is 56.9 / 20.6 / 22.5 %.
- **Chiseled geometry** (`a05`, `a08`, `b01`):
  - Period 6.184 ± 0.007 px over 10 faces, which is **5.014 mm** (0.1974 in).
  - Groove directions 89.8°, 150.2° and 29.7°: one pattern at 60° tile rotations.
  - The cross-profile is asymmetric. Its 2nd harmonic is 0.18–0.23 of the fundamental at
    ±100° relative phase, with the same strength in all three families, so the asymmetry
    comes from the groove shape, not the lighting.
  - The skew sign gives each face's tile rotation: 0° ×4, 60° ×4, 300° ×1 and 120° ×1.
  - In 7 of 10 faces a groove is centred on the tile centre.
- **Organic surface.**
  - Matte: tone and cloudiness (low band), and speckle (high band), from the 21 complete
    Matte faces.
  - Raw: relief and colour quilted from all 12 Raw faces (8 complete, 4 partial).
  - Chiseled: tone, cloudiness and ragged grain from the 9 complete Chiseled faces, with
    each face's own periodic groove profile divided out.
- **Sand colour.** The render has a smooth lighting fall-off of 6.8 % (quadratic fit to the
  per-face medians), which was divided out. The Matte base is then sRGB (244, 231, 207), and
  per-face tone variation of 1.0 % (Matte), 1.5 % (Raw) and 0.8 % (Chiseled) is kept.
- **Joint colour.** The darkest 10 % of joint-core pixels: **sRGB (206, 198, 184)**.

## Layout render: what was rejected, and why

- **The drawn joint line.** It is 1–2 px (about 1/32 in). The fixed 1/8 in joint is drawn instead.
- **The outer 5 px of every face.** A desaturated halo (R−B falls from 36 to 23) runs beside
  each joint. Matte faces are sampled at 0.968 scale (3.2 % inside the clean face); Chiseled pixels whose
  source falls in the halo take the face's low-pass colour.
- **The global lighting gradient.** Removed, as above.
- **Face 12.** Its texture largely duplicates face 6 (band-pass NCC 0.62, low band 0.90;
  all other Matte pairs have a median of 0.14). Using both would put a visible copy into
  the atlas.
- **Partial faces as whole-face sources.** Partial Chiseled faces 33, 51, 53 and partial
  Matte faces were not used as whole-face sources, because they cannot cover a face. The 4
  partial Raw faces were used only as quilting patches that fit inside their visible part.
- **The render's joint grid and face layout.** Only the measured statistics (mix ratio and
  rotations) were used; the arrangement itself was not copied.

## Lifestyle image: what it informed

- **Relief character under grazing light.**
  - Chiseled: rounded, rough-topped ridges with darker grooves about 40 % of the period, and
    visibly ragged edges.
  - Raw: dense cleft-stone relief with features of about 3–7 mm.
  - Matte: flat, with a fine sandy grain.
  - These set the relative relief terms, which were judged against it in
    `_PREVIEW_grazing_light*.jpg`.
- **Groove pitch check.** About 7.3 px per period at about 36 px/in, which is ≈ 5 mm and
  agrees with the render.
- **Joints and edges.** The joint is recessed, and the tile arrises are eased (lit edge
  highlights). That is why the bump has a joint recess below every pattern point and a
  1 mm eased edge.
- **Tone.** Measured Matte faces here give linear R/G 1.17–1.22 and B/G 0.755–0.769. The
  render gives 1.127 and 0.777, so the lifestyle is warmer. That difference is the scene's
  warm lighting and grading, which can't be separated from albedo in this image. The
  render colour was kept.

## Lifestyle image: what was rejected, and why

All pixels. It is a perspective view under raking light, with cast shadows from the plant,
mirror and faucet, strong vignetting and warm grading. Face areas visible without
occlusion are few and heavily shadowed, so rectified pixels would carry baked directional
light and shadow into the colour and bump. The repo rule of building only from a flat,
straight-on source applies. The render is that source.
