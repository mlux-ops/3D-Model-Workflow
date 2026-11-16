Phase 15 (remove the proposed hotel completely) of the 1529 N. Wieland scene plan, unattended

What this session is for

On 2026-11-13 the owner withdrew the proposed hotel at 1520-1528 N. Wells ("The Duke of Wells") that Phase 13 modelled, and asked for all hotel work to be removed and the site put back exactly as it was before Phase 13: the existing buildings and the empty lot on those parcels, as surveyed. You are doing that in the Unreal Engine 5.9 project `D:\Unreal_Engine_Projects\Wieland1527 5.9\Wieland1527.uproject`, through the editor's agent server (unreal-mcp). The plan folder is `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\`. You have no memory of earlier sessions. Nobody will answer questions; decide and keep going. This is a short job.

The supervisor has already removed the hotel's documents from the plan folder. They are still in git history, at commit `26b8b768`; read them with `git show 26b8b768:<path>`:

- `docs/unreal/1529_wieland/phase13_results.md`: its "What was saved or changed in the project" section lists every asset, level, override and variant list Phase 13 created or changed.
- `docs/unreal/1529_wieland/review/phase13/hidden_for_proposed_hotel.csv`: the existing objects Phase 13 hid when the hotel is on.
- `docs/unreal/1529_wieland/tools/wieland_hotel.py`: the tool that built it.

If `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\phase15_results.md` already exists, an earlier session started this job: read it and continue from the first unfinished line.

What to do (the owner approved these deletions on 2026-11-13)

1. Read free commit memory first; if it is under 30 GB, close and reopen the editor (nothing unsaved matters).
2. Open `/Game/Wieland1529/L_Site_M4`. Remove the streaming level `/Game/Wieland1529/Site/L_ProposedHotel` from it.
3. Put every object Phase 13 hid back to exactly its state before Phase 13 (visible, as surveyed), and remove the recorded overrides that hid them.
4. Delete the Variant Manager list `Neighbour development` (or, if it lives inside a list that Phase 13 did not create, remove only the options and bindings Phase 13 added).
5. Delete every asset Phase 13 created: the level `L_ProposedHotel`, its meshes (`SM_W1529_PH_*`), and any materials, material instances and textures made only for the hotel. Before deleting each asset, check its references with the editor's reference viewer or the asset registry; delete only assets nothing outside the hotel uses, and list any you keep with the reason. Never delete or edit a Datasmith asset.
6. Undo any other change Phase 13 made to a saved level, as listed in its results file.
7. Save the changed levels by name. Never save `/Game/Wieland/R15_Landscape/L_R15_Production` and never use "Save All".
8. Check: the hotel's parcels show the existing buildings and the empty lot again. Render three views (an aerial from the south-east over Wells Street, the rear of 1529 from its roof deck looking east, and Wieland Street), and compare them with pictures made before Phase 13 (the Phase 12 ground truth in `review\phase12\` and the Phase 11 stills made before 16:13 on 2026-11-13). Confirm that no object named for the hotel remains in the level or in the content folder.
9. Move the reference downloads folder `E:\Wieland1529_site_data\proposed_hotel\` (52 MB) to the Windows Recycle Bin, not a permanent delete.

Rules

- Nanite ray tracing stays OFF: keep the console variable r.RayTracing.Nanite.Mode at 0; it has hung the graphics card three times. Render one picture at a time.
- Do not touch `phase11_results.md` or `phase14_results.md`; other jobs handle them.

Done means

- `phase15_results.md` in the plan folder: a first line `Status: DONE` with the time, what was removed (assets with their paths, the level, the variant list, the overrides undone), what was restored, the check pictures and their comparison, anything kept with its reason, and the full path of every file you wrote. Check pictures go in `review\phase15\`.
- Any error is logged in `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\PROJECT_MEMORY.md` with cause, fix and status.
- Commit by explicit path on the current branch. Do not push. Then stop: the timelapses are redone next, then Phase 11 resumes.

Write for the owner in plain words: they know Revit and construction well and Unreal less well.
