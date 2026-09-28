# ELM Surfaces Formed — Hexagon Tile in Sand: colour + bump (xhigh arm)

A seamless 8 x 7 hexagon atlas (56 faces) of the Formed hexagon in Sand. It mixes Matte, Raw and Chiseled faces in the proportions and orientations measured on the manufacturer's layout render. It is built for a Revit material: one colour map, one 16-bit bump map, and a face-ID map for checking.

## Deliverables

| File | Format (checked from PNG header bytes) |
|---|---|
| `textures/Color.png` | 4489 x 4536, 8-bit sRGB RGB |
| `textures/Bump16.png` | 4489 x 4536, 16-bit greyscale height, white = high, black = joint floor |
| `textures/face_ids.png` | 4489 x 4536, 16-bit greyscale, joint = 0, faces 1–56 (index = row x 8 + column + 1) |
| `textures/report.json` | Per face: type, rotation, mirror flag and source. Also the mix, bump encoding, relief, wrap steps and the full `verification` block |
| `textures/_PREVIEW_*.jpg`, `_REVIEW_*.jpg` | Review images (atlas, 2x2 wrap, seam corner, labelled face types, grazing light, 1:1 crops beside the render) |
| `source/` | Build scripts. `python source/run_all.py` rebuilds everything from `../inputs/` |
| `SOURCE_SELECTION.md`, `ERRORS.md` | What was used or rejected from each source; every error and its fix |

## Revit setup

- **Sample Size: 70.148 in x 70.875 in** (5′-10 5/32″ x 5′-10 7/8″). Repeat **on** in both directions. The image aspect is 4489 : 4536 = 0.98964 and the physical aspect is 0.98974. The 0.5 px difference comes from rounding 4489.47 px to 4489, and it is not visible.
- Colour map: `Color.png`. Bump map: `Bump16.png`, with the **same Sample Size** and Repeat on.
- **Suggested bump amount: 0.5.** Lower it towards 0.3 if the joints read too heavy, because the joint uses the full black-to-white range and Raw about 65 % of it. This is not validated in Revit (none in this trial).

## Geometry and the size assumption

- Flat-top regular hexagons, **10.000 in across the flats** (11.547 in point to point), with a **1/8 in joint**. The module is 10.125 in across the flats. Atlas: 8 columns x 7 rows at 64 px/in.
- **Assumption:** "10 x 10 hexagon" cannot be literal for a regular hexagon, so 10 in is read as the across-flats size. If the tile is really 10 in point to point, every dimension scales by 0.866. The Sample Size would then be **60.750 x 61.380 in** with the same images.
- Lattice: column centres at x = (j + 0.5) x 561.125 px. Even columns have centres at y = (i + 0.5) x 648, so their horizontal joints lie on the top and bottom image edges at half width. Odd columns are offset half a row. Hexagons cross the image edges; the texture is defined on the torus, so it wraps exactly.

## Joint

- Width 8 px = 1/8 in. Measured: vertical runs of 8 px across horizontal joints, and 16 px across 60° joints (= 8 px perpendicular). The joint area implies exactly 0.1250 in.
- Colour **RGB (208, 200, 186)**, a warm light grey. It is the median of the darkest 20 % of render pixels on the joint centreline. The lifestyle's joints look darker only because the recess is shadowed; the bump carries that.
- Bump: a flat floor 2.50 mm below the face plane. The outermost half pixel of the joint takes part of the step (anti-aliasing), and a 1.2 mm eased arris (0.35 mm) sits on the tile side.

## Face-type mix and layout

| | Matte | Raw | Chiseled |
|---|---|---|---|
| Render, fully visible faces (39) | 22 (56.4 %) | 8 (20.5 %) | 9 (23.1 %) |
| Render, visibility-weighted (42) | 24.0 | 8.5 | 9.5 |
| **Atlas (56)** | **32 (57.1 %)** | **11 (19.6 %)** | **13 (23.2 %)** |

Chiseled orientations (groove direction, image coordinates): 3 + one half face at 90°, 4 at 30° and 2 at 150° in the render. The atlas uses **5 x 90°, 5 x 30° and 3 x 150°**. Placement is by simulated annealing on the torus: no two Raw or two Chiseled faces touch (0 same-type adjacencies), counts are balanced per row and column, and like orientations are kept apart. Layout by row (M Matte, R Raw, C + groove angle):

```
row 0:  C90  R    C30  M    C150 M    M    M
row 1:  R    M    M    M    M    R    C90  M
row 2:  M    M    C90  R    C30  M    R    M
row 3:  M    R    M    M    M    M    M    C30
row 4:  M    M    M    C150 R    C90  M    R
row 5:  R    C30  R    M    M    M    M    C150
row 6:  M    M    M    C90  M    R    C30  M
```

## Method

1. **Render lattice and classification.** A 2D fit to the render's joint lines gives regular hexagons at 31.08 px/in (assuming the 10.125 in module). Each of 45 cells is classified by high-pass energy and structure-tensor coherence; the three types separate with wide margins.
2. **Measured Chiseled geometry.** The 2D spectrum peak of each face gives angles of 90.2–90.35°, 29.6–30.3° and 150.3–150.5°. That is one straight groove pattern at hexagon rotations of 0 / 60 / 300°, not assumed. Pitch is **5.052 mm** (the 9 faces range 5.037–5.058 mm). A fit to the phase-folded profile gives a channel shape of ((1 + cos 2πφ) / 2)^**1.65**: narrow rounded channels and broad crests. R² is 0.998, against 0.959 for a plain sinusoid. Luminance alone cannot say which feature is the narrow one; the in-phase darkening and the lifestyle's narrow dark channels settle it.
3. **Source pools.** The render's global light trend (8–11 levels) is removed, and each face's mean is separated from its texture. Pools are built for Matte (1.93 M px), Raw (0.68 M px) and Chiseled. For Chiseled, the render's 9 faces are used with the grooves notched out; each is rotated by a multiple of 60° to the target groove direction. They carry roughness (2.7x Matte), along-ridge depth modulation (cv 0.29) and mottled colour.
4. **Quilting from source pixels.** Each atlas face is image-quilted at render scale and resampled with a cubic filter to 64 px/in:
   - Blocks are 28 px for Raw and Chiseled, 36 px for Matte.
   - Placement is translation only, so the render's light direction stays consistent.
   - Blocks are matched on overlap SSD, joined along minimum-error boundary cuts, and a usage penalty spends fresh source pixels first.

   No invented noise is added anywhere.
5. **Relief (separate terms, mm, face plane = 0).**
   - Raw: the render luminance band 0.5–3 px + 0.3 x 3–12 px, mapped to 1.60 mm.
   - Chiseled: rebuilt channels 0.70 mm deep, x (1 + source modulation), plus source roughness of 0.12 mm std capped at +1σ.
   - Matte: the 0.5–3 px band at 0.015 mm std.
   - Tile edge: 0.35 mm ease over 1.2 mm.
   - Joint floor: 2.50 mm.

   The bands were chosen so the relief's feature scale under raking light matches the lifestyle image. The Chiseled depth was set so the vertical-Chiseled / Raw contrast ratio under a left light (1.36–1.46) matches the lifestyle's 1.50. No global multiplier is used.
6. **Colour.**
   - Matte and Raw: type mean + measured per-face tone offset (std about 1 level) + quilted render texture.
   - Chiseled: the same, plus channel darkening sized so the stripe contrast matches the render's measured 5.9-level rms.
   - Joints: drawn with 1 px anti-aliasing.
7. **Export and verification.** Heights are float64 until 16-bit export (black −2.50 mm, white +0.12 mm, 4.0e-5 mm per step). `verify.py` re-derives every gate from the PNG files.

## Relief figures (measured from Bump16.png)

| Face type | Pattern relief p0.1–p99.9 | Deepest pattern point | Clearance to joint floor | Incl. edge ease |
|---|---|---|---|---|
| Matte | 0.13 mm (std 0.014) | −0.19 mm | 2.31 mm | 2.04 mm |
| Raw | 1.70 mm | −1.66 mm | **0.84 mm** | 0.49 mm |
| Chiseled | 1.31 mm (0.70 mm channels x modulation + roughness) | −1.58 mm | **0.92 mm** | 0.81 mm |
| Joint | floor −2.50 mm below the face plane | | | |

## Gate results (see `report.json` → `verification`)

1. **Fidelity.** Face types, the Sand tone (type means about RGB 243 / 231 / 207), Chiseled pitch, angles and profile, and Raw and Matte texture all come from the render. The 1:1 crops sit beside the render at the same 4 in scale in `_REVIEW_crops_1to1.jpg`.
2. **Relief reads as relief.** It is clear under 20° light in `_PREVIEW_grazing_light.jpg`, and Matte stays flat. Clearances are positive and measured (table above).
3. **Seamless.** Each wrap seam step is compared with the step one pixel away:

   | | Left/right | Top/bottom |
   |---|---|---|
   | Colour | 1.03x | 0.83x |
   | Bump | 1.03x | 0.83x |
   | Bump, in 16-bit steps | 1670 vs 1619 | 385 vs 464 |

4. **Non-repeating.**
   - Whole-face Raw comparison under all 12 hexagon symmetries: max NCC 0.03 over 55 pairs.
   - Random 1 in and 2 in Raw windows, searched over every Raw pixel under 12 transforms: max NCC 0.54 / 0.30, none above 0.8.
   - Ghost-joint detector inside Matte and Raw faces: max 5.5, against 10.5 on real joints. The top hits were inspected and are Raw crevices.
5. **Mix.** 32 / 11 / 13, against render fractions of 56.4 / 20.5 / 23.1 %; orientations 5 / 5 / 3.
6. **Format.** Exact sizes, colour 8-bit RGB, bump and IDs 16-bit grey, 8 px joints.

## Limitations (honest)

- **Source resolution.** The only orthographic source is a CG render at 31.08 px/in. The atlas is 64 px/in, so every organic pixel is a 2.06x upsample, softer than a scan, with no detail finer than about 1.5 mm. The Raw relief is still a little coarser than the lifestyle's (spectral centroid 0.264 vs 0.305 cyc/mm).
- **Pool deficit and small-scale reuse.** The render has about 8.7 Raw faces of pixels for 11 atlas faces, about 25 Matte for 32, and 9 Chiseled for 13. So 73 % of Raw and 78 % of Matte quilted pixels share their source pixel with another output location (both copies counted). Reuse is broken into min-cut pieces smaller than a block: half-inch Raw windows found near-twins in 3 of 24 samples (NCC up to 0.95), while 1 in and larger windows found none. The three Chiseled class pools are rotated copies of the same 9 faces, sitting under the rebuilt grooves.
- **Absolute relief depth is a design choice.** It cannot be measured from these sources: the lifestyle's light elevation is unknown and the render is lit art. The ratios are calibrated (Chiseled : Raw to the lifestyle, and the Matte feature scale). The absolute depths (Raw 1.6 mm, Chiseled 0.7 mm, joint 2.5 mm) are chosen to read strongly, per the owner's rule for dimensional tiles.
- **Chiseled roughness.** It is taken at about 45 % of its luminance-equivalent, because part of the render's non-groove texture is aliasing of the 6.2 px grooves.
- **Colour.** It is the render's Sand, about RGB (243, 231, 207). The lifestyle shows a deeper beige under warm light, and the physical tile may be darker than the render; tint in Revit if needed. The Raw colour keeps the render's baked shading (one consistent direction), which adds to Revit's bump shading.
- **Other assumptions.** The 10 x 10 in reading is an assumption (see above). The 1/8 in joint is fixed by the brief; the render draws a thinner line. Chiseled orientation counts (5 / 5 / 3) extrapolate from only 9.5 render faces.
- **Not tested here.** No Revit, ADSKLIB, V-Ray or Drive step was run, as the brief requires.

## Reproduce

`python source/run_all.py` (numpy, scipy, Pillow). It is deterministic with fixed seeds. A clean rebuild from `../inputs/` reproduced byte-identical PNGs (see ERRORS.md / the final check). Diagnostics that informed constants are listed in `run_all.py`.
