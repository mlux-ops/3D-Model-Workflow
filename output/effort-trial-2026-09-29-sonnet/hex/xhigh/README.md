# ELM Formed Hexagon Tile, Sand: colour + bump atlas (xhigh arm)

Colour and bump texture atlas for a wall of mixed Matte, Raw and Chiseled ELM Formed Hexagon tiles in Sand, 8 mm thick. Nothing here is a Revit, ADSKLIB, V-Ray or Drive deliverable; the brief asks for maps only.

## Files

| File | What it is |
|---|---|
| `textures/Color.png` | 4489 x 4536, 8-bit sRGB RGB |
| `textures/Bump16.png` | 4489 x 4536, 16-bit greyscale, white = high, joints lowest |
| `textures/face_ids.png` | 4489 x 4536, 16-bit, joint = 0, faces 1..56 (index = row x 8 + column + 1, zero-based row and column) |
| `textures/report.json` | Every measured number quoted below, plus one record per face |
| `textures/_PREVIEW_*.jpg`, `_REVIEW_*.jpg` | Review images (atlas, 2 x 2 wrap, wrap seam, face types, raking light, 1:1 crops, top repeat-search matches) |
| `source/` | Python build scripts (numpy, scipy, Pillow only) |
| `work/` | Intermediate measurements the scripts read and write |

SHA-256 of the maps in this delivery (a second run of `s12_build_atlas.py` reproduced all three byte-identically):

```
Color.png    ad20f78129e2280145b87bfe6f5b0e377cef36c5c5b9c2b96b5116f263592421
Bump16.png   00c3725cfc4e83c3d3e73e28923a6c2ad28e79f02bbd6716224b9bd07216a03d
face_ids.png 4a548598b4776416a1032482e0fc499831ad528933d8982aabed2506dbc09966
```

## Geometry and Revit Sample Size

- Flat-top hexagons, **10.000 in across the flats** (11.547 in point to point), 1/8 in joint drawn at half width on every outer edge, so each module is 10.125 in across the flats.
- Atlas 8 columns x 7 rows = 56 hexagons at 64 px/in = **4489 x 4536 px**. Even columns sit with a joint on the top edge; odd columns are offset by half a row, so their faces cross it. Both axes wrap by modular indexing.
- Column pitch 561.125 px (8.7685 in), row pitch 648 px (10.125 in). Face radius 320 px on the atlas's hexagon metric, module edge 324 px, joint 8 px perpendicular to the edge.
- **Revit Sample Size: 70.148 in x 70.875 in, Repeat on in both directions** (as the brief fixes). The height is exact (4536 / 64 = 70.875). The width is 4489 / 64 = 70.1406 in against the true 8 x 8.7685 = 70.148 in, a 0.007 in (0.01 %, about half a pixel) difference.
- **Size assumption.** The brief's nominal 10 in is read as across the flats. If the tile is really 10 in point to point, every dimension scales by 0.866 (the images would stay as built, and the Sample Size would become 60.75 x 61.38 in; the joint would then read 0.108 in rather than 0.125 in).
- **Risk, not a failure:** AGENTS.md records that Revit rounds Sample Size to the project length units (1/4 in in the Belmont project). 70.148 would become 70.25 in, and 70.875 would tie between 70.75 and 71.0. That is a drift of about 0.1 to 0.2 %, or 0.1 to 0.15 in over the tile. I did not test it in Revit; Revit is out of scope for this trial.

## Joint colour

Joint RGB **(218, 209, 195)**, `#DAD1C3`. Measured on the render along the joint centrelines: median (218.2, 209.0, 195.0), p10 (212.5, 204.1, 189.0), p90 (224.3, 216.2, 203.1), against the surrounding face colour (243.5, 231.7, 207.5). The render's joint is only about 2 px (0.06 in) wide and anti-aliased into the face colour, so the true joint colour is probably somewhat darker than this value. I kept the measured value rather than guessing a darker one.

## Method

All texture comes from the two supplied photographs; no noise was invented for the organic surface.

1. **Lattice fit** on the layout render: 314.815 px per 10.125 in module (31.094 px/in), giving a 2.058 x upsample to 64 px/in.
2. **Classification** of the 39 complete faces in the render: high-frequency luminance std above 4.5 is Chiseled; below 1.6 with structure-tensor coherence below 0.1 is Matte; everything else is Raw. The thresholds are fixed constants in `s04`, `s07`, `s09` and `s10`; colour is not used. Visible-fraction cut-offs are 0.90 for Chiseled and 0.95 for Matte. Measured counts 22 / 8 / 9.
3. **Matte and Raw** faces are Efros-Freeman image quilts (min-cut seams, random dihedral block transforms, a source-reuse penalty) built from the render's complete faces. Matte: 56 px blocks, 14 px overlap. Raw: 36 px blocks, 10 px overlap, with the relief channel weighted x3. The relief channel of Raw was equalised across angle to remove the render's directional light.
4. **Chiseled** faces: grooves are rebuilt from measured geometry (pitch 0.19893 in, a measured 16-bin groove profile, and a fractional-Gaussian phase wobble matched to the measured structure function). Amplitude and fine grain are quilted from the render's chiseled faces in a canonical frame and rotated to the face's wave angle. Waves in image coordinates (y down): 0 = `|`, 60 = `/`, 120 = `\`.
5. **Layout** (seed 15): the 56 positions were assigned by simulated annealing to match the measured mix without clumping, with no Raw-Raw and no Chiseled-Chiseled neighbours and no empty column. Chiseled orientations follow the render's mix of the three wave angles.
6. **Height model** (mm above the joint floor; 2.6 mm = 65535; face plane 1.6 mm). Pattern and joint are separate terms and there is no global bump multiplier. Faces ramp from the plane down to the joint floor over 2.5 px at the face edge. Matte: plane + 0.006 x z. Raw: plane + tanh-limited z (clip 1.0 mm). Chiseled: plane + 0.30 mm x groove profile x amplitude field (0.35 to 1.5) + a fine grain term.
7. **Colour model:** each face's tone is drawn from its type's measured mean and covariance (clipped to 2 sigma), plus the quilted texture and groove terms, blended into the joint colour over one pixel at the edge.

The scripts run in numeric order; the slow ones are `s02_fit_grid.py` (about 10 min), `s12_build_atlas.py` (about 80 to 90 s) and `s15_repeat_search.py` (about 106 s). Seeds are fixed (layout seed 15, atlas RNG base 20260929, repeat-null seed 20260930). Run from `source/`: `s01` to `s12` build the maps, `s13` the review images, `s14` the report, `s15` to `s17` the repeat and groove checks (`s14` reads their output, so run `s15`, `s16` and `s17` before a final `s14`). `t_*.py`, `thumbs_*.py` and `crop.py` are trial and viewing helpers.

## Relief (from Bump16, measured)

Heights are millimetres above the joint floor. These are **design heights** chosen so the raking-light look matches the sources; they are not measured depths of the real tile.

| Type | Faces | Plane median | Std | p1 to p99 | Min to max | Slope p99 | Lowest point |
|---|---|---|---|---|---|---|---|
| Matte | 32 | 1.600 mm | 0.010 | 0.051 mm | 0.184 mm | 2.5 deg | 1.485 mm |
| Raw | 11 | 1.602 mm | 0.095 | 0.464 mm | 1.062 mm | 14.3 deg | 1.007 mm |
| Chiseled | 13 | 1.462 mm | 0.129 | 0.556 mm | 1.115 mm | 21.6 deg | 0.838 mm |

- **Grout step 1.6 mm** (face plane above the joint floor at 0 mm; median over joint pixels is 0.165 mm because of the edge ramp).
- **Clearance** between the deepest pattern point and the joint floor: **0.838 mm** (worst face: index 6, Chiseled), against the 1.6 mm step. Raw's lowest point is 1.007 mm. The tile face never approaches the joint.
- The bump map uses levels 0 to 52142 (79.6 % of the 16-bit range); it is not stretched to full range, so the millimetre scale stays 2.6 mm = 65535.
- Chiseled faces sit on average about 0.14 mm below the other faces (1.462 vs 1.600 mm) because the groove profile removes material from the plane; that is a property of my height model; neither source shows whether the real chiseled face sits lower.

## Suggested Revit bump amount

**100** (whole number on the editor scale, stored 1.0). Basis: the calibration recorded in AGENTS.md for a full-range 16-bit dimensional map at 2.6 mm full scale with a 1.6 mm joint (1 showed nothing, 50 showed joints only, 100 made the tile relief read). This map has the same full scale and joint. **Not verified in Revit for this build.**

## Acceptance measurements

| Gate | Result |
|---|---|
| 1 Fidelity | Band-pass luminance std, atlas over render, difference-of-Gaussians sigma 1, 2, 4, 8, 16 render px: Matte 0.65, 0.84, 0.94, 1.02, 1.11; Raw 0.60, 0.93, 1.06, 1.00, 0.83; Chiseled 0.84, 0.92, 0.89, 0.84, 0.67. Groove pitch in the finished colour map: mean 0.19875 in (range 0.1965 to 0.2019) against 0.19893 in in the source; groove angle error max 1.20 deg, mean 0.53 deg. |
| 2 Relief | Table above. Under 18 deg raking light (`_PREVIEW_grazing_light.jpg`) Raw and Chiseled read clearly and Matte is close to flat (p1 to p99 0.051 mm, slope p99 2.5 deg). Clearance 0.838 mm. |
| 3 Wrap | Mean absolute pair step at the wrap seam vs the interior: x colour 0.700 vs 0.950 levels, y colour 0.984 vs 0.971; x bump 0.0123 vs 0.0200 mm, y bump 0.0165 vs 0.0210. Per-channel RGB seam means are all below 1.1 levels. All within the interior p99. |
| 4 Non-repeating | 194 two-inch patches searched against every window of the atlas on the torus with 8 transforms: max NCC 0.4999, p99 0.461, 6 above 0.40, none above 0.50. The same search on the render's own known-unique faces reaches 0.684. Whole-face NCC under the 12 hexagon symmetries: Matte max 0.044, Raw max 0.035. See limitations for what this cannot show. |
| 5 Mix | Render 22 / 8 / 9 of 39 complete faces (56.4 / 20.5 / 23.1 %); atlas 32 / 11 / 13 of 56 (57.1 / 19.6 / 23.2 %). Wave angles 0 / 60 / 120: render 3 / 2 / 4, atlas 4 / 3 / 6. No Raw-Raw or Chiseled-Chiseled adjacency; no empty column. |
| 6 Format | Read from PNG header bytes: Color 4489 x 4536, 8-bit, colour type 2 (RGB); Bump16 and face_ids 4489 x 4536, 16-bit, colour type 0 (greyscale); none interlaced. Face pixel counts 354,722 to 354,728 (expected 354,724); joint runs exactly 8 px on vertical edges, 7.8 to 8.1 px perpendicular on sloped edges. |
| 7 Honesty | The limitations below. |

## Limitations

- **The mix has a wide error bar.** It comes from 39 complete faces, so the binomial error is about 7 percentage points per type. The used ratios match the measured ones, but the measured ones are not precise.
- **Source resolution.** The render is 31 px/in and the atlas is 64 px/in, so the finest colour grain is softened: at the finest band the atlas has 0.60 to 0.65 of the render's energy for Matte and Raw and 0.84 for Chiseled. Sigma 2 to 8 px bands are 0.84 to 1.06 (Matte 0.84 to 1.02, Raw 0.93 to 1.06, Chiseled 0.84 to 0.92). The sigma 16 px band (the coarsest) is 1.11 for Matte, 0.83 for Raw and 0.67 for Chiseled, so Chiseled has about a third less broad tonal variation than the render.
- **Repeat test cannot clear the last 0.1.** Matte and Raw needed about 1.4 x reuse of the source library. The top matches (NCC about 0.50) cannot be separated from a heavily degraded copy: a planted copy with noise at twice the patch's std scores 0.44 to 0.46. Faces 42 and 25 share a dark micro-mark that is visible only after contrast stretching (`_REVIEW_repeat_top_matches.jpg`). The Chiseled fine grain was not numerically repeat-tested; only the groove pitch and orientation were measured (they repeat by design), and the grain was reviewed visually.
- **Relief millimetres are design values.** They were tuned by band-energy ratio against the lifestyle photo under an assumed light, not measured from the real tile. The raking-light preview is still about 2.1 to 2.3 x stronger than the lifestyle photo at the finest band for Raw and Chiseled (about 2.9 x for Raw and 1.7 x for Chiseled at mid scale), and about equal for Matte. This comparison rests on five hand-drawn boxes in the lifestyle photo (1 Chiseled, 2 Raw, 2 Matte) and an approximate lifestyle scale (about 41.2 px/in, a hand estimate), and on my Lambert raking-light model (18 deg elevation, 225 deg azimuth), not on the photo's real light. I judged the excess acceptable because AGENTS.md asks for relief to read under grazing light, but the true tile may be shallower.
- **Isotropic wobble assumption.** The Chiseled groove phase wobble (Hurst about 0.318, std 0.156 periods at 80 render px) was measured on the two vertical-groove faces only (render faces i3 j0 and i3 j3) and applied unchanged to all three wave angles and to both directions.
- **Lifestyle colour.** The lifestyle photo's Matte reads 4 to 5 % darker and warmer than the render-derived tone. The atlas follows the render; the lifestyle photo was used only as a sanity check.
- **Joint.** The atlas joint is 8 px (0.125 in) as specified; the render's joint is about 2 px, so joint colour and depth cannot be checked against the source at that width.
- **`rotation_deg` and `mirrored`.** For Matte and Raw, `rotation_deg` is 0 and `mirrored` is false because the quilt blocks carry their own dihedral transforms (counts listed in each face's `source`). For Chiseled, `rotation_deg` is the groove wave angle; the block-level mirroring inside the canonical frame is not reflected in `mirrored`.
- **Scale.** The render's pixels-per-inch (31.094) follows from the brief's 10.125 in module (10 in tile plus joint), not from an independent measurement; the lattice fit gives only the module in pixels (314.815). Groove pitch (0.1989 in) and all other physical sizes inherit that assumption.
- **Not verified in Revit:** Sample Size rounding and the bump amount of 100.
- **Unrelated:** three claude.ai connectors (Devil's Advocate, FormEdge, Meridian Connector for QuickBooks) reported needing authorisation during this session. They were not used.
