# Phase 13 results: the proposed hotel at 1520-1528 N. Wells ("The Duke of Wells")

Status: STARTED 2026-11-13 12:31 Central. Unattended run; the owner is away. Nothing is pushed.

Project: `D:\Unreal_Engine_Projects\Wieland1527 5.9\Wieland1527.uproject` (Unreal Engine 5.9).
Plan: `PLAN.md`, Phase 13. This file is the journal of the phase. A line marked PENDING is written and committed before its step starts; it is replaced by the outcome when the step ends.

Everything this phase builds is **proposed, modelled from published renderings and records, not a survey**.

Words used the same way throughout this file:

- "Level" is Unreal's word for one saved scene file. The "top level" `L_Site_M4` loads the others. The "hotel level" is the new level `/Game/Wieland1529/Site/L_ProposedHotel`.
- "Object" is one placed thing in a level (Unreal calls it an actor). "Mesh" is the stored shape an object shows. "Material" is the surface finish on a mesh.
- "Station" is a fixed camera position on the street (S1 to S9, `REFERENCE_VIEWS.md`). "Design view" is a fixed camera position in or on the building (D1 to D5). "View" means either.
- "Variant Manager" is the engine's tool that holds lists of named options; choosing one option changes a set of objects in one action. "List" means one such list; "option" means one choice in it.
- "Earlier detailed buildings" are the copies of the October 2026 neighbourhood model in the level `L_Surroundings_R15` (Phase 7). "Phase 4 survey massing" is the set of blocks built from the 2022 laser scan in `L_Surroundings`. "Revit neighbour massing" is the block of neighbours that came with the Revit export.
- "Console variable" is a named engine setting that can be changed while the editor runs.
- "Path-traced" means made by Unreal's Path Tracer, the slow renderer that follows light physically. "Real-time" means made by the renderer the walk-through uses.
- "Frame time" is the time the computer needs to draw one picture, in milliseconds (ms).
- "Parcel" is one lot of land as the county's map draws it, with its 14-digit number (PIN).

## How to resume

1. Read the journal below from the bottom up. The last line that is not PENDING is the last step known to be finished. A PENDING line means the step was started and its result is unknown: look at what exists (files in `review\phase13\`, `E:\Wieland1529_site_data\proposed_hotel\`, assets under `/Game/Wieland1529/Site/ProposedHotel/`, the level `/Game/Wieland1529/Site/L_ProposedHotel`, and the editor's unsaved packages) before repeating anything.
2. Editor: top level `/Game/Wieland1529/L_Site_M4`. After a restart the editor opens `L_R15_Production` and may show a window "Restore Packages" that blocks every tool until it is closed without restoring (`tools\close_restore_window.ps1`); then open the top level with `review\phase11\scripts\open_m4.py`. Never save `/Game/Wieland/R15_Landscape/L_R15_Production`, never use "Save All", save named assets only, never edit an asset Datasmith created.
3. Calls go through `tools\ue_call.py` (`python -B tools\ue_call.py py <script file> [timeout seconds]`). A script returns the value of its last expression. Scripts of this phase are in `review\phase13\scripts\`; the status reading is `review\phase13\scripts\status.py`.
4. `r.RayTracing.Nanite.Mode` stays 0 at all times, path-traced pictures included, and is never set to 2. One picture at a time; a freshly opened level settles five minutes first.
5. Before any heavy step read free commit memory; under 30 GB, unload and wait (see Phase 11's J3 for the lowered line of 26 GB when the 30 GB line cannot be reached). The memory log of this phase is `review\phase13\memory_log_phase13.csv` (started by `tools\memory_log.ps1`).
6. The journal helper `review\phase13\scripts\journal.py` writes every time from the clock: `python -B review/phase13/scripts/journal.py outcome.txt [next.txt]`, run from the plan folder.
7. Commit by explicit path on branch `claude/1529-wieland-scene-plan-e84a03`. Do not push.

## Checks made before work (2026-11-13 12:30 Central)

| Check | Reading |
|---|---|
| `phase13_results.md` | did not exist: this is a fresh start, not a resume |
| Editor | process 42444, started 11:09:44, agent server answers, holds 19.8 GB of commit |
| Open world | `/Game/Wieland1529/L_Site_M4`, 12 levels, 3,059 objects |
| Unsaved packages | one, `L_Site_M4`, as Phase 11 left it (temporary camera placed and removed; no content change) |
| `r.RayTracing.Nanite.Mode` | 0 |
| `r.Material.UseShaderCompilationParameters` | 0 |
| Free commit memory | 26.3 of 79.1 GB (under the 30 GB line; the same state Phase 11's J3 describes); free physical 6.6 GB |
| Working copy | branch `claude/1529-wieland-scene-plan-e84a03`, last commit `cb4bf6af` (Phase 13 inserted) |
| Advisor tool | none in this session; the closing check is done by hand and noted for the owner |

## Journal

| No. | Time (Central) | Step | Outcome |
|---|---|---|---|
| J1 | 12:33 | Step 13.1, read-only and off line: the parcels of 1520 to 1528 N. Wells and of any other lot the hotel uses, from the county parcel file `E:\Wieland1529_site_data\county_parcels_2025.json` (Phase 2), with their outlines in the project's coordinates; whether the project's rear lot line faces a public alley and Wells Street lies behind it; and which objects of the present site model stand on those parcels (earlier detailed buildings, Phase 4 survey massing, Revit neighbour massing, trees, ground). In parallel, step 13.2: reading the article, the developer's and architect's pages, the city's permit records and planning documents, and saving reference pictures under `E:\Wieland1529_site_data\proposed_hotel\`. Nothing is changed in the Unreal project. | PENDING |
