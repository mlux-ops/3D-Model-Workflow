# Phase 15 results: the withdrawn hotel removed, the site put back as surveyed

Status: IN PROGRESS since 23:41 on 2026-11-13 (Central).

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
| J1 | 23:41 | Checks before work: free commit memory, the open level, what is unsaved, how the hotel and the three objects it hid stand now, and what those three objects were before Phase 13 | DONE 23:52. Free commit 36.0 GB at 23:41 and 33.2 GB at 23:44 (over the 30 GB line, so the editor was not restarted). Editor process 44588, started 23:37. It had opened the earlier production level; `L_Site_M4` was opened at 23:41 (13 levels, 3,115 objects, nothing unsaved). `r.RayTracing.Nanite.Mode` 0. Found: 56 hotel objects in `L_ProposedHotel`; list "Neighbour development" in `LVS_W1529_Surroundings` with two options of 59 objects each; the three objects of the hide record hidden; 71 assets under `/Game/Wieland1529/Site/ProposedHotel/`. Before Phase 13 all three were shown: the list "Surroundings" is on "Earlier detailed buildings" (55 of the other 55 detailed-house parts it binds are shown, 52 of 52 massing blocks it binds are hidden), and `SB_782868` is one of 92 massing blocks no list binds, of which the other 91 are shown. Phase 13 recorded 12 levels and 3,059 objects before it started; 3,115 - 56 = 3,059. |
| J2 | 23:53 | Remove the list "Neighbour development" from `LVS_W1529_Surroundings` (the asset predates Phase 13, so only that list goes); put the three objects back to shown and test that the list "Surroundings" still shows the two parts of 1525 N. Wieland; save `LVS_W1529_Surroundings`, `L_Surroundings`, `L_Surroundings_R15` by name | DONE 23:57. List "Neighbour development" removed (1 list, its two options and 59 object bindings each); the four older lists remain: Surroundings, Revit site objects, Site ground, Season. Option "Earlier detailed buildings" of the list "Surroundings" (the option already on) switched on again: the two parts of 1525 N. Wieland came back shown, so that list still records them as shown and is intact. `SB_782868` (1520 N. Wells) shown directly with its Visible tick box. Read back: all three shown; the list "Surroundings" binds 57 detailed-house parts, all shown, and 52 massing blocks, all hidden; all 92 unbound massing blocks shown. Saved by name: `LVS_W1529_Surroundings`, `L_Surroundings`, `L_Surroundings_R15`; nothing left unsaved (scripts `j2_restore.py`, `j2_save.py`). |
| J3 | 23:58 | Remove the hotel level from the top level `L_Site_M4`, clear it from memory, and save `L_Site_M4` by name; check 12 levels, 3,059 objects and no hotel object | PENDING |
