# Phase 20 results: refining the surroundings from open images

Companion to [PLAN.md](PLAN.md), section "Phase 20", and to `KICKOFF_PHASE20.md`. Written as each step finishes, so a new session can resume from it.

Status: IN PROGRESS (started 19:32 Central on 2026-11-14, editor panel session, Opus).

## Words used here

- **Material instance**: a copy of a parent material with its own settings (colours, window grid); each Phase 17 building has one (`MI_P17_T_<county id>` for the skyline, `MI_P17_Z_<county id>` for Zones 1 and 2), made from the facade parent `M_W1529_P17_Facade`. Phase 20 changes only the instances' settings, never the parent.
- **Linear colour**: the colour numbers the engine uses for lighting; a photograph's sRGB colour is converted to linear before it is set.
- **Confidence**: 1 (pure assumption by building type) to 5 (cladding, colour and window grid all confirmed by images), for how much a building looks like the real one.
- **Work list**: the buildings Phase 20 refines, in the order of how much of the views each fills.
- Other words as in `phase17_results.md` ("Words used here").

## How to resume, if this chat ends

1. Read the journal below from the bottom up. A line that still reads PENDING marks the step that was running; inspect its outputs (images in `E:\Wieland1529_site_data\phase20\`, observations in `review\phase20\`) before repeating it.
2. Scripts are in `tools\phase20_*.py`. Images are reference only: never imported as textures, never traced into geometry.
3. Downloads are listed in `asset_downloads.csv` (rows "Phase 20").
4. Never save `L_R15_Production`, never "Save All", keep `r.RayTracing.Nanite.Mode` at 0, keep the ground object's shadow off, and set `MSYS_NO_PATHCONV=1` when passing `/Game/...` paths from Git Bash. Text with backslashes goes through the Edit or Write tool only (PROJECT_MEMORY, Phase 17, error 35).

## Journal

| No. | Time | What is done | Outcome |
|---|---|---|---|
| J1 | 19:32 | Checks before work, read-only: the owner's photograph folder `D:\Wieland1529_owner_photos\`, a Mapillary token file there, KartaView coverage around the site and along the views to downtown, the editor's state. | DONE 19:34. Owner photographs: none (the folder holds only `README.txt`); checked again before the report. Mapillary: no token file, so Mapillary is not used. KartaView (public interface, no account): no image within 540 m of the lot; 149 within 1 km, the nearest 544 m away, all from two drives (2017-09-03 and 2022-10-08), and 877 in the Loop; so KartaView cannot show Zones 1 and 2, and is not used further (coverage in `E:\Wieland1529_site_data\phase20\kartaview_coverage.json`). Editor: `L_Site_M4` open, `r.RayTracing.Nanite.Mode` 0, option "Laser-scan model (Phase 17)" shown. |
| J2 | 19:35 | Work list by `tools\phase20_worklist.py`: skyline towers (beyond 1 km, 60 m or taller) ranked by visible cells from D1 and D1S, the first 40; all 23 Zone 1 buildings; the 25 most visible Zone 2 buildings (cells summed over S1 to S6, S9, D1, D1S, D2, D5). | DONE 19:36: `review\phase20\worklist.csv`. Skyline 40 (27 resting on an assumption by building type, 13 on public descriptions or OpenStreetMap; 7 have no name in any source yet), Zone 1 23, Zone 2 25. Every other building keeps its Phase 17 material at confidence 1 or 2 and is listed as such. |
| J3 | 19:36 | Images from Wikimedia Commons (`tools\phase20_commons.py`, public interface, a pause between requests, no contact details sent): for each named skyline tower a text search of files; for every work-list building a search of geotagged files within 150 m (towers) or 400 m of the lot (Zones 1 and 2); licence, author and address read from each file's page data; non-free, "fair use" and Google-derived files refused; thumbnails of 1,280 px into `E:\Wieland1529_site_data\phase20\commons\`, listed in `asset_downloads.csv`. | PENDING |
