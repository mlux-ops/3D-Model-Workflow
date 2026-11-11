# Kickoff prompt: Phase 3, for a new chat in the Unreal 5.9 Assistant panel

Written on 2026-11-11 with the `fable-prompt-architect` skill, by the session that finished Phases 1 and 2. Use it after the editor has been restarted. Paste everything below the line into a **new chat** in the Unreal 5.9 Assistant panel. Before pasting, check that the model shows as Fable 5.2 and choose a permission mode other than "Bypass permissions".

**Run settings.** Effort: high. No subagents are needed: one editor, one writer. Nothing else to set.

**What this prompt assumes,** so that it can be corrected in one line if any is wrong: the session shapes its own scripts under `tools\` and its own content under `/Game/Wieland1529/`, and leaves everything else in the project as it is; nobody watches the work live, so updates are short and the last message carries the whole result; the standing approval of 2026-11-11 is still in force; the final report is read by the owner, who knows Revit and construction well and Unreal less well.

**After the first run,** look for five things in what the session did: stopping before the phase's acceptance lines are measured; asking for an approval the prompt already gives; long stretches with no word; work handed to helper agents; and new scripts written beside old ones that already do the job. If one shows, change that one section of the prompt and nothing else.

---

# Phase 3 of the 1529 N. Wieland scene plan: the building, imported and placed

## What this session is for

You are carrying out Phase 3 of an existing plan in the Unreal Engine 5.9 project `D:\Unreal_Engine_Projects\Wieland1527 5.9\Wieland1527.uproject`. Phases 1 and 2 were finished on 2026-11-11 by an earlier chat whose memory you do not have; everything it did is written down and committed, and you work from its records. Phase 3 brings the whole building from my Revit export into its own Unreal level, at its true position, with a repeatable way to take in later exports that keeps every Unreal-side material assignment and edit.

## Done means

Each acceptance line of the plan's Phase 3 section has a measured number in a new results file, `docs\unreal\1529_wieland\phase3_results.md`, or that file names exactly what is not measured and why. Profile M1 is saved. The plan's Phase 3 section carries a status line and a table of what it leaves for later phases, as the Phase 1 and Phase 2 sections do. Everything is committed in the plan's working copy on its current branch. Do not push.

## Read these first, and only these

This session counts against a subscription's usage limits. Read named sections, and do not repeat a measurement that is already recorded. The plan's working copy is `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\`.

1. In `docs\unreal\1529_wieland\PLAN.md`: "Rules for every phase"; the Phase 3 section; and the two tables headed "What Phase 1 leaves for later phases" and "What Phase 2 leaves for later phases", which sit in the Phase 1 and Phase 2 sections.
2. In `docs\unreal\1529_wieland\phase2_results.md`: the status block and "Step 2.5: the level frame".
3. In `docs\unreal\1529_wieland\phase1_results.md`: "How to resume" only. It holds the import and reimport method that works in this engine.
4. In `PROJECT_MEMORY.md` at the working copy's root: the last subsection, "Phase 2 build session". Search the subsection before it for a fault when you meet one; do not read it through.

## Where things stand

The editor should have been restarted since 11:39 on 2026-11-11. Your first check tells you: `r.Lumen.WorldCache.Supported` must read false and `r.Material.UseShaderCompilationParameters` must read 0. If the first reads true, the editor has not been restarted; say so in one line and carry on, because nothing in this phase but the final profile depends on it, and for that profile set `r.Lumen.WorldCache.Allowed 0` for its length.

The level frame is settled: the origin is the lot's south-west corner, north is -X along the front lot line, east is -Y, and the lot that governs is the record rectangle, 15.088 m along the street by 31.151 m deep. The Revit export sits in this frame by a shift only, as far as two figures from an older export hold. The plan's step 3.3, "place the import by the Revit survey point", cannot work as written, because the export holds no map coordinates for that point. Place the building by the lot instead, and confirm the shift from the import itself before anything is built on it: the building's street face is 10 ft 2 1/2 in behind the front lot line, 43 ft 4 in wide and centred on the lot.

There are two exports in `E:\Claude\3D-Model-Workflow\references\1529 Wieland - Datasmith\`: the first of 2026-11-10 and the second, ending `_r2`, of 2026-11-11. The second is the newer. Import the first and then reimport from the second. That ends on the newer model and runs step 3.10 and its acceptance line once, without asking me for a third export. Set up the override and swap tables and the scripts of steps 3.6 to 3.9 before the reimport, so that the reimport tests them.

The content under `/Game/Wieland1529/Scratch/` is Phase 1's test content. Do not build on it and do not remove it.

I have decided three things that the plan now records: the eight texture files missing from both exports are disregarded in the import and belong to the material audit, where they are replaced; free space on C: does not gate any step; and I do not want to be drawn into the work step by step.

## How to work

Start with the state, not the work: confirm with read-only calls that the editor answers, the two variables above, that nothing is unsaved, and how much memory is free. Write what you find into the results file before you act on it.

Before an import, a reimport or any other step that can crash the editor, write one line into the results file saying what you are about to do, and commit it. A crash ends this chat, and the next one reads that line. If you find such a line still pending when you start, the step crashed: record it, read its cause from the editor's log and from the engine's own source under `D:\Games\UE_5.9\Engine\`, change one thing and try again. After two further crashes of the same step, stop that step and report the options.

Use the scripts that exist under `docs\unreal\1529_wieland\tools\` and extend them; do not write a second script for a job one of them already does. `wieland_datasmith.py` imports, reimports, counts and checks; `wieland_geo.py` holds the level frame; `wieland_profile.py` captures.

## Approvals

A standing approval of 2026-11-11 is written in `PLAN.md` under "Approvals this plan will ask for". Read it and use it; record each use, with its size, in the results file.

Ask me before you do any of these, and collect what you need to ask into one request that names each action, its size on disk and its cost: anything with a price; deleting anything; pushing or merging; creating an account or a key; changing Windows settings or my sign-in; saving a project-wide rendering setting, other than leaving the line `r.Material.UseShaderCompilationParameters=0` where it is; and writing anywhere except this project folder, the plan's working copy, `E:\Wieland1529_site_data\` and the archive folder on H:.

These need no approval: reading files; read-only queries to the editor; creating and saving levels and assets under `/Game/Wieland1529/`; copying the two exports into the project's `ImportStaging` folder under dated names, about 0.7 GB and 0.9 GB on D:; console settings that you put back before the step ends; writing results into the plan's working copy and committing there; and retrying a call after a timeout once you have checked the editor's state.

Never save `/Game/Wieland/R15_Landscape/L_R15_Production`, and never use "Save All"; save named assets only. If the building has to be seen together with the existing surroundings, make a new level under `/Game/Wieland1529/` that holds both. Do not open the levels under `/Game/Wieland/Revit1527` without first writing the attempt into the results file. You are the only writer to this project and to the plan's working copy.

## Finishing the work

Keep going until the done list is met. Questions about decisions that are truly mine are welcome, in one request, but keep working on everything that does not depend on my answer. If you notice yourself offering to stop or handing back a list of remaining steps, do the next step instead. Errors, timeouts and failing tools are ordinary obstacles: diagnose them and work through them. Things that only I can do, such as a site visit or a change in Revit, are not reasons to stop: record them as gaps with a default that needs nothing from me, as Phase 2 did.

## Progress and the final report

Say in one line what you are about to do before you start, and give a short update as each step finishes. Finish with a report that stands on its own for someone who reads only that message: each acceptance line with its number; anything in the plan that turned out wrong and what replaced it; what was saved or changed in the project; what is still waiting on me, if anything; and the full path of every file you wrote.

I know Revit and construction well and Unreal less well. Use plain words and full sentences, say what an Unreal term means the first time you use it, and use the same word for the same thing throughout.
