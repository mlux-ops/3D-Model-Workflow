# ELM Fog Cross-Cut Chevron — 24 x 48 — Revit colour, bump, roughness, model pattern

Built 2026-09-23. Texture-only deliverable (no ADSKLIB, no RVT, no V-Ray: not requested).

## Files

| file | format | Revit slot | colour space |
|---|---|---|---|
| `textures/ELM_Fog_CrossCut_Chevron_24x48_Color.png` | 6144 x 4096, 8-bit RGB | Color → Image | sRGB |
| `textures/ELM_Fog_CrossCut_Chevron_24x48_Bump16.png` | 6144 x 4096, 16-bit grey | Bump / Relief Pattern → Image, Amount ≈ 0.5 (0.4–0.7) | linear |
| `textures/ELM_Fog_CrossCut_Chevron_24x48_Roughness.png` | 6144 x 4096, 8-bit grey, white = rough | Roughness → Image (physically based *Advanced* appearances) | linear |
| `pattern/ELM_Fog_CrossCut_Chevron_24x48_Landscape.pat` | Revit MODEL pattern, inches | Graphics → Surface Pattern | — |
| `pattern/ELM_Fog_CrossCut_Chevron_24x48_Portrait.pat` | Revit MODEL pattern, inches | Graphics → Surface Pattern (portrait use) | — |

- PNG IHDR verified from bytes 16–25: Color depth 8 / type 2, Bump16 depth 16 / type 0, Roughness depth 8 / type 0.
- Generic appearance has no roughness image slot: set Glossiness ≈ 36 (face roughness mean 0.64).

## Sample Size

| orientation | image | Sample Size (W x H) | pattern |
|---|---|---|---|
| **Landscape (as delivered)** — tile long side horizontal, chevron bands horizontal | as is | **12'-0" x 8'-0"** (144 x 96 in) | `_Landscape.pat` |
| Portrait — long side vertical, bands vertical (ELM's own room scene) | Rotation 90° in each map's Transforms | 8'-0" x 12'-0" | `_Portrait.pat` |

- Same Sample Size and rotation on all three maps. Repeat on, both directions.
- Atlas: 3 x 4 tiles of a 48 x 24 in module = tile 47-15/16 x 23-15/16 in + 1/16 in joint; stacked grid; half a joint on every outer edge, so joints fall on the module grid.

## Model pattern (grout lines you can grab and move)

1. Manage → Additional Settings → Fill Patterns → **Model** → New → Custom → Import → `_Landscape.pat` → pattern `ELM_Fog_CrossCut_Chevron_24x48_Landscape` → import scale **1.00** → OK.
2. Material → Graphics → Surface Pattern → Foreground → Pattern: that model pattern.
3. Graphics → **Texture Alignment**: drag the render appearance until its grout lines sit on the pattern lines. The texture's joints sit exactly on the 48 x 24 in grid, so a whole-tile offset aligns.
4. In the model: Tab-select a pattern line on a painted face → Move / Align / Rotate.

- Pattern = grout-joint centrelines only: `0, 0,0, 0,24` and `90, 0,0, 0,48`.
- Registration checked independently (`pattern/pattern_check.json`): parsed `.pat` rasterised over 144 x 96 in; 100 % of pattern pixels on grout, all 14 joint lines covered 100 %; portrait pattern checked against the texture rotated 90°, same result.

## Product facts

| item | value | source |
|---|---|---|
| product | ELM ElmStone **Fog** Cross-Cut Chevron = Florim USA / MILE stone EcoStone "Matte Chevron Deco" | ELM + MILE stone pages |
| manufactured size | **48 x 110 in only**, 6 mm, rectified, matte, "3D textured surface", V2 | ELM, MILE stone, 2026 brochure |
| 24 x 48 | user-specified; no 24 x 48 Chevron Deco is catalogued (24 x 48 exists only as plain Cross-Cut / Flute Deco) | — |
| joint | **ASSUMED** 1/16 in (no published joint; repo ELM convention) | — |
| colourway | Fog (swatch mean 244/240/227); not Mist (201/195/184) or Jute (218/205/185) | measured |

## Chevron geometry (measured from the 110 x 48 in slab swatch)

- 6 straight horizontal bands per 48 in (spines ±3 px over 110 in); mid spine at 24.01 in → a 24 in cut holds exactly 3 bands, spines on the tile edges.
- Tile types alternate by row: A = slab top half (/ \ /), B = bottom half (\ / \); even row count keeps the alternation across every joint and the wrap.
- Groove lines 48.3–49.6° from the long side; spacing 0.186–0.206 in (4.7–5.2 mm) with singles and pairs of incised lines between flat plateaus (components at 1.47x / 2.54x / 3.1x the pitch, scaling per band).
- Relief = each band's measured groove profile extruded along straight lines (exactly straight and parallel by construction), cut at a per-tile slab offset.

## Relief (16-bit bump, full scale 0–65535 = 1.70 mm)

| term | mm |
|---|---|
| grout floor | 0.00 |
| tile plane (groove crests) | 1.50 |
| **grout step** | **1.50** |
| **chevron groove relief** (plane → p1 groove floor) | **0.80** |
| deepest groove point below plane | 0.93 |
| **lowest face point above grout floor (clearance)** | **+0.57** |
| matte micro-relief | ±0.02 |
| eased arris | 0.30 over 1.5 mm |
| highest point | 1.60 (no clipping) |

- Pattern depth and joint depth are separate terms; the pattern was set on its own, no global multiplier.
- Grazing-light review (12–25°, both groove directions): grooves read as distinct incised relief, not a faint texture (`textures/_PREVIEW_relief_closeup_grazing.jpg`, `_PREVIEW_grazing_light_left.jpg`, `_PREVIEW_wall_scale_20x9ft.jpg`).

## Colour

- 100 % real product pixels; 7 genuinely different 48 x 24 faces: 4 non-overlapping cuts of the slab swatch (Florim's copy, 2.2x the JPEG bits of ELM's, pixel-registered), ELM's Fog Cross-Cut 24 x 48 face, 2 full tiles from MILE stone's flat 24 x 48 layout panel.
- Slab baked groove shading removed by subtracting each band's extruded profile; residual ±0.10 of the groove contrast (≈ ±0.3 grey levels).
- Groove darkening re-applied from the relief itself (exactly registered, zero-mean, 3.9 % at the groove floor, the swatch's own measured contrast).
- All faces matched to the chevron swatch mean (atlas face mean within 0.11 %); planar tilt only removed (≤0.7 %); tile shade spread ±0.6 % luminance / ±0.2 % warmth (1.1 % total); fine grain equalised to the median face (gains 0.83–1.14).
- Grout (222, 217, 206): ASSUMED matching light grout.
- Roughness: face 0.62, +0.06 in groove floors, grout 0.90 — estimates, not measured.

## Seamless / non-repeating

- Wrap: opposite edges identical in all three maps (step 0); four-way corner reviewed (`textures/_REVIEW_wrap_seam.jpg`).
- 12 cells from 7 faces: 5 faces used twice, always two rows apart, another column, rotated 180°; verifier finds exactly these 5 pairs, none adjacent on the wrapped grid (`textures/_REVIEW_cell_grid.jpg`).
- Checked at 3 x 3 repeats (36 x 24 ft) and on a 20 x 9 ft wall: no landmark tile, no visible atlas block.
- Limit: no further Fog Cross-Cut faces are published; more real faces would replace the repeats directly.

## Observation — earlier repo ELM "Jute" sources

`output/belmont_tiles/ElmStone_Jute_24x48/references/03`, `05` and `06` measure Fog-coloured (≈244/239/225), and 03/06 are the Fog chevron slab graphic without the chevron. ELM's actual Jute Cross-Cut swatch is 218/205/185. The earlier "ElmStone Jute" colour maps may be the Fog colourway. Not modified; needs confirmation.

## Limitations

- No Revit or renderer validation in this session (Linux container, no Revit). Previews are Lambertian diagnostics from the bump, not renders. Confirm bump amount, roughness slot and Texture Alignment behaviour in a disposable Revit 2025 project.
- Groove depths and roughness are design estimates; the manufacturer publishes no relief or gloss data.
- Source faces are marketing swatches (40–50 px/in); export at 42.67 px/in adds no photographic detail.

## Rebuild

```
cd source
python build_maps.py          # maps + textures/build_report.json
python make_previews.py       # review images
python make_model_pattern.py  # both .pat files + pattern/pattern_check.json
python verify_maps.py         # independent gates -> ../validation.json (non-zero exit on failure)
```

Analysis only: `analyse_chevron.py`, `analyse_grooves.py` (geometry), `degroove.py` (notch comparison; rejected, kept for `oriented_energy`).
