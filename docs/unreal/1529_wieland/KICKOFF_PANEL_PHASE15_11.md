# Kickoff prompt: remove the hotel (Phase 15), then finish Phase 11, editor panel

Written by the supervising session on 2026-11-13 for the owner to paste into the Unreal editor's agent panel. Everything below the line is the prompt.

---

Remove the withdrawn hotel, then finish Phase 11 (packaging and delivery) of the 1529 N. Wieland scene plan

What this session is for

You are working in the Unreal Engine 5.9 project `D:\Unreal_Engine_Projects\Wieland1527 5.9\Wieland1527.uproject`, for the plan in `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\PLAN.md`. You have none of the earlier sessions' memory; their records are in the plan folder. The owner is away and wants the work to keep going: decide what you can, and put anything that truly needs the owner in the final report.

There are two jobs, in this order.

Job 1, Phase 15: remove the proposed hotel completely

On 2026-11-13 the owner withdrew the proposed hotel at 1520-1528 N. Wells ("The Duke of Wells") that Phase 13 modelled, and asked for all hotel work to be removed and the site put back exactly as it was before Phase 13: the existing buildings and the empty lot on those parcels, as surveyed. The hotel's documents have already been removed from the plan folder. They are in git history at commit `26b8b768`; read them with `git show 26b8b768:<path>`:

- `docs/unreal/1529_wieland/phase13_results.md`, section "What was saved or changed in the project": every asset, level, override and variant list Phase 13 created or changed.
- `docs/unreal/1529_wieland/review/phase13/hidden_for_proposed_hotel.csv`: the existing objects Phase 13 hid.
- `docs/unreal/1529_wieland/tools/wieland_hotel.py`: the tool that built it.

A headless session began this job at 23:40 and was stopped at 23:41 after only opening `/Game/Wieland1529/L_Site_M4`; nothing was changed.

The owner approved these deletions:

1. Read free commit memory first; if it is under 30 GB, close and reopen the editor (nothing unsaved matters).
2. In `/Game/Wieland1529/L_Site_M4`, remove the streaming level `/Game/Wieland1529/Site/L_ProposedHotel`.
3. Put every object Phase 13 hid back to its state before Phase 13 (visible, as surveyed), and remove the recorded overrides that hid them.
4. Delete the Variant Manager list `Neighbour development`. A Variant Manager list is a set of switchable options. If the list was not created by Phase 13, remove only the options and bindings Phase 13 added.
5. Delete every asset Phase 13 created: the level `L_ProposedHotel`, its meshes (`SM_W1529_PH_*`), and any materials, instances and textures made only for the hotel. Check each asset's references first, and delete only what nothing outside the hotel uses. List anything you keep, with the reason. Never delete or edit an asset that Datasmith created (Datasmith is the Revit importer).
6. Undo any other change Phase 13 made to a saved level.
7. Save the changed levels by name.
8. Check the result:
   - render three views: an aerial from the south-east over Wells Street, the rear of 1529 from its roof deck looking east, and Wieland Street;
   - compare them with the Phase 12 ground truth in `review\phase12\`;
   - confirm that no hotel object remains in the level or in the content folder.
9. Move `E:\Wieland1529_site_data\proposed_hotel\` (52 MB) to the Windows Recycle Bin, not a permanent delete.
10. Write `phase15_results.md` in the plan folder. Its first line is `Status: DONE` with the time. It records:
    - what was removed, with paths;
    - what was restored;
    - the check pictures, which go in `review\phase15\`, and the comparison;
    - anything kept, with the reason.

    Commit it, then go on to job 2.

The four timelapse videos in `review\phase14\` were made with the hotel. The owner decided to keep them as they are. Do not redo or touch them.

Job 2: finish Phase 11 (packaging and delivery)

Read `phase11_results.md`: its status lines from the top down, its "How to resume" section, and its journal from the bottom up. Then continue from the first unfinished line.

- **The final stills show the site without the hotel.** A still rendered with the hotel must be rendered again without it. That means J6, re-rendered after 16:13 on 2026-11-13. Stills made before 16:13 (J1 and J3) are valid if their files are intact. Then finish D3 to D5.
- **Packaging:** H: (the owner's external USB disk) is not connected. Put render frames, the packaged build and the project archive in `D:\Wieland1529_delivery\` instead, as the owner approved, within 60 GB.
- **Google Drive** is the owner's drive F: (Google Drive for desktop). Deliver by copying the finished package into its own folder under `F:\My Drive\Folders\3D Model Workflow\3D Models\`. Check the copy by size and checksum. Google Drive uploads it in the background. Do not use a connector for large files.
- Include no hotel level or variant list in the package.

Keeping records

- Keep each phase's journal as before: write a line marked PENDING and commit it before each step, then replace it with the outcome. A phase is finished only when its first `Status:` line says DONE, with the time.
- Log every error in `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\PROJECT_MEMORY.md`, with cause, fix and status.
- Commit by explicit path on the current branch, `claude/1529-wieland-scene-plan-e84a03`. Do not push or merge.

What is still the owner's

- Covered: the no-cost rows of the plan's approvals table within their caps, the deletions named in job 1, and the D: and F: locations above.
- Not covered; put these in the final report instead:
  - anything with a price
  - any account or key
  - any other deletion
  - any download outside the approved rows
  - any change to Revit, Windows, drivers or the graphics card
  - any push or merge

Rules that apply throughout

- **Nanite ray tracing stays OFF for every render, path-traced included.** Keep the console variable `r.RayTracing.Nanite.Mode` at 0 and never set it to 2. In UE 5.9 it hung the graphics card three times, at the engine check in `NaniteClusterRayTracing.usf` line 539. Path-traced pictures trace each mesh's simplified fallback copy; say so on each sheet.
- **Rendering:**
  - render one picture at a time;
  - let a freshly opened level settle for five minutes before the first path-traced frame;
  - the editor does not respond while a path-traced picture renders, for up to about 11 minutes.
- **Saving:** never save `/Game/Wieland/R15_Landscape/L_R15_Production` and never use "Save All". Save named assets only.
- **Datasmith assets:** never edit one; apply changes as overrides, new assets or recorded swaps.
- **Memory:** the machine has about 79 GB of commit, and other programs hold a large share. Read free commit before each heavy step. If it is under 30 GB, close and reopen the editor, or wait, rather than start. Log the editor's committed memory every few seconds while rendering.
- **Settings:** put back any console or quality setting you change, and read it back to confirm.

Finishing the work

Keep going until both jobs are done. If you notice yourself offering to stop or handing back a list of remaining steps, do the next step instead. Errors, timeouts and failing tools are ordinary obstacles: diagnose them and work through them.

- If the editor crashes, check what survived against the journal, and continue once the editor is back.
- If the same step crashes twice, change one thing at a time. After two further crashes of that step, record the best workaround with evidence and move on.
- If something stalls, say in one line what is stalled, for how long, and the last stage you verified. Then try another route.

Progress and the final report

Give a one-line update as each step finishes. Finish with a report that stands on its own:

- what was removed and restored;
- each Phase 11 acceptance line with its number;
- where the package is on D: and on Google Drive;
- the short list of items that need the owner;
- the full path of every file you wrote.

The owner knows Revit and construction well and Unreal less well. Use plain words and full sentences, say what an Unreal term means the first time you use it, and use the same word for the same thing throughout.
