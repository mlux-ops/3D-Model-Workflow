# Phase 2 results: site data and georeferencing

Companion to [PLAN.md](PLAN.md). This file is written as each step finishes, so a new session can resume from it. Phase 1's record is [phase1_results.md](phase1_results.md).

**Status at 16:00 Central on 2026-11-11: Phase 2 is complete as far as it can be without the site visit. All four acceptance lines pass, two of them by a route that differs from the plan's wording; each difference is named in the acceptance list.** The owner wrote "continue" at about 15:20 after Phase 1 was closed, and approved the phase's downloads at about 15:35 (answer "B"). Nothing in the Unreal project was changed in this phase: the existing level was only read.

**What is not done, exactly:** the site visit (step 2.1) and the two steps that depend on its photographs and measurements (the rest of 2.8, and 2.9). They are the owner's. Nothing later in the plan is blocked by them: what the visit would have shown is listed in `site_gaps.md` and is shown as neutral placeholders until evidence arrives.

**The six things this phase found that later phases need:**

1. **The lot in the level.** The level's origin is the lot's south-west corner. The level's north (-X) runs along the front lot line and east is -Y, the axes of the existing level and of the Revit export. The lot that governs is the record rectangle, 49.50 ft by 102.20 ft: 15.088 m by 31.151 m.
2. **True north.** The front lot line runs 1.18 degrees west of true north.
3. **The Revit export and the existing level sit in this frame by a shift only:** new x = old x + 15,482.32 cm, new y = old y + 5,053.7 cm, as far as the earlier registration's figures hold. Phase 3 checks it against the export's own survey point.
4. **Wieland Street's right-of-way is 50 ft, not 66 ft,** and there is no alley behind the lot. The stations are re-set; station S7 cannot exist as written.
5. **The existing site model is in the right place** (within 0.25 m, turned about 1.1 degrees) with heights typically 1.1 m low, and it has no building directly behind the lot.
6. **The county's parcel is 1.1 to 1.2 ft deeper than the record lot.** Its front line is right and its rear line is not; do not take lot depth from it.

## Acceptance list

| Line | Target | Result | Status |
|---|---|---|---|
| Lot corners | Three surveyed lot corners convert from map to level coordinates and back within 0.05 m | **All four corners of the governing lot return to the start exactly (0.000 m).** The projection itself agrees with the county's own figures within 2.4 mm. The corners are the record lot's, placed on the county's front line; the plat of survey has no coordinates of its own to convert. | **Pass** |
| True north | Recorded to 0.2 degree; two methods (parcel outline and the survey's north arrow) agree within 0.3 degree | **The street grid runs 1.17 degrees west of true north by the parcel lines of the block and 1.14 degrees by the walls of its buildings in the 2022 footprints: 0.03 degree apart.** The lot's own front line gives 1.18. The plan's second method cannot be used: the survey carries no bearing, only a north arrow drawn along the street. Building walls, which come from 2022 imagery and laser scan and not from the parcel records, stand in as the independent second method. | **Pass, with a different second method** |
| Plan view | The lot outline and the neighbours' footprints over the county aerial photograph show every kerb line and building corner within 1.0 m | **The east kerb: within 0.3 m, which is the limit of 1 ft cells. Building corners that the survey ties to the lot lines: within 0.64 m.** Measured, not judged by eye: the kerb's step in the 2022 ground surface lies between 11 and 12 ft from the front lot line, where the site plan puts it at 11 ft 10 1/4 in; and the 2022 footprints' corners are set against the survey's ties, the worst being the south-west corner of number 1533. The overlay picture was made from the data and is kept outside the repository because it contains the county's photograph; it is not an engine render, since the scene has no new surroundings yet. | **Pass, by measurement** |
| Trees and street furniture | Every tree and item of street furniture visible from a station has a row in the survey table or in the gaps list | **26 rows in `site_survey.csv`, 34 tall objects in `review\phase2\site_trees.csv`, and 12 gaps in `site_gaps.md`.** Every kind of thing a station can see is in one of the three. Most trees and all street furniture are there as gaps, because the visit was not made. | **Pass, mostly by the gaps list** |

## Where each step stands

| No. | Step | Status |
|---|---|---|
| 2.1 | Site visit | **The owner's, not done.** Not required for anything below. |
| 2.2 | Download the map data for a 300 m square around the lot | **Done** with the owner's approval: 24.4 MB, against the 5.5 GB the plan allowed. See "Step 2.2". |
| 2.3 | Read each file's coordinate system; convert everything to one system | **Done.** Every file states Illinois State Plane East in US survey feet; the parcels on the 1983 datum, the rest on its 2011 adjustment. No difference between the two shows at the lot beyond about 0.1 m. See "Step 2.3" and "What is in the site data folder". |
| 2.4 | True north from the parcel outlines and from the survey | **Done,** with building walls in place of the survey's arrow. See "Step 2.4". |
| 2.5 | Level origin, level-to-map transform, the sun tool's north offset | **Done,** apart from the sign of the sun tool's offset, which Phase 8's sun check settles between two stated values. See "Step 2.5". |
| 2.6 | Re-anchor the existing site model; measure how far its buildings sit from the map data | **Done as a measurement.** The existing level was not moved or saved: it is never saved, and Phase 4 builds new surroundings. The tie between its frame and the new one is a shift. See "Step 2.6". |
| 2.7 | Ground, kerb and sidewalk levels, roof heights and shapes, tree crowns | **Done** from the state's two height surfaces and the county's footprints. See "Step 2.7". |
| 2.8 | Enter the site-visit measurements | **Part done.** `site_survey.csv` holds 26 rows from the plat of survey, the site plan and the 2022 surfaces. The rows only a visit can give are in the gaps list. |
| 2.9 | Name each tree's species from the owner's photographs | **Waits for step 2.1.** No photographs exist. |
| 2.10 | List every gap | **Done.** `site_gaps.md`, 12 gaps. |

## Checks made before any work

Made between 15:22 and 15:30 on 2026-11-11.

| Check | Result |
|---|---|
| The editor | Answers. It has **not** been restarted since 11:39 (same process, 23.4 GB, free commit 17.8 GB), so `r.Lumen.WorldCache.Supported` still reads true in the running editor. The first check that the plan asks of the next session stays open until the restart. Phase 2's first steps do not use the editor. |
| The import workaround | `r.Material.UseShaderCompilationParameters` read 0 at 13:38; the settings file has not changed since. |
| The plan's working copy | Clean at commit `b81b76f`. |
| Web access | Reading web pages works from this session, and `curl` is present. |
| Python | 3.14.6 with NumPy 2.5.0, SciPy 1.18.1, Shapely 2.1.2, Pillow 12.2.0, requests and pypdf. **No map-projection package (pyproj) and no reader for compressed laser-scan files (laspy, lazrs).** Neither is needed for the route chosen below, so no install is asked for. |
| Map data already on disk | None. The repository holds no laser-scan, parcel, footprint or georeferenced image file. |
| The Georeferencing plugin | Not enabled in the project (the project file enables Sun Position and the Datasmith importer). Step 2.5 names it as its tool. It is not needed to record the transform, which this phase keeps in a file and applies with `tools\wieland_geo.py`. Enabling it would need another editor restart; it is left off unless a later step needs it inside the engine. |
| The survey | The earlier project's registration file (`E:\Games\Claude\1527 Wieland\fbx_walkthrough\01_sources\manifests\registration_r01\registration_basis.json`) holds the building's width and floor heights and the model's axes (-X north, +Y east, -Y the Wieland frontage), **but no lot-corner coordinates and no bearings.** It names the drawing set, `25-006 1527 N Wieland_Arch_20260722.pdf` on the owner's Google Drive, with sheets T1.1 (survey) and T1.4 (site plan). The corners and the survey's north arrow have to be read from that file. |

## Step 2.3: the conversion between map coordinates and latitude and longitude

Written as `tools\wieland_geo.py`, in plain Python, so that no package has to be installed. It converts between latitude and longitude and Illinois State Plane East coordinates in US survey feet (the system of every county and state layer this phase uses), gives the angle between grid north and true north, and ties map coordinates to the Unreal level once step 2.5 has chosen the origin.

Checked on 2026-11-11 against the county's own figures for the two parcel centres (`SOURCES.md`), by running the file:

| Parcel centre | This file, east and north (ft) | County, east and north (ft) | Difference (ft) |
|---|---|---|---|
| 1529, PIN 17-04-203-010-0000 | 1,174,226.838 and 1,910,657.545 | 1,174,226.83 and 1,910,657.55 | +0.008 and -0.005 |
| 1527, PIN 17-04-203-011-0000 | 1,174,227.556 and 1,910,632.806 | 1,174,227.55 and 1,910,632.81 | +0.006 and -0.004 |

The largest difference is 0.008 ft, 2.4 mm, which is inside the rounding of the county's figures. Converting the county's east and north back gives the county's latitude and longitude to all seven decimals. A conversion there and back returns to the start within 0.000000000001 degree.

Read from the same check:

- **Grid north lies 0.4662 degrees east of true north at the site.** A true bearing is the grid bearing plus 0.4662 degrees.
- The projection stretches distances by 1.6 mm in 100 m at the site, which is far inside the phase's 0.05 m tolerance and is ignored.
- From the centre of 1527 to the centre of 1529 the line runs 1.665 degrees west of grid north, so **1.20 degrees west of true north**. This is a first figure from two points 24.74 ft apart; step 2.4 replaces it.

The plan's acceptance line "three surveyed lot corners convert from map coordinates to level coordinates and back within 0.05 m" is met by the code as far as arithmetic goes (it returns to the start exactly); it is counted as passed only when the three corners themselves are in hand.

## Step 2.2: what would be downloaded, from where, and how large

Confirmed on 2026-11-11 by reading each service's own description page. Nothing was requested for the site itself.

| Data | Source | What the service says | Extract for the 300 m square | Size |
|---|---|---|---|---|
| Parcel outlines, 2025 | Cook County, `gis.cookcountyil.gov/traditional/rest/services/parcelHistorical/MapServer/2025` | Polygons; State Plane East, 1983 datum (EPSG 3435); returns GeoJSON; fields include the 14-digit PIN | The parcels that touch the square | Under 1 MB |
| Building footprints, 2022 | Cook County, `.../buildingFootprint_2022/MapServer/0` | Polygons; State Plane East, 2011 adjustment (EPSG 6455); fields `Ground_Z`, `Max_Point`, `Height` | The footprints that touch the square | Under 1 MB |
| Aerial photograph, 2025 | Cook County, `gis.cookcountyil.gov/imagery/rest/services/CookOrtho2025/ImageServer` | 0.5 ft pixels, four bands, State Plane East 2011 | 1,970 by 1,970 pixels | About 16 MB |
| Surface heights, 2022 (roofs and tree tops) | Illinois State Geological Survey, `data.isgs.illinois.edu/arcgis/rest/services/Elevation/IL_Cook_DSM_2022/ImageServer` | 1 ft cells, heights in US survey feet above NAVD 88, State Plane East 2011; made from the 2022 laser scan | 985 by 985 cells | About 4 MB |
| Ground heights, 2022 | The same survey, `.../IL_Cook_DTM_2022/ImageServer` | As above, bare ground | 985 by 985 cells | About 4 MB |
| | | | **Total** | **About 25 MB** |

The square is 300 m on a side, centred between the two parcel centres: east 1,173,735 to 1,174,720 ft and north 1,910,153 to 1,911,138 ft in State Plane East.

**A change from the plan, and why.** The plan budgets up to 4 GB for raw laser-scan tiles and expects a point-cloud package to read them. The state publishes two ready-made surfaces from the same 2022 scan, at 1 ft cells: the top surface (roofs and tree tops) and the bare ground. Their difference is the height of everything above ground. Together with the footprints they give ground, kerb and sidewalk levels, each neighbour's roof height and roof shape, and each tree's crown height and spread, which is what step 2.7 asks for. They are about 8 MB, need no package, and carry the same terms ("No restrictions apply to these data"). Raw tiles are held back for the case where a 1 ft surface proves too coarse for a roof edge or a kerb; that would be an estimated 0.1 GB a tile (not yet confirmed on the tile page) and two small packages, and would be asked for then.

**Where it would be written:** `E:\Wieland1529_site_data\`, a new folder outside every repository, with a text file beside each download naming its address, its date and its terms. Not into the repository: the county's terms leave redistribution unclear (`SOURCES.md`), and both the plan's working copy and the main checkout's `references\` folder are under git.

### The downloads

Each is written here before it is made, as in Phase 1.

| No. | Time | What is done | Outcome |
|---|---|---|---|
| D1 | 15:42 on 2026-11-11 | With the owner's approval: create `E:\Wieland1529_site_data\` and fetch the five extracts into it with `tools\fetch_site_data.py` (a 300 m square, snapped outward to each image service's own pixel grid, nearest-neighbour sampling, each file beside a text file naming its address, time, box, checksum and terms). Then copy sheets T1.1 and T1.4 out of the drawing set, which is on the owner's Google Drive and reachable on this machine as `F:\Shared drives\SHB Jobs\25-006 1529 N Wieland\5-Drawings\PDFs\20260722_Progress\25-006 1527 N Wieland_Arch_20260722.pdf` (42.5 MB), into `E:\Wieland1529_site_data\drawings\`. The whole set is not copied. | **Done, 15:37 to 15:42.** The five extracts arrived, 24.4 MB in all: 258 parcels, 170 footprints, the two height surfaces at 985 by 985 cells, and the aerial photograph at 1,969 by 1,969 pixels. Sheets T1.1 and T1.4 were copied out of the drawing set (pages 2 and 5 of 20; 5.1 MB) and the set itself was only read. See "What is in the site data folder". |
| D2 | 15:40 on 2026-11-11 | A package had to be installed after all, under the standing approval: the survey on sheet T1.1 is a picture with no text in it, and this machine had nothing that can draw a PDF page (the session's own reader needs a program that is not installed). `pymupdf` was installed with `pip install --target`, into `E:\Wieland1529_site_data\_python_packages\`, so that nothing was added to Python itself or to C:. | **Done, and larger than it should have been: 225 MB in 3,778 files.** The package's current version pulls in a set of others (among them `onnxruntime` and a second copy of NumPy) that drawing a page does not need. It works: the sheets were drawn as pictures and read. Nothing in Python's own folders changed; the folder is put on the path only for `tools\render_pdf_page.py`. Removing the unneeded part is a deletion and was not done. |

### What is in the site data folder

`E:\Wieland1529_site_data\`, outside every repository, 277 MB at 15:42 on 2026-11-11:

| What | Files | Size |
|---|---|---|
| The five extracts, each with a `.source.txt` beside it, and `fetch_record.json` | 11 | 24.4 MB |
| `drawings\`: sheets T1.1 and T1.4 as one-page PDFs with the text found on them, four pictures drawn from them, and `drawings.source.txt` | 9 | 8.1 MB |
| `drawings\T1.1_embedded_pictures\`: 90 picture tiles pulled out of sheet T1.1 in a first attempt to read it. They are of no use, and are kept only because removing them is a deletion | 90 | 19.2 MB |
| `_python_packages\`: `pymupdf` and what it pulled in | 3,778 | 225.2 MB |

The coordinate system each file states for itself (step 2.3): the parcels say EPSG 3435 (State Plane East, 1983 datum, US survey feet); the footprints say EPSG 6455 (the same projection on the datum's 2011 adjustment); the three image services describe themselves as "NAD 1983 (2011) State Plane Illinois East, US feet", and the two height surfaces give heights in US survey feet above NAVD 88. So everything is in one projection and one unit, and the only difference is the datum's realization between the parcels and the rest. That difference is measured, not assumed, in step 2.4.

## What the survey and the site plan say

Read on 2026-11-11 from the two sheets, drawn as pictures at 220 dots per inch. The plat of survey is by Professionals Associated - MM Survey Co., order 19-94826, fieldwork 18 August 2025, signed 20 August 2025, scale 1 inch to 15 ft. It describes two parcels, "commonly known as 1527-31 North Wieland Street", 5,132.96 sq ft in all.

**The lot as measured.** Lengths in feet; "record" is the figure of the recorded plat, "measured" is what the surveyor found on the ground.

| Line | Record | Measured |
|---|---|---|
| West line, the Wieland frontage | 49.50 | 50.18 (north parcel 24.75, south parcel 25.43) |
| North line | 102.20 | 102.01 |
| East line, the rear | 49.50 | 50.50 (north parcel 24.75, south parcel 25.75) |
| South line | 102.20 | 101.93 |

| Corner | Angle inside the lot |
|---|---|
| North-west | 90 degrees 11 minutes 38 seconds |
| North-east | 89 degrees 43 minutes 03 seconds |
| South-east | 90 degrees 06 minutes 06 seconds |
| South-west | 89 degrees 59 minutes 13 seconds |

The four angles add to exactly 360 degrees, and walking the four measured sides with those angles returns to the start within 0.003 ft, so the figures were read correctly.

**Six things the sheets settle or change:**

1. **The survey carries no compass bearing.** It gives lengths and angles, and a north arrow drawn along the street. So the plan's second way of finding true north, "the survey's north arrow", is not a measurement. Step 2.4 uses a different second way; see there.
2. **Wieland Street's right-of-way is 50 ft wide, not 66 ft.** The plat marks "50' R.O.W. public street" and 25.00 ft from the front lot line to the street's centre line. The plan had assumed 66 ft, which is why station S1 fell inside the building opposite in Phase 1. The site plan gives 11 ft 10 1/4 in from the front lot line to the kerb.
3. **There is no alley behind the lot.** The rear line meets the neighbours' lots directly: a four-storey brick and concrete-block building 0.22 to 0.34 ft east of the line, and a two-storey brick and block building, number 1532, at the south-east corner. `REFERENCE_VIEWS.md` lists the alley as unseen; it does not exist here.
4. **The property lines that govern are the record ones.** The owner settled that the Revit model's property lines govern, and the site plan draws them as 49.5 ft by 102.2 ft. The measured frontage of 50.18 ft appears on the site plan only as a note (50 ft 2 1/4 in).
5. **The neighbours' walls against the lot lines:** number 1533 to the north, a five-storey brick building, stands on the north line; number 1525 to the south, a two-storey frame building, stands 0.37 to 0.68 ft south of the south line. These are used below to check the map data.
6. **In the parkway:** a concrete kerb and walk, three planters and an iron fence on the plat; two existing parkway trees and a new sod planter 5 ft by 7 ft 11 in on the site plan. The north-west lot corner is 266.87 ft south of the south line of West North Avenue.

The two houses the plat shows on the lot, numbers 1527 and 1531, are the ones since demolished.

## Step 2.4: the lot on the map, and true north

Measured at 15:45 to 15:50 on 2026-11-11 with `tools\site_analysis.py`. Every figure is in `review\phase2\site_analysis.json`.

**The county's parcel against the record and the survey.** The lot is the two county parcels of the site taken together.

| Measure | County parcels, 2025 | Record | Survey, measured |
|---|---|---|---|
| Frontage (ft) | 49.50 | 49.50 | 50.18 |
| Depth (ft) | 103.32 on the north line, 103.40 on the south | 102.20 | 102.01 and 101.93 |
| Right-of-way width at the lot (ft) | 50.05 | - | 50.00 |
| North-west corner to the south line of West North Avenue (ft) | 269.35 | - | 266.87 |

The county's parcel has the record frontage and is 1.1 to 1.2 ft too deep. Which of its two long ends is off was settled by two things that do not depend on the parcel records:

- **The kerbs.** In the 2022 ground surface the east kerb's step lies between 11 and 12 ft west of the county's front line and the west kerb's between 38 and 39 ft. The site plan puts the east kerb 11 ft 10 1/4 in from the front lot line, and the two kerbs sit evenly about the middle of the 50 ft right-of-way. So the county's front line is where the survey and the site plan have it.
- **The wall behind the lot.** The survey puts the four-storey building's wall 0.22 to 0.34 ft east of the rear line. With the record depth that is 102.4 to 102.5 ft east of the front line, and the county's 2022 footprint of that building has its near edge at 102.1 to 103.1 ft. With the county's own rear line it would have to be at 103.6.

**So the lot that governs is the record rectangle, 49.50 ft by 102.20 ft, on the county's front line, with its south-west corner at the county parcel's south-west corner.** This is also what the owner settled: the Revit model's property lines govern, and the site plan draws them at these dimensions. The county's rear corners lie 0.34 and 0.37 m beyond it and are not used. Along the street the county's parcels and the survey differ by 2.5 ft over 267 ft to North Avenue; that is a difference in other owners' lots and does not move this one, whose north line carries number 1533's wall within 0.33 ft in the 2022 footprints.

| Corner of the governing lot | Latitude | Longitude | State Plane east and north (ft) | Level x and y (cm) |
|---|---|---|---|---|
| South-west | 41.91014441 | -87.63557673 | 1,174,176.240 and 1,910,619.020 | 0.00 and 0.00 |
| North-west | 41.91028022 | -87.63558046 | 1,174,174.820 and 1,910,668.500 | -1,508.76 and 0.00 |
| North-east | 41.91028598 | -87.63520509 | 1,174,276.978 and 1,910,671.431 | -1,508.76 and -3,115.06 |
| South-east | 41.91015018 | -87.63520136 | 1,174,278.398 and 1,910,621.952 | 0.00 and -3,115.06 |

**True north.** A bearing below is the turn of a line of the street grid from north, negative to the west. Grid north of the State Plane system lies 0.4662 degrees east of true north here, so a true bearing is the grid bearing plus 0.4662.

| Method | Grid bearing (degrees) | True bearing (degrees) | Basis |
|---|---|---|---|
| The lot's front line, county parcel | -1.6438 | **-1.1776** | One line, 49.5 ft long |
| 1. Parcel lines of the block | -1.6327 | -1.1665 | 527 parcel edges over 40 ft, 300 m square; they scatter by 0.10 degree |
| 2. Building walls, 2022 footprints | -1.6074 | -1.1412 | 500 wall lines over 25 ft; they scatter by 0.75 degree |

The two methods differ by 0.025 degree. The value recorded for the site is the lot's own front line: **the level's north runs 1.18 degrees west of true north.** The county parcel's rear line bears 0.09 degree differently from its front line, which is one more sign that the rear line is the weak one.

## Step 2.5: the level frame

Recorded in `review\phase2\level_frame.json` and applied by `tools\wieland_geo.py` (`LevelFrame`).

| | |
|---|---|
| Origin | The lot's south-west corner: level 0, 0, 0 |
| Origin on the map | East 1,174,176.240 ft, north 1,910,619.020 ft (Illinois State Plane East); latitude 41.91014441, longitude -87.63557673 |
| Origin's height | 595.45 ft above NAVD 88, the ground there in the 2022 surface. Level Z = 0 is that height. |
| North | -X, along the front lot line, south to north. Its grid bearing is -1.6438 degrees and its true bearing -1.1776. |
| East | -Y, toward the rear of the lot |
| Units | Centimetres; 1 US survey foot is 30.48006 cm |

**These are the axes of the existing level and of the Revit export.** A first version of the frame had east on +Y, taken from the earlier project's registration file, which describes Blender's frame. That would have mirrored the site. It was caught before anything used it, by setting the frame beside Phase 1's record of the level's axes; `wieland_geo.py` now checks the handedness when it is run.

**The tie to the existing level and to the Revit export:** both have the lot's centre line at X = -16,236.7 and its front line at Y = -5,053.7 (`phase1_results.md`, "Positions used"), with the same axes. So

    new x = old x + 15,482.32 cm        new y = old y + 5,053.7 cm

and no turn. This rests on the earlier registration's two figures, which were taken from an older FBX export of the same Revit model.

**What the Datasmith export itself carries, read from the second export at 16:02:** a site-location object at 0, 0, 0; a survey point at (1,800.66, 1,703.06, -25,043.59) cm; and a project base point at (-3,722.25, -2,091.81, 0) cm, each with its Revit element ID. Its only data about them are the two points' positions in Revit's own coordinates. It holds no latitude or longitude, no map coordinates for the survey point and no angle to true north. In the new frame the survey point lies 173 m south and 68 m west of the lot's south-west corner and the base point 118 m south and 30 m west, so neither is a lot corner. **Step 3.3 of the plan, "place the import by the Revit survey point", therefore cannot work as written:** the survey point's place in the real world is not in the file. Phase 3 has to place the building by the lot instead: find the property lines or the site object in the import, or the building's street face (10 ft 2 1/2 in behind the front lot line, 43 ft 4 in wide, centred on the lot), and check that the shift above puts them on the governing lot.

**A true bearing to a yaw in the level:** yaw = bearing - 178.82 degrees. Phase 1 used "bearing - 180", which assumed the level's north was true north; it is 1.18 degrees off.

**The sun tool's north offset:** 181.18 or 178.82 degrees. True north lies 1.18 degrees clockwise of the level's -X, and Phase 1 found that the tool takes +X as north at offset 0; which sign the tool's offset has was not tested here. Phase 8 settles it with the sun check of step 1.10: the right value puts the sun of 15 August, 15:30 at NOAA's bearing.

**The stations, re-set.** With a 50 ft right-of-way the west kerb is 11.7 m and the far side of the west sidewalk 15.2 m west of the front lot line, so the west walking line is at 14.0 m. The plan had it at 18 m, inside the buildings opposite. `review\phase2\stations.csv` gives every station in every frame; station S1 is at latitude 41.9102097, longitude -87.6357473, which is level (-754.4, 1,400.0) and existing level (-16,236.7, -3,653.7). Station S7 has no place: there is no alley.

## Step 2.6: the existing site model against the map data

Measured at 15:50 to 15:53 on 2026-11-11, read-only. The existing level `L_R15_Production` was open with nothing unsaved before and after. Its top surface was read by tracing straight down at every point of a 2 m grid, 266 m square, with `tools\wieland_site_probe.py` (17,956 points, 5,652 of them over the model), and compared with the 2022 surfaces and footprints by `tools\compare_existing_model.py`. Records: `review\phase2\existing_model_heights_2m.*`, `existing_model_street_sections.json`, `existing_model_vs_map.json` and `.csv`.

**The level was not re-anchored in the sense of moving it.** It is never saved, and the owner settled that the surroundings are built new in Phase 4. What Phase 2 leaves is the tie between its frame and the new one (the shift under "Step 2.5") and the measure of how good it is.

| Measure | Result |
|---|---|
| Extent of the model | 104 m south to 98 m north of the lot's south-west corner; 46 m west to 136 m east |
| Position of its buildings | The overlap of its building areas with the 2022 footprints is 0.59 as it stands and at best 0.63, reached with a shift of 0.25 m and a clockwise turn of 1.1 degrees. So it is in place within a quarter of a metre, and its buildings are laid out about a degree off the lot, which fits the earlier note that its north was assumed to be true north |
| Heights | 43 buildings compared: the model is 1.1 m lower than the 2022 scan at the middle of the range; 15 are within 1 m and 36 within 3 m |
| The street at the lot | East kerb 3.6 m and west kerb about 11.5 m west of the front lot line, road crown at 7.5 m: within 0.2 m of the 2022 surface (3.6, 11.7 and 7.7 m). The west buildings' faces at 17.2 to 18.1 m, where the 2022 footprints have 17.6 and 18.1 m |
| Missing | 12 footprints of 2022 have no building in the model. One is the four-storey building directly behind the lot, 14.3 m high; the others near the lot are low structures of 3.6 to 3.8 m |

Nearest neighbours, heights above ground in metres:

| Building | Model | 2022 scan, middle of the roof | County's figure, highest point |
|---|---|---|---|
| Number 1533, north, on the lot line | 15.0 | 13.8 | 15.3 |
| Number 1525, south | 8.1 | 8.4 | 9.4 |
| Four-storey building behind the lot | none | 14.3 | 15.1 |
| Behind the lot, to the south | 10.5 | 10.0 | 14.9 |
| Number 1532, at the south-east corner | 6.8 | 5.8 | 9.7 |
| Opposite, across Wieland | 15.3 and 14.6 | 15.1 and 15.4 | 18.3 and 17.4 |

The county's figure is each building's highest point, which is a chimney, a penthouse or a parapet; the scan's figure here is the middle of the roof. A flat roof with a parapet reads about a metre apart between the two, as number 1533 does.

**Two things about the existing level that Phase 1 did not have right.** The lot itself holds no ground: a trace at the lot's centre hits nothing. And at the lot's centre line the west sidewalk is missing from 11.3 to 15.0 m west of the front lot line, which is the whole sidewalk there; station S1 stands over that hole. Phase 1's statement that the sidewalk was traced "along the whole path" holds 2.4 m to the south, where the surface is there, and not at S1 itself.

## Step 2.7: ground, kerbs, roofs and tree crowns

From the state's 2022 top surface and bare-ground surface (1 ft cells, flown leafless in spring 2022) and the county's 2022 footprints. Heights are feet above NAVD 88; the level's Z = 0 is 595.45 ft.

**Ground across the street and the lot,** through the middle of the frontage:

| Where | Ground (ft) | Above the level origin (m) |
|---|---|---|
| West right-of-way line, 50 ft west of the front lot line | 595.44 | 0.00 |
| West gutter, 37 to 38 ft west | 594.70 | -0.23 |
| Street centre line, 25 ft west | 595.33 | -0.04 |
| East gutter, 13 to 14 ft west | 594.86 | -0.18 |
| East sidewalk | 595.47 | +0.01 |
| Front lot line | 595.48 | +0.01 |
| Lot centre | 595.54 | +0.03 |
| Rear lot line | 596.78 | +0.41 |

The street is all but level; the kerbs stand 0.15 to 0.2 m above their gutters; the lot rises 0.4 m from front to rear. The full section at 1 ft steps is in `site_analysis.json`.

**Buildings.** 75 footprints lie within 260 ft of the lot. `review\phase2\site_neighbours.csv` gives each one's position in map and level coordinates, its footprint area, the ground under it, the height of the middle of its roof and of its high parts, whether the roof is flat or pitched, and the county's own height beside it. Two of the 75 are the houses that stood on the lot in 2022.

**Tall things outside buildings.** 34 within 330 ft, in `review\phase2\site_trees.csv`: everything over 15 ft above the ground and outside every footprint, 60 to 8,000 sq ft in plan. Most are tree crowns; some are poles, signs or roof parts that overhang a footprint. Four stand in Wieland's right-of-way within 150 ft of the lot, and two of those are the parkway trees the site plan marks at either end of the frontage: 12.7 m and 15.9 m tall, each about 10 m across when leafless. A crown's centre is not its trunk, and the scan is leafless, so spreads are low.

## The one approval this phase needs

Asked of the owner at 15:30 on 2026-11-11, as one request, by the plan's rule "Ask first" and the owner's instruction to this session.

| Action | Size on disk | Cost |
|---|---|---|
| Download the five extracts in the table above into a new folder `E:\Wieland1529_site_data\` | About 25 MB (E: has 65.8 GB free) | None |
| Read the survey sheet T1.1 and the site plan T1.4 from the drawing set `25-006 1527 N Wieland_Arch_20260722.pdf` on the owner's Google Drive, and keep a copy of those two sheets in the same folder | The size of the file, not yet known; the two sheets are a few MB | None |

Not asked for, because not needed on this route: any package install, raw laser-scan tiles, any change to the Unreal project.

**Approved by the owner at about 15:35 on 2026-11-11, with the answer "B".** The request had offered two answers. A was the two items above only. B, which the owner chose, is those two items **plus a standing approval** for the other items on the plan's approvals list that cost nothing, inside the plan's size caps: public-domain textures (10 GB in total), manufacturers' light-distribution files (under 50 MB), a Python package if one proves necessary, and render frames and project archives to H: as budgeted. Still asked each time: anything with a price, any deletion, and any push or merge. The standing approval is written into `PLAN.md` under "Approvals this plan will ask for".

## What only the owner can supply, and what happens without it

| Item | Step | Without it |
|---|---|---|
| The site visit: the shot list and measurement list of `REFERENCE_VIEWS.md` | 2.1, 2.8, 2.9 | The phase goes on from public data alone. Tree species, trunk sizes, street furniture, the alley, and anything built since spring 2022 are listed as gaps (step 2.10) and shown as neutral placeholders. They can be filled in whenever photographs arrive; nothing later is blocked. |
| Confirming true north against the survey's north arrow | 2.4 | Not possible for anyone: the survey carries no bearing, only an arrow drawn along the street. Building walls in the 2022 footprints took its place as the second method, and the two agree within 0.03 degree. |

## What was changed in the Unreal project

Nothing. The existing level was read with downward traces, and it had nothing unsaved before or after. No asset, level or setting was created, changed or saved. The editor had not been restarted since 11:39 when this phase ran, so the Lumen World Cache was still on in the running editor; that has no bearing on anything measured here.

No profile was run at the end of this phase: the plan asks for one from every phase that changes the scene, and this one did not.

## What the standing approval was used for

| Use | Size | Where |
|---|---|---|
| The five map extracts | 24.4 MB | `E:\Wieland1529_site_data\` |
| Sheets T1.1 and T1.4 copied out of the drawing set, with pictures drawn from them | 8.1 MB, and 19.2 MB of picture tiles of no use | `E:\Wieland1529_site_data\drawings\` |
| The Python package `pymupdf`, to draw a PDF page as a picture | 225.2 MB, far more than drawing a page needs | `E:\Wieland1529_site_data\_python_packages\` |
| Pictures made from the data, which contain the county's aerial photograph | 7.6 MB | `E:\Wieland1529_site_data\derived\` |

The folder holds 284 MB in all at 16:00. Nothing was bought, deleted or pushed. Two things in it are of no further use and could be removed if the owner wishes, 244 MB together: the picture tiles and the package. Running the tools also left a `__pycache__` folder beside them in the working copy; it is not committed.

## Files written in the plan's working copy

New:

- `docs\unreal\1529_wieland\phase2_results.md` (this file)
- `docs\unreal\1529_wieland\site_survey.csv`
- `docs\unreal\1529_wieland\site_gaps.md`
- `docs\unreal\1529_wieland\review\phase2\level_frame.json`
- `docs\unreal\1529_wieland\review\phase2\site_analysis.json`
- `docs\unreal\1529_wieland\review\phase2\site_neighbours.csv`
- `docs\unreal\1529_wieland\review\phase2\site_trees.csv`
- `docs\unreal\1529_wieland\review\phase2\stations.csv`
- `docs\unreal\1529_wieland\review\phase2\existing_model_heights_2m.f32`
- `docs\unreal\1529_wieland\review\phase2\existing_model_heights_2m.json`
- `docs\unreal\1529_wieland\review\phase2\existing_model_street_sections.json`
- `docs\unreal\1529_wieland\review\phase2\existing_model_vs_map.json`
- `docs\unreal\1529_wieland\review\phase2\existing_model_vs_map.csv`
- `docs\unreal\1529_wieland\tools\wieland_geo.py`
- `docs\unreal\1529_wieland\tools\fetch_site_data.py`
- `docs\unreal\1529_wieland\tools\extract_drawing_sheets.py`
- `docs\unreal\1529_wieland\tools\render_pdf_page.py`
- `docs\unreal\1529_wieland\tools\site_analysis.py`
- `docs\unreal\1529_wieland\tools\site_stations.py`
- `docs\unreal\1529_wieland\tools\wieland_site_probe.py`
- `docs\unreal\1529_wieland\tools\compare_existing_model.py`

Changed: `PROJECT_MEMORY.md`, `docs\unreal\1529_wieland\PLAN.md`, `docs\unreal\1529_wieland\OPEN_DECISIONS.md`, `docs\unreal\1529_wieland\REFERENCE_VIEWS.md`, `docs\unreal\1529_wieland\phase1_results.md`.

Not in the repository, on purpose: everything under `E:\Wieland1529_site_data\`. The county's terms leave redistribution unclear, and the drawing sheets are the owner's private documents. The tables in `review\phase2\` hold numbers measured from that data, not the data.
