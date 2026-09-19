# Remedy — Hydro (Fluted + Flat-role)

Scope: minimal Revit texture-map deliverable only — for each of two map pairs, ONE color
map, ONE bump map, and a Sample Size. No ADSKLIB, RVT, V-Ray material, ZIP, or Drive upload
was produced or attempted (explicitly out of scope for this task).

## 2026-09-18b correction — remedy_hydro_fluted rebuilt again (color + geometry-budget fixes)

A second review of the `remedy_hydro_fluted_*` pair (produced by
`source/build_maps_v2_2026-09-18.py`) found two further defects, fixed by
`source/build_fluted_fix_2026-09-18b.py` (touches only the fluted pair; the flat pair was
already correct and untouched):

1. **Color map read near-black with harsh blotchy banding, violating WORKFLOW.md's color-
   preservation rule.** Cause: v2 sampled small (~120 px tall) random crops directly from the
   accepted Fluted Silo swatch. That swatch is a real studio photo of the tile's actual
   sculpted grooves, so its raw per-row luminance genuinely swings from ~0.20 to ~0.54 purely
   from the real grooves' own directional key-light shading — not from the glaze itself
   changing color. Small random crops sometimes landed squarely in the darkest shadowed band
   of a real channel and reproduced it as a whole module's flat color, next to other modules
   that landed on lighter rows — an unintentional baked-shading artifact, exactly what
   WORKFLOW.md line ~30 and AGENTS.md ask NOT to do.
   **Fix:** detrend the swatch first (divide out its own smoothed per-row brightness trend,
   sigma ~18 px, then re-average per row) so the residual keeps only the glaze's real local
   variegation with the directional groove-shading trend removed. Per-module patches are then
   sampled from this flattened field across the swatch's FULL height band (not a narrow random
   slice) — the same technique `build_remedy_flat()` already used successfully — plus
   per-module tone jitter (+/-4.5%) for non-repetition, plus a small BOUNDED (+/-9%, vs v2's
   unbounded +/-22%) glaze-pooling tint tied to the flute profile (slightly lighter at the
   crests, darker in the channels — an intrinsic glaze-pooling effect, not simulated
   directional lighting). The assembled atlas's overall per-channel mean is then rescaled to
   match the raw (pre-detrend) swatch's own overall mean, per the "match the swatch's overall
   value" instruction.
2. **Grout-joint depth budget silently clamped, so the reported figure (0.18 mm) did not match
   the realized one.** Cause: v2's `grout_floor = max(base_level - PATTERN_AMPLITUDE/2 -
   micro_amp/2 - GROUT_DEPTH_FRAC, 0.02)` computed a value below 0 and silently clamped to the
   0.02 floor constant, quietly reducing the realized joint depth to ~0.15 mm while the report
   still printed 0.18 mm — an unreported/undetected discrepancy.
   **Fix:** the height budget was rebuilt explicitly with no clamping: a fixed bottom reserve
   (0.30 mm) is set aside FIRST for the joint (joint depth 0.18 mm + a 0.12 mm remaining
   clearance margin, asserted `> 0` in code), and the sculpted pattern then gets the entire
   remaining budget above that reserve, up to the top of the representable range — maximizing
   pattern relief within the clearance budget per AGENTS.md's 2026-09-18 rule, with every mm
   figure below being the value actually realized in the exported height map.

**Final numbers (float64 throughout, quantized only at export):**
- Height full range: 2.0 mm.
- Pattern (flute) relief: **1.70 mm** peak-to-valley (85% of the full range) — the dominant,
  pronounced feature; increased from the previous pass's 1.56 mm and now a verified,
  non-clamped realized value.
- Grout joint depth: **0.18 mm** — a separate, shallower recess, sunk below the pattern's own
  floor, active only in the joint border band.
- Remaining clearance (joint floor to the absolute bottom of the representable range): **0.12
  mm** (> 0, confirmed — the joint never overlaps or punctures through the pattern floor).
- Geometry itself (channel positions, ridge position, edge-crest shape) is unchanged from the
  previous pass and was already correct; only its color map and the joint-depth bookkeeping
  needed fixing.

No Revit validation was performed for this correction pass (out of scope, texture-only task).

## 2026-09-18 correction — see SOURCE_SELECTION.md and PROJECT_MEMORY.md

Both map pairs were rebuilt after several errors were found in the original version:

1. **Angled flute source + unreliable flute-pitch estimate.** The original
   `remedy_hydro_fluted_*` maps were built from `DAL_RD22_2x10_Fluted_Hydro_GL_LivePanel_Angle_01`,
   an ANGLED photo of a multi-row wall panel (~3 columns x 20 rows of tiles, with a dark frame
   baked around it) mislabelled as a single tile. The flute pitch/count was then "estimated" by
   autocorrelation on that same skewed photo (an unreliable signal), and the colour map baked in
   the photo's own perspective-skewed highlights.
2. **Wrong Sample Size.** Nominal (2x10 in, already the installed module) had the joint added a
   second time (2.125 x 10.125 in), and the image's pixel aspect did not represent any stated
   physical extent.
3. **Fix.** Switched to Daltile's flat, straight-on single-tile Silo swatches for both the
   Fluted and Handcrafted pieces (see `SOURCE_SELECTION.md`). The accepted Fluted swatch shows
   the tile in its installed orientation (10 in wide x 2 in tall) with **two rounded flute
   ridges stacked across the 2 in tall dimension, running the full 10 in length** — a directly
   sourced fact from a flat photo, not an estimate. Flute relief is built as a pure function of
   the across-height coordinate (independent of any photo perspective), so it is geometrically
   guaranteed straight/parallel/evenly spaced. Colour for both pairs comes from the accepted flat
   swatch's own robust (median) colour plus non-directional large-scale mottling only — no
   baked shading.

## Sample Size rule (2026-09-18)

**The Sample Size equals the real-world extent of everything the colour image actually
depicts — nothing else.** Remedy's 2x10 piece installs HORIZONTALLY (10 in wide x 2 in tall).
Both colour images here are a grid of Daltile's nominal 2x10 in installed module (module =
9.875 x 1.875 in actual tile, derived as nominal minus the stated 1/8 in joint since no actual
dimension is published + the 1/8 in joint, not joint added again on top of nominal).

- Modules: **3 tiles across x 12 rows down**, grid/stack bond (no Daltile-specified running
  bond was found, so the simplest full-bleed grid was used; stated here explicitly).
- Module (nominal, installed): 10 x 2 in = actual tile 9.875 x 1.875 in (derived: nominal −
  joint) + joint 1/8 in (Daltile Hydro page: "Grout Joint Recommendation: 1/8 in").
- Sample Size = (3 x 10) x (12 x 2) in = **30 x 24 in = 2'-6" x 2'-0"**.
- Image pixels: 1800 x 1440 (600 px per module width), aspect 30:24 = 1.25 = matches exactly.
- Same module/atlas layout and Sample Size for both the Fluted and Handcrafted (flat-role)
  pairs, since both are the same 2x10 Remedy Hydro nominal piece.

## Important scope note on "fluted and flat"

Daltile's Remedy collection hub (https://www.daltile.com/products/wall/remedy/) and the
Hydro colorway page (https://www.daltile.com/products/wall/remedy/hydro) publish only two
styles per color: **Fluted** (sculptural, ridged) and **Handcrafted** (undulated, an
irregular handmade-look surface). Both are described by Daltile as dimensional; there is no
literal flat/field SKU in this collection. Per the task's request for "fluted and flat," the
**Handcrafted** piece is used in the FLAT role below — built with only subtle relief plus the
grout joint, the same treatment as a genuinely flat tile — and this substitution is called
out explicitly rather than a flat product being invented.

## Sources

- Collection hub: https://www.daltile.com/products/wall/remedy/
- Hydro colorway page: https://www.daltile.com/products/wall/remedy/hydro
- Grout joint recommendation stated on the Hydro page: "Grout Joint Recommendation: 1/8 in"
  — applies to all Remedy pieces; used for both map pairs below.
- Full candidate list (angled/scene photos rejected, flat swatches accepted), see
  `SOURCE_SELECTION.md`.

### Fluted piece
- **Accepted**: `references/remedy_hydro_fluted_silo_2000x2000.jpg`
  (`DAL_RD22_2x10_Fluted_Hydro_GL_Silo_01`), flat single-tile swatch, 2000 x 2000 px.
- Rejected: `references/remedy_hydro_fluted_2000x2000.jpg`
  (`DAL_RD22_2x10_Fluted_Hydro_GL_LivePanel_Angle_01`) — angled multi-tile wall panel, kept in
  `references/` only as a record of the rejected source.
- Nominal size: 2 x 10 in, 1/2 in thick, glossy finish, color code RD22.
- `textures/_REVIEW_source_remedy_hydro_fluted.jpg` — the exact accepted swatch crop used.

### Handcrafted piece (used in the flat role)
- **Accepted**: `references/remedy_hydro_handcrafted_silo_2000x2000.jpg`
  (`DAL_RD22_2x10_Handcrafted_Hydro_GL_Silo_01`), flat single-tile swatch, 2000 x 2000 px.
- Rejected: `references/remedy_hydro_handcrafted_2000x2000.jpg`
  (`DAL_RD22_2x10_Handcrafted_Hydro_GL_LivePanel_01`) — multi-tile installation photo, kept in
  `references/` only as a record of the rejected source.
- Nominal size: 2 x 10 in, 3/8 in thick, glossy finish, color code RD22.
- `textures/_REVIEW_source_remedy_hydro_flat.jpg` — the exact accepted swatch crop used.

## Deliverable 1 — `remedy_hydro_fluted_*` (dimensional, sculpted flute relief)

- `textures/remedy_hydro_fluted_Color.png` — 1800 x 1440, 8-bit sRGB PNG (verified via PNG
  header: bit depth 8, colour type 2 / RGB).
- `textures/remedy_hydro_fluted_Bump16.png` — 1800 x 1440, 16-bit grayscale PNG (verified via
  PNG header: bit depth 16, colour type 0).
- `textures/_PREVIEW_tiling_remedy_hydro_fluted.jpg` — ILLUSTRATIVE wrap/seam check of the
  whole 3x12 atlas; confirmed to show only tile faces and joints, no scene content.
- `textures/_PREVIEW_grazing_light_remedy_hydro_fluted.jpg` — ILLUSTRATIVE raking-light shaded
  preview; both flute ridges per module read clearly and are confirmed straight/parallel (see
  below).

### Flute geometry (SOURCED from a flat photo, not estimated)

The accepted Fluted Silo swatch (a flat, straight-on photo of one 2x10 tile in its installed
orientation, 10 in wide x 2 in tall) directly shows **two rounded (half-round /
semicircular-profile) flute ridges stacked across the 2 in tall dimension**, running the full
10 in length. This replaces the original angled-photo autocorrelation estimate (~4 flutes)
and an interim single-flute guess made before this swatch was located. Daltile's product/spec
pages (fetched 2026-09-18) state no numeric flute-count/profile spec, so this remains a
photo-sourced reading, not a manufacturer figure, but it is sourced from a genuine flat
single-tile image rather than estimated from a skewed one.

Each flute is built as `height = f(y_within_module)` only — a pure function of the
across-height coordinate, constant along the length (x) axis — so it is geometrically
guaranteed straight and parallel. This was verified numerically: for each of the two flutes,
the row of its peak height was sampled at 5 columns spanning one module's face (avoiding the
joint band) and found identical at every column (see `source/build_report.json`,
`flutes_verified_horizontal_parallel.all_equal_per_flute`: `[true, true]`).

### Depth budget (float64 throughout, quantized only at export)

**Superseded by the 2026-09-18b correction above** — see that section for the current,
verified (non-clamped) figures: 2.0 mm full range, 1.70 mm pattern relief, 0.18 mm grout
joint depth, 0.12 mm remaining clearance. (Earlier figures of 1.0 mm range / 0.55 mm relief /
0.37 mm clearance, from the very first pass, are obsolete and kept only for history.)

## Deliverable 2 — `remedy_hydro_flat_*` (flat role, from the Handcrafted piece)

- `textures/remedy_hydro_flat_Color.png` — 1800 x 1440, 8-bit sRGB PNG (verified: bit depth
  8, colour type 2).
- `textures/remedy_hydro_flat_Bump16.png` — 1800 x 1440, 16-bit grayscale PNG (verified: bit
  depth 16, colour type 0).
- `textures/_PREVIEW_tiling_remedy_hydro_flat.jpg` — ILLUSTRATIVE wrap/seam check of the whole
  3x12 atlas; confirmed to show only tile faces and joints.

Built like the Poke bump map: subtle photo-derived surface micro-variation (+/- 0.07 of the
0..1 range) plus the grout-joint recess only — no sculpted flute geometry, since this piece
is standing in for a flat field tile. Each of the 36 modules uses an independently-cropped
region of the accepted swatch plus a small per-module tone jitter for non-repetition.

- Height full range: 0.35 mm.
- Grout floor: 0.10 of range -> grout recess depth approx 0.315 mm.

## What was inferred vs. sourced

- Sourced directly from Daltile pages: collection styles (Fluted, Handcrafted), nominal
  sizes, thicknesses, finish, color code, grout joint recommendation.
- Sourced directly from the accepted flat swatch photo: flute count (2) and general rounded
  profile.
- Inferred/estimated: exact flute profile curvature (modeled as semicircular, since no
  cross-section spec exists); actual tile dimension (9.875 x 1.875 in, derived as nominal
  minus joint, since Daltile publishes no measured/actual figure for this piece); all bump
  amplitude values (mm); the bond pattern (grid/stack bond, since no running-bond spec was
  found); that the Handcrafted piece is an acceptable stand-in for "flat" (no literal flat SKU
  exists in this collection).

## Limitations

- No orthographic reference or physical scan of either piece was available; both maps are
  built from single flat marketing swatch photos.
- Flute geometry is a modeled semicircular profile at a photo-sourced count/orientation, not
  digitized from an actual tile cross-section scan.
- No Revit validation, ADSKLIB, RVT, V-Ray export, or Drive upload was performed — out of
  scope for this task.
- Previews (tiling, grazing-light) are illustrative aids only, not native-application renders.
