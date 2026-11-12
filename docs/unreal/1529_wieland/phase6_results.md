# Phase 6 results: interiors

Status: IN PROGRESS. Started 2026-11-11 22:09; paused by the owner at 22:48 during J2; resumed at 22:56 in the same session (id `85926560-462e-4bf5-9139-9a4483cae6e0`) when the owner sent the Phase 6 task again. The editor had been restarted at 22:53, so nothing unsaved in it survived; nothing had been saved.

This file is the journal of the phase. A line
marked PENDING is written and committed before its step starts; the line is replaced by the
outcome when the step ends.

Words used the same way throughout this file:

- "Level" is Unreal's word for one saved scene file. The building, the surroundings and each
  interior group are separate levels that are loaded together.
- "Datasmith" is the Revit-to-Unreal importer. Everything it created is replaced at the next
  reimport, so nothing it created is ever edited here; changes are overrides, new assets or
  recorded swaps.
- "Stand-in" is a labelled grey block of the proposed size, in the place where an item that
  still waits for the owner's approval will go.

## How to resume

1. Read the journal table below from the bottom up. The last line that is not PENDING is the
   last step known to be finished. A PENDING line means the step was started and its result
   is unknown: inspect what exists (assets under `/Game/Wieland1529/Interiors/`, files in
   `review\phase6\`, rows in the CSV files) before repeating anything.
2. Editor: project `D:\Unreal_Engine_Projects\Wieland1527 5.9\Wieland1527.uproject`, level
   `/Game/Wieland1529/L_Site_M2` (loads `L_Surroundings` and `L_Building`). Never save
   `/Game/Wieland/R15_Landscape/L_R15_Production`, never use "Save All", save named assets
   only.
3. In the editor's Python, add the tools folder to `sys.path`:
   `E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools`
   and set `sys.dont_write_bytecode = True`.
4. Before any heavy step read free commit memory; under 30 GB, unload and wait.
5. Commit by explicit path on branch `claude/1529-wieland-scene-plan-e84a03`. Do not push.

## Checks made before any work (2026-11-11, 22:09 to 22:12)

| Check | Result |
|---|---|
| Editor process | 4680, started 19:52, answers the agent server, holds 18 GB of commit |
| Free commit memory | 34.2 GB of 79.1 GB (above the 30 GB floor); free physical 9.8 GB |
| Open level | `/Game/Wieland1529/L_Site_M2` with `L_Surroundings` and `L_Building`; 2,770 objects |
| `r.Material.UseShaderCompilationParameters` | 0, as required |
| Unsaved packages | only `/Game/Wieland1529/Scratch/M_Probe5`, left from before; not touched |
| Phase 5 alternatives | off (0 slots switched); Revit materials are the active default |
| Plan working copy | branch `claude/1529-wieland-scene-plan-e84a03`, head `5e4e5306`, clean |
| Advisor tool | not present in this session; the three advisor checkpoints of the owner's global rules cannot be made and are replaced by my own written checks, as in Phases 4 and 5 |

## Journal

| No. | Time | What is done | Outcome |
|---|---|---|---|
| J1 | 22:13 to 22:23 | Step 6.1: count what the Revit export holds per unit and room, set provisional D1 to D5 cameras, take grey renders, list room by room what the geometry lacks at camera distance | DONE. 29 grey pictures (D1 to D5 and 24 north rooms) under a temporary 150-candela work lamp, because rooms have no lighting yet. Gap list with 9 gaps in my own working order in `review\phase6\gap_list.md`; the owner has not prioritized. Provisional D1 to D5 positions entered in `REFERENCE_VIEWS.md` (north half). Found: the export is already partly furnished; 0 baseboards; 5 switches in the whole model; D4 bath walls are gypsum board, not tile. Nothing saved in the Unreal project. |
| J2 | 22:23 | Step 6.2, first room only: north triplex kitchen (D3). Count sharp edges within 2 m of the D3 camera, make rounded copies of those meshes as new assets under `/Game/Wieland1529/Interiors/`, generate baseboard and switch plate, record swaps in `mesh_swaps.csv`, count again, check the picture before any batch | STOPPED BY THE OWNER at 22:48, mid-step. The supervising session killed the headless agent on the owner's instruction. Unfinished: no asset was saved under `Content\Wieland1529\Interiors\` (folder absent on disk at 22:49); any meshes the agent made in the editor's memory are unsaved and may be discarded; `mesh_swaps.csv` unchanged in git. The agent's work-in-progress script `tools\wieland_refine.py` (31,782 bytes, untested as a whole) is committed as found. Redo J2 from its start. |
| J3 | 22:57 | Step 6.2, first room only, redone from its start: open `L_Site_M2`; count sharp edges within 2 m of the D3 camera (north triplex kitchen); make rounded copies of those meshes as new saved assets under `/Game/Wieland1529/Interiors/Meshes` with `tools\wieland_refine.py` (the Datasmith meshes are only read); put them on the kitchen objects as swaps in the editor's memory only; count again; take a picture and check it before any batch. Free commit is read first and the editor's memory is logged to `review\phase6\memory_log.csv`. | DONE at 23:03. Baseline counts of sharp edges within 2 m of the camera, before any change: D2 4,018 edges (376 m of edge), D3 5,905 edges (493 m), D4 1,670 edges (449 m). A sharp edge is counted where two faces of one mesh meet at an outward corner turning 60 degrees or more; the rim of a sheet that Revit modelled without thickness is not counted, because it has no corner to round. First room, D3 (north triplex kitchen): 39 meshes carry those edges. 38 rounded copies were made and saved as new assets in `/Game/Wieland1529/Interiors/Meshes` (names `SM_W1529_R_<Datasmith name>`), each face pulled back 2 mm from the edge and bridged by a narrow strip; the Datasmith meshes were only read. With the copies put on the objects in the editor's memory (153 objects, since some meshes are used more than once), the count at D3 fell from 5,905 to 451 edges and from 493 m to 10.5 m of edge. It is not zero. What is left: details smaller than the rounding (pendant lamp 148, beverage faucet 63, pocket-door hardware 58, fluted cabinet end 29, further fixtures under 30 each), and one object left unrounded (a 155,796-triangle generic model, 44 edges: its copy lost faces, so it is not used). 18 of the 39 meshes reach zero. The engine's own bevel tool was tried first and failed on the Revit export (faces are separate sheets that only touch); the rounding is therefore done by `tools\wieland_refine.py`. Pictures checked: `review\phase6irst_room\D3_rounded.png` and `D3close_rounded.png` show the kitchen whole, materials and texture placement unchanged, no torn or missing faces. Free commit 35 GB before the build. Nothing but the 38 new mesh assets was saved. |
| J4 | 23:03 | Step 6.2, batch: make rounded copies for every mesh used by an object of the four units (north and south, triplex and penthouse), one mesh per editor tick so the editor stays responsive; meshes with no sharp edge or over 60,000 triangles are skipped and listed. Free commit is read first; memory is logged. Then count D2, D3 and D4 again with the copies on. | PENDING |

## Acceptance lines

Filled in as the steps finish.

## Files written

Filled in as the steps finish.
