# ELM ElmStone Jute Cross-Cut 24x48 (new product, colour only)

New finish entry in the ElmStone Jute line, added 2026-09-20: the same stone cut across
the bed instead of along it, showing a soft mottled/cloud pattern with **no directional
veining** (per the user), as opposed to the linear vein-cut finish in the sibling
`../ElmStone_Jute_24x48/` folder.

## Deliverable

`textures/Color.png` — 8-bit sRGB, 9228 x 4620 px, **144.1875 x 72.1875 in** (a 3x3 grid
of 48.0625 x 24.0625 in cells), 64 px/in. PNG header verified: depth 8, colour-type 2.

This is the only asset in this product folder. No bump, normal, roughness, VRMAT,
VRSCENE, ADSKLIB entry, or Revit setup has been built — out of scope for the task that
created this ("create the color maps... for the fluted and flat"). See
`SOURCE_SELECTION.md` for exactly what each reference photo was, and was not, used for;
see `../ElmStone_Jute_24x48/source/build_nonrepeating_color.py` for the build (the same
script produces both this finish and the corrected flat finish).

## How it was built

**Photo-based, per user direction 2026-09-20** ("it needs to be the photo based version,
anything close to the deliverable is bad looking" — a procedural-mottle approach was
tried first and rejected for looking synthetic). 100% real photo pixels, no synthetic
geometry. Full history of the two rejected approaches is in `SOURCE_SELECTION.md`.

**Two real photos**, not one: the original straight-on swatch (06), plus a second photo
the user supplied — an angled floor installation shot — perspective-corrected using a
single-vanishing-point ground-plane rectification (grout joints found by a Hough line
search agree on one vanishing point to sub-2-pixel precision; full derivation in
`source/rectify_floor_photo.py`). Three clean, joint-free crops were cut from the
rectified result, giving **four independent real-photo sources** in total. Each of the
atlas's 9 cells draws from one of the four; the two larger photos (06, and the flat
finish's own 05) additionally get an independent roll phase (safe because they're made
seamlessly self-periodic first), while the three smaller floor crops are used directly
(rolling a small arbitrary crop produced a visible ghosting artifact on the first
attempt — fixed by skipping roll/periodicity for any source under 40% of a cell's
pixel size). Every cell also gets one of the four aspect-preserving transforms
(identity, horizontal flip, vertical flip, 180° rotation) and a small tone/warmth
jitter.

- **9 cells (3x3), real photographic detail throughout, drawn from 4 independent real
  photos** — a meaningful improvement over the single-photo repetition ceiling.
  Confirmed across the whole atlas, a 2x2 repeat (36 virtual panels), the four-way wrap
  corner, and a labelled per-cell grid.
- **Seamless by construction**: the same reveal-grey (209, 209, 209) border used by the
  sibling flat product's `Color.png` is stamped on every cell edge, so adjacent cells
  meet the way real installed panels meet and the whole atlas wraps exactly — measured
  L/R and T/B wrap step 0.000 against a typical interior step of ~3.7-3.8.
- Base colour measured from reference 06: (243.9, 238.8, 225.2).
- **Honest limitation, reduced but not eliminated**: the same dominant blob from any one
  source photo can still be found, differently positioned, in more than one cell if that
  source happens to be picked twice — now a 1-in-4 chance per pair instead of certain.
- **Disclosed quality variation**: the three floor-crop cells are visibly softer on
  close inspection than the swatch-photo cells, because the floor photo's usable crop
  height (~288 px) needs a ~5.3x stretch to fill a cell versus ~1.6-1.8x for the swatch
  photos. This is a genuine resolution limitation of that source, not synthetic content.

Review evidence, all opened and inspected before delivery: `textures/_PREVIEW_atlas_full.jpg`,
`textures/_PREVIEW_wrap_2x2.jpg`, `textures/_REVIEW_wrap_seam.jpg` (also where the
softness difference above is visible), `textures/_REVIEW_cell_grid.jpg`.
`textures/nonrepeating_crosscut_report.json` has the exact numbers, including every
cell's specific source, roll/flip/jitter values.

Rebuild with (from the sibling product's `source/` folder):
```
python ../ElmStone_Jute_24x48/source/rectify_floor_photo.py   # only if 07 changes
python ../ElmStone_Jute_24x48/source/build_nonrepeating_color.py
python ../ElmStone_Jute_24x48/source/make_nonrepeating_previews.py
```

## Limitations

- No manufacturer page or SKU. Two real photos, both user-supplied: a straight-on swatch
  and an angled floor shot (perspective-corrected — see `SOURCE_SELECTION.md`).
- The floor photo's rectification uses a locally-isotropic simplification, not a full
  metric ground-plane solve (that needs the camera's tilt/focal length, unavailable from
  one photo). It removes the visually dominant defect (converging, unevenly-spaced
  joints) but is not claimed to be metrically exact.
- No physical joint width was specified for this finish; the same 1/16 in reveal
  convention as the sibling vein-cut product was reused for consistency, not measured
  for this specific finish.
- No Revit or V-Ray validation of any kind — this folder currently holds a colour bitmap
  only, not a usable Revit material.
