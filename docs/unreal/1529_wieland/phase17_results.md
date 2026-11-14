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
| J2 | 12:34 | Step 17.1 data: read the Illinois portal's terms; fetch the surface and ground models over the whole area the project can see (coarse, 2 m cells, for the viewshed), into `E:\Wieland1529_site_data\phase17\`. Not heavy (outside the editor, a few hundred MB). | PENDING |
