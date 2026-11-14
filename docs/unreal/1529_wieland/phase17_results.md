# Phase 17 results: an accurate site model, and the downtown skyline from the roof deck

Companion to [PLAN.md](PLAN.md), section "Phase 17". Written as each step finishes, so a new session can resume from it.

Status: IN PROGRESS (started 12:33 Central on 2026-11-14, headless session, Opus).

## Words used here

- **Laser scan**: the Illinois Height Modernization airborne lidar of Cook County, spring 2022. **Surface model (DSM)**: its highest-return heights on a 1 ft grid (roofs, tree tops). **Ground model (DTM)**: its bare-ground heights on the same grid. **Point cloud**: the scan's individual classified returns (LAS/LAZ files).
- **Level**: one saved Unreal scene file. **Static mesh**: the stored shape of one object. **Nanite**: the engine's system that draws very dense meshes cheaply. **HLOD** (hierarchical level of detail): simplified far versions of groups of objects that the engine swaps in at a distance.
- **Variant Manager**: the engine's tool that holds lists of named options; choosing an option shows some objects and hides others.
- **D1**: the penthouse roof deck design view (`REFERENCE_VIEWS.md`), level position (-1300, -1560, 1684) cm, looking toward (-900, -2300, 1640).
- Level frame (`phase2_results.md`, step 2.5): origin at the lot's south-west corner, north is -X, east is -Y, centimetres, Z = 0 is 595.45 ft above NAVD 88.

## How to resume, if this chat ends

1. Read the journal below from the bottom up. A line that still reads PENDING marks the step that was running; inspect what it was making (files under `E:\Wieland1529_site_data\phase17\`, `D:\Wieland1529_lidar\`, assets under `/Game/Wieland1529/Surroundings/P17/`) before repeating it.
2. Scripts are in `tools\phase17_*.py`; each skips work whose output already exists.
3. Downloads are listed in `asset_downloads.csv` (rows "Phase 17").
4. Never save `L_R15_Production`, never "Save All", keep `r.RayTracing.Nanite.Mode` at 0.

## Journal

| No. | Time | What is done | Outcome |
|---|---|---|---|
| J1 | 12:33 | Checks before work, read-only: editor answers with `L_Site_M4` open; `r.RayTracing.Nanite.Mode` 0; `r.Material.UseShaderCompilationParameters` 0; free commit 24.4 GB of 79.1 (editor holds 21.9 GB); free disk D: 97 GB, E: 29 GB. Three levels were already marked unsaved by an earlier session (`L_Site_M4`, both penthouse levels); they are not saved by this phase. | DONE 12:33. |
| J2 | 12:34 | Step 17.1 data: read the Illinois portal's terms; fetch the surface and ground models over the whole area the project can see (coarse, 2 m cells, for the viewshed), into `E:\Wieland1529_site_data\phase17\`. Not heavy (outside the editor, a few hundred MB). | DONE 12:52. Terms read (ISGS Clearinghouse terms of use: cite "Illinois State Geological Survey"; service metadata "no restrictions"). Surface and ground models over State Plane east 1,160,000 to 1,190,000 ft, north 1,886,000 to 1,922,000 ft (9.1 by 11.0 km) at 6 ft cells, 69 + 55 MB (`rastersiew6ft_*.npz`). Two faults fixed on the way (PROJECT_MEMORY, Phase 17, 1 and 2). Point cloud: the state serves it only as five zip files of 0.74 to 0.98 TB; the server accepts range requests, so single tiles (2,500 ft square, 1.0 to 1.4 GB) are read out of the zips remotely by `tools\phase17_remote_zip.py` (members of all five parts listed, 5,337 tiles). USGS 3DEP holds only the 2017 Cook scan, not 2022. Also fetched: City of Chicago building footprints in the box (77,000, 2015 vintage, 103 MB), Cook County 2022 footprints in the box (57,531, 56 MB). |
| J3 | 12:53 | Step 17.1 viewshed by `tools\phase17_viewshed.py`: radial line of sight from D1, the south roof deck (D1S), D2, D5 and stations S1 to S6 and S9, over the 6 ft surface model, with and without trees. OpenStreetMap buildings of the downtown sector fetched in parallel (`tools\phase17_fetch_osm.py`, 0.01 degree boxes, 5 s pause). | First run DONE 12:55 (D1: 651 city footprints with a visible cell, 226 beyond 800 m with 3 or more; Willis Tower due south at 3.49 km). Re-run with the 2022 county footprints PENDING. |
