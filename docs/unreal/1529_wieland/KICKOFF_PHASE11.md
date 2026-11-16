# Kickoff prompt: Phase 11 (packaging and delivery), unattended run

Written in advance by the supervising session on 2026-11-12, so the watcher can start this phase as soon as Phase 10 closes without waiting for the supervisor. Everything below the line is the prompt.

---

Phase 11 (packaging and delivery) of the 1529 N. Wieland scene plan, unattended

What this session is for

You are carrying out Phase 11 of the plan in `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\PLAN.md`, in the Unreal Engine 5.9 project `D:\Unreal_Engine_Projects\Wieland1527 5.9\Wieland1527.uproject`, through the editor's agent server (unreal-mcp). Phases 1 to 10 are complete or closed as far as they can be without the owner. You have none of the earlier sessions' memory; their records are in the plan folder.

You are running from a terminal, not the editor's panel, and nobody will answer questions. The owner is away and has said the work must not stop. Decide what you can, and put anything that truly needs the owner in the final report. A supervisor checks your progress every 15 minutes and relaunches you if you stop.

If `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\phase11_results.md` already exists, an earlier session started this phase: read its "How to resume" section and its journal from the bottom up, inspect what exists, and continue from the first unfinished line. Do not repeat finished work.

Done means

- Every Phase 11 acceptance line in `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\phase11_results.md` has a measured number, or a workaround with its reason. Keep a journal in that file as Phases 4 to 6 did (a line marked PENDING before each step, committed before you start it, and a "How to resume" section), so a later session can continue if this one ends.
- Every error is logged in `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\PROJECT_MEMORY.md` with cause, fix and status, in a new section for Phase 11.
- Everything is committed in the plan's working copy on its current branch. Do not push.
- Then stop. The next phase starts in its own session.

Read these first, and only these

Read named sections and the ends of logs; do not re-read whole large files, and do not repeat a measurement already recorded.

1. In `PLAN.md`: "Rules for every phase", "Approvals this plan will ask for", "Budgets", "What Phase 1 leaves for later phases" (the rows for Phase 11), and "Phase 11".
2. `phase10_results.md`: its acceptance lines, what was saved or changed, and its list for the owner. Earlier results files only where Phase 11 names their outputs.
3. `REFERENCE_VIEWS.md` for stations and design views, and `OPEN_DECISIONS.md` for what is still the owner's.
4. The material and delivery sections of `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\AGENTS.md` and `WORKFLOW.md`, where they apply to this phase.
5. The last two sections of `PROJECT_MEMORY.md`.

What is still the owner's

- Standing approval: the no-cost rows of the plan's approvals table, inside their caps, are approved. Anything with a price, an account or key, any deletion, any change to Revit, Windows, drivers or the graphics card, and any push or merge is not approved: put it in the final report.
- Owner decisions not yet made (keep-or-rebuild per material, the names of finish alternatives, furniture, the site visit and photographs) stay the owner's. Build what you can around them as switchable or labelled placeholders, and record what waits on which decision.
- Writing packaged builds, render frames and the project archive to H: is covered by the standing approval up to the plan's 120 GB cap. Long renders must resume from the last finished frame.
- Upload to Google Drive is required for final packages (AGENTS.md), but this session may have no Drive connection: check; if it is missing, list every file to upload with its size in the report and do not claim delivery.
- Never push the branch or merge to main.

Rules that apply throughout

- Never save `/Game/Wieland/R15_Landscape/L_R15_Production`, never use "Save All", save named assets only, and never edit an asset that Datasmith created; apply changes as overrides, instances, new assets or recorded swaps.
- Do not change Windows, driver or graphics-card settings, and do not touch the Revit model.
- Memory: the machine has about 79 GB of commit, and other programs hold a large share. Before any heavy step, read free commit; if it is under 30 GB, unload what you can and wait rather than start. Log the editor's committed memory every few seconds during heavy steps, so a crash leaves evidence.
- Try one item first and check it before any batch.
- Every material must look seamless and non-repeating under the repository's acceptance gate; intentional tile joints are fine.
- Any profile states its conditions (lighting, viewport pixel size, editor in the foreground or not), as M2's repeat, M3 and M4 did.

Finishing the work

Keep going until the done list is met. If you notice yourself offering to stop or handing back a list of remaining steps, do the next step instead. Errors, timeouts and failing tools are ordinary obstacles: diagnose them and work through them. If the editor crashes, the supervisor restarts it; when it is back, check what survived against your journal and continue. If the same step crashes twice, change one thing at a time; after two further crashes of that step, record the best workaround with evidence and move on to the rest of the phase. If something stalls, say in one line what is stalled, for how long, and the last stage verified, then try another route.

Progress and the final report

Give a one-line update as each step finishes. Finish with a report that stands on its own: each Phase 11 acceptance line with its number; what was saved or changed in the project; the short list of decisions and items that need the owner; and the full path of every file you wrote.

The owner knows Revit and construction well and Unreal less well. Use plain words and full sentences, say what an Unreal term means the first time you use it, and use the same word for the same thing throughout.
