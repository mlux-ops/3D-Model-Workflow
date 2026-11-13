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

- J1 (step 9.1) DONE 03:37. Nothing was changed or saved; every setting was put back.
  **Part (a), profile M6 re-read** (`review\phase9\scripts\csv_breakdown.py` on the frame tables in `profiles\2026-11-12_M6\csv\`): on the exterior path the processor issues about 28,770 draw calls per frame, of which about 26,740 are shadow-map draws for the fixture lights (about 85 for each of 315 lights), and only 59 are the visible surfaces. The render thread spends 12.7 ms of each frame waiting on that shadow work, and the render thread's time equals the frame time (29.5 ms) while the graphics card needs 13.7 to 19 ms. So outdoors the frame is held by the processor preparing shadow maps for lamps, not by the graphics card. Indoors in the penthouse (85 lights in view, 4,500 shadow draws) the graphics card is the brake (about 21 ms).
  **Part (b), baseline B0** (tier conditions; 284 fixture lights lit, all casting shadows; files in `profiles\2026-11-13_M7\B0\`):

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
  **Graphics-card time by pass** (median of three single frames per station, `profiles\2026-11-13_M7\B0\gpu_passes_B0.summary.json`; the card works two queues at once, so the rows add up to more than its wall-clock time):

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

  **Ranking of the overruns, and what causes each** (from the pass trees, `review\phase9\scripts\tree_dump.py`): (1) direct light and (2) shadows are one cause: each of the 284 lit fixture lights is lit and shadowed on its own, and the engine keeps 1,403 shadow maps for them (a lamp that shines all round needs six). That costs the graphics card 5.6 ms of per-lamp lighting at S1 and about 4 to 7 ms of shadow-map work, and it costs the processor the 26,700 shadow draw calls of part (a). (3) Lumen global illumination: its rays light every hit point in full ("hit lighting", saved on the outdoor exposure volume since Phase 8), 2.1 ms at S1 and 5.7 ms at D2. (4) Translucent surfaces at S1 (the glass of the front). (5) Upscaling at D2 (a thin-geometry detection step of 0.8 ms). Geometry, Lumen scene, reflections, sky, wind and post-processing are inside their budgets, so steps 9.2, 9.5 and 9.6 are confirmations rather than savings. The work therefore starts with the fixture lights (step 9.7), then shadows (9.3), Lumen (9.4), and the rest in the plan's order.
- J2 (step 9.7) DONE 03:56. (The times first written for J1 and J2, 03:58 and 04:00, were mistyped; J1 ended at 03:37.) **Change 1: MegaLights is on for the fixture lights.** MegaLights is the engine's way of lighting and shadowing many lamps together by tracing rays, instead of keeping shadow maps for each lamp.
  **One station first, by console variable, nothing saved** (S1, then D2; `profiles\2026-11-13_M7\T_mega\`): at S1 direct light fell from 7.91 to 1.17 ms and shadows from 5.43 to 3.09 ms, the graphics card from 21.2 to 10.0 ms; at D2 direct light 4.97 to 1.49 ms, shadows 7.02 to 6.12 ms, graphics card 19.4 to 14.6 ms. The engine now keeps 17 shadow maps (the sun's) instead of 1,403.
  **Variant tried and dropped** (`T_mega_vsm\`): MegaLights with the lamps' shadows still taken from shadow maps (`r.MegaLights.DefaultShadowMethod 1`) is slower (graphics card 12.9 ms at S1, 15.3 ms at D2) and the picture reads the same, so the ray-traced shadows stay.
  **Picture check.** S1 against the Phase 12 ground truth: mean brightness +1.2 percent, no region over 2 percent of the frame off by a stop: passes (Phase 12's own real-time picture read +1.1 percent against this one). D2, same moment, MegaLights on against off, the lit part of the room: mean -0.3 percent, no 40-pixel block off by a stop (`review\phase9\sheets\j2_megalights_D2_crop.jpg`, `j2_megalights_S1_full.jpg`). The lamps' shadow edges are a little softer, which is in the plan's list of what the real-time tier gives up.
  **Finding about view D2, not caused by this change:** D2 now reads +12.6 to +14.3 percent against the ground truth with MegaLights on, off, and with all lamps hidden alike (`review\phase9\compare\T_mega`, `T_mega0`, `T_mega_vsm`, `T_nolamps`), while Phase 12's real-time picture taken at 02:08 read +2.4 percent. The unchanged scene itself reads brighter at D2 than it did two hours ago; Phase 8 noted that the clouds drift and change the sky's share of the light from minute to minute. From here on every picture check is therefore made twice: against the ground truth, and against a picture of the unchanged state taken at the same moment. D2 is rendered again at the end of the phase to see whether the reading returns.
  **How it is stored:** the setting "MegaLights" on the unbound post-process volume `LGT_Exposure_Outdoors` of `/Game/Wieland1529/Lighting/L_Light_SummerAfternoon` (a post-process volume is a box, here without bounds, that carries picture settings), set with `tools\wieland_optimize.py`; the project-wide console variable `r.MegaLights.EnableForProject` stays 0, so no settings file changes. The lighting level was saved by name. Still marked unsaved, with no content change and not saved: the four unit levels `L_W1529_*` (shown and hidden for the recordings) and `L_Site_M4` (the temporary camera of the pictures).
  **State C1** (MegaLights on, tier conditions, editor in front for the whole of every recording; `profiles\2026-11-13_M7\C1\`), before to after:

  | Recording | Frame mean (ms) | 95th percentile | Worst | Graphics card mean | Video memory peak (MB) |
  |---|---|---|---|---|---|
  | Exterior path, 60 s | 29.78 to 11.47 | 32.09 to 13.11 | 38.76 to 19.53 | 17.35 to 10.06 | 10,229 to 8,746 |
  | Triplex path, 30 s | 17.08 to 12.89 | 26.05 to 19.02 | 41.09 to 24.52 | 15.69 to 11.52 | 8,670 to 8,768 |
  | Penthouse path indoors, 20 s | 25.91 to 18.15 | 29.29 to 21.89 | 40.09 to 26.54 | 24.52 to 16.78 | 8,429 to 8,768 |
  | Penthouse path roof deck, 10 s | 23.38 to 10.55 | 32.73 to 12.20 | 39.96 to 15.30 | 20.10 to 9.18 | 11,619 to 8,768 |
  | Hold S1 | 27.45 to 11.68 | 29.07 to 13.23 | 36.55 to 18.95 | 21.24 to 10.23 | 8,679 to 8,753 |
  | Hold S2 | 29.92 to 11.65 | 31.82 to 12.91 | 35.48 to 22.33 | 16.32 to 10.23 | 9,023 to 8,762 |
  | Hold S6 | 30.96 to 10.95 | 32.90 to 12.18 | 37.23 to 21.48 | 15.57 to 9.53 | 8,906 to 8,762 |
  | Hold D5 | 14.34 to 11.88 | 15.48 to 13.07 | 21.27 to 16.61 | 13.00 to 10.49 | 7,923 to 8,704 |
  | Hold D2 | 20.79 to 16.09 | 22.14 to 17.22 | 23.56 to 22.94 | 19.38 to 14.80 | 8,090 to 8,768 |

  No frame of any recording is over 33.3 ms any more. The exterior path, the roof deck and the holds S1, S2, S6 and D5 are now inside all three limits. Still outside: the triplex path (95th percentile 19.02 ms; 425 of 2,329 frames over 16.67 ms) and the penthouse indoors (95th percentile 21.89 ms, graphics card 16.78 ms; hold D2 17.22 ms and 14.80 ms). Per pass with MegaLights on (`T_mega_volume\`), S1 / D2 in ms: shadows 3.10 / 5.88 (budget 2.0), Lumen global illumination 3.23 / 6.34 (2.5), reflections 0.94 / 2.13 (1.5), direct light 1.16 / 1.50 (1.0), translucent 0.70 / 0.85 (0.8), upscaling 1.07 / 1.49. What remains is the sun's shadow map and Lumen indoors.
  The change log is `profiles\2026-11-13_M7\change_log.csv` (written by `review\phase9\scripts\change_log.py`).
- J3 (step 9.3) DONE 05:40 (begun 03:56 by the session before; that session ended in the middle and this one resumed at 05:15). **No shadow setting is changed, because the sun's shadow map is not where the time goes.** The Virtual Shadow Map (the engine's one large shadow map for the sun, drawn in pages and kept from frame to frame) was measured at D2 and S1 under tier conditions, one thing at a time, nothing saved (`profiles\2026-11-13_M7\T_s_*`), shadows / graphics card total in ms:

  | Trial | D2 | S1 | Reading |
  |---|---|---|---|
  | `T_s_ref` unchanged | 6.34 / 14.83 | 3.04 / 10.07 | reference |
  | `T_s_forceinv` every page redrawn every frame (`r.Shadow.Virtual.Cache.ForceInvalidateDirectional 1`) | 7.24 / 15.85 | 4.02 / 11.05 | keeping pages saves only about 1 ms |
  | `T_s_notrees` the 34 trees hidden in the editor | 5.79 / 13.95 | 2.33 / 9.12 | the wind-moved trees cost 0.6 to 0.7 ms of shadow |
  | `T_s_bias05` finer shadow resolution (`r.Shadow.Virtual.ResolutionLodBiasDirectional -0.5` instead of -1.5) | 6.24 / 15.25 | 2.97 / 10.02 | resolution is not the cost |
  | `T_s_vsmoff` Virtual Shadow Maps off | worse | worse | the older shadow maps cost more |

  The engine's own page count at D2 (`r.Shadow.Virtual.AccumulateStats`, file `Saved\Profiling\VSMStats(20261113_052042).csv` in the project): 498 pages asked for per frame, 497 kept, 478 of the pages' moving layer redrawn each frame (the trees move in the wind), no page-pool overflow, no non-Nanite mesh drawn into the shadow map in a normal frame. The pass tree at D2 showed steps that cannot take that long on their own (clearing a 12-byte buffer: 2.2 ms), which means the shadow pass was waiting for the graphics card while Lumen traced rays at the same time: the 6 ms was mostly Lumen's cost showing up under the shadow heading. The first trial of step 9.4 confirms it: with Lumen's rays lit from the surface cache indoors, shadows at D2 fall from 6.34 to 1.11 ms with no shadow setting touched. Outdoors (S1) the sun's shadow stays at about 3.0 ms against a budget of 2.0, offset by geometry, Lumen scene, reflections, sky and post-processing, which are together 3.2 ms under their budgets there. One trial of the session before, `T_vsm_bias05`, is invalid and not used: it ran at screen percentage 100 instead of 82 (see `PROJECT_MEMORY.md`); `gpu_passes.py` now always adds the tier's screen percentage.
- J3b (step 9.2) DONE 05:40. **Geometry: confirmed, nothing changed.** Geometry costs 1.05 to 1.37 ms at every station against a budget of 2.0. Census of the loaded scene (`review\phase9\scripts\census.py`, `review\phase9\census.csv`): 3,422 opaque mesh components are Nanite (the engine's system that draws dense meshes at the detail the screen needs) and 148 are not; those 148 are small Datasmith meshes (curtains, fixtures, baseboards), about 164,000 triangles in all, and making them Nanite would mean editing Datasmith's assets, which the rules forbid; their cost is too small to measure. 411 components are see-through (glass), 34 are trees. Nothing is instanced (the same mesh placed many times is 128 bicycle parts per triplex and railings of 96 to 140 parts), but Nanite already draws all of it in about 59 draws per frame, so merging the glass or instancing the repeats would save nothing that can be measured, and would mean replacing Datasmith actors. Zone 3 and Zone 4 are already stand-ins: `L_FarCity` is one mesh and `L_Surroundings` is 181 Nanite meshes. No change, so no before and after.
- J4 (step 9.4) PENDING 05:40: Lumen indoors. The two interior post-process volumes `LGT_Exposure_Interior_4th` and `LGT_Exposure_Interior_LowerTo3rd` get "hit lighting for reflections" (indirect light read from Lumen's surface cache, reflections still lit in full at the hit point) instead of the outdoor volume's full hit lighting. First trial, not saved: D2 graphics card 14.83 to 9.54 ms. Interior views D1 to D5 rendered in both states at the same moment (`review\phase9\compare\T_l_hitrefl`, `T_l_ref`, `T_ref2_D34`): the mean brightness of no view moves by more than 0.6 points (D1 -3.7 / -3.7, D2 +14.0 / +13.9, D3 +62.4 / +62.3, D4 -6.1 / -5.5, D5 -1.3 / -1.2 percent against the ground truth, changed / unchanged). **Stored at 05:38: the setting is on both interior volumes and the lighting level was saved by name.** Still PENDING: the recording of all paths in this state (state C2). Three attempts at it are not valid and are kept as evidence only (`profiles\2026-11-13_M7\C2_window_minimised\`, `C2_window_minimised_2\`, and `C2_behind_browser\`): from about 05:40 somebody was working in a web browser on this computer, the editor was minimized twice (a minimized editor draws nothing: frame times of 2.6 ms with 0.08 ms of graphics-card time) and then stood behind the browser for 74 to 88 percent of every recording. The measuring tools no longer press a key to come to the front while somebody is using keyboard or mouse (`polite_front` in `tools\phase9_profile_m7.py`). To do on resume: when the computer has been idle for two minutes (`review\phase9\scripts\desk.ps1 -WaitIdle 120`), run `review\phase9\scripts\run_c2.py` again; until then do the steps that need no timing (pictures). A fourth recording was started at 06:02, after the computer had been idle for two and a half minutes.
- J5 (step 9.8) PENDING 06:03: upscaling (the engine computes the picture at a share of the output size and then enlarges it; the plan's tier is 67 percent). Picture part done: view S1 rendered at 60, 67, 75 and 100 percent (`review\phase9\realtime\U60`, `U67`, `U75`, `U100`; all four pass against the ground truth, mean brightness +0.9, +1.2, +0.6, +0.7 percent). Fine detail kept, as a share of the 100 percent picture (`review\phase9\scripts\upscale_compare.py`, sheets `review\phase9\sheets\j8_upscale_*.jpg`): brick 91 / 92 / 92, foliage at the left 89 / 86 / 87, foliage at the right 86 / 90 / 90, railing 89 / 91 / 92 (at 60 / 67 / 75 percent). Still PENDING: the cost of each on the graphics card (`gpu_passes.py` at viewport percentages 73, 82 and 92, which give the editor's viewport the pixel counts of 60, 67 and 75 percent of 2560 by 1440), which needs an idle computer.
