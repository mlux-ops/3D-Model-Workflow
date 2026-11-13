Phase 12 (material rebuild) of the 1529 N. Wieland scene plan, unattended

What this session is for

You are carrying out Phase 12 of the plan in `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\PLAN.md`, in the Unreal Engine 5.9 project `D:\Unreal_Engine_Projects\Wieland1527 5.9\Wieland1527.uproject`, through the editor's agent server (unreal-mcp). Phase 12 is the material rebuild the owner asked for on 2026-11-12. It runs after Phase 8 and before Phase 9, so that Phase 9 budgets the final textures. Phases 1 to 8 are complete or closed as far as they can be without the owner. You have none of the earlier sessions' memory; their records are in the plan folder.

You are running from a terminal, not the editor's panel, and nobody will answer questions. The owner is away and has said the work must not stop. Decide what you can, and put anything that truly needs the owner in the final report. A supervisor checks your progress every 15 minutes and relaunches you if you stop.

If `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\phase12_results.md` already exists, an earlier session started this phase: read its "How to resume" section and its journal from the bottom up, inspect what exists, and continue from the first unfinished line. Do not repeat finished work.

The owner's decisions, and where to read them

The owner answers on a review page that writes straight into `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\material_audit.csv`, columns `decision` (keep, candidate, rebuild, or blank) and `owner_note` (free text: what the finish really is). Every answer is also logged with its time in `owner_review\decisions_log.csv`. The owner may keep answering while you work, so:

- Build the work list from the table in Phase 12 of `PLAN.md` at the start: rebuild every "rebuild" row and every blank row with confidence 1 or 2; make the Phase 5 candidate active for every "candidate" row; leave "keep" rows and blank rows scored 3 to 5 alone.
- Read the two columns again before each material and before the last step. A row whose answer changed after you handled it is redone at the end. Never write to `material_audit.csv` yourself; record your work in `material_rebuild.csv`.
- The owner's note outranks anything you infer. Where there is no note and Revit never set a finish, infer it from the objects, families, categories and rooms that use the material, say so in the row, and label the result as an assumption on its sheet.

Done means

- Every Phase 12 acceptance line in `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\phase12_results.md` has a measured number, or a workaround with its reason. Keep a journal in that file as the earlier phases did (a line marked PENDING before each step, committed before you start it, and a "How to resume" section), so a later session can continue if this one ends. The first `Status:` line says DONE, with the time, only when the phase is finished.
- A new swatch sheet for every rebuilt material, Revit beside rebuilt, in the Phase 5 style, under `review\phase12\swatches\sheets\`, named exactly like the Phase 5 sheets so the owner's review page can be pointed at them.
- Every error is logged in `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\PROJECT_MEMORY.md` with cause, fix and status, in a new section for Phase 12.
- Everything is committed by explicit path in the plan's working copy on its current branch. Do not commit `material_audit.csv` or `owner_review\decisions_log.csv`; the supervisor commits the owner's answers. Do not push.
- Then stop. Phase 9 starts in its own session.

Read these first, and only these

Read named sections and the ends of logs; do not re-read whole large files, and do not repeat a measurement already recorded.

1. In `PLAN.md`: "Rules for every phase", "Approvals this plan will ask for", "Budgets", "Phase 5" (the texel-density table and step 5.8) and "Phase 12".
2. In `phase5_results.md`: "How to resume", "What was saved or changed in the project", "For the owner to decide or supply" and "Files written in this phase". Use the Phase 5 parents, candidate scripts, test method and tables rather than writing new ones.
3. In `phase8_results.md`: its status lines, its acceptance lines and the J9 entries, for the ground-truth views, the render route that worked (`j9_one.py`) and the crash notes.
4. The material sections of `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\AGENTS.md` and `WORKFLOW.md`: seamless and non-repeating materials, a colour map for every material, sculpted-tile relief under grazing light.
5. The last two sections of `PROJECT_MEMORY.md`.

What is still the owner's

- Standing approval: the no-cost rows of the plan's approvals table, inside their caps, are approved. That covers public-domain textures at no cost within the download cap; read `asset_downloads.csv` for what is already used. Anything with a price, an account or key, any deletion, any change to Revit, Windows, drivers or the graphics card, and any push or merge is not approved: put it in the final report.
- Keep-or-rebuild for materials scored 3 to 5 that the owner left blank stays the owner's. Leave them as exported and list them.

Rules that apply throughout

- Never save `/Game/Wieland/R15_Landscape/L_R15_Production`, never use "Save All", save named assets only, and never edit an asset that Datasmith created; apply changes as overrides, instances, new assets or recorded swaps, and keep every swap switchable back to the Revit material.
- Memory: the machine has about 79 GB of commit, and other programs hold a large share. Before any heavy step, read free commit; if it is under 30 GB, unload what you can and wait rather than start. Log the editor's committed memory every few seconds during rendering, so a crash leaves evidence.
- Rebuild one material first and look at its sheet before any batch.
- Every material must look seamless and non-repeating under the repository's acceptance gate; intentional tile joints are fine.
- Path-traced rendering: after opening a level, let it settle for five minutes before the first path-traced frame (the first frame crashed the graphics card once on 2026-11-12). Render one view at a time. The agent server does not answer while a picture renders, for up to about 11 minutes; check the output folder before treating it as down.
- Put back any console or quality setting you change for a render, and read it back to confirm.

Finishing the work

Keep going until the done list is met. If you notice yourself offering to stop or handing back a list of remaining steps, do the next step instead. Errors, timeouts and failing tools are ordinary obstacles: diagnose them and work through them. If the editor crashes, the supervisor restarts it; when it is back, check what survived against your journal and continue. If the same step crashes twice, change one thing at a time; after two further crashes of that step, record the best workaround with evidence and move on to the rest of the phase. If something stalls, say in one line what is stalled, for how long, and the last stage verified, then try another route.

Progress and the final report

Give a one-line update as each material or step finishes. Finish with a report that stands on its own: each Phase 12 acceptance line with its number; the materials rebuilt, switched to their candidate, or left open, with counts; what was saved or changed in the project; the short list of decisions and items that need the owner (including every finish that rests on an assumption); and the full path of every file you wrote.

The owner knows Revit and construction well and Unreal less well. Use plain words and full sentences, say what an Unreal term means the first time you use it, and use the same word for the same thing throughout.
