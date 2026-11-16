# Phase 15 results: the withdrawn hotel removed, the site put back as surveyed

Status: DONE at 23:59 on 2026-11-13 (Central). The withdrawn hotel is gone from the project: its level, its 71 assets, its Variant Manager list and its hiding of three existing objects. The existing buildings and the empty lot on its land show again, as surveyed, and three check views plus one more agree with the pictures made before Phase 13. Nothing is pushed. Phase 11 resumes next.

Project: `D:\Unreal_Engine_Projects\Wieland1527 5.9\Wieland1527.uproject` (Unreal Engine 5.9).
On 2026-11-13 the owner withdrew the proposed hotel at 1520-1528 N. Wells ("The Duke of Wells") that Phase 13 built, and asked for all of it to be removed and the site put back as it was before Phase 13. Phase 13's own record (`phase13_results.md`, `review/phase13/hidden_for_proposed_hotel.csv`, `tools/wieland_hotel.py`) is read from git commit `26b8b768`.

Words used the same way throughout this file:

- "Level" is Unreal's word for one saved scene file. The "top level" `L_Site_M4` loads the others; the "hotel level" was `/Game/Wieland1529/Site/L_ProposedHotel`.
- "Object" is one placed thing in a level (Unreal calls it an actor). "Asset" is one stored file in the project's content folder: a mesh (a shape), a material instance (a surface finish), a texture (a picture used by a finish), or a level.
- "Variant Manager" is the engine's tool that holds lists of named options; choosing one option shows or hides a set of objects in one action. "List" means one such list; "option" means one choice in it.
- "Shown" / "hidden" refers to the tick box Visible on an object's mesh.

## Journal

A line marked PENDING is written and committed before its step starts; it is replaced by the outcome when the step ends.

| No. | Time (Central) | Step | Outcome |
|---|---|---|---|
| J1 | 23:41 | Checks before work: free commit memory, the open level, what is unsaved, how the hotel and the three objects it hid stand now, and what those three objects were before Phase 13 | DONE 23:47. Free commit 36.0 GB at 23:41 and 33.2 GB at 23:44 (over the 30 GB line, so the editor was not restarted). Editor process 44588, started 23:37. It had opened the earlier production level; `L_Site_M4` was opened at 23:41 (13 levels, 3,115 objects, nothing unsaved). `r.RayTracing.Nanite.Mode` 0. Found: 56 hotel objects in `L_ProposedHotel`; list "Neighbour development" in `LVS_W1529_Surroundings` with two options of 59 objects each; the three objects of the hide record hidden; 71 assets under `/Game/Wieland1529/Site/ProposedHotel/`. Before Phase 13 all three were shown: the list "Surroundings" is on "Earlier detailed buildings" (55 of the other 55 detailed-house parts it binds are shown, 52 of 52 massing blocks it binds are hidden), and `SB_782868` is one of 92 massing blocks no list binds, of which the other 91 are shown. Phase 13 recorded 12 levels and 3,059 objects before it started; 3,115 - 56 = 3,059. |
| J2 | 23:47 | Remove the list "Neighbour development" from `LVS_W1529_Surroundings` (the asset predates Phase 13, so only that list goes); put the three objects back to shown and test that the list "Surroundings" still shows the two parts of 1525 N. Wieland; save `LVS_W1529_Surroundings`, `L_Surroundings`, `L_Surroundings_R15` by name | DONE 23:48. List "Neighbour development" removed (1 list, its two options and 59 object bindings each); the four older lists remain: Surroundings, Revit site objects, Site ground, Season. Option "Earlier detailed buildings" of the list "Surroundings" (the option already on) switched on again: the two parts of 1525 N. Wieland came back shown, so that list still records them as shown and is intact. `SB_782868` (1520 N. Wells) shown directly with its Visible tick box. Read back: all three shown; the list "Surroundings" binds 57 detailed-house parts, all shown, and 52 massing blocks, all hidden; all 92 unbound massing blocks shown. Saved by name: `LVS_W1529_Surroundings`, `L_Surroundings`, `L_Surroundings_R15`; nothing left unsaved (scripts `j2_restore.py`, `j2_save.py`). |
| J3 | 23:48 | Remove the hotel level from the top level `L_Site_M4`, clear it from memory, and save `L_Site_M4` by name; check 12 levels, 3,059 objects and no hotel object | DONE 23:48. All 56 hotel objects were in the hotel level, none in the top level. The hotel level was removed from the top level's list of loaded levels and cleared from memory. Read back: 12 levels and 3,059 objects, the same as Phase 13 recorded before it began; no hotel object; only `L_Site_M4` unsaved, then saved by name; nothing left unsaved (scripts `j3_remove_level.py`, `j3_save.py`). |
| J4 | 23:48 | List every asset whose name or folder belongs to the hotel anywhere in the content folder; read each one's users (referencers) from the asset registry, now that the levels are saved; delete only those used by nothing outside the hotel; never a Datasmith asset | DONE 23:52. 86 assets matched a hotel name anywhere under `/Game` (`review/phase15/references_before_delete.json`). 72 are the hotel's: the level and 71 assets in `/Game/Wieland1529/Site/ProposedHotel/` (56 meshes, 7 material instances, 8 textures); none has a user outside the hotel, none carries Datasmith data. The other 14 are the furniture placeholders `SM_W1529_PH_<size>` in `/Game/Wieland1529/Interiors/Generated/Placeholders/` ("PH" = placeholder, Phase 6), used by the four interior levels: not the hotel's, kept. All 72 deleted through the editor and the emptied folder removed (`review/phase15/deleted_assets.json`, script `j4_delete.py`). The editor reported the level deleted but left the file `L_ProposedHotel.umap` on disk (error logged in `PROJECT_MEMORY.md`); with the level out of memory and unused, that one file was moved to the Windows Recycle Bin. Read back: the asset registry lists 8,416 assets and none with "ProposedHotel" or the hotel's "_PH_" names; no such file is left in `Content\`; a byte search of every `.umap` and `.uasset` finds no "ProposedHotel", "W1529.ProposedHotel", "Neighbour development" or "Duke of Wells"; the 14 placeholders are still there. |
| J5 | 23:52 | Move the reference downloads folder `E:\Wieland1529_site_data\proposed_hotel\` to the Windows Recycle Bin (not a permanent delete) | DONE 23:52. 78 files, 52.2 MB, moved to the Recycle Bin of drive E: as one folder (`E:\$RECYCLE.BIN\S-1-5-21-...-1001\$RVQ9TRP`, shown there as `proposed_hotel`); the folder no longer exists at its old place. It can be put back from the Recycle Bin. |
| J6 | 23:54 | Check pictures: three real-time views (an aerial from the south-east over Wells Street, the rear of 1529 from its roof deck looking east, Wieland Street) into `review/phase15/`, compared with the Phase 12 ground truth in `review/phase12/` | DONE 23:58. Four real-time pictures at 3840 x 2160, one at a time, with the same 24 mm camera and fixed exposure as Phases 8, 10 and 12 (script `j6_view.py`, record `views/runs.jsonl`): S2 (Wieland Street from the south-west, Phase 8's station camera) 12.4 s, D1 (roof deck, Phase 8's design-view camera) 7.7 s, AIR (aerial from the south-east over Wells Street) 6.2 s, RDE (1529's roof deck looking east over the rear) 6.1 s. `r.RayTracing.Nanite.Mode` read 0 before, during and after each. The level had been open 13 minutes before the first. Comparison under Findings. Free commit read 30.1 to 33.2 GB before each render. During each render it dipped to 25.0 to 25.5 GB for a few seconds, below the 30 GB line, with the editor at up to 25.0 GB (`memory_log_phase15.csv`, 50 lines, 23:54 to 23:58). |

## Findings

### What was removed

| What | Where | How |
|---|---|---|
| The hotel level (56 objects: tower, garage, three homes) | `/Game/Wieland1529/Site/L_ProposedHotel` | Taken out of the top level `L_Site_M4`'s list of loaded levels (J3), then the asset deleted (J4). The editor left the file on disk, so `L_ProposedHotel.umap` went to the Recycle Bin of drive D: |
| 56 meshes `SM_W1529_PH_Base_*`, `_Garage_*`, `_Homes_*`, `_Tower_*`, `_Top_*` and the rest | `/Game/Wieland1529/Site/ProposedHotel/Meshes/` | Deleted (J4) |
| 7 material instances `MI_W1529_PH_RedBrick`, `_DarkBrick`, `_GreenRoof`, `_MetalPanel`, `_Interior`, `_Blind`, `_Glass` | `/Game/Wieland1529/Site/ProposedHotel/Materials/` | Deleted (J4) |
| 8 textures `T_W1529_PH_RedBrick_C`, `_DarkBrick_C`, `_Brick_N`, `_Brick_R`, `_GreenRoof_C`, `_GreenRoof_N`, `_MetalPanel_C`, `_MetalPanel_N` | `/Game/Wieland1529/Site/ProposedHotel/Textures/` | Deleted (J4) |
| The folder itself | `/Game/Wieland1529/Site/ProposedHotel/` | Removed once empty (J4) |
| The list "Neighbour development" with its options "Duke of Wells (proposed)" and "Existing buildings (as surveyed)", 59 objects each | inside `/Game/Wieland1529/Surroundings/LVS_W1529_Surroundings` | Only that list removed. The asset is older than Phase 13 and keeps its four older lists (J2) |
| The three recorded overrides: Visible = off on `SB_782868` (1520 N. Wells, `L_Surroundings`), `R15_PART_opaque_xm04_yp01_part01` and `R15_PART_glass_xm04_yp01_part01` (1525 N. Wieland, `L_Surroundings_R15`) | the two surroundings levels | Each object's Visible tick box set back on and the levels saved, so they open shown (J2) |
| Reference downloads: 78 files, 52.2 MB | `E:\Wieland1529_site_data\proposed_hotel\` | Moved to the Recycle Bin of drive E: (J5) |

Every asset was checked first. The asset registry is the editor's index of which asset uses which, and it showed that none of the 72 is used by anything outside the hotel (`review/phase15/references_before_delete.json`). None was made by Datasmith (the Revit importer). No Datasmith asset was edited or deleted, `L_R15_Production` was not saved, and "Save All" was not used.

### What was restored

- **1525 N. Wieland** (the frame house next to 1529, two parts) and **1520 N. Wells** (the 3-storey building's block from the 2022 laser scan) are shown again, exactly as before Phase 13.
- **How the earlier state was established.** The list "Surroundings" is on its option "Earlier detailed buildings": all 55 other detailed-house parts in that list are shown and all 52 survey blocks it swaps are hidden. Switching that option on again turned the two 1525 parts on, so the list itself still records them as shown. `SB_782868` is in no list, and the other 91 blocks in no list are all shown.
- **The top level** is back to 12 levels and 3,059 objects, the count Phase 13 recorded before it began.
- **Phase 13 made no other change to a saved level.** Its record lists only the hotel level, the top level, the variant asset and the two surroundings levels, and all five are dealt with above. The shown/hidden state of the Revit neighbour massing was not changed by Phase 13 and was not touched here.
- **Saved by name, and nothing else:** `LVS_W1529_Surroundings`, `L_Surroundings`, `L_Surroundings_R15` (23:47) and `L_Site_M4` (23:48). After each save the editor had nothing left unsaved.

### Check pictures and comparison

| View | Compared with | Result |
|---|---|---|
| S2, Wieland Street from the south-west (looks straight at 1525 N. Wieland) | Phase 12 real-time S2 and Phase 12 ground truth (path-traced) S2, both from before Phase 13, same camera | 1525 N. Wieland stands again where it stood. Against Phase 12's real-time picture, 6.5 % of pixels differ by more than 40 of 255, all in the moving tree leaves and their shadows; the houses, steps, fence and paving are the same (`sheet_S2_vs_phase12_realtime.jpg`). Against the ground truth: 10.6 % (Phase 12's own real-time picture: 9.7 %), mean brightness -1.4 % (Phase 12: -0.9 %). |
| D1, penthouse roof deck looking south-east | Phase 12 real-time D1 and ground truth D1, same camera | 0.77 % of pixels differ from Phase 12's real-time picture (tree leaves, thin edges). No tall building on the right, where the hotel took 6.7 % of this view in Phase 13. Against the ground truth: 1.07 % (Phase 12: 1.19 %) (`sheet_D1_vs_phase12_realtime.jpg`). |
| AIR, aerial from the south-east over Wells Street | Phase 13's aerial with the hotel (history `26b8b768`, `review/phase13/model_views/m2_air_from_southeast.png`; a different camera). Phase 12 has no aerial | The hotel land shows the empty lot as surveyed, with the survey block of 1520 N. Wells on Wells Street and the house 1525 N. Wieland beside 1529, both marked where their outlines fall on the picture (`sheet_AIR_hotel_removed.jpg`). |
| RDE, 1529's roof deck looking east over the rear | Phase 13's roof-deck sheet looking south from the same point, with and without the hotel (history `26b8b768`, `review/phase13/views/sheet_RD.jpg`). Phase 12 has no such view | The backs of the Wells Street buildings and the distant city, with no tower to the south-east (`sheet_RDE_hotel_removed.jpg`). |

All four are real-time pictures, not path-traced, which the sheets say. The 4K pictures stay on disk in `review\phase15\views\` (13 MB each) and are not committed, as in Phase 12; the sheets show them.

**No hotel object or asset remains.**
- No object in the open world carries the hotel's tag, its level or its names.
- The asset registry (8,416 assets) lists nothing with "ProposedHotel" or the hotel's mesh names.
- No such file is on disk under `Content\`.
- A byte search of every `.umap` and `.uasset` in `Content\` finds none of "ProposedHotel", "W1529.ProposedHotel", "Neighbour development" or "Duke of Wells".

### Kept, with the reason

- **14 meshes `SM_W1529_PH_<size>`** in `/Game/Wieland1529/Interiors/Generated/Placeholders/` (for example `SM_W1529_PH_101x119x117`). Here "PH" means *placeholder*: these are the furniture stand-ins of the interiors, used by the four interior levels. They match the kickoff's pattern `SM_W1529_PH_*` but are not the hotel's. Kept untouched.
- **The project's own finishes the hotel borrowed:** `MI_W1529_R_Indiana_Limestone_-_Full_Color_Blend_Seamless`, `MI_W1529_C_Concrete__Precast`, `MI_W1529_R_Aluminum_-_Matte_Black_Powdercoat`, the textures `T_W1529_P12_Flat_2D2E30_C` and `T_W1529_P12_Flat_E8E5DE_C`, and the parents `M_W1529_Opaque` and `M_W1529_Glass`. They existed before Phase 13 and other parts of the project use them. Kept.
- **`tools/phase13_hotel_meshes.py`** in the plan folder. This is the hotel's off-line mesh generator: a script in the repository, not an Unreal asset. Deleting it is not among the approved deletions, so it stays for the owner to decide.
- **The four Phase 14 timelapse videos**, made with the hotel. Kept as the owner decided; not touched.
- **The Phase 13 entries in `PROJECT_MEMORY.md`.** Kept as history, as the supervisor decided.

## For the owner

1. Please say whether `tools/phase13_hotel_meshes.py` (the hotel's mesh generator, still in the plan folder) should be deleted too. Deleting it was not covered by the approval.
2. The level file `L_ProposedHotel.umap` and the folder `proposed_hotel` are in the Recycle Bins of drives D: and E:. They are gone for good only when the Recycle Bin is emptied.
3. The model still shows 1520 N. Wells as the 2022 survey recorded it. Phase 13 found a wrecking permit for it dated 1 May 2026. If it has been demolished, the model is out of date there; changing that is a new decision for the owner.

## Files written by this phase

Plan folder `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\`:

- `phase15_results.md` (this file)
- `review\phase15\scripts\status.py`, `visibility_by_group.py`, `j2_restore.py`, `save_named.py`, `j2_save.py`, `j3_remove_level.py`, `j3_save.py`, `j4_references.py`, `j4_delete.py`, `j6_view.py`, `compare.py`, `sheets.py`, `close_results.py`, `close_results_body.md`
- `review\phase15\references_before_delete.json`, `deleted_assets.json`, `memory_log_phase15.csv`
- `review\phase15\sheet_S2_vs_phase12_realtime.jpg`, `sheet_D1_vs_phase12_realtime.jpg`, `sheet_AIR_hotel_removed.jpg`, `sheet_RDE_hotel_removed.jpg`
- `review\phase15\views\S2_realtime.0000.png`, `D1_realtime.0000.png`, `AIR_realtime.0000.png`, `RDE_realtime.0000.png` (on disk, not committed), `views\job.json`, `views\runs.jsonl`

Elsewhere:

- `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\PROJECT_MEMORY.md`: new section "Phase 15", three entries.
- Unreal project `D:\Unreal_Engine_Projects\Wieland1527 5.9\Content\`: saved `Wieland1529\L_Site_M4.umap`, `Wieland1529\Surroundings\L_Surroundings.umap`, `Wieland1529\Surroundings\L_Surroundings_R15.umap` and `Wieland1529\Surroundings\LVS_W1529_Surroundings.uasset`. Deleted the 72 hotel assets listed above.
