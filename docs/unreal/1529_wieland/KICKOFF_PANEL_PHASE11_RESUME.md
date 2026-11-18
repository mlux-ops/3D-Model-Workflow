# Kickoff prompt: resume Phase 11 (packaging and delivery) at J7, editor panel

Written by the supervising session on 2026-11-14 for the owner to paste into the Unreal editor's agent panel. Everything below the line is the prompt.

---

Finish Phase 11 (packaging and delivery) of the 1529 N. Wieland scene plan

What this session is for

You are finishing the last phase of the plan in `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\PLAN.md`, in the Unreal Engine 5.9 project `D:\Unreal_Engine_Projects\Wieland1527 5.9\Wieland1527.uproject`. You have none of the earlier sessions' memory; their records are in the plan folder. The owner is away and wants the work to keep going. Decide what you can, and put anything that truly needs the owner in the final report.

Where things stand

- **Phase 15 is done** (2026-11-13 23:59). The withdrawn hotel at 1520-1528 N. Wells is gone from the project, and the existing buildings and empty lot show again, as surveyed. Nothing of the hotel belongs in the delivery.
- **Phase 11 resumed at 00:05 on 2026-11-14.**
  - J6 is closed: the twelve stills made before the hotel are valid and back in `delivery\stills\`.
  - J7 (the animation) is the next step. The earlier session stopped at about 00:07, before J7 produced anything that is recorded.
- **The editor** was restarted at 00:09 and has been idle since.
- **Read `phase11_results.md`:** its status lines from the top down, its "How to resume" section, and its journal from the bottom up. Check what J7 left on disk before repeating anything, then continue from the first unfinished line: the animation, encoding, packaging, profiling, delivery notes, zip, the Google Drive copy, and the archive.

Where files go

- **Delivery files:** render frames, the packaged build, the zip and the project archive go in `D:\Wieland1529_delivery\`, at most 60 GB, as the owner approved. Drive H: (the owner's external USB disk) is connected again. Keep to D: for this phase, so everything is in one place, and say in the report that H: is available for a later archive copy.
- **Google Drive:** this is the owner's drive F: (Google Drive for desktop).
  - Copy the finished package into its own folder under `F:\My Drive\Folders\3D Model Workflow\3D Models\`.
  - Check the copy by size and checksum. Google Drive uploads it in the background.
  - Do not use a connector for large files.
  - Check first that no identical package is already there.

Keeping records

- **The journal:** keep it as before. Write a line marked PENDING and commit it before each step, then replace it with the outcome. The phase is finished only when the first `Status:` line says DONE, with the time.
- **Errors:** log every error in `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\PROJECT_MEMORY.md`, with cause, fix and status.
- **Commits:** commit by explicit path on the current branch, `claude/1529-wieland-scene-plan-e84a03`. Do not push or merge.

What is still the owner's

- **Covered:** the no-cost rows of the plan's approvals table, within their caps, and the D: and F: locations above.
- **Not covered; put these in the final report instead:**
  - anything with a price
  - any account or key
  - any deletion
  - any download outside the approved rows
  - any change to Revit, Windows, drivers or the graphics card
  - any push or merge
- **Owner decisions still open stay open:** keep the switchable options and labelled stand-ins as they are, and list them in the report.

Rules that apply throughout

- **Nanite ray tracing stays OFF for every render, path-traced included.** Keep the console variable `r.RayTracing.Nanite.Mode` at 0 and never set it to 2. In UE 5.9 it hung the graphics card three times, at the engine check in `NaniteClusterRayTracing.usf` line 539. Path-traced pictures trace each mesh's simplified fallback copy; say so on each sheet.
- **Rendering:**
  - render one picture or sequence at a time;
  - let a freshly opened level settle for five minutes before the first path-traced frame;
  - the editor does not respond while a path-traced picture renders, for up to about 11 minutes.
- **Saving:** never save `/Game/Wieland/R15_Landscape/L_R15_Production` and never use "Save All". Save named assets only.
- **Datasmith assets:** never edit one; apply changes as overrides, new assets or recorded swaps. Datasmith is the Revit importer, and it replaces those assets at the next reimport.
- **Memory:** the machine has about 79 GB of commit, and other programs hold a large share. Free commit was 35 GB at 04:54. Read free commit before each heavy step. If it is under 30 GB, close and reopen the editor, or wait, rather than start. Log the editor's committed memory every few seconds while rendering or packaging.
- **Settings:** put back any console or quality setting you change, and read it back to confirm.

Finishing the work

Keep going until the phase is done. If you notice yourself offering to stop or handing back a list of remaining steps, do the next step instead. Errors, timeouts and failing tools are ordinary obstacles: diagnose them and work through them.

- If the editor crashes, check what survived against the journal, and continue once the editor is back.
- If the same step crashes twice, change one thing at a time. After two further crashes of that step, record the best workaround with evidence and move on to the rest.
- If something stalls, say in one line what is stalled, for how long, and the last stage you verified. Then try another route.

Progress and the final report

Give a one-line update as each step finishes. Finish with a report that stands on its own:

- each Phase 11 acceptance line with its number;
- where the package is on D: and on Google Drive, with sizes and checksums;
- what was saved or changed in the project;
- the short list of decisions and items that need the owner;
- the full path of every file you wrote.

The owner knows Revit and construction well and Unreal less well. Use plain words and full sentences, say what an Unreal term means the first time you use it, and use the same word for the same thing throughout.
