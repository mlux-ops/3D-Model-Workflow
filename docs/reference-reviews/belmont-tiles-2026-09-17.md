# Belmont preferred tiles — appearance review, 2026-09-17

Subsequent correction: user requested implementation; see [R2 review](../../output/belmont_preferred_bath2_bath3_r2/REVIEW.md). The baseline observations below describe the preserved R1, not the corrected R2.

Reviewed the companion Material_Overview.jpg, manifest.json, generator scripts/build_preferred_tiles.py, and saved revit_validation.json for output/belmont_preferred_bath2_bath3/651_Belmont_Preferred_Tiles_R2025.rvt. The native file was not reopened or rendered in this review. Saved validation establishes prior bindings and scale, not current visual acceptance.

The generator constructs a 2 x 2 atlas for every material. All six therefore repeat a fixed four-tile block. The supplied overview displays these blocks rather than a room-sized repetition test. None is accepted under the new seamless/non-repeating requirement.

| Material | Evidence and finding | Required revision |
|---|---|---|
| B2-01 Palette Seafoam | One photographed face rotated four ways; block repeats every 12.125 x 12.125 in. Cloudy markings recur in rotated positions. | More independent faces and a larger varied layout; remove source lighting without flattening glaze character. |
| B2-02 Gems Caraibi | Four crops only about 102 x 204 native pixels each; repeat 10.125 x 20.125 in. Baked reflections are documented. | Better orthogonal face references, lighting correction, varied layout preserving six-strip direction. |
| B2-03 Bottega Caliza | One face rotated four ways; repeat 47.0541 in square. Rotations preserve the same identifiable surface features. | Independent faces and a varied installation; preserve 596 mm tile dimensions. |
| B3-01 Grounded Alabaster wall | One face with alternating 0/180-degree rotations; repeat 48.125 x 24.125 in. Repeated clouding is visible in the overview. | Independent face variation and room-scale layout with valid tile orientations. |
| B3-02 Ligne Noir | Four narrow panel crops, 156–168 x 583 pixels, stretched to nominal proportions; repeat 6.125 x 20.125 in. Captured shading repeats with the block. | Rectified/de-lit face references and varied layout preserving vertical flutes; verify relief separately. |
| B3-03 Grounded Alabaster floor | Same source/map content as B3-01, with separate material assignment. | Apply the same corrected product treatment and validate a floor-sized installation. |

Seamlessness is **pending**, not a confirmed failure: the generator places half grout joints at cell edges and uses shared color/bump layout, but that does not establish artifact-free filtered appearance or relief under lighting. Intentional grout and flute repetition should remain.

Next acceptance requires wrapped-map previews, room-scale and multiple-atlas repetition review, and native rendered checks described in WORKFLOW.md. The current request's workflow change is implemented; the original RVT, maps, and package remain unchanged and require material revision before a new final delivery. No new final material/model package was produced by this review.
