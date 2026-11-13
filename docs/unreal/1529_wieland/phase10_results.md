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

## Checks made before work (2026-11-13 07:14 to 07:15 Central)

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
| J1 | 07:15 | Handed over by Phase 9 as the first thing to do: close and reopen the editor, then render the real-time pictures again and compare them with the ground truth (Phase 9 found every interior view brighter than at 02:10 with the scene unchanged). The editor is ended without saving (the five unsaved levels hold no work) and started again at once. | DONE 07:40. (The time first written for this line, 07:22, and the "07:14 to 07:22" of the checks above were typed from an estimate; the clock read 07:15.) The editor (process 25884) was ended at 07:15 and started again at 07:15:27 (process 34192). **Obstacle:** for eleven minutes the editor's agent server accepted connections but ran nothing, because a window "Restore Packages" (the editor's offer to bring back automatic saves of the five unsaved levels) waited for an answer. It was closed at 07:27 without restoring anything; the levels held no work. The editor had opened the earlier production level `L_R15_Production` as its start level; `L_Site_M4` was opened instead, nothing was saved, nothing was marked unsaved. Then the twelve views were rendered in real time at 3840 by 2160 (`review\phase10
ealtime\R1\`) and compared with the Phase 12 ground truth (`review\phase10\compare\R1\compare.csv`, one sheet per view beside it). Mean brightness difference in percent, with Phase 12's reading at 02:10 and Phase 9's at 06:50 in brackets: S1 +0.1 (0.0 / +1.0), S2 +0.5 (+1.9 / +1.4), S3 -0.7 (+0.3 / -0.2), S4 +3.2 (+2.8 / +3.0), S5 -4.2 (-4.2 / -1.1), S6 -0.7 (+0.5 / +1.1), D1 -4.8 (-4.9 / -4.1), D2 +2.2 (+2.4 / +13.9): these eight pass. S9 +26.2 (+26.3 / +31.7), D3 +18.0 (+29.0 / +62.1), D4 -42.4 (-30.8 / -5.7), D5 -11.9 (-11.4 / -1.8): these four fail. D3, D4 and D5 were rendered a second time three minutes later (`R1b`): +19.5, -42.3, -11.6, so the readings repeat. **Finding:** a freshly started editor gives Phase 12's result again (8 of 12 views pass, the same four fail). The brighter interiors that Phase 9 measured (9 of 12, with D4 and D5 passing and D2 failing) were a state of that long editor session and not of the saved scene; Phase 9's count of 9 is therefore replaced by 8 in this review. The two changes of Phase 9 are stored in the lighting level and are in force in these pictures. Free commit memory was 25.8 to 29.2 GB during the step (under the 30 GB line with nothing left to unload: the fresh editor holds 17.8 to 19.8 GB and other programs about 33 GB); real-time pictures are light work and were made one first, then the rest, with the memory log running (`review\phase10\memory_log_phase10.csv`). After the step: `r.RayTracing.Nanite.Mode` 0; one package marked unsaved, `L_Site_M4` (the temporary camera of the pictures, removed again; no content change, not saved). |
| J2 | 07:41 | Step 10.1 and 10.2. There are no photographs, so no camera can be solved from one. In its place: read back each station's camera as the pictures use it (place, eye height over the ground under it, heading, lens) and compare it with the surveyed station list `review\phase2\stations.csv` and with `REFERENCE_VIEWS.md`. Read-only. | DONE 07:46. `review\phase10\scripts\stations_now.py` read the seven cameras and the highest visible surface under each (the ground of `L_SiteWorks`); `stations_table.py` wrote `review\phase10\stations_check.csv`. Place in plan against the surveyed list: 0.0 cm at all seven (tolerance 10 cm). Heading against the list: 0.00 degree at all seven (tolerance 0.5). Eye height over the present ground, target 160 cm: S1 163.0, S2 159.5, S3 160.8, S4 156.4, S5 157.6, S6 164.8, S9 157.3; largest difference 4.8 cm (tolerance 5 cm). The differences exist because the heights were set on the Phase 4 ground and Phase 7 laid new pavement over it. These numbers check the cameras against the list, not against reality: the tolerance's own evidence (the station taped on site, the lens read from a photograph) does not exist, so the row is "could not be checked" for reality. **Two differences from the table in `REFERENCE_VIEWS.md`, both since Phase 4:** every station camera is tilted up 8 degrees (the table says up 12 at S1, up 10 at S2, S3 and S9, level at S4, S5 and S6) and every one uses the 24 mm lens (the table says 35 mm at S2 and S3, 50 mm at S4 and S5, 28 mm at S6). The table itself says the render takes the photograph's own lens and aim once a photograph exists, so nothing is changed now; it is listed for the owner. Step 10.2 (lay each render over its photograph): cannot be done, no photograph; the sheets of J5 carry the placeholder panel. |
| J3 | 07:47 | Station S8, the plan view: one real-time picture straight down over the lot centre, 120 m by 120 m, true north up, parallel projection (no perspective), with a temporary camera that is removed again. One picture first, checked by eye. No aerial photograph is laid beside it in the repository (the county aerial is kept outside the repository and is used for positions only). | PENDING |
