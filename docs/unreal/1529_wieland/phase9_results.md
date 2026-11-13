# Phase 9 results: optimization

Status: STARTED 2026-11-13 03:22 Central. Unattended run; the owner is away. Nothing is pushed.

Project: `D:\Unreal_Engine_Projects\Wieland1527 5.9\Wieland1527.uproject` (Unreal Engine 5.9).
Plan: `PLAN.md`, Phase 9. This file is the journal of the phase. A line marked PENDING is written and committed before its step starts; it is replaced by the outcome when the step ends.

Words used the same way throughout this file:

- "Level" is Unreal's word for one saved scene file. The "top level" `L_Site_M4` loads the others.
- "Frame time" is the time the computer needs to draw one picture, in milliseconds (ms). 16.67 ms is 60 pictures a second.
- "Graphics-card time" is the part of the frame time the graphics card works. "Render thread" is the part of the processor's work that prepares each picture for the graphics card. When the render thread takes longer than the graphics card, the processor is the brake, not the card.
- "Draw call" is one order from the processor to the graphics card to draw one object once. Many thousands of them in a frame keep the render thread busy.
- "Console variable" is a named engine setting that can be changed while the editor runs; it goes back to the project's value when the editor restarts.
- "Screen percentage" is the share of the picture's width and height that is really computed before the engine's upscaler enlarges it to the full picture. The plan's real-time tier computes 67 percent of 2560 by 1440, which is 1715 by 965 pixels.
- "Nanite" is Unreal's method for drawing very detailed solid geometry at a nearly fixed cost. "Lumen" is its real-time method for bounced light and reflections. "Virtual Shadow Maps" is its real-time shadow method. "MegaLights" is its method for many shadow-casting lamps at a fixed cost.
- "Path", "hold", "station", "view" and "profile" mean what `PLAN.md` says under "The fixed camera path and the profile": a path is a recorded camera walk, a hold is the camera standing still at a station.
- "Fixture light" is one of the 571 lamps that came with the Revit model (314 lit since Phase 8).

## How to resume

1. Read the journal below from the bottom up. The last line that is not PENDING is the last step known to be finished. A PENDING line means the step was started and its result is unknown: look at what exists (files in `profiles\2026-11-13_M7\` and `review\phase9\`, the change log `profiles\2026-11-13_M7\change_log.csv`, and the editor's unsaved packages) before repeating anything.
2. Editor: top level `/Game/Wieland1529/L_Site_M4` (12 levels). Never save `/Game/Wieland/R15_Landscape/L_R15_Production`, never use "Save All", save named assets only, never edit an asset Datasmith created.
3. Calls go through `tools\ue_call.py` (`python -B tools\ue_call.py py <script file> [timeout seconds]`). A script returns the value of its last expression. Scripts of this phase are in `review\phase9\scripts\`; the editor-side module of this phase is `tools\wieland_optimize.py`.
4. `r.RayTracing.Nanite.Mode` stays 0. This phase renders nothing with the Path Tracer; the ground truth is that of Phase 12 (`review\phase12\ground_truth\`).
5. Before any heavy step read free commit memory; under 30 GB, unload and wait. The memory log of this phase is `profiles\2026-11-13_M7\memory_log_phase9.csv` (started by `tools\memory_log.ps1`).
6. The soak (step 9.11) runs inside the editor on its own ticks and writes `profiles\2026-11-13_M7\soak\soak_log.jsonl`, one line per walk. If that file exists and has fewer than 120 lines while no soak is active (`wieland_profile.status()`), the soak was interrupted: keep the file, and start a new soak into a new file name beside it.
7. Commit by explicit path on branch `claude/1529-wieland-scene-plan-e84a03`. Do not push.

## Checks made before work (2026-11-13 03:22 Central)

| Check | Reading |
|---|---|
| Editor | process 25884, started 00:24:26, agent server answers, holds 21.8 GB of commit |
| Open world | `/Game/Wieland1529/L_Site_M4` with its 12 levels |
| Unsaved packages | none |
| `r.RayTracing.Nanite.Mode` | 0 (`r.RayTracing.Nanite.MaxAppendInstances` 10,000) |
| `r.Material.UseShaderCompilationParameters` | 0 |
| Level viewport | 2,038 by 1,198 pixels; the monitor is 2,560 by 1,440, so the editor's viewport cannot show the plan's full 2,560 by 1,440 picture |
| Free commit memory | 35.4 of 79.1 GB; free physical 10.4 GB |
| Working copy | branch `claude/1529-wieland-scene-plan-e84a03`, last commit `6c75f29f` (Phase 12 done) |
| `phase9_results.md` | did not exist: this is a fresh start, not a resume |
| Advisor tool | none in this session; the closing checks are done by hand and noted for the owner |

## How every measurement of this phase is taken

Stated once here; each journal line names only what differs.

- Level `L_Site_M4` with the Phase 8 summer-afternoon lighting and the Phase 12 materials in the state "Phase 12 active".
- Named quality Epic, view mode Lit, Game View on (the editor's helper symbols hidden), frame limit lifted (`t.MaxFPS 1000`), texture pool as the journal line says.
- Editor viewport 2,038 by 1,198 pixels. **"Tier conditions"** means screen percentage 82 in this viewport, which computes 1,671 by 982 pixels: the same number of computed pixels (1.64 million) as the plan's 67 percent of 2,560 by 1,440 (1.65 million). The finished picture is then 2.44 million pixels, not 3.69 million, so the two passes that work on the finished picture (upscaling and post-processing) are measured about one third too low; their figures are also given multiplied by 1.51, marked "scaled".
- **"M6 conditions"** means screen percentage 100 in the same viewport, as profile M6 was recorded.
- Paths and holds are those of profiles M4 and M6 (`tools\phase6_profile_m4.py`): the exterior path of 60 seconds, the triplex path of 30 seconds, the penthouse path of 20 seconds indoors and 10 seconds on the roof deck, and holds of 10 seconds at S1, S2, S6, D2 and D5. While a path is recorded only the unit levels that the streaming boxes would load at that place are shown.
- The editor is asked to the front every 10 seconds; the share of a recording in which it really was in front is in each analysis file.

## Journal

- J1 (step 9.1) PENDING 03:40: read profile M6 against the budget. Part (a), from the files already on disk and without touching the editor: the frame tables of M6 are broken down by kind of draw call and by where the render thread waits, to find what holds the frame. Part (b), a new baseline "B0" of the scene as it stands now (after the material rebuild), because M6 was recorded before Phase 12, at screen percentage 100, and without per-pass times: the four paths and five holds in tier conditions, and the graphics card's per-pass times at S1, S2, S6, D2 and D5 with the editor's GPU profiler tool (three single frames each), reduced to the rows of the budget table with `tools\reduce_gpu_passes.py`. Nothing is changed or saved. Output `profiles\2026-11-13_M7\B0\`.
