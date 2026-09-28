# Effort trial brief — ELM Formed Hexagon Tile in Sand, colour + bump

Three agents run this same brief on Opus 5.5. The only difference between them is the effort level: **high**, **xhigh** or **max**. Afterwards their outputs are graded against the gates below, reviewed blind, and their token use is compared. The owner needs a production-quality texture of this tile, so treat the work as a real deliverable.

## Product (facts, from elmsurfaces.com/product/formed-hexagon-tile-in-sand)

- **Hexagon Tile in Sand**, ELM Surfaces **Formed** collection. Nominal size "10 × 10 hexagon", **8 mm** thick. Colour: Sand (a warm cream/beige). For walls, floors, backsplashes and wet areas.
- **Finishes listed on the product page: Matte, Raw, Chiseled.** The manufacturer's lifestyle image is named `..._Hexagon_Sand_Matte_Polished_Chiseled`. Both supplied images show the three face treatments mixed on one wall:
  - **Matte:** a flat, smooth face with subtle tonal cloudiness. Most faces are this type.
  - **Raw:** an organic, sculpted, rough stone-like relief across the whole face.
  - **Chiseled:** fine parallel grooves or ridges across the face. They appear at more than one orientation (vertical, plus diagonals), probably one groove pattern laid at different hexagon rotations. Measure it rather than assume.
- **These are real designed reliefs, not image artifacts.** Never filter out a periodic pattern (grooves, ridges, lines) as noise. A previous trial failed because an agent removed a product's real ridges as "scan lines".

## Inputs (read-only, in `../inputs/`). No other images of this tile exist anywhere.

| File | Pixels | What it is |
|---|---|---|
| `elm_formed_hex_sand_layout_render.webp` | 2000 × 1888 | The manufacturer's flat, straight-on layout **render**: computer-generated artwork, not a photograph. Flat-top hexagons with thin light joints, showing the Matte/Raw/Chiseled mix. It is the only orthographic view and the best source for face layout, groove spacing and orientation, and the mix ratio. |
| `elm_formed_hex_sand_lifestyle_angled.webp` | 1414 × 2000 | A manufacturer lifestyle image (render or photo) of the tile on a bathroom wall, taken at an angle. It includes a plant, mirror, faucet, towel, countertop, strong raking light and cast shadows. It is useful for relief depth and character under grazing light, and for tone. Everything that isn't tile face must be excluded. |

## Fixed geometry (so all arms are comparable; don't change it)

- Flat-top hexagons, as in the render.
- **10.000 in across the flats** (11.547 in point to point). A regular hexagon can't be 10 × 10, so this reading of the nominal size is an assumption; note it in the README. If the tile is really 10 in point to point, everything scales by 0.866.
- Joint **1/8 in**, drawn at half width on every outer edge so the image wraps. Module across the flats is 10.125 in.
- Atlas **8 columns × 7 rows = 56 hexagons** at **64 px/in**, giving **4489 × 4536 px**.
- Revit Sample Size **70.148 × 70.875 in** (5′-10 5/32″ × 5′-10 7/8″), Repeat on in both directions.
- Choose the joint colour from the sources and record it.

## Deliverables (all inside your run folder)

- `textures/Color.png`: 8-bit sRGB RGB, 4489 × 4536.
- `textures/Bump16.png`: 16-bit greyscale height map, same size. White is high. Joints sit below the tile face.
- `textures/face_ids.png`: 16-bit greyscale, same size. Joint pixels are 0; each hexagon's pixels are its face index 1…56.
- `textures/report.json`, containing:
  - per face: `index`, `type` (exactly `"matte"`, `"raw"` or `"chiseled"`), `rotation_deg`, `mirrored`, and a `source` description;
  - the mix ratio you measured in the render and the one you used;
  - wrap-seam steps for colour and bump;
  - relief figures: pattern relief in mm per face type, joint depth in mm, and the clearance between the deepest pattern point and the joint floor in mm;
  - the suggested Revit bump amount.
- `README.md`: what was built, Sample Size, the size assumption, the joint colour, the method, relief figures, the suggested bump amount, and honest limitations.
- `SOURCE_SELECTION.md`: what you used from each source and what you rejected, with reasons.
- Review images. Open each one yourself. Never `Read` an image wider than 800 px: make ≤800 px thumbnails or crops with PIL first.
  - `textures/_PREVIEW_atlas_full.jpg` (≤ 2000 px).
  - `textures/_PREVIEW_wrap_2x2.jpg`.
  - `textures/_REVIEW_wrap_seam.jpg`: the four-way corner, magnified.
  - `textures/_REVIEW_face_types.jpg`: the atlas with each face labelled by index and type.
  - `textures/_PREVIEW_grazing_light.jpg`: the colour shaded by the bump under a low (≤ 20°) raking light, like the lifestyle image.
  - `textures/_REVIEW_crops_1to1.jpg`: one 1:1 crop of each face type, next to the matching region from the render at the same physical scale.
- `source/`: the Python build scripts. Re-running them must reproduce the maps.
- `ERRORS.md`: every error you hit, with cause, fix and status.

No ADSKLIB, no Revit, no V-Ray and no Drive upload. The winning texture is packaged separately after the trial.

## Acceptance gates

1. **Fidelity to the product.** Each face type matches its appearance in the sources at true scale. That covers Matte tone and cloudiness, Raw relief character and scale, Chiseled groove spacing, width, orientation set and profile, and the Sand colour. Designed geometric motifs (the Chiseled grooves) may be rebuilt from measured geometry, as with the fluted tiles in this repo. Organic surface (Matte cloudiness, Raw relief, fine grain) must come from source pixels, not invented noise. Don't invent face types or features the sources don't show.
2. **Relief reads as relief.** Raw and Chiseled must read clearly under grazing light; Matte stays essentially flat. Set pattern depth and joint depth as separate terms. Don't use a global bump multiplier. Pattern relief must stay above the joint floor (clearance > 0, measured).
3. **Seamless.** Colour and bump both wrap on both axes with no visible seam. Report the measured steps.
4. **Non-repeating.** No recognizable repeated face, patch or feature across the atlas or the 2 × 2 repeat. No ghosting, smearing, stretching, or visible seams inside faces. Chiseled grooves repeat by design; that's fine.
5. **Mix.** Face-type proportions follow the render, arranged without obvious clumping or pattern. Chiseled orientations follow what the sources show.
6. **Format.** Exact pixel sizes; colour 8-bit RGB, bump and face IDs 16-bit grey, checked from the PNG header bytes; joints in the specified width.
7. **Honesty.** Limitations go in the README. Nothing is claimed that wasn't measured.

## Rules for this trial

- Work **only** inside your own run folder (`../high/`, `../xhigh/` or `../max/`). Route every write through a guard that refuses paths outside it. Don't modify any other repo file, including `PROJECT_MEMORY.md`, `AGENTS.md` and `WORKFLOW.md`. Don't commit to git.
- **Don't look at earlier builds of this tile or the other arms.** Don't open, list or grep `output/hex_10in_dimensional/`, `PROJECT_MEMORY.md` entries about the 10 in dimensional hexagon, claude-mem memories about it, or `../high|xhigh|max` folders other than your own.
  - You may read `AGENTS.md`, `WORKFLOW.md`, the `3d-model-workflow` skill, and other repo precedents, such as `output/remedy_hydro/` (procedural flutes) and `output/blush_terrazzo_hex_9in/` (hex atlas geometry).
- Python has numpy, scipy and Pillow. OpenCV and scikit-image are **not** installed.
- Write Python files with the Write tool, not bash heredocs: heredocs with apostrophes or backslashes break in this shell. Use forward slashes in paths.
- Known quirk: large PNG saves sometimes fail with `OSError` errno 22. An immediate retry works.
- Don't delegate to other agents, and don't ask questions. If something is ambiguous, choose, and record it in the README.
- Stop when every gate passes and your review is done.
- Final message: under 300 words, covering what you built, each gate with its measured result, and limitations.

## How the trial is graded

- **Objective:** formats and sizes from PNG headers, wrap steps, joint width, relief clearance measured from `Bump16.png`, face-type mix, and repetition between Raw faces (whole-face comparisons over 60° rotations and mirrors, plus a random-window patch search).
- **Blind visual review:** a reviewer given these same product facts compares the atlases, labelled A/B/C, with the sources. It judges fidelity, relief under grazing light, repetition and artifacts.
- **Baseline:** the earlier build of this tile is graded alongside, for reference only.
- **Cost:** output and thinking tokens, input tokens split into cache writes and reads, turns, tool calls, wall time and list-price cost.
