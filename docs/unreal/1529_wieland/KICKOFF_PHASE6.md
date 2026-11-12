# Kickoff prompt: Phase 6 (interiors), unattended run

Written by the supervising session at 22:15 on 2026-11-11, after Phase 5 closed (commit `cfc69a97`). Run as a headless Fable session against the open editor; the owner is away and has asked that the work not stop. Everything below the line is the prompt.

---

Phase 6 (interiors) of the 1529 N. Wieland scene plan, unattended

What this session is for

You are carrying out Phase 6 of the plan in `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\PLAN.md`, in the Unreal Engine 5.9 project `D:\Unreal_Engine_Projects\Wieland1527 5.9\Wieland1527.uproject`, through the editor's agent server (unreal-mcp). Phases 1 to 5 are complete. You have none of the earlier sessions' memory; their records are in the plan folder.

You are running from a terminal, not the editor's panel, and nobody will answer questions. The owner is away and has said the work must not stop. Decide what you can, and put anything that truly needs the owner in the final report. A supervisor checks your progress every 15 minutes.

Done means

- Every Phase 6 acceptance line in a new `...\docs\unreal\1529_wieland\phase6_results.md` has a measured number, or a workaround with its reason. Keep a journal in that file as Phases 4 and 5 did (a line marked PENDING before each step, committed before you start it, and a "How to resume" section), so a later session can continue if this one ends.
- Every error is logged in `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\PROJECT_MEMORY.md` with cause, fix and status, in a new section for Phase 6.
- Everything is committed in the plan's working copy on its current branch. Do not push.
- Then stop. Phase 7 starts in its own session.

Read these first, and only these

Read named sections and the ends of logs; do not re-read whole large files, and do not repeat a measurement already recorded.

1. In `PLAN.md`: "Rules for every phase", "Approvals this plan will ask for", "Budgets", and "Phase 6".
2. `phase5_results.md`: its acceptance lines, "Audit table in short", "What was saved or changed" and "For the owner to decide or supply". `phase3_results.md`: how the building was grouped into units and levels.
3. `mesh_swaps.csv`, `material_alternatives.csv` and the header and a few rows of `material_audit.csv`.
4. `REFERENCE_VIEWS.md`: design views D1 to D5.
5. The material sections of `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\AGENTS.md` and `WORKFLOW.md` (seamless materials; dimensional tile relief under grazing light).
6. The last two sections of `PROJECT_MEMORY.md`.

What the owner has already decided, and what is still the owner's

- Decided on 2026-11-10: two mirrored, identically finished halves, each a triplex below and a penthouse above; all four units read as fully finished; one furniture set per room type, approved once and reused; interiors load by where the viewer stands; alternatives are switchable for kitchens, baths and floors.
- Not yet decided, so do not decide it for the owner:
  - The `decision` column of `material_audit.csv` is empty. Step 6.3 therefore applies nothing as a replacement. The Revit materials stay the active default; the Phase 5 candidates stay switchable alternatives.
  - The owner has not named the kitchen, bath and floor alternatives. For step 6.7, build the switching mechanism with the engine's variant tool (Variant Manager: a list of named options that each change a set of objects in one click), using as its first options "Revit as exported" and "Phase 5 candidates" for each kitchen, bath and floor surface. The owner renames or adds options later.
  - Furniture is not approved. For step 6.4, write the proposal only (`furniture_proposal.csv`: room type, item, source, licence, size on disk, cost). Acquire nothing: furniture downloads are not covered by the standing approval, which covers public-domain textures only. For step 6.5, place labelled grey stand-in blocks of the proposed sizes, tagged `W1529.Placeholder`, so rooms do not read empty from the street; record that the dressing waits for approval.
  - Which repository packages under `E:\Claude\3D-Model-Workflow\output\` belong to this building is not recorded. Use only packages whose manifest names a product that the Revit material or family names match, list each match with its evidence, and list unmatched ones for the owner.
- Step 6.1: the owner prioritizes; you propose. Work the list in your own order of what shows most at camera distance in D1 to D5, and say so.
- Step 6.2: geometry refinement (rounded edges, reveals, cabinet door gaps, baseboards, switch plates) is in scope. Make new meshes as new assets and record every swap in `mesh_swaps.csv`; never edit an asset Datasmith created.
- Step 6.6: if the halves turn out not to be exact mirrors, measure where they differ and record it; refine those rooms separately.

Rules that apply throughout

- Never save `/Game/Wieland/R15_Landscape/L_R15_Production`, never use "Save All", save named assets only, and never edit an asset that Datasmith created; apply changes as overrides, instances or recorded swaps.
- Do not change Windows, driver or graphics-card settings, and do not touch the Revit model.
- Memory: the machine has about 79 GB of commit, and other programs hold a large share. Before any heavy step (mesh build, import, render, profile), read free commit; if it is under 30 GB, unload what you can and wait rather than start. Log the editor's committed memory every few seconds during heavy steps, so a crash leaves evidence. Phase 5's log stayed between 32 and 37 GB free; interiors add objects fast, so check often.
- Build one room's refinement first and check it before any batch, as Phase 4 did with one mesh file.
- Every material must look seamless and non-repeating under the repository's acceptance gate; intentional tile joints are fine. Judge tile relief under grazing light and record relief, grout step and clearance in millimetres.
- Profile M4 must state its conditions (lighting, viewport pixel size, editor in the foreground or not) as M2's repeat and M3 did.

Finishing the work

Keep going until the done list is met. If you notice yourself offering to stop or handing back a list of remaining steps, do the next step instead. Errors, timeouts and failing tools are ordinary obstacles: diagnose them and work through them. If the editor crashes, the supervisor restarts it; when it is back, check what survived against your journal and continue. If the same step crashes twice, change one thing at a time; after two further crashes of that step, record the best workaround with evidence and move on to the rest of the phase. If something stalls, say in one line what is stalled, for how long, and the last stage verified, then try another route.

Progress and the final report

Give a one-line update as each step finishes. Finish with a report that stands on its own: each Phase 6 acceptance line with its number; what was refined, mirrored, and set up for loading and alternatives; what was saved or changed in the project; the short list of decisions and items that need the owner; and the full path of every file you wrote.

The owner knows Revit and construction well and Unreal less well. Use plain words and full sentences, say what an Unreal term means the first time you use it, and use the same word for the same thing throughout.
