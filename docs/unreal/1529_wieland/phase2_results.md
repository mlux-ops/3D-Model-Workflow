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

## The one approval this phase needs

Asked of the owner at 15:30 on 2026-11-11, as one request, by the plan's rule "Ask first" and the owner's instruction to this session.

| Action | Size on disk | Cost |
|---|---|---|
| Download the five extracts in the table above into a new folder `E:\Wieland1529_site_data\` | About 25 MB (E: has 65.8 GB free) | None |
| Read the survey sheet T1.1 and the site plan T1.4 from the drawing set `25-006 1527 N Wieland_Arch_20260722.pdf` on the owner's Google Drive, and keep a copy of those two sheets in the same folder | The size of the file, not yet known; the two sheets are a few MB | None |

Not asked for, because not needed on this route: any package install, raw laser-scan tiles, any change to the Unreal project.

## What only the owner can supply, and what happens without it

| Item | Step | Without it |
|---|---|---|
| The site visit: the shot list and measurement list of `REFERENCE_VIEWS.md` | 2.1, 2.8, 2.9 | The phase goes on from public data alone. Tree species, trunk sizes, street furniture, the alley, and anything built since spring 2022 are listed as gaps (step 2.10) and shown as neutral placeholders. They can be filled in whenever photographs arrive; nothing later is blocked. |
| Confirming true north against the survey's north arrow | 2.4 | The session reads the arrow from sheet T1.1 itself and records both figures; the plan's test is that the two methods agree within 0.3 degree. |

## Files written in the plan's working copy

- `docs\unreal\1529_wieland\phase2_results.md` (this file)
- `docs\unreal\1529_wieland\tools\wieland_geo.py`
