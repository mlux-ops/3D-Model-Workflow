# 1529 N. Wieland: reality-match review (Phase 10)

Written 2026-11-13 by the Phase 10 agent, unattended. Journal of the work: `phase10_results.md`.

## What this review is, and what it is not

The plan's Phase 10 compares the owner's photographs of the street with pictures of the scene. **There are no photographs and no site visit has been made.** So this review has three kinds of entry, and keeps them apart:

- **Pass** or **fail**: the scene was measured against evidence that exists (the plat of survey, the county's parcel and building outlines, the 2022 aerial laser scan, the Revit model, the NOAA sun calculator, or the path-traced picture of the same view). The number is given.
- **Could not be checked**: the evidence the tolerance names does not exist. The missing evidence is named each time. Where a weaker measurement could be made in its place, it is given and labelled as such; it does not turn the entry into a pass.
- No tolerance is reported as met without a measurement.

Words used the same way throughout:

- "Station" is a fixed camera position on the street (S1 to S9). "Design view" is a fixed camera position in or on the building (D1 to D5). "View" means either.
- "Path-traced picture" is a picture made by Unreal's Path Tracer, the slow renderer that follows light physically. "Real-time picture" is a picture made by the renderer the walk-through uses (Lumen, Unreal's real-time method for bounced light).
- "Level" is Unreal's word for one saved scene file.
- "Tolerance" is a row of the table "Tolerances proposed" in `REFERENCE_VIEWS.md`.
- "Laser scan" is the aerial laser survey of Cook County of 2022. "County outline" is the county's 2022 outline of a building.
- "Stop" is a factor of two in brightness.
- "Zone 1" is everything within 40 m of the lot.

Street imagery (Google Street View or any map service) was not opened, saved, traced or sampled. Looking at it beside the summer pictures is the owner's step (see "For the owner" at the end).

## Result in one table

| | Count | Which |
|---|---|---|
| Tolerances that pass | 6 of 19 | building on its lot, lot in the world, true north, tree height, transfer from Revit, sun direction |
| Tolerances that pass in part and fail in part | 3 of 19 | neighbours' walls in plan, ground levels, real-time against path-traced |
| Tolerances that fail | 1 of 19 | neighbours' heights |
| Tolerances that could not be checked | 9 of 19 | trunk position, trunk diameter, tree species, street furniture, camera station, photograph overlay, shadow edges, colour of materials, sidewalk brightness |
| Stations with a sheet | 9 of 9 | S1 to S6 and S9 (four panels each), S7 (cannot exist), S8 (plan) |
| Design views with a sheet | 5 of 5 | D1 to D5 |
| Failures listed for the owner's mark | 8 | F1 to F8 in `review\phase10\owner_marks.csv` |

Sheets: `review\phase10\sheets\<view>_sheet.jpg`. Every number below is also in `review\phase10\tolerances.csv` (per tolerance), `review\phase10\station_scores.csv` (per station) and `review\phase10\design_scores.csv` (per design view).

## Per tolerance

| Tolerance | Limit | Measured today (2026-11-13) | Against | Verdict |
|---|---|---|---|---|
| The building on its lot | 0.05 m | Street corners of the first-floor slab 0.1 to 0.3 mm from the lot's side lines plus setbacks; all 2,585 placed objects within 0.5 mm of their place in the Revit export (Phases 3 and 6; the building has not been moved since) | Revit model's lot lines, record lot 49.50 ft wide | **Pass.** Open point: the owner has not said whether the survey's frontage (50.18 ft) or the record width (49.50 ft) governs (decision 7). The rear corners have no figure of their own in the drawings. |
| The lot in the world | 1.0 m | Lot corners convert between map and level with 0.000 m; the projection is within 2.4 mm of the county's figures; the east kerb is within 0.3 m of the site plan (Phase 2) | County parcels, laser scan, site plan | **Pass** |
| True north | 0.2 degree | Street grid 1.17 degrees off true north by parcel lines and 1.14 by building walls, 0.03 degree apart (Phase 2) | County parcels and outlines | **Pass.** The survey carries no bearing, so a second independent method stands in for it. |
| Neighbours' street walls in plan | 0.3 m (0.5 m from laser scan alone) | At the five points the plat of survey ties to a neighbour's wall, today's walls stand 10, 30, 10, 0 and 5 cm from the surveyed place. Against the county outlines in Zone 1: 50 of 76 building sides within 0.5 m, 59 within 1.0 m, largest 3.0 m | Plat of survey; county outlines | **Pass at the five surveyed points. Fail for 26 of 76 sides in Zone 1** (failure F2). Against a tape on site: could not be checked. |
| Neighbours' heights | 0.3 m | Zone 1: 3 of 19 buildings within 0.3 m, middle value 1.02 m too low, largest 2.83 m. All 50 measured: 6 within 0.3 m, 37 off by more than 1 m, largest 12.07 m. Number 1533 +1.10 m, number 1525 -1.02 m, rear building -1.30 m | Laser scan | **Fail** (failure F1) |
| Ground, kerb and sidewalk levels | 0.1 m to the lot; 0.2 m absolute | 99.8 percent of 53,266 m2 within 0.2 m. Everything but the roadway: 99.5 percent within 0.1 m; pavements in front of the lot all within 0.1 m (largest 9.7 cm). Roadway: 13.1 cm too low, 10.5 percent within 0.1 m | Laser scan's ground | **Pass for 0.2 m. Pass for 0.1 m on pavements and yards. Fail for 0.1 m on the roadway** (failure F3) |
| Tree trunk position | 0.3 m (1.0 m from scan alone) | 20 of 34 trunks stand at the scan's point; 14 were moved 1.1 to 3.6 m off a roadway or out of a building | Crown tops in the laser scan, which are not trunks | **Could not be checked.** Missing: a tape to each trunk from two fixed points. |
| Tree trunk diameter | 2 cm | Not measured | none | **Could not be checked.** Missing: a girth tape on each trunk. |
| Tree height and crown spread | 1.0 m | 34 of 34 trees at the scan's height (largest difference 0.0 m); crown width set to the scan's width | Laser scan, leaves off, 2022 | **Pass against the scan.** Growth since 2022 is not known. |
| Tree species | named, with confidence | None known; models chosen by shape (19 ginkgo, 9 Norway maple, 5 English oak, 1 silver birch) | none | **Could not be checked.** Missing: bark, buds and form seen on site, or leaves in summer. |
| Poles, hydrant, signs, fences, stoops | 0.3 m in plan; 0.1 m in height | This plan placed none. The earlier detailed model of the neighbours carries its own stoops, railings, iron fences and a utility pole with wires inside its meshes; they were compared with nothing | none | **Could not be checked.** Missing: each item taped on site. |
| Camera station | 0.1 m, 0.05 m eye height, 0.5 degree | Against the surveyed station list: place 0.0 cm, heading 0.00 degree, eye height 156.4 to 164.8 cm over today's ground (target 160; largest difference 4.8 cm) | The station list, not reality | **Could not be checked.** Missing: the station taped on site and the lens read from the photograph's file. |
| Photograph and render overlay | 1.5 percent of image width | Not measured | none | **Could not be checked.** Missing: the owner's photograph at each station. |
| Transfer from Revit to Unreal | 1 mm; 5 mm floor levels; 10 mm fixtures | Known dimension 0.1 to 0.3 mm; floor levels 0.4 mm at most; fixtures within 0.5 mm of their place in the Revit export | Drawings and the Revit export | **Pass.** A Revit view per design camera, to see that no fixture is missing, does not exist. |
| Sun direction | 0.5 degree | Bearing 241.72 against 241.67 degrees; height 46.40 against 46.34 degrees; 15 August 2026, 15:30 Central Daylight Time | NOAA calculator | **Pass** |
| Shadow edges on the ground | 0.3 m | Not measured. In its place: the shadow of a 3.00 m test pole is 4.6 cm longer than calculated (Phase 8) | calculation only | **Could not be checked.** Missing: a photograph with its time of capture. |
| Colour of principal materials | colour difference 5 | Not measured | none | **Could not be checked.** Missing: a photograph of each material with a grey card in it. |
| Brightness of sunlit sidewalk | one third of a stop | Not measured. In its place: the sunlit sidewalk reads 0.09 stop over middle grey; a grey card in sun reads 0.178 against 0.18 (Phase 8) | the render's own grey card | **Could not be checked.** Missing: a photograph of the sunlit sidewalk with a grey card in it. |
| Real-time against path-traced | mean 10 percent; no region over 2 percent of the frame off by more than one stop | 8 of 12 views pass: S1 +0.1, S2 +0.5, S3 -0.7, S4 +3.2, S5 -4.2, S6 -0.7, D1 -4.8, D2 +2.2 percent. 4 fail: S9 +26.2, D3 +18.0, D4 -42.4, D5 -11.9 percent | Path-traced pictures of Phase 12 | **Pass at 8 views, fail at 4** (failures F4 to F7) |

## Per station

The same twelve scores stand under each street station's sheet. What differs from station to station is the camera reading and the real-time score; the rows on neighbours, ground, trees and street furniture are the scene's figures and are the same at every station, because which building is seen from which station was not separated.

| Station | Sheet | Photograph | Camera against the station list (place, heading, eye height) | Real-time against path-traced | Overlay, shadow, colour, sidewalk brightness |
|---|---|---|---|---|---|
| S1 Frontal | `S1_sheet.jpg` | PLACEHOLDER: none | 0.0 cm, 0.00 degree, 163.0 cm | +0.1 percent, largest region 0.23 percent: pass | could not be checked (no photograph) |
| S2 From the south-west | `S2_sheet.jpg` | PLACEHOLDER: none | 0.0 cm, 0.00 degree, 159.5 cm | +0.5 percent, 0.04 percent: pass | could not be checked (no photograph) |
| S3 From the north-west | `S3_sheet.jpg` | PLACEHOLDER: none | 0.0 cm, 0.00 degree, 160.8 cm | -0.7 percent, 0.27 percent: pass | could not be checked (no photograph) |
| S4 Long view from the south | `S4_sheet.jpg` | PLACEHOLDER: none | 0.0 cm, 0.00 degree, 156.4 cm | +3.2 percent, 0.04 percent: pass | could not be checked (no photograph) |
| S5 Long view from the north | `S5_sheet.jpg` | PLACEHOLDER: none | 0.0 cm, 0.00 degree, 157.6 cm | -4.2 percent, 0.29 percent: pass | could not be checked (no photograph) |
| S6 Along the frontage | `S6_sheet.jpg` | PLACEHOLDER: none | 0.0 cm, 0.00 degree, 164.8 cm | -0.7 percent, 0.39 percent: pass | could not be checked (no photograph) |
| S7 From the rear | `S7_sheet.jpg` | none can be taken | The station cannot exist: there is no alley, and the point lies inside the rear neighbour's lot | does not apply | does not apply |
| S8 Plan | `S8_sheet.jpg` | The county's aerial photograph, kept outside the repository | Straight down over the lot centre, 120 m by 120 m, true north up | no number: the path-traced plan picture could not be made (the graphics card hung at 08:01, the known fault of Nanite ray tracing in Unreal 5.9); the real-time plan picture stands alone | Lot in the world, true north, building on its lot: pass. Plan picture against the aerial photograph: looked at side by side, no number (see below) |
| S9 Opposite side | `S9_sheet.jpg` | PLACEHOLDER: none | 0.0 cm, 0.00 degree, 157.3 cm | +26.2 percent, two regions of 2.1 and 2.0 percent about four stops brighter: **fail** | could not be checked (no photograph) |

At every street station: neighbours' walls pass at the surveyed points and fail at 26 of 76 sides; neighbours' heights fail; ground passes except the roadway; tree height passes against the scan; trunk position, trunk diameter, species and street furniture could not be checked; sun direction passes.

**Station S8 and the aerial photograph.** The county's aerial photograph (public county data, downloaded in Phase 2 and kept outside the repository) was laid beside the plan picture in one sheet outside the repository: `E:\Wieland1529_site_data\phase10\S8_plan_beside_aerial.jpg`. It is for looking at only. Nothing was traced from it and no colour was taken from it, so the overlay tolerance has no number at S8. Seen by eye: buildings, street, pavements and the large paved yard south-east of the lot lie in the same places in both. The aerial photograph shows the house that stands on the lot today; the scene shows the new building. The yard and the kerbs hold parked cars in the photograph and none in the scene. In the repository's own S8 sheet the lot and the county outlines are drawn over the plan picture from data: the lot's outline encloses the new building, and the outlines of numbers 1533 and 1525 and of the row across the street lie on the drawn buildings.

**Camera differences from the table in `REFERENCE_VIEWS.md`.** Every station camera is tilted up 8 degrees and uses the 24 mm lens. The table says up 12 degrees at S1, up 10 at S2, S3 and S9, level at S4, S5 and S6, and a 35 mm lens at S2 and S3, 50 mm at S4 and S5, 28 mm at S6. Nothing was changed, because the table also says the render takes the photograph's own lens and aim once a photograph exists.

## Design views D1 to D5

| View | Sheet | Revit view | Transfer from Revit | Sharp edges within 2 m (target zero) | Real-time against path-traced |
|---|---|---|---|---|---|
| D1 Penthouse roof deck | `D1_sheet.jpg` | PLACEHOLDER: none | pass | not counted at this view | -4.8 percent: pass |
| D2 Penthouse living space | `D2_sheet.jpg` | PLACEHOLDER: none | pass | 569 left of 4,018: fail | +2.2 percent: pass |
| D3 Triplex kitchen | `D3_sheet.jpg` | PLACEHOLDER: none | pass | 451 left of 5,905: fail | +18.0 percent, one region of 3.3 percent two stops brighter: **fail** |
| D4 Triplex bathroom | `D4_sheet.jpg` | PLACEHOLDER: none | pass | 328 left of 1,670: fail | -42.4 percent, a quarter of the frame 1.2 stops darker: **fail** |
| D5 Triplex rear patios | `D5_sheet.jpg` | PLACEHOLDER: none | pass | not counted at this view | -11.9 percent, no region off by a stop: **fail** |

"Revit view: could not be checked" at all five. Missing: a view exported from Revit at the same camera. These sessions do not open the Revit model.

**Correction to Phase 9.** Phase 9 reported 9 of 12 views passing, with D4 and D5 passing and D2 failing. After the editor was closed and started again, the same saved scene gives Phase 12's result: 8 of 12, with S9, D3, D4 and D5 failing. D3, D4 and D5 were rendered twice and repeat within 1.5 percent. Phase 9's brighter interiors were a state of that long editor session, not of the saved scene. This review counts 8.

## Failures: cause and proposed fix

Each failure is a row of `review\phase10\owner_marks.csv` with an empty column for the owner's mark, "fix" or "accept".

| No. | What fails | Measured | Cause | Proposed fix | Phase that owns the fix |
|---|---|---|---|---|---|
| F1 | Neighbours' heights | Zone 1: 3 of 19 within 0.3 m; number 1533 +1.10 m, number 1525 -1.02 m, rear building -1.30 m; overall up to 12.07 m | Phase 7 kept the earlier detailed models of the neighbours as modelled and fitted them to the ground only | Stretch each earlier model to the laser scan's roof level where the difference is under about 1 m; show the plain Phase 4 block with its material where it is larger. Numbers 1533 and 1525 first, after a laser reading on site if a visit is made | Phase 7 |
| F2 | Neighbours' walls away from the surveyed points | 26 of 76 sides in Zone 1 over 0.5 m from the county outline, largest 3.0 m | As F1. The county outline is itself good to about 0.5 m and includes eaves and porches | Look at the worst sides in the S8 sheet; move or replace only buildings seen from a station; accept the rest | Phase 7 |
| F3 | Roadway level | 13.1 cm under the laser ground | Phase 7 made the kerb by lowering the whole roadway 13 cm under the laser ground, which already is the real roadway | Raise the roadway to the laser ground; give the kerb the height the scan shows between sidewalk and gutter, or the height taped on site | Phase 7 |
| F4 | S9, real-time against path-traced | +26.2 percent; upper windows across the street four stops brighter | The real-time picture mirrors the bright sky in the neighbours' glass; the path-traced picture draws the same glass dark. Which is right is not known without a photograph | Find why the Path Tracer draws no sky in that glass, correct the wrong one, repeat S9 in both | Phase 8 |
| F5 | D3, real-time against path-traced | +18.0 percent; the pendant lamp's glass shade two stops brighter | The shade glows in the real-time picture and is clear in the path-traced one | A shade material both renderers draw alike; repeat D3 in both | Phases 5 and 8 |
| F6 | D4, real-time against path-traced | -42.4 percent; a quarter of the frame 1.2 stops darker | Windowless bath: Lumen carries less bounced lamp light in a small closed room than the Path Tracer | One change at a time: higher Lumen quality in this room; if that fails, a weak fill lamp for the real-time tier only, recorded as such; or accept | Phase 9 |
| F7 | D5, real-time against path-traced | -11.9 percent; no region off by a stop | Less bounced daylight under the covered patio | Same trial as F6; or accept (1.9 percent over the limit) | Phase 9 |
| F8 | Sharp edges at D2, D3, D4 | 569, 451 and 328 left | Detail finer than the 2 mm rounding inside fixtures | Remodelled fixtures; or accept | Phase 6 |

## Could not be checked: the evidence that is missing

| What | Missing evidence | Who can supply it |
|---|---|---|
| Photograph overlay at S1 to S6 and S9 | One photograph per station at 1.60 m eye height, with the camera's time and focal length in the file | Owner, site visit (shot list in `REFERENCE_VIEWS.md`) |
| Camera station against reality | Each station taped from two fixed points | Owner, site visit |
| Shadow edges | The same photographs, with their time of capture | Owner, site visit |
| Colour of principal materials | A square-on photograph of each material with a grey card in it | Owner, site visit |
| Brightness of sunlit sidewalk | A photograph of the sunlit sidewalk with a grey card in it | Owner, site visit |
| Tree trunk position | A tape from two fixed points to each trunk | Owner, site visit |
| Tree trunk diameter | A girth tape at 1.37 m above ground | Owner, site visit |
| Tree species | Bark, buds and form, or leaves in summer | Owner, site visit |
| Poles, hydrant, signs, fences, stoops | Position and size of each, taped | Owner, site visit |
| Neighbours' walls against a tape | A tape from the lot corners to each neighbour's street wall | Owner, site visit |
| Plan picture against the aerial photograph, by number | The owner's look at the side-by-side sheet, or the owner's leave to measure on the aerial photograph | Owner |
| Design views against Revit | A view exported from Revit at each design camera | Owner (Revit is not opened by these sessions) |
| Summer look of the street | The owner's own look at street imagery of August beside the summer pictures | Owner (step 10.5) |

## Also seen in the pictures (not tolerance rows)

- From above (S8) the street trees are drawn in their far, simplified form and read as conifers.
- The far city behind the roof deck (D1) is a stand-in, not the real skyline (Phase 7).
- The lawn does not pass the material gate closer than 1 m (Phase 7); the furniture is labelled stand-in furniture (Phase 6); finish alternatives carry working names. These wait on the owner's decisions and are unchanged.
- The scene has no cars, no road markings and no people.

## What waits on the owner

Steps 10.8 and 10.9 of the plan are the owner's marks and the fixes that follow them. Neither was done. The list is in "For the owner" at the end of `phase10_results.md`.
