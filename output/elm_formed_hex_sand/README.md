# ELM Surfaces Formed Hexagon Tile in Sand: colour + 16-bit bump (production, 2026-09-26)

A Revit texture pair for the ELM Surfaces **Formed** "10 × 10 hexagon" in **Sand**. It shows the three face treatments the manufacturer mixes on one wall: **Matte**, **Raw** and **Chiseled**.

The build is the max-effort arm of the 2026-09-26 effort trial (`output/effort-trial-2026-09-26-hex/`), which ranked first in the blind review. Three production fixes and a tone change were applied after that review (see *What changed*).

## Delivered

| File | Where | What it is |
|---|---|---|
| `ELM Formed Hexagon Sand - 5'-10.148in x 5'-10.875in.png` | `F:\My Drive\Revit Material Maps - 25-012 651 Belmont` | Colour, 4489 × 4536, 8-bit sRGB |
| `ELM Formed Hexagon Sand - 5'-10.148in x 5'-10.875in - Bump 100.png` | same folder | Bump, 4489 × 4536, 16-bit grey. White is high; 0 = joint floor |
| `ELM Formed Hexagon Sand - Model Pattern.pat` | same folder | Revit model (surface) fill pattern at real scale, flat-top hexagons on the joint centrelines |
| This package (README, source selection, errors, report, validation, face IDs, previews, scripts) | `3D Model Workflow/Material Packages/ELM_Formed_Hexagon_Sand_Package.zip` | Everything except the two maps |

Both maps are `textures/Color.png` and `textures/Bump16.png` here, renamed to the owner's convention: tile name, then Sample Size in feet and inches, then (bump only) the Revit bump amount. No ADSKLIB, per the owner.

## Revit set-up

- **Sample Size: 70.148 × 70.875 in (5′-10.148″ × 5′-10.875″ = 5′-10 5/32″ × 5′-10 7/8″), Repeat on in both directions.**
- Load the colour map into the *Image*. Load the bump map into *Bump*, with **Amount 100** (editor value).
  - The editor takes whole numbers from 0 to 1000 and shows the stored value ×100: Autodesk's stored default of 0.3 appears as 30. A decimal such as 0.5 rounds to 0.
  - **Checked by the owner** in a Revit view of the 25-012 651 Belmont floor:
    - at 1, no visible relief;
    - at 50, joints only;
    - at **100**, the Raw and Chiseled relief reads, and the joints read as recessed with an eased edge.
  - Higher values thicken the joint lines before they strengthen the faces much. If the faces need more at 100, ask for a softened-joint version of the bump map rather than raising the amount.
  - Earlier copies named `... - Bump 0.5.png` and `... - Bump 1.png` (identical pixels, wrong amounts) were moved to Drive trash on 2026-09-26 with the owner's approval.
- **Model pattern:** Manage > Additional Settings > Fill Patterns > Model > New > Custom > Import `ELM Formed Hexagon Sand - Model Pattern.pat`, Import scale 1.
  - Flat-top hexagons, 10.125 in across the flats on the joint centrelines (side 5.8457 in), the same orientation as the maps.
  - The pattern origin is the maps' top-left corner. The first hex centre sits 4.384 in right of it and 5.0625 in down.
  - Use Align on a pattern line to match the tiling start.
  - `source/e01_model_pattern.py` re-reads the file and checks it against `face_ids.png`: all 406 joint runs have a line within 0.46 px (0.007 in) of their centre. Preview: `textures/_PREVIEW_model_pattern.jpg`.
- **Replacing the earlier maps:** material B1-01 currently points at `B1-01 - Multi texture hexagon - Sand.png` and `B1-01 - Bump - Hexagon multip textured.png`. Those are the trial's max maps, byte for byte. Repoint the material's two maps to the new files. The old files were left in place and not overwritten.
- **Atlas:** 8 columns × 7 rows = 56 flat-top hexagons at 64 px/in, a 10.125 in module across the flats (10 in tile + 1/8 in joint). It wraps exactly.

## Size assumption

A regular hexagon can't be 10 × 10, so "10 × 10 hexagon" is read as **10.000 in across the flats** (11.547 in point to point). If the tile is really 10 in point to point, every physical figure scales by 0.866: Sample Size 60.75 × 61.38 in.

## What changed from the trial's max atlas

1. **Tone, at the owner's request.**
   - **Why:** the installed (lifestyle) image reads a darker, warmer beige than the CG render.
   - **Measured tone:** lit, shadow-free Matte faces in the lifestyle image average sRGB **224.5 / 210.0 / 186.2** in linear light, against the render's 243.6 / 231.0 / 206.8.
   - **Adjustment:** one per-channel linear gain (0.831 / 0.807 / 0.791) moves the whole colour map onto that target. All variation within and between faces is kept.
   - **Joint:** now sRGB **190 / 180 / 166**.
2. **Groove stripes removed from the Chiseled colour** (review fix 1).
   - **Why:** the render's stripes are shading, which belongs to the bump, not the albedo.
   - **Method:** no groove modulation is added now, and residual stripes are removed by local demodulation at each face's own groove phase.
   - **Result:** the relative stripe fundamental is now 0.22–0.28 %, down from 0.7–1.1 %.
3. **Chiseled grooves roughened and broken up** (review fix 2).
   - **Ridge irregularity from the render:** crest height and sideways wander follow each render Chiseled face's own measured local groove fundamental. Strength cv is 0.18–0.26 and wander 0.03–0.04 period; the lifestyle measures 0.18 and 0.05.
   - **Source grain raised** from σ 0.07 to 0.20 mm and clipped deeper than it is raised, so chips remove material.
   - **Roughness-to-groove ratio** under matched raking light: 0.28 before, **0.67** now, against 1.02 in the lifestyle, whose figure includes image speckle and compression.
4. **Review fix 3 needed no change.** The "Chiseled face fades mid-face" finding was moiré in a half-scale review image; at 1:1 the grooves are even.
5. **New artifact found and fixed:** a rim of perfectly regular grooves ran round every Chiseled face. The fix samples the source 6 % further inside its clean area.

The rest of the method is unchanged. See `METHOD_FROM_MAX_TRIAL.md`.
- Raw is quilted from all 12 render Raw faces.
- Matte combines the tone of one render face with the speckle of another.
- Chiseled grooves are rebuilt from measured geometry: 5.014 mm period, 90° / 150° / 30°, asymmetric profile.
- Mix is 32 / 11 / 13, following the render's 22 / 8 / 9 complete faces.

## Results

Measured from the delivered PNGs by `source/b06_verify.py`, which exits 0 only when every gate passes. The full figures are in `textures/validation.json` and `textures/report.json`. All 7 gates pass.

| Gate | Measured |
|---|---|
| Format (PNG IHDR bytes) | Colour 4489 × 4536, 8-bit RGB. Bump and face IDs 4489 × 4536, 16-bit grey. |
| Joints | Exactly **8 px** (1/8 in) on all 168 scans. Joint area is 2.454 %, which is the theoretical figure. |
| Wrap, colour (8-bit mean step) | Left/right edge **1.22** against 0.98–1.29 at matched interior boundaries. Top/bottom **0.44** against 0.53–0.76. |
| Wrap, bump (16-bit counts) | Left/right **1379** against 919–1457. Top/bottom **237** against 439–1099. |
| Relief | Joint depth **1.60 mm**. Pattern relief (0.5–99.5 %): **Matte 0.05, Raw 1.35, Chiseled 1.41 mm**. Chiseled groove design depth is 0.70 mm; chips and grain account for the rest. |
| Clearance above the joint floor | Deepest pattern point **0.30 mm**. Lowest face pixel **0.12 mm**, at the eased edge. |
| Mix | 32 / 11 / 13 (57.1 / 19.6 / 23.2 %) against the render's 56.4 / 20.5 / 23.1 %. Chiseled rotations 0° ×5, 60° ×5, 300° ×2, 120° ×1. |
| Raw repetition | Whole faces, 12 symmetries: max NCC **0.041** (colour) and **0.054** (height). 1 in windows: **0.40 / 0.48**, against the render's own independent faces at 0.45 / 0.36. |
| Independent grader (trial harness) | 56/56 faces classified as labelled. Raw 3 in patch search max 0.28. Grooves at −60 / 0 / +60°. |
| Relief balance (`a11_contrast.py`, 15° light) | Chiseled:Raw contrast 1.35, against 1.40 for the trial atlas and 1.14 for the lifestyle. |

**Review.** I opened every image below myself, through views no larger than 800 px:
- the 1:1 colour and grazing crops of each face type;
- the whole face 29 at 1:1;
- the 25 in grazing centre;
- the 2 × 2 repeat and the four-way wrap seam panels;
- the side-by-side against the lifestyle Chiseled patch.

No seams, ghosting, stripes in the Chiseled colour, or regular-groove rims remain.

## Limitations

1. **Resolution.** The only orthographic source is a 31.3 px/in CG render, so organic texture is upsampled about 2× and looks soft at 1:1. No detail was invented.
2. **Tone.** The tone comes from a scene-lit photo-style image, so the absolute albedo is an estimate. If Revit renders look too dark or light, adjust the appearance's image fade or tint rather than rebuilding.
3. **Depths are designed.** The flat render carries no depth. Relief was calibrated against the lifestyle image, and the bump amount is unverified in Revit.
4. **Raw reuse.** 11 Raw faces come from about 8.3 faces of source. About 2 % of Raw samples are reused under an exact hexagon symmetry, as slivers. No reuse falls between touching faces.
5. **Roughness.** Chiseled roughness sits below the lifestyle figure (0.67 against 1.02) on purpose, because part of the lifestyle figure is image noise.
6. **Scope.** No ADSKLIB, RVT or V-Ray, per the owner.

## Rebuild

`python source/build_all.py` rebuilds everything from `references/` (the two manufacturer images), in about 40 minutes. Every write goes through `source/guard.py`, which refuses paths outside this folder.

**Map SHA-256:**
- Color `c9e50983b8cd97117a0c6d5cfd2f7e7a0350ea941cfb5e5ad744802d784985dc`
- Bump16 `073ff46c201266c5295aee1d1f74df52c667999fa51491c58eb5e49d90403814`
- face_ids `8d189cd4f86c3874b964755320d0270b01b9c5ef295d24571d1259dced41cce1`
