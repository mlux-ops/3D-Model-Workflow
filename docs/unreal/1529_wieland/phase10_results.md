# Phase 10 results: reality-match review

Status: STARTED 2026-11-13 07:14 Central. Unattended run; the owner is away. Nothing is pushed.

Project: `D:\Unreal_Engine_Projects\Wieland1527 5.9\Wieland1527.uproject` (Unreal Engine 5.9).
Plan: `PLAN.md`, Phase 10. This file is the journal of the phase. A line marked PENDING is written and committed before its step starts; it is replaced by the outcome when the step ends.

Words used the same way throughout this file:

- "Station" is a fixed camera position on the street (S1 to S9, `REFERENCE_VIEWS.md`). "Design view" is a fixed camera position in or on the building (D1 to D5). "View" means either.
- "Level" is Unreal's word for one saved scene file. The "top level" `L_Site_M4` loads the others.
- "Path-traced picture" or "ground truth" is a picture made by Unreal's Path Tracer, the slow renderer that follows light physically; it is the plan's offline tier. "Real-time picture" is a picture made by the renderer the walk-through uses (Lumen, Unreal's real-time method for bounced light); it is the plan's real-time tier.
- "Console variable" is a named engine setting that can be changed while the editor runs; it goes back to the project's value when the editor restarts.
- "Sheet" is one picture file that lays several panels side by side for one view.
- "Tolerance" is a row of the table "Tolerances proposed" in `REFERENCE_VIEWS.md`.
- "Could not be checked" means the evidence the tolerance names does not exist; the missing evidence is named each time.

## How to resume

1. Read the journal below from the bottom up. The last line that is not PENDING is the last step known to be finished. A PENDING line means the step was started and its result is unknown: look at what exists (files in `review\phase10\`, `REVIEW.md`, and the editor's unsaved packages) before repeating anything.
2. Editor: top level `/Game/Wieland1529/L_Site_M4` (12 levels). Never save `/Game/Wieland/R15_Landscape/L_R15_Production`, never use "Save All", save named assets only, never edit an asset Datasmith created.
3. Calls go through `tools\ue_call.py` (`python -B tools\ue_call.py py <script file> [timeout seconds]`). A script returns the value of its last expression. Scripts of this phase are in `review\phase10\scripts\`.
4. `r.RayTracing.Nanite.Mode` stays 0 except during one path-traced picture; before a path-traced picture the level settles five minutes, one picture at a time, and the variable is read back as 0 afterwards. The ground truth of the twelve views is that of Phase 12 (`review\phase12\ground_truth\`); Phase 9 changed two real-time settings only, so it still stands.
5. Before any heavy step read free commit memory; under 30 GB, unload and wait.
6. This phase changes nothing in the scene unless a journal line says so. The review itself is `REVIEW.md`; the owner's marks go into `review\phase10\owner_marks.csv`.
7. Commit by explicit path on branch `claude/1529-wieland-scene-plan-e84a03`. Do not push.

## Checks made before work (2026-11-13 07:14 to 07:22 Central)

| Check | Reading |
|---|---|
| Editor | process 25884, started 00:24:26, agent server answers, holds 25.3 GB of commit |
| Open world | `/Game/Wieland1529/L_Site_M4` |
| Unsaved packages | five, as Phase 9 left them (J11 of Phase 9): `L_Site_M4` and the four unit levels `L_W1529_*`; they hold no work |
| `r.RayTracing.Nanite.Mode` | 0 |
| `r.Material.UseShaderCompilationParameters` | 0 |
| Free commit memory | 26.7 of 79.1 GB (under the 30 GB line); free physical 6.0 GB |
| Working copy | branch `claude/1529-wieland-scene-plan-e84a03`, last commit `8a7bf1bc` (Phase 9 done) |
| `phase10_results.md` | did not exist: this is a fresh start, not a resume |
| Owner photographs | none; no site visit has been made |
| Advisor tool | none in this session; the closing checks are done by hand and noted for the owner |

## What this phase can and cannot do without the owner

The plan's Phase 10 compares the owner's photographs with renders. There are no photographs and there has been no site visit. So:

- Every tolerance that rests on a photograph, a tape or a grey card is entered as "could not be checked", with the missing evidence named.
- Every tolerance that can be measured in the scene against the survey, the laser scan of 2022, the county data, the Revit model or the NOAA calculator is measured, or taken from the earlier phase that measured the scene in its present state.
- Each station's sheet carries a "PLACEHOLDER: no photograph" panel where the photograph would be.
- Street imagery is not opened, saved, traced or sampled. Looking at it beside the summer pictures (step 10.5) is the owner's step.
- The owner's marks (step 10.8) and the fixes that follow them (step 10.9) wait on the owner. A file for the marks is prepared.

## Journal

| No. | Time (Central) | Step | Outcome |
|---|---|---|---|
| J1 | 07:22 | Handed over by Phase 9 as the first thing to do: close and reopen the editor, then render the real-time pictures again and compare them with the ground truth (Phase 9 found every interior view brighter than at 02:10 with the scene unchanged). The editor is ended without saving (the five unsaved levels hold no work) and started again at once. | PENDING |
