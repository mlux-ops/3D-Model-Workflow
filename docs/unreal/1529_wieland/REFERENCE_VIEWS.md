# Reference views: camera stations, reference images and tolerances

Written 2026-11-10. Companion to [PLAN.md](PLAN.md). Sources and their terms are in [SOURCES.md](SOURCES.md).

## What a reference view is

A reference view is a fixed camera position on the real street, a photograph taken there, and a render from the same position, lens and time. The review in Phase 10 lays the two side by side and scores them against the tolerances below.

Three facts shape this file:

1. **The building is new.** City records show demolition permits issued in June 2026 and marked complete, street imagery shows the lot cleared by August 2026, and a new four-story building was permitted on 2026-09-03. A photograph can therefore check the surroundings, and it cannot check the building. The building is checked against the Revit model.
2. **The reference photographs must be the owner's own.** Google does not allow Street View images to be saved, so a Street View image cannot be the saved half of a side-by-side. Each station lists a Street View link as a live cross-check to look at in a browser, with its capture date.
3. **The season is a problem.** The agreed reference condition is a clear, leaf-on summer afternoon. A site visit in November gives leaf-off photographs. This file therefore defines two photograph sets: a leaf-off set now, used for positions, massing and materials, and a leaf-on set in summer 2027 if the owner wants the foliage match scored. Until then the leaf-on look is judged by eye against the August 2026 Street View in a browser.

## Positions used in this file

All positions are provisional until Phase 2 replaces them with surveyed ones. They derive from the county's parcel centres and the lot depth on the owner's site plan, and are good to about 3 m.

| Point | Latitude | Longitude | Basis |
|---|---|---|---|
| Centre of the combined lot | 41.910215 | -87.635389 | Mean of the two parcel centres (county Assessor) |
| Front lot line at the lot's centre line | 41.910215 | -87.635577 | 15.58 m west of the centre: half the 102.20 ft record depth |
| West sidewalk opposite | 41.910215 | -87.635794 | 18 m west of the front lot line: an assumed 66 ft (20.1 m) right-of-way, less about 2 m from the far lot line to the walking line. **The right-of-way width is unverified.** |

Headings are true bearings, clockwise from true north. The street is taken to run about one degree west of true north; Phase 2 measures it.

### Corrected by Phase 2 on 2026-11-11

Phase 2 measured the street and the lot (`phase2_results.md`). Three things in this file are wrong as written, and the figures below replace them. The tables further down are left as they were written, so that the change can be seen.

- **The right-of-way of Wieland Street is 50 ft (15.24 m), not 66 ft.** The plat of survey says so, and the county parcels and the 2022 ground surface agree. The west kerb is 11.7 m and the far side of the west sidewalk 15.2 m west of the front lot line. The west sidewalk's walking line is therefore 14.0 m west of the front lot line, not 18 m; a point 18 m west is inside the buildings opposite.
- **Every station on the west sidewalk (S1 to S5) moves 4 m east.** Their latitudes change by less than a metre. Every station's position in latitude and longitude, in State Plane coordinates, in the new level frame and in the existing level is in `review\phase2\stations.csv`. S1 is at latitude 41.9102097, longitude -87.6357473.
- **There is no alley behind the lot, so station S7 cannot exist as written.** The rear lot line meets the neighbours' lots, with a four-storey building 0.2 to 0.3 ft beyond it. A rear view has to be taken from the building's own rear decks, and is a design view, not a reference view.

The lot centre used in this file, latitude 41.910215 and longitude -87.635389, is right within 0.2 m. True north is now measured: the lot's front line runs 1.18 degrees west of it. A bearing in the station table converts to a yaw in the level as yaw = bearing - 178.82 degrees.

## What the owner settled on 2026-11-10

- The scene is for design review of finishes, and nothing is published.
- There is one review condition: the summer afternoon, with every light fixture on at its real output. The site-visit match is kept only for scoring against the owner's photographs. The summer morning and dusk rows below are kept as a record and are not rendered.
- The building is two mirrored halves, each a triplex below and a penthouse above. The design views below are set in one triplex and one penthouse.
- The Revit model's property lines govern the building's position.

## Lighting conditions

| Name | Date and time | Sun (hand-calculated; Phase 8 replaces this with the engine's value checked against the NOAA calculator) | Purpose |
|---|---|---|---|
| Summer afternoon (primary) | 15 August, 15:30 Central Daylight Time | About 46 degrees above the horizon, bearing about 242 degrees. The street facade faces west (about 270 degrees), so the sun strikes it 28 degrees off square: direct light with short shadows from reveals and sills. | The agreed reference condition. |
| Summer morning | 15 August, 10:30 Central Daylight Time | Sun in the south-east; the street facade is in shade. | Matches the light in Google's August 2026 capture, judged by eye from shadow directions. Live cross-check only. |
| Site-visit match | The date and time stamped in each owner photograph | Computed per photograph | Scoring the leaf-off set. |
| Dusk, interior lights on | 15 August, 20:15 Central Daylight Time (about 25 minutes after sunset) | Below the horizon | Checks fixtures with their photometric files against fixed exposure. |

## Exterior stations

Eye height is 1.60 m above the sidewalk at every street station. Lens values are 35 mm full-frame equivalents. The render uses the photograph's actual focal length, read from the image file, in place of the nominal value.

"To be taken" means the owner's photograph does not exist yet. Its capture date and time are read from the image file when it is filed, and are entered in this table then. The county aerial photograph for S8 is the 2025 edition, whose record says it was flown in 2026; its flight date is read from the file's metadata when it is downloaded.

| Station | Position (provisional) | Heading, pitch | Lens | What it tests | Owner photograph | Live Street View cross-check |
|---|---|---|---|---|---|---|
| S1 Frontal | West sidewalk opposite the lot's centre line: 41.910215, -87.635794 | 90, up 12 | 24 mm | The building's whole street facade between its two neighbours; kerb, parkway, sidewalk | To be taken | August 2026, from the roadway 10 m nearer: https://www.google.com/maps/@41.910283,-87.6356719,3a,90y,90h,95t/data=!3m6!1e1!3m4!1sT-uodVN21DptY_uY8doNMg!2e0!7i16384!8i8192 |
| S2 From the south-west | West sidewalk 25 m south of S1: 41.909990, -87.635794 | 45, up 10 | 35 mm | The south side wall, the frame house at 1525, the large tree and street light south of it | To be taken | August 2026, looking south-east from the same panorama: https://www.google.com/maps/@41.910283,-87.6356719,3a,75y,125h,95t/data=!3m6!1e1!3m4!1sT-uodVN21DptY_uY8doNMg!2e0!7i16384!8i8192 ; November 2025, before demolition: https://www.google.com/maps/@41.9102539,-87.6356797,3a,75y,125h,95t/data=!3m6!1e1!3m4!1sO-GLxn-B8NqXRQZBi26Kgg!2e0!7i16384!8i8192 |
| S3 From the north-west | West sidewalk 25 m north of S1: 41.910440, -87.635794 | 135, up 10 | 35 mm | The north side wall against the brick apartment building at 1533, its arcade, fence and parkway tree | To be taken | None looked at from this position |
| S4 Long view from the south | West sidewalk 50 m south of S1: 41.909765, -87.635794 | 15, level | 50 mm | The building in the row of the east side; how far detailed surroundings must extend northward | To be taken | August 2026, looking north from the panorama: https://www.google.com/maps/@41.910283,-87.6356719,3a,90y,0h,92t/data=!3m6!1e1!3m4!1sT-uodVN21DptY_uY8doNMg!2e0!7i16384!8i8192 |
| S5 Long view from the north | West sidewalk 60 m north of S1: 41.910755, -87.635794 | 165, level | 50 mm | The same toward the south, with the distant towers behind | To be taken | August 2026, looking south from the panorama: https://www.google.com/maps/@41.910283,-87.6356719,3a,90y,180h,92t/data=!3m6!1e1!3m4!1sT-uodVN21DptY_uY8doNMg!2e0!7i16384!8i8192 |
| S6 Along the frontage | East sidewalk 20 m north of the lot's north line: 41.910462, -87.635607 | 180, level | 28 mm | Close materials at walking distance: fence, stoop, planting, paving joints, the houses opposite in reflection | To be taken | None |
| S7 From the alley | Alley behind the lot, 15 m south of its centre line: 41.910080, -87.635172 | 330, up 8 | 24 mm | The rear wall and garage, rear neighbours, alley paving and poles | To be taken | None. **The alley was not seen in any imagery; its width and paving are unknown.** |
| S8 Plan | Directly above the lot centre, looking straight down, 120 m by 120 m, true north up | n/a | Parallel projection | Positions of buildings, kerbs, trees and poles in plan | County aerial photograph, 2025 edition, 6-inch pixels (needs download approval) | n/a |
| S9 Opposite side | East sidewalk at the lot's centre line, looking at the houses across the street: 41.910215, -87.635607 | 270, up 10 | 24 mm | The west side, which fills the building's windows and reflections: hydrant, utility pole with transformers, garages | To be taken | August 2026, looking west from the panorama: https://www.google.com/maps/@41.910283,-87.6356719,3a,90y,270h,95t/data=!3m6!1e1!3m4!1sT-uodVN21DptY_uY8doNMg!2e0!7i16384!8i8192 |

## Design views with no real-world reference

These are scored against a path-traced render of the same view, which Phase 8 treats as ground truth for light, and against the Revit model for geometry. No photograph can exist for them until the building is built.

| Station | Position | What it tests |
|---|---|---|
| D1 Penthouse roof deck | On the penthouse's roof deck at standing eye height, looking south-east | The distant-city stand-in, sky, deck finishes and pergola |
| D2 Penthouse living space | The penthouse's largest street-facing room, looking toward the windows | Interior finishes, furniture, daylight through glass, the view of the street from inside |
| D3 Triplex kitchen | Looking along the counter run with a window to one side | Cabinet, counter and splashback finishes and their alternatives, under daylight and fixtures |
| D4 Triplex bathroom | Tiled wall under a wall light at a glancing angle | Tile relief under grazing light, as this repository's material rules require, and the tile alternatives |
| D5 Triplex rear patios | From the covered patio looking out across the uncovered patio | Exterior paving, metalwork and door finishes and their alternatives |

The owner names the half of the building and the exact rooms for D2 to D4. Each design view's exact position, heading and lens are then set from the Revit model in Phase 6 and entered in this table. Until then they are: standing eye height of 1.60 m, a 24 mm lens, and the heading described in the table.

### Provisional positions set in Phase 6 (2026-11-11), pending the owner's choice of half and rooms

The owner has not yet named the half or the rooms, so Phase 6 used the north half and the rooms below. Positions are in the Unreal level's frame, in centimetres (origin at the lot's south-west corner, north is -X, east is -Y, up is +Z). The eye is 1.60 m above the finished floor and the lens is 24 mm on a 36 mm frame (73.7 degrees wide) in every view. Headings are compass bearings (0 = north, 90 = east); pitch is degrees below the horizon. The same numbers are in `tools\wieland_interiors.py` (`DESIGN_VIEWS`).

| Station | Room used | Camera X, Y, Z (cm) | Looks at X, Y, Z (cm) | Heading | Pitch down |
|---|---|---|---|---|---|
| D1 | North penthouse roof deck, under the pergola | -1300, -1560, 1684 | -900, -2300, 1640 | 118 | 3.0 |
| D2 | North penthouse, 4th floor, street-facing kitchen room | -960, -840, 1339 | -1200, -330, 1320 | 295 | 1.9 |
| D3 | North triplex, 1st floor kitchen, along the counter toward the street window | -1100, -930, 363 | -1340, -560, 320 | 303 | 5.6 |
| D4 | North triplex, 2nd floor hall bath (tub, toilet, basin, wall light) | -1375, -2020, 688 | -1250, -2210, 630 | 123 | 14.3 |
| D5 | North triplex, 1st floor covered rear patio, looking out to the rear | -1190, -2262, 363 | -1190, -2800, 330 | 90 | 3.5 |

Two things the owner should know about these rooms. The penthouse's largest street-facing room is its kitchen and island; the living and dining space is behind the stair and faces the rear. In the Revit model, the walls of the D4 bath carry the gypsum-board material and no tile; only the shower fitting carries a porcelain material. D4 can therefore test tile relief only through a tile alternative (see `phase6_results.md`), not through the material Revit exported.

## Tolerances proposed, and the evidence behind each

A tolerance is only proposed where a named source can support it. "Site visit" means the owner's tape or laser measurement.

| Quantity | Tolerance | Evidence that the source can support it |
|---|---|---|
| The building on its lot | 0.05 m to the governing lot lines | The owner's survey (fieldwork 2025-08-18) and the Revit model's lot lines. The survey's measured frontage (50.18 ft) and the record width (49.50 ft) differ by 0.21 m; the owner states which governs (OPEN_DECISIONS.md, decision 7), and the check is made against that one. |
| The lot in the world | 1.0 m | County parcel outlines publish no accuracy. The 2017 lidar states 0.41 m and 0.36 m horizontal error. The earlier model claimed 1.5 m. |
| True north | 0.2 degree | The survey's bearings are the evidence. The county parcel outline is a cross-check only, because its accuracy is unpublished; a 31 m lot line would have to be good to 0.1 m to give 0.18 degree. |
| Neighbours' street walls, in plan, relative to the lot | 0.3 m | Site visit: tape from lot corners. Lidar alone (0.22 m point spacing) supports about 0.5 m. |
| Neighbours' heights (parapet, eave, ridge) | 0.3 m | 2022 lidar: vertical error 0.09 m, but edges are sampled every 0.22 m. Site visit laser readings tighten this to 0.15 m where taken. |
| Ground, kerb and sidewalk levels | 0.1 m relative to the lot; 0.2 m absolute | 2022 lidar: 0.09 m root-mean-square, 0.18 m at 95 percent. Survey spot levels where they exist. |
| Tree trunk position | 0.3 m | Site visit: tape from two fixed points. From lidar and aerial photography alone: 1.0 m. |
| Tree trunk diameter | 2 cm, measured at 1.37 m above ground | Site visit only. No public record exists. |
| Tree height and crown spread | 1.0 m | 2022 lidar, leaf-off, plus up to four seasons of growth; site visit laser reading where the top is visible. |
| Tree species | Named with a stated confidence | Site visit: bark, buds, form and fallen leaves in November; leaves in summer. Not from street imagery alone. |
| Poles, hydrant, signs, fences, stoops | 0.3 m in plan; 0.1 m in height for items under 3 m | Site visit only. No public record exists. |
| Camera station | 0.1 m in plan, 0.05 m in eye height, 0.5 degree in heading | Site visit: the station is taped from two fixed points and the lens is read from the image file. |
| Photograph and render overlay | After the camera is solved from the photograph: fixed edges (the corner of 1533, the ridge of 1525, the kerb line) within 1.5 percent of image width, which is 38 pixels at 2560 | An object 0.3 m out of place at 20 m shifts by 1.5 percent of a 24 mm frame. Solving the camera from the photograph removes the station and heading errors, which would otherwise add about 1 percent. |
| Transfer from Revit to Unreal | 1 mm on a known dimension; 5 mm on floor levels; 10 mm on fixture positions | Both are exact digital models. These figures check the transfer and say nothing about reality. |
| Sun direction | 0.5 degree in bearing and height against the NOAA calculator | The calculator and the engine's sun tool both compute from latitude, longitude, date and time. |
| Shadow edges on the ground | 0.3 m against the photograph taken at the same time | Follows from true north at 0.2 degree and heights at 0.3 m. |
| Colour of principal materials | Colour difference of 5 or less (CIEDE2000) after balancing both images on the grey card | Site visit: a grey card in every photograph. Without the card no colour tolerance is claimed. |
| Brightness of sunlit sidewalk concrete | Within one third of a stop | Same grey-card method. |
| Real-time render against the path-traced render of the same view | Mean brightness difference of 10 percent or less over the facade and ground; no region larger than 2 percent of the frame differing by more than one stop | **A proposal.** The first measured pair in Phase 8 confirms or resets it. |

Where the site visit does not happen, every "site visit" row falls back to the weaker figure named in its evidence column, and the species, trunk and colour rows cannot be scored at all.

## Site visit: shot list and measurement list

Bring a tape or laser measure, a grey card, a phone or camera that records time and focal length in its files, and chalk or a marker for station points.

**At each exterior station S1 to S7 and S9**

1. Mark the station. Tape its distance to two fixed points that will survive construction (a fence post of 1533, a kerb joint, a pole base) and note them.
2. Take the photograph at 1.60 m eye height at the heading and pitch in the table, in landscape format, with the grey card held in the first frame and removed for the second. Aim the centre of the frame at a named fixed target (for example the south corner of 1533 at sidewalk level) and note the target; the heading is recovered from it.
3. Take three exposures of the second frame: metered, one stop under, one stop over.
4. Note the clock time if the camera does not record it.

**Materials, each as a square-on photograph with the grey card and a tape visible for scale, plus one at a glancing angle**

5. Brick, stone bands and arch faces of 1533; its iron fence; its window frames.
6. Siding, trim, windows, steps and roof edge of 1525.
7. Each building opposite the site: wall material, garage door, stair, railing.
8. Sidewalk concrete with a joint, kerb, asphalt including a patch, driveway apron, parkway soil.
9. Alley paving, garage doors and fences behind the lot.

**Trees: for every tree whose crown is visible from any station**

10. Position: tape from two fixed points to the trunk centre.
11. Trunk circumference at 1.37 m above ground.
12. Photographs of the bark, a twig with buds, the whole form from two directions, and any fallen leaves beneath.
13. Height by laser if the top is visible.

**Street furniture: for every pole, hydrant, sign, cabinet and fence within 40 m of the lot**

14. Position as for trees. Height or mounting height. A photograph of the whole item and of its head or face.
15. For light poles: the fixture's label if readable, and whether the light is warm or cool at dusk.

**Dimensions**

16. Roadway width kerb to kerb, parkway width, sidewalk width, kerb height, on both sides.
17. Alley width.
18. Height of 1533's parapet and of 1525's eave and ridge by laser.
19. The construction fence and any site hoarding as it stands, for the record.

**Keep out of frame where possible:** people's faces and vehicle plates. Any that appear are blurred before a photograph enters the project.
