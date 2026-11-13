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

- J1 (step 9.1) DONE 03:58. Nothing was changed or saved; every setting was put back.
  **Part (a), profile M6 re-read** (`review\phase9\scripts\csv_breakdown.py` on the frame tables in `profiles6-11-12_M6\csv\`): on the exterior path the processor issues about 28,770 draw calls per frame, of which about 26,740 are shadow-map draws for the fixture lights (about 85 for each of 315 lights), and only 59 are the visible surfaces. The render thread spends 12.7 ms of each frame waiting on that shadow work, and the render thread's time equals the frame time (29.5 ms) while the graphics card needs 13.7 to 19 ms. So outdoors the frame is held by the processor preparing shadow maps for lamps, not by the graphics card. Indoors in the penthouse (85 lights in view, 4,500 shadow draws) the graphics card is the brake (about 21 ms).
  **Part (b), baseline B0** (tier conditions; 284 fixture lights lit, all casting shadows; files in `profiles6-11-13_M7\B0\`):

  | Recording | Frame mean (ms) | 95th percentile | Worst | Frames over 33.3 ms | Graphics card mean | Render thread mean | Video memory peak (MB) |
  |---|---|---|---|---|---|---|---|
  | Exterior path, 60 s | 29.78 | 32.09 | 38.76 | 45 of 2,015 | 17.35 | 29.77 | 10,229 |
  | Triplex path, 30 s | 17.08 | 26.05 | 41.09 | 4 of 1,757 | 15.69 | 17.07 | 8,670 |
  | Penthouse path indoors, 20 s | 25.91 | 29.29 | 40.09 | 4 of 773 | 24.52 | 25.91 | 8,429 |
  | Penthouse path roof deck, 10 s | 23.38 | 32.73 | 39.96 | 15 of 428 | 20.10 | 23.37 | 11,619 |
  | Hold S1 | 27.45 | 29.07 | 36.55 | 1 | 21.24 | 27.44 | 8,679 |
  | Hold S2 | 29.92 | 31.82 | 35.48 | 3 | 16.32 | 29.91 | 9,023 |
  | Hold S6 | 30.96 | 32.90 | 37.23 | 10 | 15.57 | 30.95 | 8,906 |
  | Hold D5 | 14.34 | 15.48 | 21.27 | 0 | 13.00 | 14.34 | 7,923 |
  | Hold D2 | 20.79 | 22.15 | 23.56 | 0 | 19.38 | 20.79 | 8,090 |

  The editor was the front window for the whole of every recording (share 1.00). Against the acceptance line (95th percentile at most 16.67 ms, no frame over 33.3 ms, graphics card at most 14.5 ms): every path fails all three; only the hold at D5 is inside.
  **Graphics-card time by pass** (median of three single frames per station, `profiles6-11-13_M7\B0\gpu_passes_B0.summary.json`; the card works two queues at once, so the rows add up to more than its wall-clock time):

  | Budget row | Budget (ms) | S1 | S2 | S6 | D2 | D5 | Worst overrun |
  |---|---|---|---|---|---|---|---|
  | Shadows (Virtual Shadow Maps) | 2.0 | 5.43 | 5.63 | 5.47 | 7.02 | 3.84 | +5.02 |
  | Direct light | 1.0 | 7.91 | 3.83 | 3.41 | 4.97 | 2.87 | +6.91 |
  | Lumen global illumination | 2.5 | 4.46 | 4.12 | 3.78 | 6.77 | 3.74 | +4.27 |
  | Translucent surfaces | 0.8 | 2.12 | 0.84 | 0.66 | 1.16 | 0.21 | +1.32 |
  | Temporal upscaling (scaled by 1.51 to the full picture) | 1.2 | 1.08 (1.63) | 1.04 (1.57) | 1.13 (1.71) | 1.76 (2.66) | 1.10 (1.66) | +1.46 scaled |
  | Geometry | 2.0 | 1.37 | 1.64 | 1.46 | 1.05 | 1.18 | inside |
  | Lumen scene | 1.5 | 0.75 | 0.74 | 0.78 | 0.93 | 0.94 | inside |
  | Reflections | 1.5 | 0.51 | 0.39 | 0.36 | 1.39 | 1.29 | inside |
  | Sky, clouds, fog | 0.8 | 0.40 | 0.49 | 0.70 | 0.57 | 0.39 | inside |
  | Foliage wind | 0.4 | 0.22 | 0.22 | 0.21 | 0.21 | 0.21 | inside |
  | Post-processing (scaled) | 0.8 | 0.28 (0.42) | 0.28 (0.42) | 0.28 (0.42) | 0.26 (0.39) | 0.28 (0.42) | inside |
  | Not in the budget table | none | 0.95 | 1.06 | 1.10 | 0.54 | 0.45 | |

  **Ranking of the overruns, and what causes each** (from the pass trees, `review\phase9\scripts	ree_dump.py`): (1) direct light and (2) shadows are one cause: each of the 284 lit fixture lights is lit and shadowed on its own, and the engine keeps 1,403 shadow maps for them (a lamp that shines all round needs six). That costs the graphics card 5.6 ms of per-lamp lighting at S1 and about 4 to 7 ms of shadow-map work, and it costs the processor the 26,700 shadow draw calls of part (a). (3) Lumen global illumination: its rays light every hit point in full ("hit lighting", saved on the outdoor exposure volume since Phase 8), 2.1 ms at S1 and 5.7 ms at D2. (4) Translucent surfaces at S1 (the glass of the front). (5) Upscaling at D2 (a thin-geometry detection step of 0.8 ms). Geometry, Lumen scene, reflections, sky, wind and post-processing are inside their budgets, so steps 9.2, 9.5 and 9.6 are confirmations rather than savings. The work therefore starts with the fixture lights (step 9.7), then shadows (9.3), Lumen (9.4), and the rest in the plan's order.
- J2 (step 9.7, first part) PENDING 04:00: trial of MegaLights on the fixture lights, by console variable only, one station first (S1), then D2: per-pass times, frame time, and a look at the picture. Nothing saved.
