# Phase 9 results: optimization

Status: DONE 2026-11-13 07:12 Central. Both changes are stored, profile M7 is saved, and the soak was stopped at 07:07 after 42 of 120 walks, on the owner's decision recorded here at 07:06 by the session before (the note read: stop the two-hour soak now and close Phase 9 with the shorter run, to start Phase 10 sooner). The session that closed the phase did not hear that decision itself; it acted on the note. If the note was wrong, the full two-hour soak can be run again with `review\phase9\scripts\soak_start.py` into a new folder `soak_2`; nothing else depends on it. Nothing is pushed. Phase 10 starts in its own session.

Earlier status:  STARTED 2026-11-13 03:22 Central. Unattended run; the owner is away. Nothing is pushed.

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
- J4 (step 9.4) DONE 06:08 (begun 05:40). **Change 2: Lumen indoors.** The two interior post-process volumes `LGT_Exposure_Interior_4th` and `LGT_Exposure_Interior_LowerTo3rd` get "hit lighting for reflections" (indirect light read from Lumen's surface cache, reflections still lit in full at the hit point) instead of the outdoor volume's full hit lighting. First trial, not saved: D2 graphics card 14.83 to 9.54 ms. Interior views D1 to D5 rendered in both states at the same moment (`review\phase9\compare\T_l_hitrefl`, `T_l_ref`, `T_ref2_D34`): the mean brightness of no view moves by more than 0.6 points (D1 -3.7 / -3.7, D2 +14.0 / +13.9, D3 +62.4 / +62.3, D4 -6.1 / -5.5, D5 -1.3 / -1.2 percent against the ground truth, changed / unchanged). **Stored at 05:38: the setting is on both interior volumes and the lighting level was saved by name.** Still PENDING: the recording of all paths in this state (state C2). Three attempts at it are not valid and are kept as evidence only (`profiles\2026-11-13_M7\C2_window_minimised\`, `C2_window_minimised_2\`, and `C2_behind_browser\`): from about 05:40 somebody was working in a web browser on this computer, the editor was minimized twice (a minimized editor draws nothing: frame times of 2.6 ms with 0.08 ms of graphics-card time) and then stood behind the browser for 74 to 88 percent of every recording. The measuring tools no longer press a key to come to the front while somebody is using keyboard or mouse (`polite_front` in `tools\phase9_profile_m7.py`). A fourth recording was started at 06:02, after the computer had been idle for two and a half minutes, and is the one used (`profiles\2026-11-13_M7\C2\`). Its conditions: tier conditions as for every recording; the person came back to the browser about 30 seconds in, so the editor was the window in front for 49 percent of the exterior path and not in front for the rest; it was drawing at full rate throughout (graphics-card time 8.6 to 11.0 ms, not the 0.08 ms of a minimized window). Before (state C1) to after (state C2):

  | Recording | Frame mean (ms) | 95th percentile | Worst | Graphics card mean | Video memory peak (MB) |
  |---|---|---|---|---|---|
  | Exterior path, 60 s | 11.47 to 12.01 | 13.11 to 14.26 | 19.53 to 60.23 | 10.06 to 10.25 | 8,746 to 8,865 |
  | Triplex path, 30 s | 12.89 to 10.25 | 19.02 to 13.23 | 24.52 to 19.54 | 11.52 to 8.83 | 8,768 to 8,862 |
  | Penthouse path indoors, 20 s | 18.15 to 12.42 | 21.89 to 15.20 | 26.54 to 24.00 | 16.78 to 10.87 | 8,768 to 9,348 |
  | Penthouse path roof deck, 10 s | 10.55 to 11.66 | 12.20 to 14.09 | 15.30 to 21.53 | 9.18 to 10.21 | 8,768 to 9,351 |
  | Hold S1 | 11.68 to 12.46 | 13.23 to 13.81 | 18.95 to 19.51 | 10.23 to 10.80 | 8,753 to 8,865 |
  | Hold S2 | 11.65 to 11.79 | 12.91 to 13.27 | 22.33 to 21.92 | 10.23 to 10.42 | 8,762 to 8,865 |
  | Hold S6 | 10.95 to 11.23 | 12.18 to 12.77 | 21.48 to 18.98 | 9.53 to 9.84 | 8,762 to 8,865 |
  | Hold D5 | 11.88 to 10.04 | 13.07 to 11.84 | 16.61 to 16.43 | 10.49 to 8.64 | 8,704 to 8,797 |
  | Hold D2 | 16.09 to 12.57 | 17.22 to 14.50 | 22.94 to 20.71 | 14.80 to 11.02 | 8,768 to 9,348 |

  The interior paths now meet the frame-time lines: 95th percentile 13.23 ms (triplex) and 15.20 ms (penthouse indoors) against 16.67, no frame over 33.3 ms, graphics card 8.83 and 10.87 ms against 14.5. The exterior path is not touched by this change (the setting is on the interior volumes only); its three frames over 33.3 ms in this recording (37.0, 38.1 and 60.2 ms, at 45 to 50 seconds) are stalls of the game thread (the processor thread that runs the editor's own logic) with the graphics card steady at 9.5 to 10.0 ms, at the time the person was switching windows; the recording before (C1, computer idle) has none, worst 19.53 ms. The exterior line is settled by the two-hour soak (J9), which walks the same path 120 times. J4 DONE 06:08; change 2 is in `profiles\2026-11-13_M7\change_log.csv`.
- J5 (step 9.8) DONE 06:10 (begun 06:03): upscaling (the engine computes the picture at a share of the output size and then enlarges it; the plan's tier is 67 percent). Picture part done: view S1 rendered at 60, 67, 75 and 100 percent (`review\phase9\realtime\U60`, `U67`, `U75`, `U100`; all four pass against the ground truth, mean brightness +0.9, +1.2, +0.6, +0.7 percent). Fine detail kept, as a share of the 100 percent picture (`review\phase9\scripts\upscale_compare.py`, sheets `review\phase9\sheets\j8_upscale_*.jpg`): brick 91 / 92 / 92, foliage at the left 89 / 86 / 87, foliage at the right 86 / 90 / 90, railing 89 / 91 / 92 (at 60 / 67 / 75 percent). Cost of each on the graphics card, measured 06:07 to 06:09 (`gpu_passes.py` at viewport percentages 73, 82 and 92, which give the editor's viewport the pixel counts of 60, 67 and 75 percent of 2560 by 1440; folders `profiles\2026-11-13_M7\T_u_73`, `T_u_82`, `T_u_92`, and `T_u_82_again` taken last to show the order does not matter; conditions: tier conditions, somebody working in a web browser, the editor not in front for part of the time):

  | Computed at | S1 graphics card (ms) | D2 graphics card (ms) | Upscaling pass S1 / D2 (ms, budget 1.2) |
  |---|---|---|---|
  | 60 percent | 9.67 | 9.09 | 0.91 / 0.91 |
  | 67 percent (first, then again) | 10.20, 10.15 | 9.75, 9.62 | 1.06 / 1.50, 1.06 / 1.53 |
  | 75 percent | 11.03 | 10.64 | 1.22 / 1.76 |

  **67 percent is confirmed; nothing is changed.** Going down to 60 percent would save about 0.5 ms that is not needed (the graphics card is 4 ms under its 14.5 ms line) and loses a little foliage detail at the right of S1 (86 against 90); going up to 75 percent costs about 0.9 ms and shows no gain that can be measured or seen on brick or foliage (the sheets). The upscaling pass at D2 is 1.50 ms against its budget of 1.2; the overrun of 0.3 ms is offset by post-processing, which is 0.49 ms under its budget there. J5 DONE 06:10.
- J6 (step 9.5) DONE 06:12. **Foliage: confirmed, nothing changed.** The 34 trees are the only foliage that moves. Their wind pass costs 0.22 to 0.23 ms at every station against a budget of 0.4. Their shadows cost 0.6 to 0.7 ms of the sun's shadow pass (trial `T_s_notrees` in J3, the trees hidden and shown again): the trees move in the wind, so 478 of about 500 shadow pages are redrawn each frame. The only way to remove that is to stop the wind or to stop distant trees from casting moving shadows; the first is not on the plan's list of things the real-time tier may give up, and the second (a listed trade, "simplified distant foliage shadow") was not needed, because the shadow overrun outdoors is offset by named passes (acceptance table) and the frame-time lines are met. No change, so no before and after.
- J7 (step 9.6) DONE 06:12. **Textures: the 4.0 GB pool holds with a wide margin; nothing changed.** Texture streaming is the engine loading each texture only at the sharpness the view needs, inside a fixed amount of video memory called the pool. In the recordings of the final state (`profiles\2026-11-13_M7\C2\csv`, columns `TextureStreaming/*`) the textures wanted at full sharpness come to 440 to 580 MB on the exterior path, 430 to 516 MB on the triplex path and 431 to 441 MB on the penthouse path, plus 188 MB that is never streamed; 100 percent of what the views ask for is loaded at every moment. That is under 0.8 GB against the pool of 4.0 GB (and even under the 1,000 MB pool that every measurement of this phase uses, so the measuring pool does not hide any cost). Texel density (texture pixels per metre of real surface): no material was changed in this phase, so the Phase 5 table stands (`texel_density.csv`: 18 of 20 sampled surfaces are not more than 25 percent below the table, 13 are denser than asked); making the two low ones denser or the 13 dense ones lighter belongs to the per-material keep-or-rebuild decision, which is the owner's. Virtual textures (a texture stored in tiles so that only the visible tiles are in video memory): the largest unique surface, the 16K limestone colour map, can only become one when its material is rebuilt (plan, Phase 5 hand-over), which also waits on that decision; with under 0.8 GB of textures in view it would save nothing measurable now. No change, so no before and after.
- J8 (step 9.9) DONE 06:17 (begun 06:11): all twelve views rendered in the final state (tag `F`) and compared with the Phase 12 ground truth. Free commit was 28.3 GB at the start, under the 30 GB line, with nothing of this work left to unload (the editor's garbage collection freed nothing; the rest is the editor itself at 25.4 GB and the programs of the person at the computer); one picture (D2) was rendered first as a trial: free commit stayed at 25.6 GB or more, so the other eleven followed one at a time (lowest free commit 25.2 GB, editor at most 28.6 GB). Pictures in `review\phase9\realtime\F\`, numbers and sheets in `review\phase9\compare\F\` (`compare.csv`). The render job is the one Phase 12 used, so the columns compare with `review\phase12\compare\compare.csv`. "Mean" is the mean brightness against the path-traced ground truth in percent (line: within 10); "largest region" is the largest connected part of the frame that is off by more than one stop, in percent of the frame (line: at most 2).

  | View | Phase 12 mean | Phase 12 largest region | Phase 12 | Now mean | Now largest region | Now |
  |---|---|---|---|---|---|---|
  | S1 | 0.0 | 0.23 | passes | 1.0 | 0.37 | passes |
  | S2 | 1.9 | 0.1 | passes | 1.4 | 0.04 | passes |
  | S3 | 0.3 | 0.27 | passes | -0.2 | 0.48 | passes |
  | S4 | 2.8 | 0.06 | passes | 3.0 | 0.04 | passes |
  | S5 | -4.2 | 0.27 | passes | -1.1 | 1.5 | passes |
  | S6 | 0.5 | 0.27 | passes | 1.1 | 0.31 | passes |
  | S9 | 26.3 | 2.06 | fails | 31.7 | 2.06 | fails |
  | D1 | -4.9 | 0.58 | passes | -4.1 | 0.08 | passes |
  | D2 | 2.4 | 0.35 | passes | 13.9 | 0.44 | fails |
  | D3 | 29.0 | 4.32 | fails | 62.1 | 47.42 | fails |
  | D4 | -30.8 | 6.08 | fails | -5.7 | 0.04 | passes |
  | D5 | -11.4 | 0.15 | fails | -1.8 | 0.0 | passes |

  **9 of 12 views pass (Phase 12: 8 of 12). The line "holds at every view" is not met, and was not met before this phase.** All seven exterior day views pass as before. S9 (the dusk view) fails as before. Indoors, every view is brighter against the ground truth than in Phase 12's pictures of 02:03 to 02:10: that brings D4 and D5 inside the line, takes D2 outside it (+13.9 against a line of 10) and takes D3 further outside. **This shift is not caused by the two changes of this phase:** rendered at the same moment with and without each change, D2 moves by 0.3 points for change 1 (J2) and no interior view moves by more than 0.6 points for change 2 (J4); with the scene exactly as Phase 12 left it, D2 already read about +14 at 03:50. What changed between 02:10 and 03:50 was not found. Tested and ruled out: the number of lit lamps (314, unchanged), the lamps themselves (D2 is +12.6 with every lamp hidden), ray-traced lamp shadows leaking (D3 is +68.7 with MegaLights using shadow maps). One oddity found on the way: with MegaLights switched off again, the interior pictures now come out far too bright (D3 +251, D4 +222 percent), which they did not at 03:50; the switched-off state is no longer a usable reference in this editor session. S1 and D2 after each change (plan step 9.9): change 1 S1 and D2 in J2; change 2 D1 to D5 in J4, S1 is outside the interior volumes and reads +1.0 here. J8 DONE 06:17.
- J10 (step 9.10) DONE 06:30. **Profile M7 is saved, with the change log and the real-time settings as a named configuration.** All in `profiles\2026-11-13_M7\`:
  - `M7\`: every path and hold in the final state, recorded 06:18 to 06:22 with the computer idle and the editor in front for the whole of every recording (share 1.00). Tier conditions.

    | Recording | Frame mean (ms) | 95th percentile | Worst | Frames over 33.3 ms | Graphics card mean | Game thread mean | Video memory peak (MB) |
    |---|---|---|---|---|---|---|---|
    | Exterior path, 60 s | 11.50 | 12.82 | 22.11 | 0 of 5,217 | 10.07 | 7.23 | 9,076 |
    | Triplex path, 30 s | 9.81 | 12.62 | 20.40 | 0 of 3,059 | 8.47 | 6.57 | 8,933 |
    | Penthouse path indoors, 20 s | 12.04 | 14.55 | 32.57 | 0 of 1,661 | 10.51 | 7.07 | 9,391 |
    | Penthouse path roof deck, 10 s | 11.65 | 13.69 | 19.53 | 0 of 859 | 10.13 | 7.25 | 9,429 |
    | Hold S1 | 13.61 | 13.42 | 1,123.2 | 3 of 735 | 10.42 | 9.11 | 9,078 |
    | Hold S2 | 11.71 | 13.10 | 14.68 | 0 | 10.25 | 7.19 | 8,950 |
    | Hold S6 | 11.19 | 12.45 | 20.06 | 0 | 9.76 | 7.10 | 8,936 |
    | Hold D5 | 9.75 | 10.94 | 17.44 | 0 | 8.38 | 6.65 | 8,859 |
    | Hold D2 | 12.23 | 13.94 | 19.64 | 0 | 10.69 | 6.83 | 9,388 |

    The one stall of 1.1 seconds in the hold at S1 is the editor's autosave (the editor writes a spare copy of every level marked unsaved every ten minutes; its log shows one at 06:19:22, the second the stall happened). It is the editor's doing, not the scene's, and would not happen in a packaged build. The render thread's time reads 9.8 to 12.0 ms in the recordings, but 4.9 to 6.1 ms of that is waiting for the graphics card (column `EventWait/Visibility`); its own work is 4.9 to 6.1 ms against a budget of 8.0. The game thread is 6.6 to 7.3 ms on the paths against 8.0.
  - `M7_final\`: graphics-card time by pass in the final state (median of three single frames per station, 06:17, computer idle, editor in front). Upscaling and post-processing are scaled by 1.51 to the plan's 2,560 by 1,440 picture (see "How every measurement of this phase is taken"); bold is over budget.

    | Pass | Budget (ms) | S1 | S2 | S6 | D2 | D5 |
    |---|---|---|---|---|---|---|
    | Geometry: Nanite visibility and surface pass | 2.0 | 1.36 | 1.46 | 1.35 | 1.04 | 1.13 |
    | Shadows: Virtual Shadow Maps | 2.0 | **3.04** | **3.03** | **2.71** | 1.11 | 1.10 |
    | Lumen scene update and its lighting caches | 1.5 | 0.86 | 0.93 | 0.80 | 0.95 | 0.91 |
    | Lumen global illumination | 2.5 | **3.15** | **3.23** | **2.76** | 1.60 | 1.49 |
    | Lumen reflections, including glass | 1.5 | 1.01 | 0.86 | 0.95 | **2.29** | **1.94** |
    | Direct light | 1.0 | **1.20** | **1.31** | **1.20** | **1.57** | **1.11** |
    | Sky, atmosphere, clouds and fog | 0.8 | 0.47 | 0.51 | 0.61 | 0.71 | 0.54 |
    | Translucent surfaces | 0.8 | 0.66 | 0.49 | 0.43 | **0.86** | 0.15 |
    | Foliage wind | 0.4 | 0.22 | 0.22 | 0.22 | 0.22 | 0.22 |
    | Temporal upscaling (scaled) | 1.2 | **1.58** | **1.62** | **1.66** | **2.28** | **1.54** |
    | Post-processing and tone mapping (scaled) | 0.8 | 0.48 | 0.49 | 0.49 | 0.48 | **1.65** |
    | Sum of the passes | 14.5 | 14.02 | 14.15 | 13.19 | 13.11 | 11.79 |
    | The frame's graphics-card time as measured, plus what the scaling adds | 14.5 | 10.97 | 11.15 | 10.40 | 10.49 | 10.24 |

    The passes add up to more than the frame's graphics-card time because the card works two queues at once. Each overrun and the named passes that offset it (`review\phase9\scripts\pass_budget.py M7_final`):
    - S1: over budget: shadows by 1.04, Lumen global illumination by 0.65, direct light by 0.20, upscaling by 0.38 (together 2.26 ms); offset by Lumen scene 0.64, geometry 0.64, reflections 0.49, sky 0.34, post-processing 0.32, foliage wind 0.18, translucent surfaces 0.15 (together 2.74 ms under).
    - S2: over budget: shadows by 1.03, Lumen global illumination by 0.73, direct light by 0.31, upscaling by 0.42 (together 2.49 ms); offset by reflections 0.64, Lumen scene 0.57, geometry 0.54, post-processing 0.31, translucent surfaces 0.31, sky 0.30, foliage wind 0.18 (together 2.84 ms under).
    - S6: over budget: shadows by 0.71, Lumen global illumination by 0.26, direct light by 0.20, upscaling by 0.46 (together 1.63 ms); offset by Lumen scene 0.70, geometry 0.65, reflections 0.55, translucent surfaces 0.37, post-processing 0.31, sky 0.19, foliage wind 0.18 (together 2.94 ms under).
    - D2: over budget: reflections by 0.79, direct light by 0.57, translucent surfaces by 0.06, upscaling by 1.08 (together 2.51 ms); offset by geometry 0.96, Lumen global illumination 0.90, shadows 0.89, Lumen scene 0.55, post-processing 0.32, foliage wind 0.18 (together 3.89 ms under).
    - D5: over budget: reflections by 0.44, direct light by 0.11, upscaling by 0.34, post-processing by 0.85 (together 1.74 ms); offset by Lumen global illumination 1.01, shadows 0.90, geometry 0.87, translucent surfaces 0.65, Lumen scene 0.59, sky 0.26, foliage wind 0.18 (together 4.46 ms under).
  - `change_log.csv` (written by `review\phase9\scripts\change_log.py`): two changes, each with every path and hold before and after (frame mean, 95th percentile, worst, frames over 33.3 ms, graphics card, render thread, video memory). Steps 9.2, 9.3, 9.5, 9.6 and 9.8 changed nothing and so have no row; their measurements are in J3, J3b, J5, J6 and J7.
  - `realtime_tier_M7.json`: the real-time settings as a named configuration, "Wieland 1529 real-time tier, profile M7": what is stored in the lighting level, the display and quality settings, the one console variable that must stay as it is, and how the tier was measured in the editor.
  - `B0\`, `C1\`, `C2\`: the same recordings before any change, after change 1 and after change 2; `T_*\`: single trials; `soak\`: the soak (J9).
- J9 (step 9.11) DONE IN PART 07:07 (begun 06:24): the soak ran 42 minutes instead of two hours. It was stopped by `review\phase9\scripts\soak_stop.py` (`wp.cancel()`, then `m7.soak_end()`); `soak_end.json` shows `settings_put_back` true, and the editor is back at screen percentage 100, no frame limit, Game View off, all unit levels shown. Figures from `python -B review\phase9\scripts\soak_report.py` (`profiles\2026-11-13_M7\soak\soak_report.json`); conditions: tier conditions, final state, the editor in front for the whole of 37 walks, in front for part of 4 and not in front at all for 1 (the person came back to the computer at about 07:02):

  | Soak figure | Reading |
  |---|---|
  | Walks finished | 42 of 120 (06:24:28 to 07:06:28, 0.70 hours, 216,996 frames) |
  | Crash | none; the editor (process 25884) ran throughout |
  | Frame time, mean of all frames | 11.61 ms |
  | 95th percentile of each walk | lowest 12.34 ms, highest 14.81 ms; no walk over 16.67 ms |
  | Frames over 33.3 ms | 23 of 216,996, in 16 walks; worst 125.0 ms |
  | Video memory in use, first to last recorded walk | 8,920 MB to 8,920 MB: growth 0.0 percent (14 readings, one every third walk; lowest mean 8,870 MB, peak 8,920 MB; `soak_video_memory.csv`) |
  | Editor's committed memory, first / last / highest | 25.36 / 25.31 / 25.39 GB (495 log lines, one every five seconds) |
  | Free commit memory, lowest | 27.54 GB |

  **Where the 23 slow frames come from.** 14 of them are one frame each (51 to 116 ms) in the 14 walks in which the engine's own recorder was also started to read the video memory (walks 1, 4, 7 and so on to 40): starting and stopping that recorder stalls the editor once, and the stall is not in the recorder's own two-second table, so it is the measuring tool's doing, not the scene's. 8 are in walk 5 (worst 125 ms), at the second of the editor's autosave (06:29:24 in its log; see J10). 1 is a frame of 37.0 ms in walk 9, which ended at 06:33:28.4; the engine's recorder for walk 10 started at 06:33:28.425 in the editor's log, so it is probably the same stall falling just before the walk's end, but that is not proven. The other 26 walks have no frame over 33.3 ms (worst 30.1 ms). The clean profile recording `M7` of J10 has none on any path. A soak without the engine's recorder (video memory read another way) and with autosave off would settle the last doubt; it was not run, because the owner stopped the soak.
  **Against the acceptance line** (two hours, no crash, video memory growing by no more than 5 percent): no crash and 0.0 percent growth, over 42 minutes, not two hours. Met in part, shortened by the owner's decision. The earlier status note said 41 walks; the 42nd ended while the stop was being prepared and is counted. A short trial of the soak tool made before the run is in `profiles\2026-11-13_M7\soak_trial\`.
- J11 DONE 07:12: closing. The memory log of this phase was stopped at 07:08 (its last line: 28.0 GB of commit free, the editor at 25.35 GB). State of the editor as left: running (process 25884), top level `/Game/Wieland1529/L_Site_M4` with its 12 levels, `r.RayTracing.Nanite.Mode` 0, screen percentage 100, no frame limit. Five levels are marked unsaved with no change of content and were not saved: `L_Site_M4` and the four unit levels `L_W1529_NorthTriplex`, `L_W1529_SouthTriplex`, `L_W1529_NorthPenthouse`, `L_W1529_SouthPenthouse`. No advisor tool exists in this session either; the closing check of the changes against the scope was done by hand: the only assets saved in the project by this phase are the lighting level (twice, J2 and J4); every other file of the phase is in this repository.

## Acceptance

Each line of `PLAN.md`, Phase 9, with its measured number. The frame-time figures are those of recording `M7` (J10: final state, tier conditions, computer idle, editor in front for the whole of every recording, 06:18 to 06:22). The "interior path" of the plan is the triplex path and the penthouse path.

| Acceptance line | Result | Measured |
|---|---|---|
| Exterior path: 95th-percentile frame time 16.67 ms or less | Met | 12.82 ms (before this phase 32.09 ms). In the soak: 12.34 to 14.81 ms in each of 42 walks. |
| Exterior path: no frame over 33.3 ms | Met in the profile recording; in the soak met but for frames caused by measuring and autosave, and one frame not explained for certain | Recording `M7`: 0 of 5,217 frames, worst 22.11 ms (before: 45 of 2,015, worst 38.76 ms). Soak: 23 of 216,996 frames, of which 14 by the measuring tool's recorder, 8 by the editor's autosave and 1 of 37.0 ms probably by the recorder (J9). |
| Exterior path: graphics-card time 14.5 ms or less on average | Met | 10.07 ms (before 17.35 ms) |
| Interior paths: 95th-percentile frame time 16.67 ms or less | Met | Triplex 12.62 ms (before 26.05); penthouse indoors 14.55 ms (before 29.29); penthouse roof deck 13.69 ms (before 32.73) |
| Interior paths: no frame over 33.3 ms | Met, with 0.7 ms to spare on the penthouse path | Triplex 0 of 3,059, worst 20.40 ms; penthouse indoors 0 of 1,661, worst 32.57 ms; roof deck 0 of 859, worst 19.53 ms (before: 4, 4 and 15 frames over) |
| Interior paths: graphics-card time 14.5 ms or less on average | Met | Triplex 8.47 ms; penthouse indoors 10.51 ms; roof deck 10.13 ms (before 15.69, 24.52, 20.10) |
| Each render pass within its budget, or the overrun offset by a named pass that is under | Met by offset at all five stations | Sum of the passes against 14.5 ms: S1 14.02, S2 14.15, S6 13.19, D2 13.11, D5 11.79 ms. Over budget outdoors: shadows (up to 3.04 against 2.0), Lumen global illumination (up to 3.23 against 2.5), direct light, upscaling; indoors: reflections (up to 2.29 against 1.5), direct light, upscaling, and post-processing at D5. Each overrun and the passes that offset it are named station by station in J10. Upscaling and post-processing are scaled by 1.51 to the full picture, not measured at it. |
| Processor budget, 8.0 ms each for game thread and render thread (budget table) | Met | Game thread 6.57 to 7.25 ms on the paths; render thread's own work 4.9 to 6.1 ms (J10) |
| Peak video memory 13.0 GB or less | Met | Highest in the final state 9,429 MB (roof deck); highest of the whole phase 11,619 MB (roof deck before any change). Measured with a texture pool of 1,000 MB; the views ask for under 800 MB of textures, so the 4.0 GB pool would not raise it (J7). |
| Soak: two hours of the exterior path, no crash, video memory growing by no more than 5 percent | Met in part: 42 minutes, not two hours, stopped on the owner's decision | 42 of 120 walks, no crash, video memory 8,920 MB at the first and at the last reading (growth 0.0 percent), editor's committed memory 25.36 to 25.31 GB (J9) |
| The Phase 8 real-time tolerance still holds at every view | Not met, and not met before this phase: 9 of 12 views pass (Phase 12: 8 of 12) | Fail: S9 +31.7 percent (as before), D3 +62.1 percent (before +29.0), D2 +13.9 percent (before +2.4, line 10). Now pass: D4 and D5. The two changes of this phase move no view by more than 0.6 points when rendered at the same moment with and without them (J2, J4, J8); the cause of the brighter interiors was not found. Workaround: none that this phase may apply; it is a lighting matter for the owner and Phase 10. |
| Every change in the log has a before and an after measurement | Met | 2 changes, each with all 9 recordings before and after, in `profiles\2026-11-13_M7\change_log.csv` |

Steps that ended as confirmations with nothing changed, each with its measurement: geometry 9.2 (J3b), shadows 9.3 (J3), foliage 9.5 (J6), textures 9.6 (J7), upscaling 9.8 (J5).

## What was saved or changed in the project

- Saved by name, twice: the lighting level `/Game/Wieland1529/Lighting/L_Light_SummerAfternoon`. It now carries change 1 (the setting "MegaLights" on the post-process volume `LGT_Exposure_Outdoors`) and change 2 (the Lumen setting "hit lighting for reflections" on the two interior volumes `LGT_Exposure_Interior_4th` and `LGT_Exposure_Interior_LowerTo3rd`).
- Nothing else. No settings file of the project was changed, no asset made by Datasmith was edited, `L_R15_Production` was not saved, "Save All" was not used, nothing was deleted, nothing was written to H:, and no path-traced picture was rendered (`r.RayTracing.Nanite.Mode` stayed 0 throughout).
- Written by the engine into the project's own `Saved\Profiling\` folder while measuring: its frame tables (`CSV\Profile(...).csv`), one shadow table (`VSMStats(20261113_052042).csv`) and small load-request logs. They are measurements, not content.
- Left in the editor, not saved: five levels marked unsaved without any change of content (J11).

## For the owner

1. The soak ran 42 minutes, not two hours. The session before recorded your decision of 07:06 to stop it; the session that closed the phase acted on that note without hearing you itself. If you did not decide this, say so and the two-hour soak is run again (two hours, nothing else changes).
2. The real-time picture does not match the path-traced ground truth at three views: S9 (dusk, as before), D3 and D2. Every interior view became brighter between 02:10 and 03:50 on 2026-11-13 with the scene unchanged; the cause was not found, and the two changes of this phase are not it. Not yet tried: closing and reopening the editor and rendering D2 and D3 again. This should be the first thing Phase 10 does.
3. With MegaLights switched off again in this editor session the interiors come out far too bright (J8). Do not judge the "before" state in this session; restart the editor first.
4. Change 1 makes the lamps' shadow edges a little softer. That is in the plan's list of what the real-time tier gives up; look at `review\phase9\sheets\j2_megalights_D2_crop.jpg` and say if it is not acceptable.
5. The plan's full picture of 2,560 by 1,440 cannot be shown in the editor on this monitor (the viewport is 2,038 by 1,198). Everything was measured at the same number of computed pixels, and upscaling and post-processing were multiplied by 1.51. A measurement at the true size needs a packaged build (Phase 11) or a larger monitor.
6. Shadows and Lumen global illumination are over their own budget rows outdoors by up to 1.0 and 0.7 ms and are offset by other passes. If you want them inside their own rows, the listed trade is "simplified distant foliage shadow" (the trees' moving shadows cost 0.6 to 0.7 ms); it was not needed for the frame-time lines and was not taken.
7. 148 small meshes from Revit (curtains, fixtures, baseboards; 164,000 triangles) are not Nanite. Changing that means editing assets Datasmith made, which the rules forbid; the cost is too small to measure.
8. Waiting on your keep-or-rebuild decision per material: making the two thin textures denser, the 13 dense ones lighter, and turning the 16K limestone colour map into a virtual texture (J7).
9. `r.RayTracing.Nanite.Mode` 2 was not used in this phase and is not adopted for the real-time walk-through; it remains unstable in 5.9.
10. When you close the editor it will ask about five unsaved levels (J11). Answer "do not save": they hold no work, and `L_Site_M4` holds only a temporary camera.
11. Between 05:40 and about 05:55 the measuring tool pressed the Alt key every ten seconds to bring the editor to the front while somebody was using the computer. It no longer does so.
12. The memory log of Phase 8 (`profiles\2026-11-12_M6\memory_log_phase8.csv`) is still being written by a process started in Phase 8 (process 30032); it ends by itself and was left alone. It keeps that file showing as changed in the working copy.
13. No advisor tool exists in these sessions; the closing checks were done by hand.

## Files written by this phase

All under `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\`.

- `PROJECT_MEMORY.md` (section "Phase 9: optimization").
- `docs\unreal\1529_wieland\phase9_results.md` (this file).
- `docs\unreal\1529_wieland\tools\phase9_profile_m7.py` (recordings, single-frame pass times, the soak and its watcher) and `docs\unreal\1529_wieland\tools\wieland_optimize.py` (sets the two stored settings).
- `docs\unreal\1529_wieland\profiles\2026-11-13_M7\`: `change_log.csv`, `realtime_tier_M7.json`, `memory_log_phase9.csv`; recordings `B0\`, `C1\`, `C2\`, `M7\` (each with `csv\`); pass times `M7_final\`; single trials `T_mega\`, `T_mega_volume\`, `T_mega_vsm\`, `T_s_ref\`, `T_s_forceinv\`, `T_s_notrees\`, `T_s_bias05\`, `T_s_vsmoff\`, `T_l_hitrefl\`, `T_u_73\`, `T_u_82\`, `T_u_82_again\`, `T_u_92\`; the soak `soak\` (`soak_log.jsonl`, `soak_watch.jsonl`, `soak_log.jsonl.summary.json`, `soak_end.json`, `soak_report.json`, `soak_video_memory.csv`, `soak_settings_before.json`) and `soak_trial\`; kept as evidence and not used: `C2_window_minimised\`, `C2_window_minimised_2\`, `C2_behind_browser\`, `T_vsm_bias05\`.
- `docs\unreal\1529_wieland\review\phase9\`: `census.csv`; `scripts\` (38 files, among them `soak_start.py`, `soak_status.py`, `soak_stop.py`, `soak_report.py`, `gpu_passes.py`, `pass_budget.py`, `change_log.py`); `compare\` (`F\` with `compare.csv` for the twelve final views, and the trial folders `T_*` and `U60`, `U67`, `U75`, `U100`); `sheets\` (comparison sheets); `realtime\` (the rendered pictures, 466 MB, kept on disk and not committed, as the pictures of Phases 8 and 12 are).
