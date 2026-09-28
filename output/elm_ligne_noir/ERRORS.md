# ELM Vivid Ligne Noir build: errors and fixes (2026-09-26)

Every entry is also logged in `PROJECT_MEMORY.md`.

## Errors in the previous Ligne Noir deliverables

These were found while sourcing this build.

1. **Sep 25 package `ELM_Ligne_Noir_3x10_Color_Bump_Maps.zip`: wrong tile size.**
   - Cause: it treated the nominal 3 x 10 in as the module and assumed a 1/16 in joint. The Nemo brochure gives an actual size of 2.75 x 9.66 in, and both spec sheets recommend a 3/16 in joint.
   - Effect: its tiles were 2.94 x 9.94 in, so 7 % too wide and 3 % too long.
   - Fix: this build. The old package is superseded but kept on Drive.
2. **Sep 25 package: wrong bump amount.**
   - Cause: it quoted 0.4, a stored-value decimal. The Revit editor rounds that to 0 (see the 2026-09-26 bump-scale entry).
   - Fix: this build quotes the editor value, 100.
3. **Belmont B3-02 R2 maps: made from an image-generated glaze field and perspective panel crops.**
   - Their size was the nominal 3 x 10 with a 1/16 in joint.
   - They are left untouched in the Belmont folder under the owner's names.

## Errors during this build (all resolved)

4. **The Bash `cd` changed the session's working directory twice.** No files were affected. From now on, absolute paths only.
5. **A reference size listing printed nothing.**
   - Cause: Windows Python was given `/e/...` paths, so the glob matched nothing.
   - Fix: use `E:/` paths.
6. **`fftconvolve(mode="valid")` raised ValueError.**
   - Cause: the resampled template was larger than the search image.
   - Fix: crop the template.
7. **False "same photo" correlation.**
   - The first check gave an NCC of 0.89–0.95 for both orientations, because the rib period dominated.
   - Fix: remove along-rib structure before correlating. The result, 0.76 at 180° and 0.04 otherwise, shows the retailer swatch is the ELM photo rotated.
8. **Quilt broadcast error.**
   - Cause: the patch loop overran the accumulator.
   - Fix: pad the accumulator by 2 patches.
9. **Wood-grain streaks in the colour map.**
   - Cause: residual rib shading ran along the ribs in the de-lit swatch, with a relative sd of 0.185.
   - Fix: subtract a 0.5 in running mean along the ribs. The relative sd is now 0.084, and I checked the result at 1:1.
10. **The verifier crashed writing JSON.**
    - Cause: numpy bools.
    - Fix: cast them to `bool`.
11. **The verifier's edge half-joint probe sat on a horizontal joint row** and reported 40 px.
    - Fix: probe at mid-tile. It now reads 10 + 10 px.
12. **Nemo product-page URLs returned 404.**
    - Fix: the collection page led to the brochure PDF, which has the actual size.

## Limitations (not defects)

- There is one glaze source photo. All 48 faces are quilted from about 9.3 x 2.5 in of real glaze, in 0.48 in patches. The faces are distinct (max NCC between tiles 0.01), but no large-scale glaze clouding is represented.
- The relief depths (1.5 mm ribs, 1.2 mm field above the grout) are designed; no section drawing exists. The rib shape is taken from photos.
- The joint is 3/16 in per the spec, although ELM's own photo looks nearer 1/16 in.
- The grout colour is ELM's photographed grout (near-white). It is baked into the colour map, so a different grout needs a rebuild.
