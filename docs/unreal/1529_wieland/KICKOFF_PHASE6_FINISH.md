# Kickoff prompt: finish Phase 6 (interiors), editor panel

Written by the supervising session on 2026-11-12 after Phase 7 closed (commit `e0c7284b`), for the owner
to paste into the Unreal editor's agent panel. Built with the Fable 5.2 prompt guidance. Everything below
the line is the prompt.

---

Finish Phase 6 (interiors) of the 1529 N. Wieland scene plan

What this session is for

You are finishing Phase 6 of the plan in `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\PLAN.md`, in the Unreal Engine 5.9 project `D:\Unreal_Engine_Projects\Wieland1527 5.9\Wieland1527.uproject`, through the editor's agent server. The scene and its tools are yours to shape within the rules below. You have none of the earlier sessions' memory; their records are in the plan folder.

Phase 6 was paused by the owner at 09:14 on 2026-11-12 after journal line J11, so that Phase 7 (site, surroundings and vegetation) could run first. Phase 7 is now done. Three pieces of Phase 6 remain:

1. Step 6.9, journal line J12: pictures of the design views D1 to D5, each once in plain grey and once with the materials as saved, beside the matching Revit views. J12 was started at 09:15 and stopped by the owner before it finished, so treat its result as unknown. Look in `review\phase6\` for any pictures it left, and redo the step in full rather than mixing old and new pictures.
2. Step 6.10: run the two interior walking paths and save profile M4.
3. The Phase 6 final report.

What changed since Phase 6 paused

Phase 7 saved changes to the top level `/Game/Wieland1529/L_Site_M2`. It added the earlier detailed neighbour buildings as the default view, the ground and street materials and vegetation levels, a Variant Manager list called `Surroundings`, and a recorded override that hides the Revit site slab and neighbour massing. Before rendering, read the sections "What was saved or changed in the Unreal project" and "For the owner" in `phase7_results.md`. Then check that the Phase 6 work still holds with the Phase 7 levels loaded:

- the unit levels and their level streaming volumes from J6 and J7 (a streaming volume is an invisible box; standing inside it loads that unit's level)
- the rounded-edge swaps
- the baseboards
- the furniture stand-ins
- the three Phase 6 Variant Manager lists

Render with the site as it now stands by default, with the earlier detailed buildings, and say so on each sheet. Where Phase 7 broke a Phase 6 result, fix it as an override or a new asset, journal it, and log it in project memory.

Done means

- Every Phase 6 acceptance line in `phase6_results.md` has a measured number, or a workaround with its reason. That includes the lines for D1 to D5 and for M4.
- The journal is kept as before. Write a line marked PENDING and commit it before each step, then replace it with the outcome. The status lines at the top say the phase is DONE, with the time.
- Every error is logged in `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\PROJECT_MEMORY.md` with cause, fix and status, in a section headed "Phase 6 finish".
- Everything is committed by explicit path on the current branch, `claude/1529-wieland-scene-plan-e84a03`. Do not push.
- Then stop. Phase 8 (lighting) starts in its own session.

Read these first, and only these

Read the named sections; do not re-read whole large files or repeat a measurement already recorded.

1. In `phase6_results.md`: the status lines, "How to resume", the journal from J9 to J12, "Acceptance lines" and "Files written".
2. In `PLAN.md`: "Rules for every phase", "Budgets", and Phase 6 steps 6.9 and 6.10 with their acceptance lines. The M4 conditions and paths are defined there and in the earlier profiles M2 and M3. Reuse those conditions so the numbers can be compared.
3. `REFERENCE_VIEWS.md`, for the cameras of D1 to D5 and the matching Revit views.
4. In `phase7_results.md`: the two sections named above.
5. The last two sections of `PROJECT_MEMORY.md`.

What is still the owner's

- **Covered by standing approval:** the no-cost rows of the plan's approvals table, inside their caps.
- **Not approved; put it in the final report instead of doing it:**
  - anything with a price
  - any account or key
  - any deletion
  - any download or store asset outside those rows
  - any change to Revit, Windows, drivers, the graphics card or project-wide settings files
  - any push or merge
- **Owner decisions still open:** keep-or-rebuild per material, the names of the finish alternatives, furniture, and the site visit and photographs. Leave them as they are: switchable options or labelled stand-ins. Say on each picture sheet which of those decisions the picture waits on.
- **Without asking:** reading files, running the editor's Python, rendering, profiling, saving the named Phase 6 assets, and retrying a call that failed for an ordinary reason. Do these and keep going.

Rules that apply throughout

- Never save `/Game/Wieland/R15_Landscape/L_R15_Production` and never use "Save All". Save named assets only.
- Never edit an asset Datasmith created (Datasmith is the Revit-to-Unreal importer, and it replaces those assets at the next reimport). Apply changes as overrides, new assets or recorded swaps.
- Memory: the machine has about 79 GB of commit, and other programs hold a large share. Read free commit before each heavy step. If it is under 30 GB, unload what you can and wait rather than start. Log the editor's committed memory every few seconds during rendering and profiling, so that a crash leaves evidence.
- Try one design view first and check its pictures before rendering the rest.
- Put back any sun, console or quality setting you change for a picture or a profile, and read it back to confirm.
- A profile states its conditions: lighting, viewport pixel size, whether the editor was in the foreground, and which levels and Variant Manager options were active. M4 must be comparable with M2 and M3.

Finishing the work

Keep going until the done list is met. If you notice yourself offering to stop or handing back a list of remaining steps, do the next step instead. Errors, timeouts and failing tools are ordinary obstacles: diagnose them and work through them. If the editor crashes, check what survived against the journal and continue once it is back. If the same step crashes twice, change one thing at a time. After two further crashes of that step, record the best workaround with evidence and move on to the rest. If something stalls, say in one line what is stalled, for how long, and the last stage you verified, then try another route.

Progress and the final report

Give a one-line update as each step finishes. Finish with a report that stands on its own for the owner, who comes back to it later. It covers:

- each Phase 6 acceptance line with its number;
- what was saved or changed in the project in this session;
- anything Phase 7 had broken, and how it was fixed;
- the short list of decisions and items that need the owner;
- the full path of every file you wrote.

The owner knows Revit and construction well and Unreal less well. Use plain words and full sentences, say what an Unreal term means the first time you use it, and use the same word for the same thing throughout.
