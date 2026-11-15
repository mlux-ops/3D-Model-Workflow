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
| J1 | 19:32 | Checks before work, read-only: the owner's photograph folder `D:\Wieland1529_owner_photos\`, a Mapillary token file there, KartaView coverage around the site and along the views to downtown, the editor's state. | PENDING |
