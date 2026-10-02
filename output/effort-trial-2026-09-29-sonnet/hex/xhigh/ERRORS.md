# Errors and defects

Date of all entries: 2026-09-29. "Status" is what I verified, not what I expect.

## Runtime and tool errors

### E1. `s12_build_atlas.py` first run: PermissionError writing outside the run folder
- **Observed:** `PermissionError: write outside run folder refused: ...\xhightextures\Color.png`.
- **Cause:** `guard.RUN` has no trailing slash, and the script built the path as `guard.RUN + "textures/Color.png"`, giving `xhightextures`. The guard did its job and refused the write.
- **Cost:** about 90 s of build time, because the write is the last step.
- **Fix:** paths are now `guard.RUN + "/textures/..."` in `s12`, `s13`, `s14`, `s15`, `s16`, `s17`.
- **Status:** fixed and verified; every later write succeeded. A second full `s12` run reproduced all three maps with identical SHA-256.

### E2. `t_quilt.py`: ValueError on library windows of unequal shape
- **Observed:** `ValueError: all input arrays must have the same shape`.
- **Cause:** two Matte windows on the render's border were 357 x 318 px while the others were of the full window size.
- **Fix:** added `quilt.pad_windows` and the `SH`/`SW` attributes to `Library`, so windows are padded to a common shape and the padding is excluded through the mask.
- **Status:** fixed and verified; the quilt runs and the libraries are used by `s12`.

### E3. `s04_groove_measure.py`: invalid entry for face i0 j3
- **Observed:** period 1.41 px, a NaN concentration and a RuntimeWarning for the face at the left image edge.
- **Cause:** the crop window `x0 = cx - 210` went negative, so the slice came back wrong (wrapped or empty).
- **Fix:** that entry in `work/groove_measure.json` is not used. The pitch, profile and wobble come from other faces with valid windows. `s06`, `s07` and `s10` pad the image for edge faces instead of slicing raw.
- **Status:** worked around, not fixed at source: the `s04` window is still unguarded, and the invalid entry is still in the JSON. Anyone re-running `s04` will see it again; skip i0 j3.

### E4. Heredoc patch to retune `s12` constants: ModuleNotFoundError
- **Observed:** `ModuleNotFoundError: No module named 'guard'`.
- **Cause:** a stdin Python script that contained `import guard` ran from outside `source/`, so the constants were not changed, and the `s12` re-run that followed used the old values.
- **Fix:** edited the constants with the file-edit tool, then re-ran `s12` and `s13`. Confirmed by the contrast numbers changing.
- **Status:** resolved.

## Slow step (performance, not a wrong result)

### P1. `s02_fit_grid.py` took about 9 min 57 s
- **Cause:** a Python-loop `edge_points` inside a Nelder-Mead objective.
- **Result:** the fit was correct (module 314.815 px, score 6.19).
- **Status:** not changed. If a re-fit is needed, vectorise `edge_points`.

## Incorrect outputs found by measurement

### D1. First atlas: texture energy and relief too far from the sources
- **Observed:** Raw and Chiseled colour texture at about 0.5 x the render's band energy; raking-light relief about 3 to 5 x stronger than the lifestyle photo.
- **Cause:** the first height and colour gains were guesses.
- **Fix:** retuned the height and colour gain constants in `s12` using `t_contrast.py` and `t_life_contrast.py`. Current values: `K_MATTE_H` 0.006, `K_RAW_H` 0.03, `CHIS_DEPTH_MM` 0.30, `K_GRAIN_H` 0.02, `K_RAW_COL` 1.15, `K_GRAIN_COL` 1.1, `K_GROOVE_COL` 0.95. Colour band ratios atlas/render are now 0.83 to 1.11 for Matte and Raw at sigma 2 to 16 px, and 0.67 to 0.92 for Chiseled (0.67 at sigma 16).
- **Status:** improved, not eliminated. The finest colour band is still 0.60 to 0.65 of the render for Matte and Raw (2.06 x upsample), and the Raw and Chiseled raking-light preview is still about 2.1 to 2.3 x stronger than the lifestyle at the finest band. Recorded in the README as limitations.

### D2. Layout run one: an all-Matte column
- **Observed:** the first `s11_layout.py` result had a column with no Raw or Chiseled face, so the wall looked clumped.
- **Cause:** the energy function had no per-column or second-ring density term.
- **Fix:** added per-column and ring-2 density terms, and raised the annealing iterations and restarts.
- **Status:** fixed and verified; final layout (seed 15) has no empty column, no Raw-Raw and no Chiseled-Chiseled adjacency (`report.json`, `mix.layout`).

## Wrong assumptions corrected

### A1. "Ample Matte source area"
- **Observed:** recomputing the area showed Matte and Raw would need about 1.4 x reuse of the source library.
- **Fix:** quilting with a per-source-pixel reuse penalty and random dihedral block transforms instead of tiling.
- **Status:** mitigated; reuse cannot be avoided, which is why gate 4 is reported with caveats (see the README).

## Drafts corrected before running (no runtime error)

- `s03_classify.py`: the first visible-fraction expression was convoluted; rewritten before the run.
- `s13_review.py`: the first `grazing()` draft had leftover junk lines; cleaned before the run.

## Test limitations (confirmed, not failures)

- **Repeat search:** the top matches (NCC about 0.50) cannot be separated from a heavily degraded copy: a planted copy with noise at 2 x the patch std scores 0.44 to 0.46. Faces 42 and 25 share a dark micro-mark visible only after contrast stretching. Status: recorded as a limitation. Gate 4 is not claimed as a clean pass.
- **Render whole-face NCC for Chiseled pairs** reaches 0.79, which is not interpretable because periodic grooves correlate by phase. The Chiseled faces are therefore not covered by the numeric repeat test.

## Not tested

- The bump amount of 100 and the Sample Size after Revit's 1/4 in rounding: Revit is out of scope in this trial. Status: untested risk, not a failure.
- Three claude.ai connectors (Devil's Advocate, FormEdge, Meridian Connector for QuickBooks) reported needing authorisation. They were not used, and the session is non-interactive, so this needs the user to authorise them in the claude.ai connector settings if wanted. Not related to the texture work.
