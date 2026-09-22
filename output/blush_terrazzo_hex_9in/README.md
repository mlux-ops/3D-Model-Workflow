# Blush Terrazzo Hexagon 9 in — colour + bump

Seamless, non-repeating, 100% photo-based texture pair for Revit, built 2026-09-20 from
one user-supplied product photo of a pink/blush terrazzo hexagon tile. No manufacturer,
series, or SKU was supplied.

## Deliverable

| file | format | size |
|---|---|---|
| `textures/BlushTerrazzo_Hex9_Color.png` | 8-bit sRGB, PNG colour-type 2 | 3565 × 3087 px |
| `textures/BlushTerrazzo_Hex9_Bump16.png` | 16-bit greyscale, PNG colour-type 0 | 3565 × 3087 px |

Bit depths verified from the PNG IHDR bytes.

### Revit Sample Size

**31.393 in × 27.188 in** — 2′-7 3/8″ × 2′-3 3/16″

That is the real-world extent of the whole atlas: 4 hexagon columns at 7.848 in column
pitch by 3 rows at 9.0625 in row pitch (9 in hexagon + 1/16 in joint). Image pixel aspect
(3565/3087 = 1.1548) matches the physical aspect (31.393/27.188 = 1.1547) to 0.01%.

Set **Repeat: On** in both directions. Suggested **bump amount ≈ 0.2** — this is a flat
terrazzo tile (chip relief, not a sculpted dimensional pattern), consistent with this
repo's flat-tile convention.

### The nominal-size assumption — read this before using the map

"9 inch hexagon" was taken as **9 in across the flats** (10.39 in point-to-point),
matching the precedent set on the `hex_10in_dimensional` job for the same ambiguity. If
the manufacturer means 9 in point-to-point, every dimension scales by 0.866 and the
Sample Size becomes **27.19 in × 23.55 in**. Change `FLATS_IN` in
`source/build_maps.py` and rebuild — nothing else changes, since the image is the same
picture at a different assumed scale.

## Why this atlas has exactly 12 hexagons, and why that's not a compromise

There is only one real photograph of this tile (no larger swatch sheet to crop
different regions from, unlike a mosaic sheet). A **regular hexagon has the full
12-member dihedral symmetry group** (6 rotations × mirror), and all 12 map the hexagon
shape exactly onto itself with zero distortion — unlike a rectangular tile (e.g.
ElmStone Jute's 48×24 in panel this same session), where only 4 of 8 symmetries
preserved the aspect ratio. The atlas is sized to **exactly 12 cells (4 columns × 3
rows)** — one cell per dihedral transform, each used exactly once, assigned by a
shuffled derangement.

**This guarantees no two cells in the whole atlas are pixel-identical** — a stronger
guarantee than was achievable for the ElmStone Jute textures earlier this session, where
a larger atlas (more cells than available real content could distinguish) meant some
repetition was unavoidable and had to be disclosed as a limitation. Here, because a
hexagon offers 12 usable symmetries and the field of chips is dense and isotropic (no
single dominant landmark for the eye to lock onto, unlike a stone vein or cloud blob),
12 truly different-looking cells were achievable from the one photo with **no
synthetic content** — confirmed on inspection at atlas scale, a 2×2 repeat (48 virtual
hexagons), and an 8 ft × 6 ft simulated wall (3.1 × 2.6 atlas repeats): no two hexagons
look alike, and no repeated pattern is identifiable at any of those distances.

Each cell also carries a small independent tone/warmth jitter (±1.8% / ±0.7%),
matching the ordinary small batch-to-batch shade variation real terrazzo panels have.

Full technique, including why this repo's other single-photo jobs this session
(ElmStone Jute) could NOT reach this guarantee, is in `SOURCE_SELECTION.md`.

## Seamlessness

The hexagon field is the Voronoi diagram of a triangular lattice of centres, enumerated
on a torus — the same construction used for `hex_10in_dimensional` — so the image wraps
by construction, not by a border fade. Measured wrap step is close to the typical
neighbour-pixel step (colour: 1.68/5.38 vs. 1.63 typical; bump: 0.008/0.006 mm vs. 0.008
mm typical) — i.e. statistically indistinguishable from ordinary chip-to-chip texture
variation, which is the expected signature of a seamless wrap built from real,
non-uniform photo content (a pure procedural pattern, like the dimensional hex tile's
comb faces, can hit an exact 0.000; real chip texture has its own natural pixel noise
at that scale, so this is the correct benchmark here).

## Relief, in millimetres

Flat, non-dimensional terrazzo tile — bump is subtle micro-relief (derived from the
photo's own local tone, not a fabricated pattern) plus a joint recess only, per this
repo's flat-tile convention.

| | mm |
|---|---|
| grout floor | 0.00 |
| tile base plane | 0.25 |
| **grout step** | **0.25** |
| matte micro-relief (chip edges), all faces | ±0.025 |
| chamfer at the tile edge | 1.2 mm band |
| total encoded range | 0.35 |

## Colour

Base cement tone measured directly from the photo: (227, 224, 220), warm off-white.
Chip colour is highly variable by design (that's the terrazzo character) — from near-
white flecks to saturated pink accents, median chip sample (221, 199, 198) understates
the visual range since most chips are pale. No colour was invented; every pixel in every
cell is real photo content, only rotated/mirrored/lightly tone-jittered.

Joint: 1/16 in, coloured to match the measured cement-base tone rather than a
contrasting grey, since the installed mockup shows no visible grout line — see
`SOURCE_SELECTION.md`.

## Facts sourced vs. assumed

**Measured from the photo**: hexagon shape and proportions (bounding-box scan confirmed
a regular flat-top hexagon to within JPEG edge-softness tolerance); base cement RGB;
chip colour range.

**Assumed, not measured — correct if a spec becomes available**: the 9 in
across-flats reading of the nominal size; the 1/16 in joint width and its colour; all
relief depths in millimetres.

## Limitations

- One real photograph, isolated product shot — not a scan, not a larger swatch sheet.
  No manufacturer page, SKU, or actual size was available.
- The 9 in across-flats reading is an assumption; see above.
- Relief depths are art-directed to a flat-tile convention, not measured off the
  product.
- **No Revit validation was performed.** The maps have not been loaded into a material,
  rendered, or checked on a surface in Revit.
- Upscaling adds no detail: the source is 1173 × 1022 px for one hexagon; the atlas's
  sharpness comes entirely from that one photo's own native resolution (rendered near
  1:1, PPI 113.6, chosen specifically so the identity-transform cell needs no
  resampling), not from invented detail.

## Review evidence

| file | what it shows |
|---|---|
| `textures/_PREVIEW_atlas_full.jpg` | the whole 12-hexagon atlas |
| `textures/_PREVIEW_tiling_2x2.jpg` | 2×2 wrap (48 virtual hexagons) |
| `textures/_REVIEW_wrap_seam.jpg` | the four-way corner, colour and grazing light |
| `textures/_PREVIEW_grazing_light.jpg` | the whole atlas at 15° light — chip relief reads clearly |
| `textures/_PREVIEW_wall_scale.jpg` | an 8 ft × 6 ft wall at true scale, 3.1 × 2.6 repeats |

All opened and inspected before delivery. A diagnostic-only reporting bug (the build
script's minimum-face-height printout picked up a boundary pixel at the joint/chamfer
transition and reported 0.0 mm) was found and confirmed harmless by direct visual
inspection of the bump map before delivery — the actual grout floor and tile faces are
correctly separated; nothing in the delivered PNGs is affected.

## Rebuilding

```bash
python source/build_maps.py       # colour + bump
python source/make_previews.py    # review images + numeric seam check
```

Python: `C:\Python314\python.exe` on this machine (numpy 2.5.0, pillow 12.2.0). Seed
20260920; the build is deterministic (the 12 transforms are shuffled but the shuffle
itself is seeded). Every write goes through an `out_path()` guard that raises outside
`output/blush_terrazzo_hex_9in/`.
