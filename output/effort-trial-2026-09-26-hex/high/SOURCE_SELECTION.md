# Source selection — ELM Formed Hexagon Tile in Sand

The brief supplies two images. No other images of this tile were used.

## `elm_formed_hex_sand_layout_render.webp` (2000 × 1888, CG layout render): the only pixel source

**Used:**
- **Lattice and scale.**
  - Method: flat-top hex lattice fitted to the drawn joint lines with FFT correlation (`analyse_render.py`).
  - Result: module 314.87 px across the flats, which is **31.10 px/in** at 10.125 in per module.
  - Check: the overlay matches at opposite corners.
- **Faces.**
  - The render holds 39 complete faces and 20 partial faces of at least 10 % area on the edges.
  - Classification uses high-pass energy and structure-tensor coherence, checked on a contact sheet (`textures/_REVIEW_render_faces.jpg`).
  - Result: **22 Matte, 8 Raw, 9 Chiseled** among the complete faces.
- **Duplication check.**
  - The render's same-type faces were compared under all 12 hex symmetries (`check_source_duplicates.py`).
  - Raw faces are distinct from one another (maximum window NCC 0.22), so the 8 Raw faces are 8 independent samples.
- **Matte:**
  - colour (tone and cloudiness), with no alteration apart from resampling;
  - bump: fine grain only (difference of Gaussians) at 0.010 mm std.
- **Raw:**
  - Colour, with 75 % of the high-frequency baked shading kept. Reducing it lets faces rotate without the baked light direction fighting the bump.
  - Height from the render's own shading. The shading gradients of all 8 Raw faces share one axis: lower-left ↔ upper-right, at an image angle of 150°. The band-passed luminance is integrated along that axis (regularised Fourier division).
  - Re-shading the height map correlates with the source shading at r ≈ 0.70.
- **Chiseled: groove geometry measured per face** from a windowed 2-D FFT with sub-bin refinement:
  - Period **5.04–5.06 mm (0.199 in)** on all 9 faces.
  - Orientations **89.6–89.8°, 149.7–150.4° and 29.6°**, i.e. one vertical groove design laid at the three hexagon rotations.
  - Cross-section profile measured by folding each face's pixels over its demodulated phase.
  - Local amplitude and phase are kept from the source, which preserves the broken, chisel-mark irregularity; the source residual adds the rest.
- **Joint colour.** The darkest 20 % of core pixels on the drawn joint line give **RGB (206, 198, 184)**, a light warm grey. The render draws the joint thinner than 1/8 in (about 2 px ≈ 0.06 in), so only the colour was taken, not the width.
- **Partial edge faces.** These were made available to the Matte and Raw mosaic faces as extra, otherwise unused pixels.

**Rejected:**
- **Joint geometry and joint shading.** The drawn line is symmetric CG line-work with no depth cue. Joint depth is a design value (1.6 mm), not a measurement.
- **The render's global exposure** was taken as the Sand base colour without changes. No tone correction was invented.

## `elm_formed_hex_sand_lifestyle_angled.webp` (1414 × 2000, angled bathroom scene)

**Used (reference only, no pixels):**
- It confirms the three face treatments and the groove orientations: vertical grooves plus diagonals, matching the render's 90/150/30°.
- It shows how the reliefs read under raking light, which I used to judge the grazing preview. Raw reads as a coarse, scaly stone relief, Chiseled as fine, slightly irregular grooves, and Matte as flat.
- It confirms the light, low-contrast joint.

**Rejected as a pixel source:**
- Every face is strongly foreshortened by the oblique view, roughly 0.5–0.6 horizontal compression. Rectifying it would stretch the pixels about 2× in one axis, which conflicts with the no-stretching gate.
- Strong raking light and cast shadows from the plant, mirror and faucet are baked in. They are inconsistent with the render's frontal lighting.
- The usable Raw faces are partly occluded by the plant.
- Everything that is not tile face (plant, mirror, faucet, towel, countertop, shadows) was excluded by not using the image's pixels at all.

## What was not used

No earlier builds of this tile, no other arms' folders and no project-memory entries about the 10 in dimensional hexagon were opened. Repo precedent consulted: `output/blush_terrazzo_hex_9in` (the hex atlas geometry approach and the bump-amount note) and WORKFLOW.md (dimensional-tile relief guidance).
