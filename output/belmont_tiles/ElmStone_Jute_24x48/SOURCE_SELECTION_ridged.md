# Source selection — finely-ridged bump variant

Two images were supplied by the user on 2026-09-20, alongside the request for a new
ridged bump variant of the already-delivered ELM ElmStone Jute Vein-Cut 24x48 material.
No product page or additional candidates were available.

| # | file | px | view type | verdict | reason |
|---|------|----|-----------|---------|--------|
| 03 | `references/manufacturer_03_flat_swatch.webp` | 2000 × 875 | flat, seamless stone-look swatch | **REJECTED for this task** | Matches the character of the already-shipped `Color.png` (same vein-cut travertine look) but carries no ridge texture at all. Not used: the shipped colour map already covers this, and a second colour rebuild was not requested. |
| 04 | `references/manufacturer_04_installed_ridged.jpg` | 1052 × 631 | near-frontal installed product photo, sink + mirror + faucet in frame | **ACCEPTED — direction and fineness only** | The only image showing the ridged finish. Used to confirm the ridges run **vertically** and are very fine and regular. **Not used for a measured pitch**: there is no object of known size in the frame, so no px-to-mm calibration exists. Two clean crops (x470-700 and x830-1040, away from the mirror and faucet) gave self-consistent pitches top-to-bottom within each crop (5.23 px and 4.88 px respectively, both checked at two different heights with no vertical drift — i.e. no evidence of vertical foreshortening), which supports the ridges being straight and evenly spaced, but the two crops disagree with each other by about 7%, consistent with ordinary horizontal camera-angle perspective at this scale. That disagreement is exactly why no mm value was taken from this photo. |

## What was actually built

The ridge geometry is **procedural**, not derived from either photo's pixels, per this
repo's established fluted-tile precedent (`output/remedy_hydro`): a pure function of the
across-ridge coordinate, so it is exactly straight, parallel and periodic by
construction. The **2.00 mm pitch is a stated design estimate** for a "finely ridged"
linear/reeded finish, not a measured fact. If a manufacturer spec or scaled reference
photo becomes available, `source/build_ridged_bump.py` takes the pitch as a single
constant (`RIDGE_PITCH_MM`) and can be rebuilt immediately.

**Orientation correction, 2026-09-20**: the first build ran the ridges vertically,
following reference 04's apparent direction. The user corrected this: the ridges must
run **parallel to the veining**, not to whatever direction the install photo happened to
show — that photo is a different panel/orientation and was the wrong cue for direction.
The shipped `Color.png`'s vein grain was then measured directly (structure-tensor
gradient analysis, not by eye) and runs at 178.4° from the image x-axis — horizontal,
parallel to the 48 in width. The ridges were rebuilt to match. Reference 04 is retained
only as evidence that the finish is fine and regular, not for its direction.

No new colour, normal or roughness map was produced. The shipped `Color.png`,
`Normal.png` and `Roughness.png` are unchanged and are reused as-is with the new bump.
