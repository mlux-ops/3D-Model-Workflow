# Errors and fixes: Porcelanosa Vendome Nature 47x47 build (2026-09-27)

Each entry: date, artifact/action, observed error, cause, fix, status. Copied to PROJECT_MEMORY.md under
"Porcelanosa Vendome Nature 47x47 build — 2026-09-27".

1. 2026-09-27, `source/a00_thumbs.py`: `TypeError: Object of type IFDRational is not JSON serializable` when writing
   `_work/thumbs/index.json`. Cause: Pillow returns the JPEG `dpi` as IFDRational objects. Fix: cast to float.
   Status: resolved (rerun passed).
2. 2026-09-27, research: WebFetch of the Porcelanosa technical data sheet (FTEC PDF) returned "unable to extract,
   binary PDF". Cause: the fetch summariser cannot read PDFs. Fix: the tool had saved the PDF; copied it to
   `references/Porcelanosa_FTEC_100348304_EN.pdf` and read it with the Read tool. Status: resolved.
3. 2026-09-27, source colour (risk found, not a failure): all 9 supplied JPEGs carry an **Adobe RGB (1998)** ICC
   profile. Reading them as sRGB would have shifted the colour (over-saturated, darker mid-tones in Revit).
   Fix: `source/colour_io.py` decodes Adobe RGB -> XYZ -> linear sRGB in float64 before any processing.
   Status: resolved by design; the verifier re-derives the conversion.
4. 2026-09-27, `source/b02_previews.py`, whole-map grazing-light bump preview: a fine diagonal hatching over every
   tile face. Cause: preview aliasing, not the map. The first version resized a mode-"I" integer image after
   shading; the second shaded a 4x block mean and then Lanczos-resized to 800 px. The 1:1 graze crop showed no
   hatching, and a 2-D FFT of a piece bump found no periodic peak (max 23x median, the noise expectation for
   2 M bins; no 8.5 px JPEG-block grid). Fix: 8x float block mean, shaded at the final size, with no resize after
   shading; a zoom of the result shows grain only. Status: resolved; the maps were unchanged.
5. 2026-09-27, `source/b03_verify.py`, wrap gate, first version: colour and bump steps across the wrap were 0.0,
   and the same was true of interior joints. Cause: the step was measured between the two pixels next to the image
   edge, and both are grout (a 1 px half joint on each side), so the gate could not fail. Fix: measure between the
   face pixels that flank each joint (column 1 against W-2; interior x-2 against x+1). Status: resolved.
6. 2026-09-27, `source/b03_verify.py`, wrap gate, second version: FAILED on designed (0.102 against 1.5 x 0.060)
   and on all 8 pieces. This was a false failure. Causes: (a) designed: the wrap mixes a vein-continuous vertical
   joint with a non-continuous horizontal one, but it was compared with a mean over mostly continuous interior
   joints; (b) pieces: a single-piece map has no interior joint, and was compared with the face's own 3 px step.
   Fix: compare each wrap direction with interior joints of the same direction. For single pieces, compare with
   the source photo's own opposite-edge step, which is the joint the product shows when a piece meets itself.
   Built and source agree within 1 %. The largest is piece 8's top against bottom, 0.233 against 0.234: piece 8
   is darker along its bottom edge, which is product content. Status: resolved; the maps were unchanged. The README
   discloses the piece-8 step.
