# Phase 2 results: site data and georeferencing

Companion to [PLAN.md](PLAN.md). This file is written as each step finishes, so a new session can resume from it. Phase 1's record is [phase1_results.md](phase1_results.md).

**Status at 15:30 Central on 2026-11-11: begun; the groundwork that needs no approval is done; the next step waits for one approval.** The owner wrote "continue" at about 15:20 after Phase 1 was closed, and the session read that as: go on with the plan. Nothing has been downloaded, installed or changed in the Unreal project in this phase.

**What is waiting, exactly:** step 2.2 downloads public map data, and the plan and the owner's standing instruction both require approval before any download. The request is under "The one approval this phase needs". Everything after step 2.2 depends on that data.

## Where each step stands

| No. | Step | Status |
|---|---|---|
| 2.1 | Site visit | **The owner's, not done.** Not required for the steps below. Without it, everything a station can see that has no evidence goes into the gaps list of step 2.10 and gets a neutral placeholder, as the plan's rules say. |
| 2.2 | Download the map data for a 300 m square around the lot | **Prepared; waits for approval.** The sources are confirmed and the request is sized: about 25 MB, against the 5.5 GB the plan allowed. See "Step 2.2". |
| 2.3 | Read each file's coordinate system; convert everything to one system | **The conversion is written and checked;** the files' own headers are read when the files arrive. See "Step 2.3". |
| 2.4 | True north from the parcel outlines and from the survey | Not started. A first figure from the two parcel centres: the street runs 1.20 degrees west of true north. The parcel outlines (step 2.2) and the survey sheet give the real one. |
| 2.5 | Level origin, level-to-map transform, the sun tool's north offset | Not started. The transform's code is written (`tools\wieland_geo.py`, `LevelFrame`). |
| 2.6 | Re-anchor the existing site model; measure how far its buildings sit from the map data | Not started. Needs the editor, and is better made after the owner's restart. |
| 2.7 | Ground, kerb and sidewalk levels, roof heights and shapes, tree crowns | Not started. Planned from the state's ready-made height surfaces, not from raw laser-scan tiles; see "Step 2.2". |
| 2.8 | Enter the site-visit measurements | Waits for step 2.1. |
| 2.9 | Name each tree's species from the owner's photographs | Waits for step 2.1. |
| 2.10 | List every gap | Not started. |

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
| Confirming true north against the survey's north arrow | 2.4 | The session reads the arrow from sheet T1.1 itself and records both figures; the plan's test is that the two methods agree within 0.3 degree. |

## Files written in the plan's working copy

- `docs\unreal\1529_wieland\phase2_results.md` (this file)
- `docs\unreal\1529_wieland\tools\wieland_geo.py`
