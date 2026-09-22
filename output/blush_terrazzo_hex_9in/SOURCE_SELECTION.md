# Source selection — Blush Terrazzo Hexagon 9 in

Two images were supplied by the user on 2026-09-20. No manufacturer, series name or
product page was given.

| # | file | px | view type | verdict | reason |
|---|------|----|-----------|---------|--------|
| 01 | `references/01_single_tile_isolated.jpg` | 1199 × 1200 | flat, straight-on, single hexagon tile isolated on white | **ACCEPTED — the sole colour/texture source** | Clean product photography of one full tile, no perspective, no baked scene lighting, no props. Cropped to its exact non-white bounding box (x 12–1185, y 89–1111 → 1173 × 1022 px) and used directly. |
| 02 | `references/02_installed_hex_grid_mockup.webp` | 1200 × 1200 | rendered installation preview, multiple hexagons | **REJECTED as a texture source, used only for reference** | This is a manufacturer/marketing visualization built by repeating tile 01, not a second independent photograph — sampling it would only reintroduce the same chip layout already available from 01, at lower effective resolution per tile. Used only to (a) confirm this is a hairline-joint installation (no visible grout line in a middle-row brightness scan, min/max luma 194–242 with no distinct joint signature) and (b) as a visual sanity check for the final atlas's overall look. |

## Why a single photo is workable here (unlike a directional stone photo)

This repo's other single-photo, non-repeating jobs this session (ElmStone Jute
vein-cut and cross-cut) hit a hard ceiling: with one photo, even the best available
transform set left one or two dominant large-scale features (a vein streak, a cloud
blob) recognizable across cells. **Terrazzo is a different case.** A regular hexagon has
the full 12-member dihedral symmetry group (6 rotations × mirror), and ALL 12 map the
hexagon shape exactly onto itself — unlike ElmStone's rectangular panel, where only 4 of
8 symmetries preserved the 2:1 aspect. Combined with terrazzo's dense, isotropic field of
many small chips (no single dominant landmark for the eye to lock onto), 12 genuinely
different-looking orientations of the one real photo, one per atlas cell, produce an
atlas with **no two cells identical** and no obviously recognizable repeated feature —
confirmed on inspection at atlas scale, 2×2 repeat, and simulated wall-distance
(`textures/_PREVIEW_wall_scale.jpg`, 8 ft × 6 ft, 3.1 × 2.6 atlas repeats).

This is 100% photo-based, consistent with the user's standing instruction from the
ElmStone Jute work this session ("it needs to be the photo based version, anything
close to the deliverable is bad looking") — no chip pattern is synthesised.

## Assumptions, stated because nothing was specified

- **"9 inch hexagon" taken as 9 in across the flats** (11.5° point-to-point... actually
  10.39 in point-to-point), matching the precedent set on the `hex_10in_dimensional`
  job for the same ambiguity. If the manufacturer means 9 in point-to-point, every
  dimension in `source/build_maps.py` scales by 0.866 — a one-constant change
  (`FLATS_IN`) and rebuild.
- **Joint width 1/16 in**, since none was stated and the installed mockup shows no
  visible grout line at the resolution available — modelled as a near-hairline joint
  rather than inventing a wider, more visible one.
- **Joint colour matches the tile's own measured cement-base tone** (227, 224, 220),
  for the same reason — the mockup does not show a contrasting grout.
- **Relief depths** (0.35 mm total range, 0.25 mm tile plane, ±0.025 mm micro-relief
  derived from the photo's own tone variation, not a separately measured or fabricated
  pattern) are design estimates for a flat, non-dimensional terrazzo tile, per this
  repo's standard flat-tile convention ("bump = subtle micro-relief + joint recess
  only").
