# ELM ElmStone Jute Vein-Cut 24x48 Matte

Tile/chip: [48, 24] inches. Layout: stacked grid. Texture repeat: 48.062500 x 24.062500 inches. Set V-Ray UV channel 1 to these physical dimensions; do not scale a multi-tile repeat to one chip.

Color uses PrimaryBath_Wall_ELM_ElmStone_Jute_Vein-Cut_24x48.jpg. Native source detail: (1890, 945). Export: 4096 x 2051; resampling adds no photographic detail. Keep textures beside the VRMAT; Revit references this workspace's texture paths and needs repathing if moved.

Bump and RGB normal are 16-bit, calculated in floating point from smooth joints/edges, with estimated 0.15 mm relief. Printed veins remain flat. Displacement disabled. Normal is tangent-space OpenGL, linear/raw; roughness and bump linear/raw; color sRGB. Surface finish values are visual estimates, not measured PBR scans. Fine glaze/stone relief cannot be recovered reliably from one lit photo and is not fabricated from its luminance.

Use the shared Belmont_New_Tiles_R2025.adsklib and select Belmont - ELM ElmStone Jute Vein-Cut 24x48 Matte. Native V-Ray rendering requires a working Chaos license; no final native render is claimed.

## Finely-ridged bump variant — added 2026-09-20

`textures/Bump_FinelyRidged16.png` is an additional companion bump map for a second,
genuinely ridged finish option of this same colour map (a fine linear/"reeded" surface,
shown in `references/manufacturer_04_installed_ridged.jpg`). It is a new file alongside
the original; **Color.png, Normal.png, Roughness.png, Bump.png, the VRMAT and the
VRSCENE are unchanged.** To use it, point the material's Bump slot at
`Bump_FinelyRidged16.png` instead of `Bump.png` — same UV channel, same 48.0625 x
24.0625 in repeat, no other change needed. No matching normal map was built for this
variant (out of scope for this task); Revit's own Bump slot computes its normal
response directly from the greyscale bump.

- **Pixel-identical registration**: 4096 x 2051, exactly matching `Color.png`.
- **Ridges run horizontally, parallel to the veining** — user correction 2026-09-20.
  The reference install photo (`manufacturer_04_installed_ridged.jpg`) actually shows
  vertical ridges, but that is a different panel/orientation and was the wrong cue to
  follow; the shipped `Color.png`'s own vein grain was measured directly with a
  structure-tensor gradient analysis and runs at 178.4° from the image x-axis, i.e.
  horizontal, parallel to the 48 in width. Ridges are built parallel to that
  (periodic across the 24 in height, constant along the width), procedurally straight
  and parallel, not derived from either photo's pixels. See
  `SOURCE_SELECTION_ridged.md`.
- **Pitch: 2.00 mm, a stated design estimate** — no scale reference exists in the
  reference photo, so this is not a measured fact. A single constant
  (`RIDGE_PITCH_MM` in `source/build_ridged_bump.py`) controls it.
- **Relief, in a 0.55 mm encoded range**: reveal/joint floor 0.00 mm; tile plane
  (ridge valley) 0.15 mm; ridge crest 0.50 mm (0.35 mm peak-to-valley). The ridge
  valley — the pattern's lowest point — clears the reveal floor by 0.15 mm.
  Pattern relief was set on its own; the reveal floor was not touched to compensate.
- **Seamless**: the ridge field is an exact analytic period over the full pixel
  height (306 ridges across 24.0625 in), so it wraps with a measured edge step of
  0.00 against a typical row-to-row neighbour step of ~5143 (16-bit units). The
  4 px edge-reveal band matches the shipped `Bump.png` exactly, so both bump
  variants stay physically consistent companions to the one Color/Normal/Roughness
  set.
- Suggested Revit **Bump Amount ≈ 0.5–0.7** — noticeably higher than a flat finish,
  consistent with this being a genuinely dimensional linear texture rather than a
  photo-derived micro-bump.

Review evidence, all opened and inspected before delivery:
`textures/_PREVIEW_ridged_closeup.jpg` (individual ridges legible against the
existing colour), `textures/_REVIEW_ridged_wrap_seam.jpg` (four-way corner,
magnified — no seam in the ridge lines or the colour), `textures/_PREVIEW_ridged_tiling.jpg`
(2x2 wrap), `textures/_PREVIEW_ridged_grazing.jpg` (whole 48x24 in panel; aliases at
this preview's downsampled resolution since 2 mm ridges are near the display's pixel
limit at full-panel scale — not a defect in the map itself, see the close-up).
`textures/ridged_build_report.json` has the exact numbers.

Rebuild with:
```
python source/build_ridged_bump.py
python source/make_ridged_previews.py
```

**No Revit or V-Ray validation was performed on this variant.** It has not been loaded
into a material or rendered natively; confirm before using it on a live job.

## Corrected colour atlas — added 2026-09-20, revised same day per user direction

`textures/Color_NonRepeating.png` is a candidate replacement for the shipped
`Color.png`. The shipped file **wraps** (its edges match exactly) but is **not
non-repeating**: it is one photograph, so the same two vein streaks would appear
identically in every 48x24 in panel across a real wall — the failure WORKFLOW.md names
by example ("rotating one face, adding random tint... is not sufficient variation").

**Two approaches were tried and rejected before this one.** (1) Roll + flip + tone
jitter of the single photo: the same recognizable streak pair was still visible in
every cell, just repositioned. (2) Procedurally synthesised veins, statistically
matched to measurements of the real photo, replacing the layer that was causing the
repeat: this did stop the literal repeat, but the user reviewed it and rejected it on a
more important ground — it read as visibly synthetic rather than photographic, and no
amount of grain-amplitude tuning closed that gap without introducing new artifacts
(near-invisible at low gain, harsh digital noise at higher gain). **User instruction:
"it needs to be the photo based version, anything close to the deliverable is bad
looking."**

**What is actually delivered is approach (1)** — 100% real photo pixels, no synthetic
geometry — restored per that direction. The single photo is made seamlessly
self-periodic (so any cyclic roll of it is artifact-free), then each of the atlas's 9
cells gets an independent roll phase, one of the four grain-direction-preserving
transforms (identity, horizontal flip, vertical flip, 180° rotation — a 90/270 rotation
would turn the horizontal veins vertical), and a small independent tone/warmth jitter.

**Honest limitation, not fixed by this approach and not fixable without a second real
photograph**: with only one photo of this finish, there is a hard ceiling on achievable
non-repetition. The same two dominant vein streaks can still be found, differently
positioned, in every cell if the cells are compared side by side — visible in
`textures/_PREVIEW_atlas_full.jpg`. What this approach avoids is inventing content that
is not in the photo; per WORKFLOW.md's own guidance for this exact situation ("if
source images cannot support convincing variation, obtain additional faces or document
the limitation"), that second option is what's applied here. **If a second real
photograph of a different area of this stone becomes available, it should replace one
or more cells rather than this being re-processed further.**

- **9 cells (3x3), 144.1875 x 72.1875 in total, 9228 x 4620 px, 64 px/in.** This is a
  new, larger Sample Size than the shipped single-panel `Color.png` — see "What still
  needs reconciling" below before treating this as a drop-in replacement.
- Cell-to-cell joints use the same reveal-grey (209, 209, 209) band as the shipped
  `Color.png`'s own edges (measured directly from its pixels), at the same ~0.047 in
  width. Two adjacent cells' half-bands combine into one full reveal, matching how real
  adjacent panels actually meet; the outer perimeter of the whole atlas gets the same
  half-band, which is why the atlas wraps exactly (L/R and T/B step 0.000 against a
  typical interior step of ~6.3) with no additional blending.
- Every cell's specific roll/flip/tone-jitter combination is recorded in
  `textures/nonrepeating_flat_report.json` for reproducibility.

**What still needs reconciling before this is a full replacement delivery**: `Bump.png`,
`Normal.png` and `Roughness.png` remain sized to the single 48.0625 x 24.0625 in panel,
as does the finely-ridged `Bump_FinelyRidged16.png` added earlier in this same session.
None of the four match `Color_NonRepeating.png`'s new 144.1875 x 72.1875 in extent. The
VRMAT and VRSCENE still reference the old `Color.png` and the old repeat size. Bringing
the whole material up to the new atlas size (rebuilding or re-tiling the other three
maps to match, and updating the VRMAT's UV channel 1) is a follow-on task, out of the
explicit scope of "create the color maps" — flagged here rather than silently left
inconsistent.

Review evidence, all opened and inspected before delivery:
`textures/_PREVIEW_atlas_full.jpg` (all 9 cells at once — the residual repeat of the
photo's two dominant streaks is visible here, per the honest limitation above),
`textures/_PREVIEW_wrap_2x2.jpg` (36 virtual panels), `textures/_REVIEW_wrap_seam.jpg`
(four-way corner, magnified), `textures/_REVIEW_cell_grid.jpg` (every cell labelled).
`textures/nonrepeating_flat_report.json` has the exact numbers.

Rebuild with:
```
python source/build_nonrepeating_color.py
python source/make_nonrepeating_previews.py
```
(the same script also builds the paired cross-cut product; see
`../ElmStone_Jute_CrossCut_24x48/README.md`.)
