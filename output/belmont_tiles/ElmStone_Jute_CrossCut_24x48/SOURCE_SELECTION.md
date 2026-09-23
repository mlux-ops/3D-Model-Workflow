# Source selection — ELM ElmStone Jute Cross-Cut 24x48 (new product)

Introduced 2026-09-20 as a new finish of the ElmStone Jute product line: the same
stone, cut across the bed (cross-cut) instead of along it (vein-cut), which the user
stated shows **no directional veining**. Two references now exist.

| # | file | px | view type | verdict | reason |
|---|------|----|-----------|---------|--------|
| 06 | `references/06_new_fluted_crosscut.webp` | 2000 × 875 | flat, seamless-looking stone-look swatch | **ACCEPTED** | Mottled, isotropic cloud/blotch pattern with no linear streaks — confirmed visually and consistent with the user's "no directional veining" description. This image is identical (re-compression aside; mean pixel difference 0.6/255) to an image supplied earlier in this same session and originally mislabelled as a second flat/vein-cut swatch — it is in fact the cross-cut reference, per the user's clarification. |
| 07 | `references/07_new_floor_angled_crosscut.jpg` | 2000 × 349 | **angled** floor installation photo, moderate perspective, two off-frame shadow blobs top-right | **ACCEPTED, perspective-corrected** | Supplied 2026-09-20 as "the only other cross cut image I have," explicitly angled. Per WORKFLOW.md ("correct photographic perspective and baked lighting while preserving the product's actual color and character") this was rectified rather than rejected outright — see below — because it is a genuine second real photograph of this material, which the atlas badly needed (see "Why a second source mattered"). |

No manufacturer page or further candidates exist.

## Perspective correction of reference 07

Four grout joints running "away" from the camera were found with a weighted Hough line
search over a locally-darker-than-surround mask (the same grout-isolation approach used
elsewhere in this repo). Their pairwise line intersections agreed to better than 2 px,
giving a vanishing point at (1144.0, -933.4) in image pixels — strong evidence these are
genuinely parallel real-world joints, not a coincidental fit. A second, independent
check confirmed it: these joints are very evenly spaced at the bottom (closest) row
(528/537/527 px), and the standard ground-plane prediction that image spacing scales
with `(y - vanishing_point_y)` matches the measured spacing at a distant row to within
0.1% (predicted ratio 1.303 between two rows, measured 1.303).

Rectification used a **locally-isotropic simplification** of the standard
single-vanishing-point ground-plane formula (the full metric version needs the camera's
tilt/focal length, which one photo can't supply, and this is texture extraction, not a
survey): straighten the joints and correct the depth compression using the same local
magnification factor at every row, referenced to the closest (highest native-resolution)
row so nothing is upsampled beyond its own captured detail — only the farther, more
compressed rows are stretched to undo their compression. Full derivation and code:
`../ElmStone_Jute_24x48/source/rectify_floor_photo.py`. Result: `references/07_floor_rectified.png`
(2000 × 301) — joints now run perfectly vertical and evenly spaced (visually confirmed).
A shadow visible in the original's top-right corner was checked and found not to
contaminate the result (a numeric brightness check found 0.02% of pixels below a
shadow-level threshold, and that residual is outside the three crops used below).

Three clean, joint-free crops were then cut from the rectified image for use as
additional atlas sources: `07_crop_tile1.jpg` (488×288 px), `07_crop_tile2.jpg`
(495×288 px), `07_crop_tile3.jpg` (490×288 px) — each from a different one of the first
three visible tiles, each independently verified joint-free by eye.

## Why a second source mattered, and a defect it caused and fixed

The atlas is a 3x3 grid; with only ONE real photo (06), even the best photo-based
technique (roll + flip + tone jitter) has a hard ceiling: the same dominant blob is
still recognizable, just repositioned, in every cell. Adding the three floor-photo
crops as additional independent sources (each cell now draws from one of 4 real photos,
not 1) meaningfully raises the achievable variety while remaining 100% photographic.

**Defect found and fixed on review**: the first attempt applied the same
`make_tileable_rgb` (half-period cross-fade) and roll treatment used for the large
06/05 photos to these small crops too. `make_tileable_rgb` blends an image's own
left/right and top/bottom halves together so any roll of it is seamless — invisible on
a large photo whose own edges already look similar, but on a small, arbitrary crop it
produced an obvious ghosted double-exposure band, worsened by the crop then being
stretched 5-7x to fill a full cell. Fixed in `build_nonrepeating_color.py`: any source
under 40% of the cell's pixel dimensions skips both the periodicity blend and the roll
(it's simply resized once and used, with only flip and tone jitter applied) — there is
no benefit to making a crop "roll-safe" when it is never rolled.

**Known, disclosed quality difference**: the three floor crops (native ~288 px tall)
are stretched about 5.3x to fill a 1540 px cell height, versus about 1.6-1.8x for the
06/05 photos (native 875-945 px). Cells drawn from the floor crops are visibly softer on
close inspection (see `textures/_REVIEW_wrap_seam.jpg`) — a genuine resolution
limitation of the second source's short capture height, not a synthetic-content defect.

## History: two rejected approaches before this one

A first attempt (roll + flip + tone jitter of photo 06 alone) left the same large soft
cloud blob recognizable in nearly every cell of the 3x3 atlas, just repositioned or
mirrored — the "not sufficient variation" failure WORKFLOW.md names explicitly. A second
attempt fixed that with **procedurally synthesised mottle** (randomly placed soft blobs,
statistically matched to the photo's measured contrast) but was rejected by the user on
a different, more important ground: it read as visibly synthetic rather than
photographic. **User instruction: "it needs to be the photo based version, anything
close to the deliverable is bad looking."** Full detail on both in the git/session
history; what matters going forward is what's below.

**What is delivered**: 100% real photo pixels, no synthetic geometry, drawn from FOUR
independent real photos (06 plus the three floor crops above) rather than one — which is
what actually improves on the first attempt's repetition ceiling, per "why a second
source mattered" below.

## What was measured, and used, from the accepted photos

- Base RGB (photo 06): (243.9, 238.8, 225.2).
- No directional component in either photo: confirmed both visually (no linear streaks
  anywhere in either frame) and by there being no single dominant orientation — this
  justified using all four aspect-preserving transforms (not just two, as the
  vein-cut finish must) when building the atlas.
- Every cell's specific source, roll offset, transform and tone/warmth jitter is
  recorded in `textures/nonrepeating_crosscut_report.json`, reproducible from the
  source photos alone.

## Transform constraint

The panel's 2:1 physical aspect ratio (48.0625 x 24.0625 in), not grain direction, is
what limits the atlas construction to the same four aspect-preserving transforms used
for the flat finish (identity, horizontal flip, vertical flip, 180° rotation) — a 90/270
rotation would swap width and height and require stretching the pattern back to 2:1,
which would visibly distort it regardless of whether the material has directional
grain. See `../ElmStone_Jute_24x48/source/build_nonrepeating_color.py` for the shared
build code (both finishes are produced by the one script).

## What this new product does not yet include

Only a colour map exists (`textures/Color.png`, 9228 x 4620 px, 144.1875 x 72.1875 in,
3x3 cells of 48.0625 x 24.0625 in). No bump, normal, roughness, VRMAT, VRSCENE, or
Revit/ADSKLIB entry has been built for this finish. This was explicitly out of scope for
"create the color maps" and is recorded here as pending, not implied complete.
