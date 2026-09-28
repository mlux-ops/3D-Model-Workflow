# Errors and findings: ELM Jute Vein-Cut 24x48 + 1x3 mosaic, 2026-09-26

Each entry gives the artifact or action, the observed error, the cause, the fix and the status. Also appended to
`PROJECT_MEMORY.md`.

1. **Inline Python print (source research), tool error.**
   - Observed: `UnicodeEncodeError: 'charmap' codec can't encode character '≤'` while printing MILE page text.
   - Cause: `PYTHONIOENCODING=utf-8` was left off one command, so the Windows console fell back to cp1252.
   - Fix: re-ran with the variable set.
   - Status: resolved.

2. **Brief premise check: u09 vs the older 05 file (finding, not a defect).**
   - Observed: u09 is not the same photo as `05_new_flat_veincut.jpg` (NCC 0.34 to 0.37). u09 is the same photo as `jute_original.jpg`, PrimaryBath, ELM w01 and MILE w04 (0.99 or more).
   - Observed: 05 is a second, genuinely different face, but in a much paler colour (239/233/219).
   - Observed: `manufacturer_03` is the ridged cross-cut 06 (0.998), not a vein-cut swatch.
   - Fix: 05 is used as face B, re-toned to the Jute colour of its own halves in the MILE panel w05.
   - Status: recorded in SOURCE_SELECTION.md.

3. **`b03_verify.py` joint gate, 24x48 (verifier false failure, maps unchanged).**
   - Observed: the first run failed with a joint width of 4.0 px, against a design of 4.5 px.
   - Cause: the gate estimated coverage as `1 - h/h_edge`. With a 4.5 px joint, the edge pixel is 75 % face, but its eased-edge height is above `h_edge`, so it counted as 0 % joint.
   - Second attempt: widths from the colour profile read 5.3 to 5.5 px. Cause: the face level was averaged over both sides, and neighbouring tiles differ in tone.
   - Fix: face level taken per side, then the width fitted by least squares against the restated eased-edge section, using each joint line's mean bump profile. The colour-profile width is kept as a sanity check.
   - Result: 4.500 px on every line.
   - Status: resolved.

4. **`b03_verify.py` joint gate, mosaic (verifier false failure, maps unchanged).**
   - Observed: colour-profile widths of 4.2 ± 1.4 px per segment, against a design of 3.0 px.
   - Cause: a light, low-contrast grout, a short 38 px segment and ±9 % chip tone, so single segments are noise.
   - Fix: average along each whole joint line, plus the bump-model fit from item 3.
   - Result: 3.000 px on every line; colour sanity check 3.17 ± 0.15 px.
   - Status: resolved.

5. **Mosaic, first build, own review of `_PREVIEW_colour_tiled3x3.jpg`.**
   - Observed: random chip placement left low-frequency clusters of light or dark chips. Repeated 3 x 3, these can act as landmarks for the eye.
   - Fix: `b11` now re-orders chips on the grid with random pair swaps, which halves the sd of the low-passed chip-luminance field (0.0099 to 0.0049 log). It stops there, so the grid is not driven towards a regular pattern.
   - Status: resolved. No crop was changed or reused.

6. **Drive wait, tool error (logged after the packages were built, so not in the zipped copy).**
   - Observed: a foreground `sleep 100` in Bash was blocked by the harness.
   - Cause: foreground sleeps are disallowed (a known rule).
   - Fix: background wait plus Monitor.
   - Status: resolved.

## Disclosed limitations (not errors)

- **Actual tile size is not published.** ELM, MILE (page, catalog, brochure and tech specs) give nominal sizes only. Used 600 x 1200 mm, the Florim metric rectified convention.
- **Joint recommendation is not published.** Used 1/8 in (24x48, assumption). The mosaic uses 1/16 in, measured on the MILE sheet and u11.
- **24x48: only 6 distinct real faces exist in the published imagery.** Each face appears 3 times in the 18-tile atlas, in different flips (never touching itself, including across the wrap). The W windows each share a 12 to 17 % corner area with face A, because the 48x110 slab photo contains the 24x48 swatch.
- **Grout colour (208/198/180) is a design choice.** It is cued by u11, where the grout reads close to the face tone. Pass `R,G,B` to the build script for a variant.
