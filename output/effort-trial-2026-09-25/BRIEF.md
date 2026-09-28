# Effort trial brief — ElmStone Jute Cross-Cut non-repeating colour atlas

Two agents run this same brief on Opus 5.5. The only difference between them is the effort level: one runs at **high**, the other at **xhigh**. Afterwards their outputs are graded blind against the gates below, and their token use is compared.

The task replays the hardest texture job this repo has handled offline. It took five sessions and one user-reported regression. The requirements below are the ones the owner finally accepted.

## Product

- ELM Surfaces ElmStone Jute, **cross-cut** finish, 24 × 48 in matte porcelain wall tile, stacked grid. Cross-cut means a mottled, cloudy stone face with no directional veining.
- Joint: 1/16 in. Joint/reveal colour: sRGB (209, 209, 209).
- One panel repeat including its joint: 48.0625 × 24.0625 in.

## Inputs (read-only, in `../inputs/`)

| File | Pixels | What it is |
|---|---|---|
| `crosscut_swatch.webp` | 2000 × 875 | Manufacturer swatch photo of the cross-cut face. Assume it spans roughly the full 48 in panel length, about 41.7 px/in. Record the scale you use. |
| `crosscut_floor_angled.jpg` | 2000 × 349 | High-resolution photo of an installed floor of the same cross-cut tile, taken at an angle, so the perspective is skewed. It is the only other real photo of this finish. |

## Deliverable

Build one seamless, non-repeating colour atlas for Revit:

- `textures/Color.png`: 8-bit sRGB RGB, **9228 × 4620 px**. That is 3 × 3 panels at 64 px/in. Revit Sample Size **144.1875 × 72.1875 in** (12′-0 3/16″ × 6′-0 3/16″).
- `README.md`: what was built, the Revit Sample Size, the scale assumptions, the method, and honest limitations.
- `textures/report.json`: gate measurements, including wrap-seam steps (L/R and T/B) against the typical interior neighbour-pixel step, plus the source and transform used for each cell.
- Review images, which you must open and inspect yourself before you finish:
  - `textures/_PREVIEW_atlas_full.jpg`: the whole atlas.
  - `textures/_PREVIEW_wrap_2x2.jpg`: a 2 × 2 repeat of the atlas.
  - `textures/_REVIEW_wrap_seam.jpg`: the four-way wrap corner, magnified.
  - `textures/_REVIEW_cell_grid.jpg`: all 9 cells, labelled.
- `source/`: the Python build script or scripts. Re-running them must reproduce `Color.png`.
- `ERRORS.md`: every error you hit (failed command, bad output, failed check), with its cause, fix and status.

No bump, normal or roughness maps, no ADSKLIB, no V-Ray, no Revit and no Drive upload. This is a test run.

## Acceptance gates

1. **Photographic only.** Every pixel must come from the two supplied photos. Allowed: crop, resample, flip, roll, perspective correction, blending between real photo regions, and gentle tone/warmth adjustment. **Not allowed:** procedurally synthesized veins, mottle, clouds, grain or noise. The owner has rejected synthetic stone content as "CG-looking" before, and any fabricated texture fails this gate.
2. **Perspective.** Correct the floor photo's perspective before using it. State the method and how you validated it.
3. **Seamless.** The atlas wraps on both axes with no visible seam. Report the measured wrap steps.
4. **Non-repeating.** No recognizable repeated block or feature across the 9 cells, or across the 2 × 2 repeat. No ghosting, double exposure, smearing or visible stretching artifacts.
5. **Scale.** Stone detail sits at true physical scale (64 px/in in the atlas). Resample from each source's physical scale; don't tile native pixels unscaled.
6. **Format.** Exact pixel size, 8-bit RGB PNG, and the joint drawn in the specified colour and width.
7. **Honesty.** Known limitations go in the README. Nothing is claimed that wasn't measured.

## Rules for this trial

- Work **only** inside your own run folder (`../high/` or `../xhigh/`). Don't modify any other file in the repo, including `PROJECT_MEMORY.md`, `AGENTS.md` and `WORKFLOW.md`. Don't commit to git.
- **Don't look at the previous solution.** Don't open, list or grep `output/belmont_tiles/ElmStone_*`, the ElmStone/Jute entries in `PROJECT_MEMORY.md`, claude-mem memories about ElmStone or Jute, or the other agent's run folder. You may read `AGENTS.md`, `WORKFLOW.md`, the `3d-model-workflow` skill, and other `PROJECT_MEMORY.md` entries.
- Don't delegate to other agents, and don't ask questions. If something is ambiguous, choose, and record the assumption in the README.
- Known machine quirk: saving large PNGs sometimes fails with `OSError` errno 22. An immediate retry works.
- Stop when every gate passes and your review is done. Don't polish beyond the gates.
- Final message: under 300 words, covering what you built, each gate with its measured result, and remaining limitations.

## How the trial is graded (after both finish)

- **Objective:** PNG format and size, joint colour and width, wrap steps, and cross-cell similarity (the maximum normalized correlation between any two cells, including flipped versions).
- **Blind visual review:** a separate reviewer sees the two atlases as A and B, next to the source photos, and judges photographic authenticity, repetition and artifacts against the gates.
- **Cost:** from each agent's transcript: output tokens (including thinking), input tokens split into fresh input, cache writes and cache reads, turns, tool calls and wall time.
