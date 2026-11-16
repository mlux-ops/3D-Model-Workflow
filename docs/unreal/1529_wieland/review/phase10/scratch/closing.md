
## Acceptance

The four acceptance lines of the plan's Phase 10, each with its number.

| Acceptance line | Number | Met? |
|---|---|---|
| Every exterior station S1 to S9 has a side-by-side sheet and a score against every tolerance that applies | 9 of 9 stations have a sheet in `review\phase10\sheets\`; 94 scores in `review\phase10\station_scores.csv` (12 at each of the seven street stations, 1 at S7, 9 at S8). The photograph panel of every street station is "PLACEHOLDER: no photograph" | Met for the sheets and scores. **Workaround** for the photograph side: there is no photograph and no site visit, so each sheet lays the path-traced picture, the real-time picture and their difference beside a placeholder panel |
| Every "could not be checked" entry names the missing evidence | Tolerance table: 9 of 9 such rows name it. Station scores: 52 of 52. Design-view scores: 10 of 10. Entries without missing evidence: 0 | Met |
| No tolerance is reported as met without a measurement | 6 tolerances pass, each with its number and what it was measured against (building on its lot 0.1 to 0.3 mm; lot in the world 0.000 m; true north 0.03 degree between two methods; tree height 34 of 34 at the scan's height; transfer from Revit 0.1 to 0.4 mm; sun 0.05 degree). 3 pass in part and fail in part, 1 fails, 9 could not be checked. Rows marked "pass" without a number: 0 | Met |
| The owner has marked every failure | 0 of 9 failures marked | **Not met; waits on the owner.** Workaround: the nine failures F1 to F9 are in `review\phase10\owner_marks.csv`, each with cause, proposed fix and the phase that owns the fix, and an empty column for "fix" or "accept". Step 10.9 (fixes and repeat) follows the marks and was not done |

The plan's steps, for completeness: 10.1 no camera could be solved from a photograph (none exists); the station cameras were read back against the surveyed list instead (J2). 10.2 both tiers exist for the seven street stations and for S8; "at the photograph's size" has no meaning yet. 10.3 sheets made, placeholder panel in place of the photograph and difference panel in place of the edge overlay. 10.4 scored (J4, J5). 10.5 summer pictures exist; the owner's look at street imagery beside them is the owner's. 10.6 design views scored against the ground truth; against Revit views could not be checked (none exported). 10.7 `REVIEW.md`. 10.8 and 10.9 wait on the owner.

Real-time against path-traced, the one row measured by pictures: 8 of 12 views pass after a fresh start of the editor (S1 +0.1, S2 +0.5, S3 -0.7, S4 +3.2, S5 -4.2, S6 -0.7, D1 -4.8, D2 +2.2 percent); S9 +26.2, D3 +18.0, D4 -42.4 and D5 -11.9 percent fail; the plan picture S8 fails at +38.5 percent.

## What was saved or changed in the project

**Nothing.** This phase saved no asset and no level in `D:\Unreal_Engine_Projects\Wieland1527 5.9\` and changed no setting file. Every measurement was read-only; every picture was made with a temporary camera that was removed again.

- The editor was closed and started again three times during the phase: once on purpose (J1, 07:15), once by the graphics-card crash of 08:01 (J7), and once by the watcher after that crash (08:09). Each time it was closed without saving; the levels marked unsaved held no work.
- State at the end: the editor is open (process 16168) on `/Game/Wieland1529/L_Site_M4`; one package is marked unsaved, `L_Site_M4`, from the temporary camera of the S8 picture (placed and removed; no content change). When the editor is closed, the answer is "do not save".
- `r.RayTracing.Nanite.Mode` reads 0. It is stored in no configuration file, so the editor always starts with 0.
- `L_R15_Production` was never saved; "Save All" was never used; no asset made by Datasmith was edited; Revit, Windows, drivers and the graphics card's settings were not touched; nothing was downloaded; nothing was pushed.
- Outside the project and the repository, one file was written: `E:\Wieland1529_site_data\phase10\S8_plan_beside_aerial.jpg` (the county's aerial photograph beside the plan picture, for looking at only).
- Crash record left by the engine at 08:01: `D:\Unreal_Engine_Projects\Wieland1527 5.9\Saved\Crashes\UECC-Windows-39A0AFB345D4B496FD524A929669FE9F_0001\`. The crash reporter's window was left open and nothing was sent.
- In the plan's working copy two tools were changed so that mode 2 can no longer be set by default: `tools\wieland_truth.py` and `review\phase10\scripts\s8_pt.py`.

## For the owner

1. **Mark the nine failures.** Open `review\phase10\owner_marks.csv` (or the table "Failures: cause and proposed fix" in `REVIEW.md`) and write "fix" or "accept" for F1 to F9. The fixes are then made by the phase named in each row and only the affected views are rendered and scored again (step 10.9).
2. **The site visit and the photographs** are still the largest gap: 9 of 19 tolerances could not be checked for want of them (photograph overlay, camera station, shadow edges, material colour, sidewalk brightness, trunk position, trunk diameter, tree species, street furniture). The shot list is in `REFERENCE_VIEWS.md`. Decision 5 of `OPEN_DECISIONS.md` (one visit now, or also one in summer) is open.
3. **Your look at street imagery** (step 10.5): put the August street imagery in a browser beside the summer pictures on the sheets `S1_sheet.jpg` to `S6_sheet.jpg` and `S9_sheet.jpg`. These sessions did not open, save, trace or sample street imagery.
4. **Neighbours' heights fail (F1).** Within 40 m of the lot 3 of 19 neighbouring buildings are within 0.3 m of the 2022 laser scan; number 1533 stands 1.10 m too high, number 1525 1.02 m too low, the rear building 1.30 m too low. Phase 7 kept the earlier detailed model of the neighbours as it was modelled (decision 4 of `OPEN_DECISIONS.md` is about that model). The plain blocks with the laser heights are still in the project as the hidden option.
5. **The roadway is 13.1 cm too low (F3).** Phase 7 made the kerb by lowering the roadway under the laser ground. A kerb height taped on site would settle it.
6. **Four views and the plan picture do not match between the two renderers (F4 to F7, F9).** At S9 it is not known which picture is right (sky mirrored in the neighbours' glass, or not) without a photograph.
7. **Phase 9's count is corrected.** Phase 9 reported 9 of 12 views passing. After a fresh start of the editor the saved scene gives 8 of 12, the same as Phase 12. Phase 9's brighter interiors were a state of that long editor session.
8. **Nanite ray tracing mode 2 is switched off for good.** It hung the graphics card a third time at 08:01 during this phase. Path-traced pictures from now on trace the meshes' simplified fallback copies: in the S8 plan picture the trees are drawn as coarse triangles. The twelve path-traced pictures of Phase 12 were made with mode 2 before the rule and were not made again; if you want all path-traced pictures made under the same rule, that is twelve pictures, one at a time with a five-minute settle each, at no cost (the S8 picture itself took 56 seconds).
9. **Station cameras differ from the table in `REFERENCE_VIEWS.md`:** all are tilted up 8 degrees and use the 24 mm lens. Nothing was changed, because the table says the photograph's own lens and aim are taken once a photograph exists. Say so if you want the table's lenses used meanwhile.
10. **Decision 7** (the survey's frontage of 50.18 ft or the record width of 49.50 ft) is open; the building passes against the record width.
11. **Design views against Revit** could not be checked: no view was exported from Revit at the five cameras, and these sessions do not open Revit. Five exported views (D1 to D5 in `REFERENCE_VIEWS.md`) would close it.
12. **The plan picture against the county's aerial photograph** has no number, because nothing may be traced from the aerial photograph in these sessions. Look at `E:\Wieland1529_site_data\phase10\S8_plan_beside_aerial.jpg`, or give leave to measure on the aerial photograph.
13. Still waiting on your decisions and unchanged by this phase: keep-or-rebuild per material, the names of the finish alternatives, the furniture (labelled stand-ins), the far city behind the roof deck (a stand-in).
14. When you close the editor it will ask about one unsaved level, `L_Site_M4`: answer "do not save". When the editor starts after a crash it shows a window "Restore Packages" and runs nothing until that window is closed; it was closed twice in this phase without restoring anything. The editor also opens the earlier production level `L_R15_Production` as its start level; setting `L_Site_M4` as the start level would be a change to a project setting file and was not made.
15. The crash reporter's window from 08:01 is still open on the desktop; nothing was sent. Close it or send it as you wish.
16. The memory log of Phase 8 (process 30032) is still running and keeps `profiles\2026-11-12_M6\memory_log_phase8.csv` showing as changed in the working copy; it ends by itself and was left alone.
17. No advisor tool exists in these sessions; the closing check of the changed files against the scope was done by hand.
18. A measurement of the real-time tier at the true picture size of 2,560 by 1,440 is still open from Phase 9; it needs a packaged build (Phase 11) or a larger monitor.

## Files written by this phase

All under `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\` unless a full path is given.

- `PROJECT_MEMORY.md` (section "Phase 10: reality-match review", and the outcome added to the supervisor's entry "Nanite ray-tracing crash, third occurrence").
- `docs\unreal\1529_wieland\phase10_results.md` (this file).
- `docs\unreal\1529_wieland\REVIEW.md` (the review).
- `docs\unreal\1529_wieland\tools\wieland_truth.py` (changed: the Path Tracer's default is mode 0).
- `docs\unreal\1529_wieland\review\phase10\tolerances.csv`, `station_scores.csv`, `design_scores.csv`, `owner_marks.csv`.
- `docs\unreal\1529_wieland\review\phase10\stations_check.csv`, `stations_now.json`, `neighbours_now.csv`, `neighbours_now.json`, `survey_ties_now.csv`, `ground_now.json`, `trees_check.csv`, `trees_now.json`, `sun_now.json`, `furniture_now.json`, `memory_log_phase10.csv`.
- `docs\unreal\1529_wieland\review\phase10\sheets\`: `S1_sheet.jpg` to `S9_sheet.jpg` and `D1_sheet.jpg` to `D5_sheet.jpg` (14 sheets).
- `docs\unreal\1529_wieland\review\phase10\compare\`: `R1\` (`compare.csv`, `compare.json` and twelve sheets), `R1b\` (the repeat of D3, D4, D5), `S8\` (`compare.csv`, `compare.json`).
- `docs\unreal\1529_wieland\review\phase10\heights\`: `job.json`, `objects.json`, `objects_siteworks.json`, `ties_job.json`, `top_today.npz`, and the folders `r15fit\`, `siteworks\`, `ties\` (ray-cast height maps; kept on disk, not committed).
- `docs\unreal\1529_wieland\review\phase10\realtime\`: `R1\` and `R1b\` (the real-time pictures of the twelve views, with `runs.jsonl` and the run logs), `S8\` (`S8_realtime.0000.png`, `S8_pathtraced.0000.png`, `S8_small.jpg`, `S8_pathtraced_small.jpg`, `pt_job.json`), `job.json`. The full-size pictures (185 MB) are kept on disk and not committed, as those of Phases 8, 9 and 12 are.
- `docs\unreal\1529_wieland\review\phase10\scripts\` (22 files): `state.py`, `journal.py`, `rt_check.py`, `rt_views.py`, `stations_now.py`, `stations_table.py`, `s8_plan.py`, `s8_pt.py`, `s8_compare.py`, `heights_now.py`, `neighbours_now.py`, `ties_now.py`, `ties_table.py`, `ground_now.py`, `trees_now.py`, `trees_table.py`, `sun_now.py`, `furniture_now.py`, `tolerances_table.py`, `station_sheets.py`, `design_sheets.py`, `owner_marks.py`.
- `docs\unreal\1529_wieland\review\phase10\scratch\` (journal texts and small previews; working files).
- Outside the repository: `E:\Wieland1529_site_data\phase10\S8_plan_beside_aerial.jpg`.
