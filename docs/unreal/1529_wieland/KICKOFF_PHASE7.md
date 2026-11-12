# Kickoff prompt: Phase 7 (site, surroundings and vegetation), unattended run

Written in advance by the supervising session on 2026-11-12, so the watcher can start this phase as soon as Phase 6 closes without waiting for the supervisor. Everything below the line is the prompt.

---

Phase 7 (site, surroundings and vegetation) of the 1529 N. Wieland scene plan, unattended

What this session is for

You are carrying out Phase 7 of the plan in `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\PLAN.md`, in the Unreal Engine 5.9 project `D:\Unreal_Engine_Projects\Wieland1527 5.9\Wieland1527.uproject`, through the editor's agent server (unreal-mcp). Phases 1 to 6 are complete or closed as far as they can be without the owner. You have none of the earlier sessions' memory; their records are in the plan folder.

You are running from a terminal, not the editor's panel, and nobody will answer questions. The owner is away and has said the work must not stop. Decide what you can, and put anything that truly needs the owner in the final report. A supervisor checks your progress every 15 minutes and relaunches you if you stop.

If `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\phase7_results.md` already exists, an earlier session started this phase: read its "How to resume" section and its journal from the bottom up, inspect what exists, and continue from the first unfinished line. Do not repeat finished work.

Done means

- Every Phase 7 acceptance line in `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\phase7_results.md` has a measured number, or a workaround with its reason. Keep a journal in that file as Phases 4 to 6 did (a line marked PENDING before each step, committed before you start it, and a "How to resume" section), so a later session can continue if this one ends.
- Every error is logged in `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\PROJECT_MEMORY.md` with cause, fix and status, in a new section for Phase 7.
- Everything is committed in the plan's working copy on its current branch. Do not push.
- Then stop. The next phase starts in its own session.

Read these first, and only these

Read named sections and the ends of logs; do not re-read whole large files, and do not repeat a measurement already recorded.

1. In `PLAN.md`: "Rules for every phase", "Approvals this plan will ask for", "Budgets", "What Phase 1 leaves for later phases" (the rows for Phase 7), and "Phase 7".
2. `phase6_results.md`: its acceptance lines, what was saved or changed, and its list for the owner. Earlier results files only where Phase 7 names their outputs.
3. `REFERENCE_VIEWS.md` for stations and design views, and `OPEN_DECISIONS.md` for what is still the owner's.
4. The material and delivery sections of `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\AGENTS.md` and `WORKFLOW.md`, where they apply to this phase.
5. The last two sections of `PROJECT_MEMORY.md`.

What is still the owner's

- Standing approval: the no-cost rows of the plan's approvals table, inside their caps, are approved. Anything with a price, an account or key, any deletion, any change to Revit, Windows, drivers or the graphics card, and any push or merge is not approved: put it in the final report.
- Owner decisions not yet made (keep-or-rebuild per material, the names of finish alternatives, furniture, the site visit and photographs) stay the owner's. Build what you can around them as switchable or labelled placeholders, and record what waits on which decision.
- SCOPE, by the owner's instruction of 2026-11-12: this phase works SOLELY on the site model and its surroundings: the neighbouring buildings, the site itself (ground, street, kerbs, sidewalks, alley, paving, fences, street furniture) and vegetation. It does the plan's Phase 7 (vegetation) and reopens Phase 4's surroundings to make them look right. It does not touch the interiors, the house's own materials, lighting (Phase 8, apart from a fixed daylight for review renders), optimisation or delivery. The goal is a site that reads as photoreal at stations S1 to S9, at least as good as the earlier production level.
- Step 7.0, buildings, first: the owner finds the Phase 4 grey surroundings poor and wants the earlier detailed site buildings back. They are the 58 merged parts of the old production level `/Game/Wieland/R15_Landscape/L_R15_Production` (see `SITE_MODEL_AUDIT.md` A3 to A10, R4 and ML1 to ML10, and `phase4_results.md`). Make a new level `/Game/Wieland1529/Surroundings/L_Surroundings_R15` holding new placed copies of those parts (same meshes and materials, same positions; the old level is only read, never saved), and add it to `L_Site_M2`. Make it the default view, and hide the Phase 4 grey buildings it overlaps; keep the Phase 4 ground and the far buildings it does not cover. Make the choice switchable in one action (Variant Manager list `Surroundings`: options "Earlier detailed buildings" and "Phase 4 survey massing"). Measure and record where the two disagree (footprint and height of each overlapping building, against the Phase 4 laser-scan comparison), since the earlier heights are estimates (audit A3) and 1525 differs from the real house (A4).
- Step 7.1, the rest of the surroundings: give every Phase 4 building that the earlier level does not cover materials (brick, siding, stone, roofing, windows as material, not bare grey) using the Phase 5 parents and the CC0 sets already on disk; fix the audit's site findings that need no photograph (A5 siding gaps and the step texture, ML2 repeating brick bands on 1533, the world ending in view A10 with a distant-city stand-in). Where the old level's merged parts carry the R14 stand-alone materials (ML10), you may put Phase 5 parent instances on the new copies as recorded swaps.
- Step 7.2, the site: ground, street, kerbs, sidewalks, alley, parkway lawn, paving and fences with materials at their physical scale, seamless and non-repeating. The Revit site slab overlaps the new street by up to 92 cm and the Revit neighbour massing sits inside the neighbours: do not edit them (Datasmith assets) and do not touch Revit; hide them in the site view by a recorded per-object override, and list the Revit fix for the owner.
- Step 7.3, vegetation, as in the plan's Phase 7. The earlier production level also holds trees and planting: bring those across into a new level the same way as the buildings, as the default, where they match the 2022 aerial photograph and laser scan; record each tree's position against those data.
- Review: render S1 to S9 (S7 if its alley exists) with the earlier buildings and with the Phase 4 massing, beside the earlier production level's renders where they exist, with the same "PLACEHOLDER: no photograph" panel on the photograph side.
- Tree, shrub and plant models from Fab or any other library need the owner's approval per item and are not covered by the standing approval. Propose them (`vegetation_proposal.csv`: species, size, source, licence, size on disk, cost) and acquire nothing. Use only vegetation assets already in the project whose licence is recorded in `asset_licences.csv`; the Megaplant library has no licence record (Phase 5), so it may be used for placement and measurement tests but every use is listed for the owner.
- There is no site survey of trees yet. Place trees from the 2022 laser scan and aerial photograph already on disk (Phase 2 and 4 data), mark each as surveyed from data, not from a site visit, and tag stand-ins `W1529.Placeholder`.

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

Give a one-line update as each step finishes. Finish with a report that stands on its own: each Phase 7 acceptance line with its number; what was saved or changed in the project; the short list of decisions and items that need the owner; and the full path of every file you wrote.

The owner knows Revit and construction well and Unreal less well. Use plain words and full sentences, say what an Unreal term means the first time you use it, and use the same word for the same thing throughout.
