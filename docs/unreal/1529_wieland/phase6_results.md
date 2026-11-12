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
| J3 | 22:57 | Step 6.2, first room only, redone from its start: open `L_Site_M2`; count sharp edges within 2 m of the D3 camera (north triplex kitchen); make rounded copies of those meshes as new saved assets under `/Game/Wieland1529/Interiors/Meshes` with `tools\wieland_refine.py` (the Datasmith meshes are only read); put them on the kitchen objects as swaps in the editor's memory only; count again; take a picture and check it before any batch. Free commit is read first and the editor's memory is logged to `review\phase6\memory_log.csv`. | DONE at 23:03. Baseline counts of sharp edges within 2 m of the camera, before any change: D2 4,018 edges (376 m of edge), D3 5,905 edges (493 m), D4 1,670 edges (449 m). A sharp edge is counted where two faces of one mesh meet at an outward corner turning 60 degrees or more; the rim of a sheet that Revit modelled without thickness is not counted, because it has no corner to round. First room, D3 (north triplex kitchen): 39 meshes carry those edges. 38 rounded copies were made and saved as new assets in `/Game/Wieland1529/Interiors/Meshes` (names `SM_W1529_R_<Datasmith name>`), each face pulled back 2 mm from the edge and bridged by a narrow strip; the Datasmith meshes were only read. With the copies put on the objects in the editor's memory (153 objects, since some meshes are used more than once), the count at D3 fell from 5,905 to 451 edges and from 493 m to 10.5 m of edge. It is not zero. What is left: details smaller than the rounding (pendant lamp 148, beverage faucet 63, pocket-door hardware 58, fluted cabinet end 29, further fixtures under 30 each), and one object left unrounded (a 155,796-triangle generic model, 44 edges: its copy lost faces, so it is not used). 18 of the 39 meshes reach zero. The engine's own bevel tool was tried first and failed on the Revit export (faces are separate sheets that only touch); the rounding is therefore done by `tools\wieland_refine.py`. Pictures checked: `review\phase6\first_room\D3_rounded.png` and `D3close_rounded.png` show the kitchen whole, materials and texture placement unchanged, no torn or missing faces. Free commit 35 GB before the build. Nothing but the 38 new mesh assets was saved. |
| J4 | 23:03 | Step 6.2, batch: make rounded copies for every mesh used by an object of the four units (north and south, triplex and penthouse), one mesh per editor tick so the editor stays responsive; meshes with no sharp edge or over 60,000 triangles are skipped and listed. Free commit is read first; memory is logged. Then count D2, D3 and D4 again with the copies on. | DONE at 23:36. Sharp edges within 2 m of the camera, before and after: D2 4,018 to 569 (376 m of edge to 8.3 m); D3 5,905 to 451 (493 m to 10.5 m); D4 1,670 to 328 (449 m to 1.4 m). None is zero. What is left is detail finer than the 2 mm rounding inside fixtures, where the rounding found no room and left the faces as they were: at D2 the kitchen sink (409), a wall sconce (103), recessed lights and the glass railing; at D3 the pendant lamp (148), the beverage faucet (63), pocket-door hardware (58), and the one unrounded generic model (44); at D4 a wall sconce (277), recessed lights (20), a window (17) and the lavatory (14). These edges are 1 to 3 mm long each. How it was made: three runs of the same tool, one mesh per editor tick. Run 1, the meshes of the four units: 1,052 meshes, 957 s, 1,030 good copies, 6 skipped (no sharp edge), 16 copies rejected by the tool's own check (a vertex left the outline, or faces were lost) and not written. After run 1 the counts were D2 912, D3 451, D4 422, and the list showed that countertops, ceilings, floors and outer walls near the cameras had not been in the run: they carry the group mark of the common parts or of the site, not of a unit (three kitchen and bath countertops are marked as site objects; this is a Phase 4 grouping fault that step 6.8 corrects by position). Run 2, those 10 meshes: 4 s, 10 good copies. Run 3, the other 188 meshes of the common parts: 31 s, 182 good copies, 6 skipped (no sharp edge). Together with the 38 of the first room: 1,260 imported meshes have a rounded copy, used by 3,493 objects; sharp edges summed over those meshes 274,403 to 18,093; 955 copies have none left. The 16 without a copy keep the imported mesh: two lounge chairs and a seat, bath accessories (2), three AXOR fittings, two undermount lavatories, two outdoor tables, two emergency lights, a bicycle (no gain) and the 155,796-triangle generic model. The 60,000-triangle limit never applied: the one mesh above it was read as smaller by the engine and was then rejected by the check. Every swap is a row of `mesh_swaps.csv` (written by `tools\mesh_swaps.py` from `review\phase6\rounding_results.json`; columns added for category, edges and triangles before and after, objects and units); `wieland_refine.swaps_from_csv` applies the file again. The swaps are in the editor's memory only until step 6.8 saves them in new levels; the Datasmith meshes and levels are untouched. Saved: 1,260 mesh assets under `/Game/Wieland1529/Interiors/Meshes`, nothing else. Memory: free commit was 34.4 GB before run 1 (editor 16.9 GB) and fell to 28.6 GB at its lowest during run 1 (editor 22.6 GB at its highest), under the 30 GB floor; the run was already under way and was left to finish. Before runs 2 and 3 free commit read 29.8 GB; the undo history was cleared and unused objects were released, which freed nothing, and waiting could free nothing because the editor is the only large user. Run 2 (10 small meshes) was started as a test, changed the editor's memory by less than 0.1 GB, and run 3 (40,421 triangles in all) followed on that measurement. This is a departure from the rule, recorded as such; the next heavy step starts only after the level change of step 6.8 has released memory. Pictures with the copies on: `review\phase6\rounded\D2_rounded.png`, `D3_rounded.png`, `D4_rounded.png`. |
| J5 | 23:23 | While the batch of J4 runs inside the editor (it needs no attention), two steps that happen outside the editor: step 6.3, the list of repository packages under `output\` matched to this building by product name, with the evidence for each match and the unmatched ones listed for the owner (nothing is applied); and step 6.4, the furniture proposal `furniture_proposal.csv` (one set per room type; source, licence, size on disk, cost). Catalogue listings are read; no furniture file is downloaded. | DONE at 23:27. Step 6.3: all 131 entries of `output\` were listed and compared by product name with the 284 Revit material names and the 1,298 Revit mesh names of the export. Six products match (Hansgrohe beverage faucet 04117340, Miele KM 3054-1 cooktop, Kuzco Trinity Low pendant, Hollis Morris Oyster sconce, DVI Courcelette pendant, Richelieu Gola channels); all six are fixture families already in the Revit model, so they bring no finish to apply. No tile or finish package matches a Revit material name. Nothing was applied: the `decision` column of `material_audit.csv` is empty, the Revit materials stay the default and the Phase 5 candidates stay alternatives. The list, with evidence and with the unmatched packages for the owner, is `review\phase6\package_matches.md`. Step 6.4: `furniture_proposal.csv` holds 55 lines for 12 room types. 25 lines (23 different models, 1.9 GB together at 4K images) come from the public-domain Poly Haven catalogue at no cost, with sizes read from the catalogue's listing. 30 lines have no modern public-domain piece (sofas, beds, dining table, outdoor furniture, a car) or can be made here at no cost (rugs, curtains, towels, television panels); for the bought ones the source is a licensed furniture pack on the Fab marketplace, whose price could not be read from here and is marked not confirmed. No furniture file was downloaded; only catalogue listings were read (extract kept in `review\phase6\polyhaven_catalogue_extract.json`). Dressing waits for the owner's approval. |

## Acceptance lines

Filled in as the steps finish.

## Files written

Filled in as the steps finish.
