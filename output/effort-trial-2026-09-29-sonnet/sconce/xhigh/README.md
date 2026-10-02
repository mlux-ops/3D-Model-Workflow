# Nodes Angled Wall Sconce, KW1041MBK, Midnight Black / Milk — Revit 2025 family

`Visual_Comfort_Nodes_KW1041MBK_Midnight_Black_R2025.rfa`: native Revit 2025 family, category **Lighting Fixtures**, built from `Generic Model face based.rft`, placement type **WorkPlaneBased**. Real solids only (no imports). Type `KW1041MBK - Midnight Black / Milk`. Manufacturer `Visual Comfort Studio`, Model `KW1041MBK`. All validation was run in headless Revit 2025 (25.0.2.419) through `_harness/revit_run.py`; every number below is in `validation.json` (raw data in `work/validation_raw.json`).

## What is in the family

| Part (subcategory) | Solid | Material parameter | Faces |
|---|---|---|---|
| Backplate | disc 5.25 dia x 0.125 on the host face | Metal Finish | 4 |
| Body | drum 4.24 dia, from the plate to an angled cut plane | Metal Finish | 4 |
| Socket | short neck 1.06 dia x 0.56 at the cut face | Metal Finish | 4 |
| Disc | 8.00 dia x 0.094 steel disc on the cut face, 1.06 dia centre hole | Metal Finish; visibility = Show Disc | 6 |
| Shade | hollow milk-glass sphere R 1.75 truncated at 3.25 along its axis, open at the base | Glass Finish | 6 |
| Light source | Revit light source at the lamp | n/a | 2 |

Parameters: `Metal Finish` and `Glass Finish` (type, Material; defaults `KW1041 Midnight Black` RGB 34/32/32 gloss 0.42, class Metal, and `KW1041 Milk Glass` RGB 244/240/234 gloss 0.62, class Glass). `Show Disc` (**instance**, Yes/No, default Yes). I chose instance so one type can be placed with and without the disc. The finishes are type parameters because a finish is a product variant. Also `Lamp` (`JCD/G9/3W/120V LED`), `Wattage Comments` (`3 W`), `Apparent Power` (3.00 VA), `Light Source Symbol Size`.

**Placement.** The family projects along +Z out of the host face, with family Y up. To place it upright, pass `referenceDirection = up x faceNormal` (on a wall with exterior normal +Y that is (-1,0,0)). Reference direction +X gives an upside-down fixture (family Y -> world -Z); this is measured (`FacingOrientation` (0,0,-1)). Upright, the disc leans with its top edge further from the wall than its bottom edge, so its face looks down and out.

**Show Disc.** The visibility parameter takes effect in project instances only. A family-document view ignores it (exports with Show Disc = No were pixel-identical to Yes), so the disc-off views in `views/` come from a hosted project (`source/render_hosted_off.py`).

## Dimensions and their basis

Confidence: high = published or verified to under 0.01 in by Revit measurement; medium = read from an image or drawing, roughly 0.05 in; low = assumed.

| Dimension | Value (in) | Basis | Confidence |
|---|---|---|---|
| Overall width | 8.00 | published (disc diameter) | high |
| Overall height | 7.63 | published; not modelled directly, it fixes the cut angle (below) | high |
| Overall projection | 5.50 | published; sets the shade position along the axis | high |
| Backplate dia x thickness | 5.25 x 0.125 | published | high |
| Shade max dia, axial height | 3.50, 3.25 | published | high |
| Disc dia | 8.00 | published | high |
| Disc cut angle | 18.179 deg | inferred: solved from H = 8 cos(t) + 0.094 sin(t) = 7.63 for a flat circular disc | medium |
| Cut-plane centre depth | 1.975 | measured on the install-sheet vector drawing as the mean of the top (2.65) and bottom (1.30) body-edge depths | medium |
| Body dia | 4.24 | measured on the install-sheet vector drawing | medium |
| Disc thickness | 0.094 | measured on the install-sheet vector drawing (0.094 to 0.10) | medium |
| Socket dia x length | 1.06 x 0.56 | measured on the install-sheet vector drawing | medium |
| Shade base flat dia | 1.8028 | derived: truncating R 1.75 to 3.25 axial height | high (derived) |
| Shade sphere centre | 1.50 from the base | derived from the same truncation | high (derived) |
| Shade base offset along the axis | 0.368 | derived: it makes the apex land at the published 5.50 projection | medium |
| Glass wall thickness | 0.10 | **inferred**; no source states it. The shade must be hollow, otherwise Revit reports "light source inside solid geometry" | low |
| Lamp lumens, colour temperature | 250 lm, 2700 K | **assumed** (typical 3 W G9 LED); no source states them | low |

The install sheet is an exploded diagram with no stated scale. I converted its vector coordinates with the published parts drawn on it, and I did not keep a separate record of which reference I used; treat the four drawing-measured values as +/-0.05 in estimates.

## Light source

One Revit light source, Point, Spherical distribution, **250 lm** (assumed), **2700 K** (assumed), light loss factor 1.0, symbol size 0.05 ft. It sits at the shade sphere centre (family coordinates (0, -0.583, 3.75)); measured distance from that centre in a placed instance is 3e-15 in, with 1.29 in clearance to the inner glass after the 0.36 in symbol radius. 3 W and 3 VA are recorded in the parameters. "On" here means the source exists with a positive flux and Revit reports no light-inside-solid warning; the family has no on/off switch.

## Validation results (all in `validation.json`)

| Gate | Result |
|---|---|
| 1 Native | reopens with 0 warnings; Lighting Fixtures; WorkPlaneBased; one type; 483,328 bytes; project warnings after load, place and views: none |
| 2 Hosting | placed on a wall's exterior face; backplate at 0 to 0.125 in from the face; fixture out to 5.4998 in; face reference present |
| 3 Envelope | instance `get_BoundingBox` 8.000 W x 7.630 H x 5.500 D (deviation under 1e-15 in); tessellated 8.0000 x 7.6300 x 5.4998. Show Disc off: 5.25 x 5.25 x 5.4998; no other part moves (0.0 in for all five) |
| 4 Parts | backplate 5.25 dia x 0.125; shade outer sphere fit R 1.7500 (max dia 3.5000), axial height 3.2500 (residual under 3e-6 in); body dia 4.24; socket 1.06 |
| 5 Materials | Metal Finish swap changes Backplate, Body, Disc and Socket only; Glass Finish swap changes the 6 Shade faces only; restoring the defaults restores every face |
| 6 Light | 1 source, 250 lm, inside the shade cavity, no warning |
| 7 Fidelity | reviewed by me, not blind; passes with the deviations below |
| 8 Honesty | this table and `SOURCES.md` |

`Solid.GetBoundingBox` is loose on curved solids (8.1256 x 7.7556 x 5.5, +1.57 % per side); I did not use it for any gate. The envelope numbers use the instance bounding box and face tessellation.

## Fidelity, honestly

The angled view was compared by registering the black-variant photo to the model. A least-squares camera fit (`source/fit_camera_black2.py`, cut angle fixed at 18.18 deg) matched the disc rim to RMS 3.1 px and the shade sphere to RMS 1.6 px (about 0.03 in and 0.016 in), and `work/match_overlay.png` shows the rendered model over the photo. That is a fit with seven free camera parameters, not an independent check. Roll and elevation are degenerate: roll -14.5 deg with elevation 6.5 deg (camera C) fits slightly better than roll 0 with elevation -12.4 deg (camera D, the level-camera reading). Both are in `views/`.

Deviations I measured and did not fix:

- Shade apex: 5.66 in from the wall in the photo (side photo, plate 5.25 in as scale), against the published 5.50. The model keeps the published 5.50.
- Shade centre: 3.92 in from the plate back and 0.44 in below the plate centre in the photo, against 3.75 and 0.58 in the model.
- Drum: about 15.6 deg cut angle in the photo, against 18.18 deg (fixed by the published 8.00 x 7.63), and about 0.35 in longer at mid-length. The photo's drum reaches further left in the overlay (RMS about 15 px, 0.15 in, on the plate and drum silhouette).
- The white-finish photos show no 8 in disc, so the side and front comparisons use Show Disc = No.
- Revit's views are parallel projection; the photos have mild perspective (fitted about 0.011 per inch of depth).
- The shade in the photo glows because it is lit; the model is a plain shaded render.
- The room photo `833919_additional.jpg` gave no usable form.

## Limitations

- Materials were checked in Shading mode only; Realistic and ray-trace renders were not run (headless Revit's Realistic export is unreliable). Appearance values (colour, gloss, reflectivity) are my estimates from the photos, not manufacturer data.
- The glass wall thickness, lamp lumens and colour temperature are assumptions (table above); no photometric file exists for the fixture.
- The family views show the template's grey host slab, which cannot be hidden in the face-based template. Hosted views hide walls and show the fixture alone.
- The three drawing-measured dimensions have medium confidence, as stated.
- Not tested: Revit 2024 or earlier (the file is a 2025 family), nested-family use, rendering on other walls (only a straight vertical wall was used), and the family loaded into a real project with a material library.
- One 15-minute runner stall occurred during the build (`ERRORS.md`).

## Files and rebuild

- `source/build_sconce.py` builds the family and the three family-view exports; `source/validate_sconce.py` reopens it and runs the hosted checks; `source/render_hosted_off.py` and `source/render_hosted_match.py` render the disc-off and photo-matched views; `source/finalize.py` builds `views/`, `_REVIEW_compare.jpg` and `validation.json`. `source/guard.py` restricts every write to this folder.
- Run a Revit script with `python E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/_harness/revit_run.py <absolute script.py> <timeout_s>`; the script's own JSON says whether it succeeded, not the exit code.
- `views/`: `front`, `side`, `oblique` (family document, disc on), `hosted_on_wall*` (project, disc on), `hosted_disc_off_*` (project, Show Disc = No), `hosted_photo_match_C` and `_D_level` (project, photo-fitted camera), and `_REVIEW_compare.jpg`.
