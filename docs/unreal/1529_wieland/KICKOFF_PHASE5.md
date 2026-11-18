# Kickoff prompt: Phase 5 (materials), unattended run

Written by the supervising session at 20:45 on 2026-11-11, after Phase 4 closed (commit `ef859cd1`). Run as a headless Fable session against the open editor; the owner is away and has asked that the work not stop. Everything below the line is the prompt.

---

Phase 5 (materials) of the 1529 N. Wieland scene plan, unattended

What this session is for

You are carrying out Phase 5 of the plan in `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\PLAN.md`, in the Unreal Engine 5.9 project `D:\Unreal_Engine_Projects\Wieland1527 5.9\Wieland1527.uproject`, through the editor's agent server (unreal-mcp). Phases 1 to 4 are complete. You have none of the earlier sessions' memory; their records are in the plan folder.

You are running from a terminal, not the editor's panel, and nobody will answer questions. The owner is away and has said the work must not stop. Decide what you can, and put anything that truly needs the owner in the final report. A supervisor checks your progress every 15 minutes.

Done means

- Every Phase 5 acceptance line in a new `...\docs\unreal\1529_wieland\phase5_results.md` has a measured number, or a workaround with its reason. Keep a journal in that file as Phase 4 did (a line marked PENDING before each step, committed before you start it, and a "How to resume" section), so a later session can continue if this one ends.
- Every error is logged in `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\PROJECT_MEMORY.md` with cause, fix and status, in a new section for Phase 5.
- Everything is committed in the plan's working copy on its current branch. Do not push.
- Then stop. Phase 6 starts in its own session.

Read these first, and only these

Read named sections and the ends of logs; do not re-read whole large files, and do not repeat a measurement already recorded.

1. In `PLAN.md`: "Rules for every phase", "Approvals this plan will ask for", "Budgets" (video memory), and "Phase 5".
2. `phase4_results.md`, its acceptance table and its "Needs the owner" list; `phase3_results.md`, its material table.
3. `material_audit.csv`, `material_map.csv` and `mesh_swaps.csv` in the plan folder (made in Phase 3).
4. `SITE_MODEL_AUDIT.md`, findings ML1 to ML9 only.
5. The material sections of `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\AGENTS.md` and `WORKFLOW.md` (seamless and non-repeating materials; dimensional tile relief). These are rules for this work.
6. The last two sections of `PROJECT_MEMORY.md`.

What the owner has already decided, and what is still the owner's

- The owner's rule for materials (2026-11-10): Revit's materials stay as exported by default. Audit every material, give a confidence figure from 1 to 5 for how faithfully it shows the specified finish, and the owner decides "keep" or "rebuild" from that. Surfaces with alternatives are switchable alternatives, not replacements.
- So, in this run: complete step 5.0 in full and make a swatch sheet per material. For every material you score 3 or lower, build the native Unreal candidate as an instance of the new parents, assigned through a switchable alternative (a material swap the scene can turn on and off, recorded in a table), with the Revit material left as the active default. The owner will then only have to choose.
- There are no owner photographs yet (the site visit has not happened). Steps 5.3 and 5.9 cannot be done as written: say so in the results, and for 5.9 make grey or material renders of S1, S3 and S6 with the same "PLACEHOLDER: no photograph" panel used in Phase 4. Do not take textures, traces or colours from Google Street View or any map imagery: its terms allow looking only.
- Step 5.4 (public-domain sets): use the standing approval recorded in the plan for no-cost items inside its caps, if it covers this; record each download with its licence in `asset_licences.csv`. Anything with a price, an account, or outside the standing approval goes in the final report instead.
- Step 5.1: record a licence line for every texture and asset. Do not delete or remove any asset that lacks one; list it for the owner. Deletion is not approved.
- Step 5.5: this repository's material packages are under `E:\Claude\3D-Model-Workflow\output\`; keep their physical scale.

Rules that apply throughout

- Never save `/Game/Wieland/R15_Landscape/L_R15_Production`, never use "Save All", save named assets only, and never edit an asset that Datasmith created; apply changes as overrides, instances or recorded swaps.
- Do not change Windows, driver or graphics-card settings, and do not touch the Revit model.
- Memory: the machine has about 79 GB of commit, and other programs hold a large share. Before any heavy step (texture import, large material compile, render), read free commit; if it is under 30 GB, unload what you can and wait rather than start. Log the editor's committed memory every few seconds during heavy steps, so a crash leaves evidence.
- Every material must look seamless and non-repeating under the repository's acceptance gate; intentional tile joints are fine.
- Phase 4 noted that profile M2 was not like-for-like with M1. Before step 5.10, repeat M2 under fixed, recorded conditions (lighting, viewport pixel size, editor in the foreground if you can), then record M3 the same way.

Finishing the work

Keep going until the done list is met. If you notice yourself offering to stop or handing back a list of remaining steps, do the next step instead. Errors, timeouts and failing tools are ordinary obstacles: diagnose them and work through them. If the editor crashes, the supervisor restarts it; when it is back, check what survived against your journal and continue. If the same step crashes twice, change one thing at a time; after two further crashes of that step, record the best workaround with evidence and move on to the rest of the phase. If something stalls, say in one line what is stalled, for how long, and the last stage verified, then try another route.

Progress and the final report

Give a one-line update as each step finishes. Finish with a report that stands on its own: each Phase 5 acceptance line with its number; the audit table summary (material, confidence, candidate built or not); what was saved or changed in the project; the short list of decisions and items that need the owner; and the full path of every file you wrote.

The owner knows Revit and construction well and Unreal less well. Use plain words and full sentences, say what an Unreal term means the first time you use it, and use the same word for the same thing throughout.
