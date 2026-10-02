# Nodes Angled Wall Sconce KW1041MBK, Midnight Black / Milk: Revit 2025 face-based lighting fixture

Kelly Wearstler for Visual Comfort Studio (Lightology spec VCS833919). One family, one type, Midnight Black / Milk finish only.

## Result

Gates 1 to 6 pass on the saved RFA in a headless Revit 2025 (25.4.50.35); `validation.json` has `all_native_gates_pass: true`. Gates 7 and 8 are review gates. The gate 7 review below is my own, not a blind judgement.

| Gate | Measured result |
|---|---|
| 1 Native | The RFA reopens with 0 warnings. Category Lighting Fixtures, placement type WorkPlaneBased, one type `KW1041MBK - Midnight Black / Milk`. |
| 2 Hosting | Placed on the exterior face of a wall (`Generic - 4" Brick`, from `Default-Multi-discipline.rte`). Backplate back face 0.000 in from the wall face, projection 5.4996 in, the instance Z axis equals the wall's exterior normal. |
| 3 Envelope | Disc on: 8.0000 W x 7.6301 H x 5.4996 D in. Disc off: 5.2500 x 5.2500 x 5.4996 in. Socket, Body, Backplate and Shade are unchanged with the disc off, and the Disc solid is absent. See the caveat below. |
| 4 Parts | Backplate 5.25 x 5.25 x 0.125 in. Shade maximum diameter 3.50 in, 3.25 in along its axis. |
| 5 Materials | Default: Body 4, Backplate 4, Socket 4 and Disc 6 faces in Midnight Black; Shade 6 faces in Milk Glass. After substituting test materials in `Metal Finish` and `Glass Finish`, the same faces carry the substitutes; they were restored afterwards. |
| 6 Light | One light source at (0, -0.3443, 3.4453) in the family frame, 2e-5 in from the intended point. Inside the shade (26 of 26 rays end on shade or socket, nearest wall 1.18 in). 3 W, nonzero intensity. |
| 7 Fidelity | My own review against the photos: see "Fidelity review". |
| 8 Honesty | Every dimension is labelled Published, Measured, Derived or Inferred in the table below. Where photo and published values disagree, the published value is kept and both are listed. |

**Caveat on gate 3.** Revit adds the light source's symbol to this family's placed-instance geometry (other families were not tested). It is a 24 in sphere centred on the light (2 faces, 7238.2 in3, subcategory Light Source, symbol size read-only). `get_Geometry` with `Options()` defaults, DetailLevel Fine, `IncludeNonVisibleObjects` and `get_BoundingBox(null)` all return it, so an unfiltered envelope of the placed instance reads 24 x 24 x 24 in. A view-bound `Options` in a section-boxed view returns it clipped (1214.4 in3). It is not fixture hardware and is hidden in the exported views. `validation.json` therefore measures the envelope from the five named part solids, matched by graphics style. It also lists the raw all-solids envelope and the excluded solid (`G3_envelope`, `geometry_option_probe`). A checker that filters the Light Source subcategory gets 8.00 x 7.63 x 5.50 in. A checker that takes every solid gets 24 in from this family, because it carries the light source the brief requires.

## Files

| Path | Content |
|---|---|
| `Visual_Comfort_Nodes_KW1041MBK_Midnight_Black_R2025.rfa` | The family (483,328 bytes). |
| `source/` | pyRevit IronPython 2.7 scripts that reproduce the RFA: `build_sconce.py` (build), `common.py` (constants and helpers), `validate_sconce.py` (native gates and views), `run_validation.py` (validation only), `guard.py` (write guard). `probe_light.py`, `probe_light2.py` and `probe_light3.py` are the light-source discovery record, see `ERRORS.md` items 6, 7, 12, 13 and 16. |
| `validation.json` | Native Revit checks: gates, part sizes, light source, option probe, warnings. |
| `views/` | Revit PNG exports: `family_front`, `family_side`, `family_oblique` (family editor, disc on), `hosted_on_wall_front`, `hosted_on_wall_side`, `hosted_on_wall_oblique` (placed instance, disc on), `hosted_no_disc_front`, `hosted_no_disc_side`, `hosted_no_disc_oblique` (placed instance, `Show Disc` = No). `_REVIEW_compare.jpg` is the side-by-side against the photos. |
| `SOURCES.md` | What was used from each input and what was rejected. |
| `ERRORS.md` | Every error, cause, fix and status. |
| `_work/` | Python 3 analysis helpers, registered overlays (`overlays/`), PDF renders (`pdf/`) and small JSON records of the measurements quoted below. Scratch outputs (`thumbs/`, `candidates/`) were deleted at the end; the helpers recreate them, and `cand_sheet.py` needs a build run first. |

## Reproduce

Every Revit run goes through the shared serialized runner. Build, save and validate (about 35 s):

```
python E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/_harness/revit_run.py E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/max/source/build_sconce.py 540
```

`build_sconce.py` builds the family from `Generic Model face based.rft`, saves the RFA, then calls `validate_sconce.run_all`, which reopens the file, places it in a disposable project, writes `validation.json` and exports the views. Validation of the saved RFA alone (about 25 s): the same command with `source/run_validation.py`. The runner exit code does not prove success: read `_work/build_result.json` and `validation.json`. The comparison sheet is rebuilt outside Revit with `python _work/make_compare.py`.

## What the family contains

Family frame: X across the host face, Y up the host face, Z out of the host face (host plane at Z = 0). Inches.

| Part | Solid | Subcategory |
|---|---|---|
| Backplate | Cylinder R 2.625, Z 0 to 0.125. | Backplate |
| Body | Cylinder R 2.155 from Z 0.125, its front cut by a plane through CF = (0, 0.0832, 2.1122) with normal N = (0, -0.3054, 0.9522), tilted 17.78 degrees from the wall normal, out and slightly down. | Body |
| Socket | Collar R 0.79, 0.22 high along N, standing on the cut face at CF. | Socket |
| Disc | Annulus, outside R 4.00, hole R 0.79, 0.04 thick, back face on the cut plane, top edge leaning out. A true extrusion, so its Visible property is linked to `Show Disc`. | Disc |
| Shade | Hollow sphere shell about the axis through CF along N. Sphere centre at axial 1.72, outer R 1.75, inner R 1.65, open neck at axial 0.22 (outer r 0.9014, inner r 0.6874), outer pole at axial 3.47. | Shade |

The solids are built with `GeometryCreationUtilities` (extrude, revolve, boolean difference) and added as native forms; there are no imported meshes, DWG or SAT. The face-based template's placeholder host slab (an Extrusion, 96 x 96 x 12 in, id 1537) is left as shipped. It stands in for the wall in the family editor, is not one of the five parts and does not appear in the placed instance's geometry.

Parameters:

- `Metal Finish` (Material, group Materials) drives Backplate, Body, Socket and Disc. Default `Midnight Black`.
- `Glass Finish` (Material, group Materials) drives the Shade. Default `Milk Glass`.
- `Show Disc` (Yes/No, **instance**, group Visibility), default Yes, drives the Disc's visibility.
- Identity: Manufacturer `Visual Comfort Studio`, Model `KW1041MBK`, a Description with size, lamp and location data, and Type Comments stating that the family is a visualisation built from published dimensions and photos. `Lamp` and `Wattage` are left empty because the brief does not ask for them.

Materials are generic appearance assets with no bitmaps. `Midnight Black`: diffuse 32/32/35, glossiness 0.45, reflectivity 0.05 at 0 degrees and 0.5 at 90 degrees, class Metal. `Milk Glass`: diffuse 242/240/232, glossiness 0.9, rendering transparency 0.35, shaded-view transparency 0, class Glass.

## Dimensions and their basis

P = published (Lightology spec sheet and product page, agree with each other). M = measured from an image. D = derived by calculation from P and M values. I = inferred by judgement, not measured. Confidence is my estimate of how close the modelled value is to the real product.

| Dimension (in) | Modelled | Label | Basis | Confidence |
|---|---|---|---|---|
| Overall width | 8.00 | P | Spec 8" W. The disc is the only part that can reach it. | High |
| Overall height | 7.6301 | P | Spec 7.63" H, produced by the disc tilt below. | High |
| Overall projection | 5.4996 | P | Spec 5.5" D (projection from the wall). The shade's foremost point sits at Z = 5.4996. | High |
| Backplate | 5.25 dia x 0.125 | P | "Round, 5.25" Dia x 0.125"D". Photos show a thicker plate, see limitations. | High for the diameter, medium for the thickness |
| Shade diameter | 3.50 | P | Spec "3.5" Dia". Photo fit 3.47. | High |
| Shade height | 3.25 along its axis | P | Spec "3.25"H", read as the length along the shade's axis. | Medium (the axis reading is my interpretation) |
| Lamp, power, location | 1 x JCD/G9 3 W 120 V LED, bulb not included, standard dimming, damp | P | Spec sheet. | High |
| Disc diameter | 8.00 | D | The widest element must match the published width, and only the disc can. | Medium-high |
| Disc tilt | 17.78 degrees | D | Solves 8 cos(t) + 0.04 sin(t) = 7.63 for the published width and height. Cross-check M: the cut-face edges on the matte-white side photo fit 15.6 degrees (upper) and 19.0 degrees (lower), mean about 17.3. | Medium-high |
| Disc thickness | 0.04 | M/D | Rim band on the hero photo reads about 0.03 (median 0.030, mean 0.043, n = 13, plus or minus 0.01). 0.04 is the nearest round value above Revit's short-curve tolerance (0.0307 in, read from the API). | Medium |
| Disc hole radius | 0.79 | I | Equal to the socket collar: the install sheet shows the plate screwing onto the socket. | Medium |
| Body diameter | 4.31 | M | Matte-white side photo, registered on the plate height (5.25 in = 241.7 px/in). The final registered fit (`_work/side_metrics.json`) reads 4.26, which is 0.05 in smaller than modelled. | Medium-high |
| Cut-plane position (CF) | (0, 0.0832, 2.1122) | M | Cut-face position on the side photo, registered on the plate. Registered on the plate front, the upper cut-face edge deviates -0.009 in and the lower -0.033 in from the photo. | Medium-high |
| Shade centre | 1.72 along the axis from CF, 0.442 below the plate centre | M | Circle fit to the globe on the side photo: centre 0.445 below the plate centre in the photo, 0.443 in the model. | High |
| Socket collar | 1.58 dia x 0.22 high | I | Seen in the photos as a short cylindrical neck between the cut face and the globe. Height is the least certain value. | Low-medium |
| Shade wall | 0.10 | I | Not visible in any image. | Low |
| Shade neck | Opens at axial 0.22, r 0.9014 outside | D/I | Truncating the 3.5 in sphere 1.5 in below its centre gives the published 3.25 in height. The opening size follows from that. | Medium |
| Light position | 1.40 along the axis from CF | I | Centre of a G9 capsule in the globe. | Medium |

## Light source

The Light Source property of the family is set to Yes, which creates the source element (id 3202 in the reopened family). Revit has no on/off parameter for a family light source, so "on" means the source exists and its initial intensity is nonzero; the gate reads both.

- Shape Point, distribution Spherical.
- Initial intensity: `InitialWattageIntensity`, 3.0 W at 90 lm/W = 270 lm. The 90 lm/W is my assumption for an LED lamp: the bulb is not included and the spec gives only the wattage.
- Colour: custom 2700 K (assumed warm white, same reason).
- Light loss factor 1.0.
- Position (0, -0.3443, 3.4453) in the family frame, which is 1.40 in along the shade axis from the cut-face centre. The shade cavity spans axial 0.22 to 3.37 and its inner radius at the light is 1.6187 in, so the point is inside the shade.
- The template default (Line shape, 9.29 W, 148.54 lm/W, 3200 K) was replaced.
- There is no solid bulb: the product ships without one.

## Fidelity review (gate 7)

I compared the exported views with the photos on `views/_REVIEW_compare.jpg` (rows: front, side, angled; columns: photo, model, model in a second view) and on registered overlays in `_work/overlays/`. The photos of the disc-less matte-white version are compared with the model hosted on a wall with `Show Disc` = No. The Midnight Black hero photo is compared with the model with the disc on.

**Side** (registered on the plate height and plate front only; nothing else fitted, `_work/side_metrics.json`):

- Body top and bottom edges within 0.03 in (top -0.029, bottom +0.025), registered on plate height and centre.
- Cut-face plane within 0.01 to 0.03 in of the photo (upper edge -0.009, lower -0.033), registered on the plate front.
- Globe diameter 3.50 in the model against 3.47 in the photo.
- Globe centre 3.617 in out from the plate front in the model against 3.628 in the photo.
- Depth from the plate front 5.370 in both, to the pixel (0.004 in).
- Silhouette IoU 0.82, registered on plate height and back face only. The thicker plate in the photo and its edge artefacts lower it; nothing was fitted to raise it.
- The cut-face angle in the model (17.78 degrees) sits between the photo's upper and lower edge fits (15.6 and 19.0), so the tilt is right on average but the photo shows the two edges slightly non-parallel.

**Front:** the layout matches: round plate, cut-face ellipse, globe in the lower half. The photo's globe is about 8 % larger and lower than the model's, consistent with the photo's perspective and its roughly 4 to 5 degree pitch. I did not fit a camera to the front photo.

**Angled** (hero photo, disc on): the disc's size and tilt, the dark body behind the disc on the left, and the globe in front of the disc's lower left follow the photo. Globe to disc size ratio is 0.46 in the photo and 0.445 in the model. The globe's offset from the disc centre is about 0.20 disc heights in the photo against 0.165 in the model, a difference of about 0.27 in (0.035 disc heights of 7.63 in). I could not resolve this: the side photo supports the modelled globe position to 0.01 in, so I left the geometry unchanged. Candidate causes are perspective shifting the fitted ellipse centre and camera-fit ambiguity.

**Rendering, not geometry:** Revit's shaded style shows the milk-glass sphere grey on its lower left, where the photographed lamp glows white. The materials are generic with no bitmaps, so the disc has no satin sheen and reads as flat black.

## Decisions where the brief left a choice

1. `Metal Finish` and `Glass Finish` are **type** parameters. Revit convention, and the type name carries the finish, so another finish would be a sibling type. The brief calls only `Show Disc` an instance parameter. A script that sets them through an instance lookup finds nothing and must read them from the family symbol. To make them instance parameters, change the last argument of the two `AddParameter` calls at `source/build_sconce.py` lines 315 to 316 to `True` and rebuild.
2. The disc is 0.04 in thick, not the measured 0.03 in, so it stays above the short-curve tolerance (0.0307 in). I did not build a 0.03 in disc.
3. Published values win over photo values (plate 0.125 in, depth 5.50 in).
4. The envelope is measured from the five named parts (see the gate 3 caveat).
5. The light is a point source at the lamp centre without a solid bulb.
6. The disc is a true extrusion so that `Show Disc` can drive its visibility; the other parts are free-form forms built from solids.

## Limitations

- **Plate thickness and depth.** The photo shows a plate about 0.257 in thick against the published 0.125 in, and a projection of 5.63 in from the back face against the published 5.50 in. The 0.124 in difference is the plate thickness. Registered on the plate front, the depths agree. I kept the published values.
- **Tilt.** The photo's two cut-face edges differ (15.6 and 19.0 degrees, mean 17.3), the model uses 17.78 degrees from the published width and height.
- **Body diameter** is 0.05 in larger than the final registered photo reading.
- **Shade position in the angled view** differs from the hero photo by about 0.27 in, unresolved.
- **Not modelled:** the screw head visible on the photographed backplate, edge breaks and fillets, mounting hardware, the junction box, the lamp. The disc is a flat annulus with no raised rim, none was visible.
- **Inferred values** (collar height, shade wall, light position, disc hole) have low to medium confidence; the table says which.
- **Materials** are generic appearance assets with no bitmaps, so they do not show the photographs' sheen.
- **Family editor preview.** Setting `Show Disc` with `FamilyManager.Set` in the family document does not hide the disc in family-view exports (the exported file was byte-identical); the cause is unknown. It works on the placed instance, where the disc is absent with `Show Disc` = No and returns when it is set back to Yes. The no-disc previews therefore come from the placed instance.
- **Light source symbol.** See the gate 3 caveat. The symbol size is read-only, so an unfiltered geometry read of this family's instance reads 24 in.
- **Light photometrics** (90 lm/W, 2700 K) are assumptions.
- **Gate 7 was judged by me, not blind.**
