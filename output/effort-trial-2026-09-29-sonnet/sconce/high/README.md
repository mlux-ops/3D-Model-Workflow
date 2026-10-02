# Visual Comfort Studio Nodes Angled Wall Sconce, KW1041MBK, Midnight Black / Milk

Native Revit 2025 family: `Visual_Comfort_Nodes_KW1041MBK_Midnight_Black_R2025.rfa`.
Category Lighting Fixtures, placement WorkPlaneBased (face-based, hosts on a wall face). Type `KW1041MBK - Midnight Black / Milk`. Manufacturer `Visual Comfort Studio`, Model `KW1041MBK`.

## Family contents
- Five real solids, each in its own subcategory: Backplate, Body (drum with slanted face), Socket, Disc, Shade.
- Type material parameters `Metal Finish` (Backplate, Body, Socket, Disc; default `KW1041MBK - Midnight Black Metal`) and `Glass Finish` (Shade; default `KW1041MBK - Milk Glass`).
- Instance Yes/No parameter `Show Disc`, default Yes. It drives the visibility of the Disc solid only.
- One light source (see below).
- Frame: Z = 0 is the host face and +Z points out of the wall. X runs across the wall, Y is up.

## Dimensions (inches)
Basis: **published** = stated by the manufacturer/retailer; **measured** = scaled from the product photos against a published dimension; **inferred** = my choice where nothing states it.

| Dimension | Value in model | Label | Basis | Confidence |
|---|---|---|---|---|
| Overall width | 8.00 (disc diameter) | published | Lightology / spec sheet | High |
| Overall height | 7.63 | published | Same. The tilted 8 in disc is exactly this tall (see tilt below) | High |
| Overall projection | 5.4995 (target 5.50) | published | Same. Shade front lands at 5.4995, 0.0005 in short | High |
| Backplate diameter | 5.25 | published | Spec | High |
| Backplate depth | 0.125 | published | Spec | High |
| Shade maximum diameter | 3.4998 (3.5) | published | Spec | High |
| Shade length along its axis | 3.250 | published | Spec | High |
| Disc diameter | 8.00 | published | Width figure is the disc; the fixture without the disc is 5.25 wide | Medium-high |
| Drum diameter | 4.25 | measured | Side photo scaled against the 5.25 backplate (4.27 read, rounded to 4.25) | Medium |
| Socket collar diameter | 1.55 | measured | Side photo | Low-medium |
| Face tilt from vertical | 17.93 degrees | inferred (solved) | Solved so the 8 in disc is 7.63 in tall. The side photo reads about 15.8 degrees; the published height wins | Medium |
| Slanted-face centre depth | 2.13 | inferred (solved) | Chosen so the shade front is at 5.50. The photo reads about 2.32; the difference follows from the tilt compromise | Medium |
| Disc thickness | 0.06 | inferred | Sheet-steel gauge | Low |
| Disc position | flush on the slanted face | inferred | Photo shows the disc parallel to and on the face | Medium |
| Shade glass wall | 0.08 | inferred | Typical blown opal glass | Low |
| Shade neck offset from the face | 0.20 | inferred | Photo | Low-medium |
| Lamp-holder stem | radius 0.55, length 0.60 | inferred | Hidden inside the shade | Low |
| Shade shape | sphere of radius 1.75 truncated at the neck | inferred | The published 3.25 in axial length against 3.5 in diameter implies a truncated sphere | Medium |

Omitted small details: screw heads, canopy fasteners, wiring, the lamp itself, edge radii on the backplate and disc.

## Light source
- Enabled by setting the family's Light Source flag (`FBX_ASSET_TYPE` = 1). Point shape, spherical distribution.
- Position: the centre of the shade sphere, 1.7 in along the shade axis from the slanted face, family frame (0, -0.5233, 3.75). Distance from the shade centre 0.0 in. It lies inside the shade cavity (inner radius 1.67 in).
- Initial intensity: 3 W at 90 lm/W (about 270 lm) as an `InitialWattageIntensity`. **The 3 W is published (G9 LED); the 90 lm/W efficacy is inferred**, because no lumen figure was given.
- Colour: 2700 K, **inferred** typical warm-white G9 LED. Loss factor 1.0.
- The project instance reads 3.0 W.

## Acceptance results
Measured in a disposable project (`NewProjectDocument`, closed unsaved) with the family hosted on a wall's exterior face. Full numbers are in `validation.json` (`gates`).

| Gate | Result |
|---|---|
| 1 Native | Saves and reopens with 0 warnings; category Lighting Fixtures; WorkPlaneBased. Project warnings: none. PASS |
| 2 Hosting | Host is the wall; backplate at 0.000 to 0.125 in from the face; all solids on the exterior side. PASS |
| 3 Envelope | 8.000 W x 7.630 H x 5.4995 D (tolerance 0.02). With Show Disc off: 5.25 x 5.25 x 5.4995; maximum shift of any other part 0.000. PASS |
| 4 Parts | Backplate 5.250 dia x 0.125; shade 3.4998 dia and 3.250 along the axis; other part extents in `validation.json`. PASS |
| 5 Materials | Metal Finish to a test material changed 24 faces (Backplate 4, Body 4, Socket 10, Disc 6) and none on the Shade; Glass Finish changed the Shade's 6 faces. PASS |
| 6 Light | Enabled, inside the shade, 3 W read back in the family and in the project. PASS |
| 7 Fidelity | Reviewed by eye (below). Judged acceptable, with the differences listed |
| 8 Honesty | Table above |

### Fidelity review
I opened every exported view and `views/_REVIEW_compare.jpg`.
- Side: the drum's slanted face leans the same way as the photo (top projects further), the ball sits on the face at the same relative size, and the disc is a thin tilted plate parallel to the face. The ball reads slightly larger against the drum than the photo, and the drum is a plain cylinder with no screw or edge radius.
- Oblique: disc, drum and ball proportions and the disc's overhang match the black-finish photo closely. The photo's shade looks glossier and brighter (it is lit from inside); the Revit shaded view is flat.
- Front: no straight-on product photo was supplied; the lifestyle render in the compare sheet is only context, so the front view is checked by measurement, not by comparison.
- Hosted: the fixture sits on the wall face with the backplate flush.

## Limitations
- The tilt (17.93 degrees) differs from the photo-measured about 15.8 degrees because the published height fixes it. Depth of the face centre differs by about 0.2 in from the photo for the same reason.
- Revit adds a fixed 24 in Light Source proxy solid to instance geometry and `get_BoundingBox`. It is not part of the model, its size is read-only, and a bounding-box check that includes it reads 24 in. The envelope figures above exclude it and it is hidden in the views.
- Inferred sizes (disc thickness, glass wall, neck, stem) are single best guesses without a source.
- The family uses generic appearance assets (colour, gloss); no textures or brushed-metal detail.
- Photometry is a point source with a nominal efficacy; no IES file was available.
- The shaded views come from the Revit viewport, not a rendering, so the glass does not glow.
- Only one type is provided (Midnight Black / Milk); other finishes need a change of `Metal Finish`.
- The Revit host wall in the views is a stock wall with a graphics override; it is not part of the deliverable.

## Files
- `source/common.py`, `source/build_sconce.py`, `source/validate_sconce.py`: run through the harness under pyRevit to reproduce the RFA, `validation.json` and the views. `source/summarise_gates.py` (plain Python 3) writes the gate summary. `source/explore_*.py` are exploration scripts (light-source API, template slab, proxy size); they are not needed to rebuild.
- `validation.json`, `build_result.json`: machine-readable results.
- `views/`: front, side, oblique, hosted_on_wall (Revit exports) and `_REVIEW_compare.jpg`.
- `SOURCES.md`, `ERRORS.md`, `_work/` (scratch and thumbnails, not deliverables).
