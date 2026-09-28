# ELM Surfaces Formed Hexagon Tile in Sand: colour + 16-bit bump atlas (max arm)

Revit texture pair for the ELM Surfaces **Formed** "10 × 10 hexagon" in **Sand**. It carries
all three face treatments the manufacturer shows mixed on one wall: **Matte**, **Raw** and
**Chiseled**.

| File | What it is |
|---|---|
| `textures/Color.png` | 4489 × 4536, 8-bit sRGB RGB |
| `textures/Bump16.png` | 4489 × 4536, 16-bit greyscale height. White is high; 0 = joint floor |
| `textures/face_ids.png` | 4489 × 4536, 16-bit greyscale. 0 = joint, 1…56 = face index |
| `textures/report.json` | Per-face type, rotation, mirror flag and source; mix; wrap steps; relief; bump amount |
| `textures/validation.json` | Independent re-derivation of every gate from the PNG files |
| `textures/_PREVIEW_*`, `_REVIEW_*` | Review images (all opened and checked, see *Review*) |
| `source/` | Build scripts. `python source/build_all.py` reproduces everything from the two inputs (31 min here; the Raw quilt takes about 18) |
| `_work/` | Intermediate measurements and arrays that `build_all.py` regenerates, plus the review views that were opened |

## Revit set-up

- **Sample Size: 70.148 × 70.875 in (5′-10 5/32″ × 5′-10 7/8″), Repeat on in both directions.**
- Colour → Generic *Image*. `Bump16.png` → *Bump*, suggested **Amount 0.5**. See *Relief*.
- The atlas is 8 columns × 7 rows = 56 flat-top hexagons at 64 px/in.
  - Module across the flats is 10.125 in (10 in tile + 1/8 in joint).
  - Column pitch is 8.7685 in. The image is 70.148 in wide and wraps exactly, so its
    horizontal scale is 63.993 px/in.

## Size assumption

A regular hexagon can't be 10 × 10. "10 × 10 hexagon" is read here as **10.000 in across
the flats** (11.547 in point to point), as the brief fixes. If the tile is really 10 in
point to point, every physical figure scales by 0.866: Sample Size 60.75 × 61.38 in,
groove period 4.34 mm. Relief depths in mm would stay as designed.

## Joint

- **1/8 in** (8 px), drawn with half its width on each tile edge, so the image wraps.
- Colour **sRGB (206, 198, 184)**, a warm light grey. It is the darkest 10 % of the joint-core
  pixels in the layout render, whose own joint line is only 1–2 px wide.
- In the bump the joint sits 1.60 mm below the face plane, below every pattern point.

## Method

All organic surface comes from render pixels. Only the Chiseled groove geometry is rebuilt,
from measured numbers. Details and rejected material are in `SOURCE_SELECTION.md`; every
step is a script in `source/`.

1. **Render calibration.**
   - Fitted the flat-top lattice to the render's joint lines: row pitch 314.79 px, 31.33 px/in.
   - Classified all 55 visible faces.
   - Divided out the render's smooth 6.8 % lighting fall-off.
   - Masked the 5 px joint halo out of every face.
2. **Mix.**
   - The render's 39 complete faces are 22 Matte, 8 Raw and 9 Chiseled (56.4 / 20.5 / 23.1 %).
   - The atlas uses **32 Matte, 11 Raw, 13 Chiseled** (57.1 / 19.6 / 23.2 %), the closest
     56-face split.
   - Placement was annealed on the torus: no two Raw faces touch, no two Chiseled faces
     touch, and textured-face density is even across the atlas and its repeat.
3. **Matte (32).**
   - Each face combines the low band (tone and cloudiness) of one render Matte face with
     the high band (speckle) of a different one, each under its own hexagon rotation or
     mirror.
   - 21 source faces are used. Face 12 is excluded because it duplicates face 6.
   - A low band is used at most twice, never in nearby cells, and with ≥120° rotation and a
     different mirror state. So no two atlas faces are the same combination.
   - Bump: flat face plane plus micro-relief from the speckle (σ 0.008 mm).
4. **Raw (11).** Image quilting at render resolution from all 12 render Raw faces (8
   complete, 4 partial).
   - Patches are 2.04 in, with a 0.38 in overlap and minimum-error seams.
   - Orientations keep the render's Raw texture axis (≈32°, shared by all 8 render Raw faces).
   - Per-patch rules, each allowing a small share of violating pixels (3 %; 10 % for 30
     patches; 5 % with a third use for 19 patches):
     - no reuse within one face or between touching faces;
     - a reused pixel must differ from its earlier use by a transform that is **not** a
       hexagon symmetry (±8° jitter).
   - The final audit (`a13_quilt_audit.py`) finds:
     - no reuse between touching faces (Raw faces never touch);
     - 0.6 % of Raw samples repeated inside a face, as slivers at seams;
     - about 2 % of Raw samples (6.4 % of the reused source pixels) whose two uses are
       related by an exact hexagon symmetry.
   - Colour: source colour ÷ its face mean × the atlas face's tone.
   - Bump: the render Raw relief band (luminance band-pass, 0.7–10 px) × 0.30 mm per σ,
     soft-clipped at ±1.0 mm.
5. **Chiseled (13).** The grooves are rebuilt from measured geometry:
   - **Period 5.014 mm** (6.184 ± 0.007 px over 10 faces).
   - **Directions 90°, 150° and 30°**: one pattern at 60° tile rotations.
   - **Asymmetric profile.** The render's groove luminance has a 2nd harmonic of 0.18–0.23
     at ±100° relative phase, the same in every family, so the shape itself is skewed. The
     rebuild uses a 0.30 harmonic (de-blurred), which gives a steep flank and a long gentle
     flank.
   - **Registration.** A groove is centred on the tile centre, as in 7 of 10 render faces.
   - **Rotations follow the render**: 0° ×5, 60° ×5, 300° ×2, 120° ×1. The render shows
     4 / 4 / 1 / 1.
   - Colour comes from a render Chiseled face, rotated onto the target grooves and
     phase-locked to them. Its own periodic profile is divided out, so tone, cloudiness
     and ragged detail stay. It is then multiplied by a crisp groove modulation of the
     measured strength.
   - Bump: groove profile × 0.70 mm, plus organic grain from the same source residual
     (σ 0.07 mm, clipped at ±0.22 mm).
6. **Heights** are built in millimetres as separate terms and quantised once at export:
   joint depth, pattern relief, and a 1 mm eased edge that drops 0.25 mm at the arris.
   There is no global bump multiplier.

## Results

All figures below were measured from the delivered PNGs by `source/b06_verify.py`, which
exits non-zero on a failed gate. The full numbers are in `textures/validation.json`.

| Gate | Measured |
|---|---|
| Format (PNG IHDR bytes) | `Color.png` 4489 × 4536, 8-bit, colour type 2 (RGB). `Bump16.png` and `face_ids.png` 4489 × 4536, 16-bit, colour type 0 (grey). |
| Joint width | All 168 vertical scans across horizontal flats cross exactly **8 px** of joint. Joint area is 2.454 %, the theoretical figure for 1/8 in. Joint pixels are one colour in `Color.png` and 0 in `Bump16.png`. |
| Wrap: colour (mean \|step\|, 8-bit) | Left/right edge **1.68** against 1.22–1.81 (mean 1.58) at the 7 interior column boundaries with the same lattice phase. Top/bottom edge **0.48** against 0.64–1.32. |
| Wrap: bump (16-bit counts) | Left/right **1435** against 865–1459 (mean 1250), which is 0.0569 mm against 0.0496 mm. Top/bottom **237** against 329–891. |
| Relief (from `Bump16.png`) | Joint floor 0.000 mm, face plane 1.600 mm, so **joint depth 1.600 mm**. |
| Pattern relief (0.5–99.5 %) | **Matte 0.05 mm, Raw 1.35 mm, Chiseled 0.91 mm**. Full ranges: 0.05, 1.88 and 1.13 mm. |
| Clearance | Deepest pattern point **0.648 mm above the joint floor**, so clearance is 0.648 mm. Counting the eased-edge ring as well, the lowest face pixel is still 0.518 mm above it. |
| Mix | 32 / 11 / 13, which is 57.1 / 19.6 / 23.2 %. Render (complete faces): 56.4 / 20.5 / 23.1 %. |
| Chiseled rotations | 0° ×5, 60° ×5, 300° ×2, 120° ×1, against 4 / 4 / 1 / 1 in the render. |
| Raw repetition: whole faces | NCC between the 11 atlas Raw faces over all 12 hexagon symmetries and ±12 px shifts: max **0.041** (colour), **0.054** (height). |
| Raw repetition: random windows | 1 in windows, 24 of them, searched through every other Raw face: max NCC **0.40** under the 12 symmetries and **0.48** at ±8°/±16°. The same test between the render's own independent Raw faces gives 0.45 and 0.36. |
| Reproducibility | `build_all.py` was re-run from the two inputs in a scratch copy of `source/`: 31 min, exit 0. It produced `Color.png`, `Bump16.png` and `face_ids.png` byte-identical to the delivered files (SHA-256 in `_work/final_png_sha256.txt` and `_work/repro_png_sha256.txt`). Its gates, relief, wrap and cache-free repetition figures were identical too. The scratch copy was then deleted. |

**Why the wrap test compares like with like.** The step across any boundary depends on
where it cuts the hexagon lattice:

- The left/right edge falls midway between hexagon columns, where every row crosses a
  slanted joint.
- The top/bottom edge runs inside a horizontal joint for half the columns.

So each edge is compared with the interior boundaries at the same phase: x = k·W/8 and
y = k·H/7. Against the all-column average, the left/right ratio would read 1.29 (colour)
and 1.55 (bump) even though no seam exists. That metric was replaced; see `ERRORS.md`
item 10. Four ×3 seam panels in `_REVIEW_wrap_seam.jpg` show no seam: the four-way corner,
and edges cutting through Raw faces 25 and 52 and Chiseled face 24.

## Relief and Revit bump amount

- **Scale.** `Bump16` value v gives height = v / 65535 × 2.60 mm, where 0 is the joint
  floor. Joint depth, pattern relief and the eased edge are separate terms, and there is no
  global multiplier.
- **Why the joint is 1.60 mm deep.** The joint sits below every pattern point, so the face
  never reads as punctured.
- **Chiseled: 0.70 mm crest to groove bottom, plus grain (σ 0.07 mm).** The depth is
  calibrated against the lifestyle image. There, about 40 % of each vertical groove period
  is dark under raking light. This profile at 0.70 mm is 43 % shadowed at 20° and 59 % at
  15°; 0.90 mm gave 57–65 %, too dark.
- **Raw: 0.30 mm per σ of the render relief band** (1.35 mm from 0.5 to 99.5 %). This keeps
  the Raw:Chiseled grazing contrast at 1.09, against 1.14 in the lifestyle.
- **Matte: σ 0.008 mm micro-relief only**, so it stays essentially flat. Its grazing
  contrast is 0.029, against 0.056 in the lifestyle, where colour speckle is included.
- These depths are **design values**: a flat render carries no depth. They are sized so the
  relief reads clearly in `_PREVIEW_grazing_light*.jpg` (15° from the left, like the
  lifestyle).
- **Suggested Revit bump Amount: 0.5.** This is the repo's fluted-tile range upper end
  (0.3–0.5), used because the pattern relief here is deeper than typical flutes. Lower it
  to 0.3–0.4 if joints read too dark in close-ups. It has not been tried in Revit.

## Review

Every review image was opened through ≤800 px views:

- **`_PREVIEW_atlas_full.jpg`.** Reads like the manufacturer render: cream faces, light
  joints, subtle Raw and Chiseled texture, no clumping.
- **`_PREVIEW_wrap_2x2.jpg`.** No visible repeat blocks or seams.
- **`_REVIEW_wrap_seam.jpg`.** Four seam panels in colour and bump are continuous.
- **`_REVIEW_face_types.jpg`.** All 56 labels and rotations are correct.
- **`_REVIEW_crops_1to1.jpg`.** Matte, Raw, Chiseled 0° and Chiseled 60° each match the
  render region at the same physical scale in tone, feature scale, groove spacing and
  orientation. The atlas grooves are crisper.
- **`_PREVIEW_grazing_light.jpg`** and **`_detail`.** Matte is flat. Raw reads as
  cleft-stone relief with shadow flecks. Chiseled reads as ragged ridges, darkest where the
  grooves are perpendicular to the light. Joints read as recessed.
- **1:1 checks of the last-built Raw faces (20, 30, 52).** No seam is visible in colour or
  under grazing light. One short straight min-cut seam in face 52 is faintly visible only
  in a contrast-stretched view of the bump.

## Limitations

1. **Resolution.** The render has 31.3 px/in and the atlas 64 px/in. Matte and Raw content,
   and Chiseled tone and grain, are upsampled 2.04× and look soft at 1:1. No detail was
   invented. Only the Chiseled groove geometry is crisp, because it is procedural.
2. **Source limits.** The render is computer-generated artwork, not a scan, and it is the
   only orthographic source. Its Raw faces share one texture axis (≈32°), which is kept,
   so the Raw faces aren't rotated between tiles. Real installs would be.
3. **Raw reuse.** Eleven Raw faces had to come from about 8.3 faces of source area.
   - Of the clean source Raw pixels, 39.6 % appear once, 36.7 % twice, 4.2 % three times and
     0.1 % four times; 19.4 % are unused.
   - 19 of 506 patches needed the logged third-use relaxation.
   - No reuse falls between touching faces.
   - Inside faces, 0.6 % of Raw samples repeat, as seam slivers.
   - About 2 % of Raw samples are reused under an exact hexagon symmetry, also slivers
     admitted by the per-patch allowance. The rest of the reuse differs by a non-symmetry
     rotation of at least 8°.
   - The symmetry and ±8/16° window searches find nothing above the independent-surface
     baseline (max NCC 0.40 / 0.48 against 0.45 / 0.36). An exhaustive search at the exact
     reuse angle could still match reused patches. This is a finite atlas, not mathematical
     non-repetition.
4. **Raw height from luminance.** It uses bright = high, from the render's 0.7–10 px
   luminance band. The Chiseled analysis found no measurable orientation-dependent
   (directional) shading in the render: groove contrast and skew are the same in all three
   families. But if the Raw texture has baked directional light, the relief is slightly
   offset from the true surface.
5. **Depths are designed.** All depths are chosen (see *Relief*), and the lifestyle's
   light angle is unknown. The Chiseled profile shape is inferred from the render's
   luminance harmonics; the true cross-section is unknown. The groove registration (a
   groove on the tile centre) follows 7 of 10 render faces.
6. **Colour map.** It keeps the render's mild groove darkening, as the source shows.
   Sand is kept as the render depicts it: very light, sRGB ≈ (244, 231, 207). The
   lifestyle photo looks warmer and darker under its scene lighting. If renders look too
   bright, adjust the Revit appearance rather than the map.
7. **Mirroring.** Mirrored content is used in Matte bands and Raw patches, where it isn't
   visible in organic texture; a real tile can't be mirrored. Four Chiseled faces take
   their grain from a source mirrored along the grooves, which leaves the groove geometry
   unchanged.
8. **Matte sources.** 21 render faces serve 32 atlas faces. Each low band is used at most
   twice, always with a different high band, rotation and mirror state. Face 12 is excluded.
9. **Not validated in Revit.** Sample Size, bump amount and appearance are unverified
   there. The grazing preview is this build's own render: Lambertian shading with hard
   cast shadows at 15° and 0.25 ambient.
10. **Size.** The size reading is an assumption; see *Size assumption*. No ADSKLIB, RVT,
    V-Ray or Drive upload, per the brief.
