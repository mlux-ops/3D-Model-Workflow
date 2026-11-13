# Phase 11 results: packaging and delivery

Status: PAUSED by the owner at 08:48 on 2026-11-13 for the 5-hour usage limit, during J1 (final stills; PENDING since 08:36). The agent was stopped mid-step; a path-traced still may have been rendering in the editor. Resumes automatically at 10:15. On resuming: wait until the editor's agent server answers (a render may still be finishing), check which of the twelve stills exist in full, render only the missing ones with r.RayTracing.Nanite.Mode 0, then continue.

Earlier status:  STARTED 2026-11-13 08:28 Central. Unattended run; the owner is away. Nothing is pushed.

Project: `D:\Unreal_Engine_Projects\Wieland1527 5.9\Wieland1527.uproject` (Unreal Engine 5.9).
Plan: `PLAN.md`, Phase 11. This file is the journal of the phase. A line marked PENDING is written and committed before its step starts; it is replaced by the outcome when the step ends.

Words used the same way throughout this file:

- "Station" is a fixed camera position on the street (S1 to S9, `REFERENCE_VIEWS.md`). "Design view" is a fixed camera position in or on the building (D1 to D5). "View" means either.
- "Level" is Unreal's word for one saved scene file. The "top level" `L_Site_M4` loads the others.
- "Still" is one finished picture of a view. "Path-traced" means made by Unreal's Path Tracer, the slow renderer that follows light physically (the plan's offline tier). "Real-time" means made by the renderer the walk-through uses (Lumen, Unreal's real-time method for bounced light).
- "Console variable" is a named engine setting that can be changed while the editor runs; it goes back to the project's value when the editor restarts.
- "Level sequence" is Unreal's word for a saved camera move with a time line, the thing an animation is rendered from. "Move" means one of the two 30-second camera moves of the animation.
- "Movie Render Queue" and "Movie Render Graph" are the engine's two tools that render a level sequence or a view to picture files.
- "Packaged build" is the scene turned into a program that runs without the Unreal editor. "Cooking" is the step of packaging that converts every asset into the form the program reads.
- "Frame time" is the time the computer needs to draw one picture, in milliseconds (ms); 16.67 ms is 60 pictures a second.
- "Delivery folder" is `docs\unreal\1529_wieland\delivery\` in the plan's working copy. Its large files are kept on disk and are not committed.

## How to resume

1. Read the journal below from the bottom up. The last line that is not PENDING is the last step known to be finished. A PENDING line means the step was started and its result is unknown: look at what exists (files in `delivery\` and `review\phase11\`, new assets under `/Game/Wieland1529/Delivery/`, and the editor's unsaved packages) before repeating anything.
2. Editor: top level `/Game/Wieland1529/L_Site_M4` (12 levels). After a restart the editor opens `L_R15_Production` and may show a window "Restore Packages" that blocks every tool until it is closed without restoring. Never save `/Game/Wieland/R15_Landscape/L_R15_Production`, never use "Save All", save named assets only, never edit an asset Datasmith created.
3. Calls go through `tools\ue_call.py` (`python -B tools\ue_call.py py <script file> [timeout seconds]`). A script returns the value of its last expression. Scripts of this phase are in `review\phase11\scripts\`.
4. `r.RayTracing.Nanite.Mode` stays 0 at all times, path-traced pictures included, and is never set to 2. One picture at a time; a freshly opened level settles five minutes first.
5. Before any heavy step read free commit memory; under 30 GB, unload and wait. The memory log of this phase is `review\phase11\memory_log_phase11.csv` (started by `tools\memory_log.ps1`).
6. **Drive H: is not connected** (see the checks below). Everything the plan sends to H: goes to the delivery folder on E: instead, until the owner connects the disk.
7. The journal helper `review\phase11\scripts\journal.py` writes every time from the clock.
8. Commit by explicit path on branch `claude/1529-wieland-scene-plan-e84a03`. Do not push.

## Checks made before work (2026-11-13 08:28 to 08:35 Central)

| Check | Reading |
|---|---|
| Editor | process 16168, started 08:09:41, agent server answers, holds 17.8 GB of commit |
| Open world | `/Game/Wieland1529/L_Site_M4`, 12 levels, 3,059 objects |
| Unsaved packages | one, `L_Site_M4`, as Phase 10 left it (a temporary camera placed and removed; no content change) |
| `r.RayTracing.Nanite.Mode` | 0 |
| `r.Material.UseShaderCompilationParameters` | 0 |
| Free commit memory | 35.4 of 79.1 GB (over the 30 GB line); free physical 7.1 GB |
| Working copy | branch `claude/1529-wieland-scene-plan-e84a03`, last commit `591595fc` (Phase 10 closed) |
| `phase11_results.md` | did not exist: this is a fresh start, not a resume |
| **Drive H:** | **Not connected.** Windows lists no volume H:; the external disk ("Seagate Expansion Desk") is known to Windows but reported as not present. The plan writes render frames, the packaged build and the project archive to H: |
| Free disk space | C: 16.3 GB, D: 33.3 GB, E: 44.1 GB |
| Project size | `Content` 7.09 GB in 8,433 files; `Config` under 1 MB; `Saved` 2.39 GB, `Intermediate` 5.15 GB, `Backups` 1.03 GB, `ImportStaging` 1.74 GB, `DerivedDataCache` 0.17 GB. The plan's estimate of "about 30 GB" for the archive is far too high: content, settings and project file are about 7.1 GB |
| Encoder | `ffmpeg` 9.0.2 is installed (`C:\Users\cowey\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_...\bin\ffmpeg.exe`); nothing needs installing |
| Google Drive connection | **None in this session.** No Drive tool is offered to the session and no Drive command-line program is installed. The Google Drive desktop program is running on the machine, but a copy into its folder is not proof of upload under `AGENTS.md`, so nothing is copied there |
| Advisor tool | none in this session; the closing check is done by hand and noted for the owner |
| Project start level and game start level | both still name the earlier production level `L_R15_Production` (`Config\DefaultEngine.ini`); not changed |

## Decisions this session took in the owner's absence

- **H: is missing, so the delivery folder on E: takes its place.** The standing approval names H:; the rule "Storage limits are lifted" says no storage limit applies any more, and the delivery folder is inside the plan's working copy, so no file is written outside the repository and the project. What the plan sends to H: (stills, animation frames, packaged build, project archive) is written to `docs\unreal\1529_wieland\delivery\`. Copying it to H: when the disk is back is listed for the owner.
- **Station S7 cannot be rendered** (Phase 2: there is no alley; the point lies inside the rear neighbour's lot). The delivery list of step 11.1 therefore has 12 stills that can exist, not 13. The rear of the building is shown by design view D5.
- **No finish alternative still is rendered**, because the owner has not asked to compare any alternative and has not named them.

## Journal

| No. | Time (Central) | Step | Outcome |
|---|---|---|---|
| J1 | 08:36 | Step 11.1, the final stills. Twelve path-traced stills at 3,840 by 2,160 pixels in the summer afternoon condition (S1 to S6, S9, D1 to D5; S7 cannot exist), 1,024 samples each, with `r.RayTracing.Nanite.Mode` 0 (the Path Tracer traces each mesh's simplified fallback copy), through Movie Render Graph's quick render as in Phases 8 and 12, with the same temporary camera, exposure and settings as the Phase 12 ground truth. The level has been open since 08:12 and has settled. One still first (S1), checked by eye and compared with the Phase 12 picture of S1 made with mode 2; then the rest, one at a time, each waiting for 30 GB of free commit memory, with the memory log running. Output: `delivery\stills\`. Nothing is saved in the project. | PENDING |
