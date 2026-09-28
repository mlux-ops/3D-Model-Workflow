# Errors — ELM Formed Hexagon (Sand), high arm, 2026-09-26

Each entry covers the error, its cause, the fix and its status. All entries are resolved unless marked otherwise.

1. **The lattice search timed out (over 600 s).**
   - *Cause:* `analyse_render.py` scored about 2,650 offset candidates. Each one evaluated a hexnorm over the full image.
   - *Fix:* The offset search now uses one FFT cross-correlation per pitch, taking 80 s in total.
   - *Status:* resolved.

2. **Process kill was too broad.** *Status: side effect, cannot be undone.*
   - *What happened:* To stop the timed-out run I used `Stop-Process` on **every** `python` process. At that moment, around 00:20, it may also have stopped Python processes belonging to the other trial arms running on the same machine. I cannot tell whether any were running.
   - *Fix:* From then on I stopped only processes identified by PID, after listing their command lines.
   - *Action for the trial owner:* check the xhigh/max arms for an unexplained interrupted run at about that time.

3. **The fitted pitch was wrong (F = 755 px instead of 315 px).**
   - *Cause:* The row-profile FFT band (80–400 px periods) let a low-frequency brightness component win over the joint fundamental.
   - *Fix:* The profile is detrended, and the band is limited to the F/2 fundamental (120–250 px).
   - *Status:* resolved. The overlay check confirms the fit.

4. **The lattice fit was offset 2–4 px from the joints.**
   - *Cause:* I assumed the joints were light lines. They are thin **grey** lines, darker and less saturated than the face.
   - *Fix:* The joint response is now local-mean minus luminance, plus local-mean minus saturation.
   - *Status:* resolved. The overlay matches at opposite corners of the render.

5. **All complete faces were reported as partial (0.67).**
   - *Cause:* Wrong hexagon area from the apothem (3√3·a² instead of 2√3·a²).
   - *Fix:* Formula corrected.
   - *Status:* resolved. 39 complete faces (22/8/9).

6. **The Raw height map was all fine noise, with no relief forms.**
   - *Cause:* The σ = 3 px high-pass removed the 0.3–0.8 in forms before shading integration.
   - *Fix:* Raw now uses a σ = 12 px band (lightly smoothed against webp blocking) and a smaller share of raw luminance (0.15).
   - *Status:* resolved (visual check).

7. **A dotted dark line ran just inside every face edge in Color.png.**
   - *Cause:* The source colour and height layers were zero outside each face's safe area. Bicubic sampling at the face edge pulled in those zeros.
   - *Fix:* Every layer is extended past the safe boundary with its nearest safe pixel (a distance-transform fill).
   - *Status:* resolved (the four-way seam crop is clean).

8. **Chiseled faces went black-striped and grey overall under the grazing preview.**
   - *Cause:* The preview used Lambert shading with no ambient term and hard highlight clipping. The groove depth of 0.8 mm was also my own starting assumption, not a measurement.
   - *Fix:* The preview now has a 0.35 ambient term and a soft highlight roll-off. The groove depth is set to 0.60 mm.
   - *Status:* resolved (visual).

9. **Adjacent Matte mosaic faces (17 and 24) showed the same distinctive grey cloud.**
   - *Cause:* Both mosaics drew cells from render face 145, which was also used as a pure face.
   - *Fix:* Mosaic cells may not use a render face already used by the same face or its six neighbours. A usage map limits each source pixel to two appearances. Reused pixels are steered to areas with low low-frequency contrast.
   - *Status:* resolved (visual, plus the Matte whole-face check in report.json).

10. **`build_atlas.py` crashed with IndexError: index 3777478 is out of bounds.**
    - *Cause:* The mosaic validity check used a 1,500-point subsample of the footprint. The full footprint could leave the render, and the usage write overflowed.
    - *Fix:* The subsample is now 5,000 points, the indices are clipped, and every `map_coordinates` call uses `mode="nearest"`.
    - *Status:* resolved.

11. **The patch search found a Raw copy (NCC 0.986, face 34 vs face 21, identity transform).**
    - *Cause:* A mosaic cell's random rotation (61.1°) landed 1.1° from the pure copy of the same source (60°). A second near-miss was a mirrored pair with an angle sum of 364.6°.
    - *Fix:* Every reuse of a render face must sit at least 12° from all 12 hexagon symmetries of its earlier appearances. The comparison uses the rotation difference for the same mirror state and the rotation sum for opposite mirror states.
    - *Status:* resolved. On re-check the maximum Raw patch NCC is 0.797. The top hits are between different render faces, with no shared source pixels.

12. **Matte mosaic faces showed sharp-edged tone blotches in Color.png.**
    - *Cause:* The cells' low-frequency tone switched over the narrow 6 px detail feather.
    - *Fix:* Low-frequency tone is now cross-faded with σ = 40 px weights. Detail keeps the narrow variance-preserving blend.
    - *Status:* resolved (visual).

13. **The first wrap-seam metric was misleading (left/right ratio 1.75).**
    - *Cause:* It compared the edge step with the mean interior step. The image edges cross joint vertices, so their statistics differ from the average column.
    - *Fix:* The edge step is now compared with the steps at lattice-equivalent interior lines (x = m·W/8, y = m·H/7).
    - *Status:* resolved. Ratios are 1.01–1.16.

14. **A background check would have overwritten the report.**
    - *Cause:* `check_outputs.py` was still running on old maps while I rebuilt. It would have overwritten report.json at the end.
    - *Fix:* I stopped it by PID and re-ran it after the build.
    - *Status:* resolved.

15. **The background check was killed when the turn ended.**
    - *Cause:* I ended the turn while `check_outputs.py` was running in the background, and the session teardown stopped it.
    - *Fix:* Re-ran it in the foreground (8 min 17 s), exit 0.
    - *Status:* resolved.
