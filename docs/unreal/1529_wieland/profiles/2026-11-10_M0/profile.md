# Profile M0: the existing scene, before any change

Milestone M0 of [PLAN.md](../../PLAN.md), taken in Phase 1, step 1.6. A profile is a saved set of performance measurements; later milestones are compared with this one.

## Conditions

| Item | Value |
|---|---|
| Date | 2026-11-10, 22:40 to 22:55 Central |
| Engine | Unreal Engine 5.9.0 (build 60351404) |
| Project and level | `D:\Unreal_Engine_Projects\Wieland1527 5.9\`, `/Game/Wieland/R15_Landscape/L_R15_Production`, unchanged and unsaved |
| Scene | 58 building parts, 11 trees, 2,557 ground plants; no building on the lot, no interior |
| Workstation | NVIDIA RTX 4080 (16 GB, driver 610.88), Ryzen 7 7800X3D, 32 GB, Windows 11; monitor 2560 by 1440 at 239 Hz |
| **Output size (the editor's viewport)** | **2038 by 782 pixels** (1.59 million pixels), horizontal field of view 90 degrees |
| **Internal size at 100 percent** | 2038 by 782. This is close to the pixel count the plan's real-time tier will render (67 percent of 2560 by 1440 is 1715 by 965, 1.66 million pixels). |
| **Internal size at 152 percent** | 3098 by 1189 (3.68 million pixels), read from the renderer's own pass names. This matches the pixel count of 2560 by 1440 (3.69 million). The picture is then scaled down to the viewport. |
| Quality level "Epic" | Every quality group at 3, texture pool 1,000 MB. These are the October benchmark's settings. |
| Quality level "Cinematic" | Every quality group at 4, texture pool 3,000 MB. **This is how the editor was found.** |
| Other settings | Lumen with hardware ray tracing, Virtual Shadow Maps, Substrate, the engine's temporal upscaler; vertical sync off; Game View on; real-time on; frame cap lifted (see below) |
| Method | As in October: 8 seconds of warm-up, then the engine's CSV profiler (a per-frame log of timings) records 10 seconds per view, or 60 seconds for the path. The 95th percentile is the value at position floor(0.95 x (n - 1)) of the sorted frame times; every frame counts. |

Three things to know when reading the numbers:

1. **The editor caps itself at 120 frames per second when no cap is set.** With `t.MaxFPS` at 0 the frame time never fell below 8.333 ms. Setting `t.MaxFPS` to 1000 for the captures lifted this. A first capture taken before this was understood is kept as `capture_A_views_epic_sp100.json` and is not used below.
2. **The editor was not the front window during these captures**; the owner was working in another program. The editor is set not to slow down in the background ("Use Less CPU when in Background" is off), and the two views that were also captured in the foreground earlier that evening agree within 0.3 ms of graphics-card time, so the effect is small. It is recorded with every capture as `foreground_fraction`.
3. **The viewport is wider and shorter than the October images** (2.6 to 1 against 1.9 to 1). At the same horizontal field of view it shows less sky and less ground. Matching the pixel count does not make the picture the same.

## The three October views

Frame time is the whole frame. Graphics-card time is the part the plan's 14.5 ms budget applies to.

| Setting | View | Frame mean (ms) | 95th percentile (ms) | Worst (ms) | Graphics-card mean (ms) | Frames per second | Frames |
|---|---|---|---|---|---|---|---|
| **October, engine 5.8, Epic, 100 percent, size not recorded** | Frontage and context | 12.678 | 14.990 | 16.765 | 10.02 | 78.9 | 790 |
| | Dense planting | 11.898 | 14.372 | 17.111 | 9.22 | 84.0 | 840 |
| | Block overview | 12.922 | 15.252 | 16.188 | 10.18 | 77.4 | 774 |
| **Now, engine 5.9, Epic, 152 percent** (pixel count of 2560 by 1440) | Frontage and context | 10.828 | 13.203 | 18.774 | 9.45 | 92.4 | 924 |
| | Dense planting | 9.921 | 12.002 | 17.265 | 8.64 | 100.8 | 1,008 |
| | Block overview | 10.571 | 12.665 | 15.181 | 9.31 | 94.6 | 947 |
| **Now, engine 5.9, Epic, 100 percent** (2038 by 782) | Frontage and context | 8.471 | 10.603 | 25.916 | 6.91 | 118.0 | 1,181 |
| | Dense planting | 7.510 | 10.097 | 20.900 | 6.02 | 133.2 | 1,332 |
| | Block overview | 8.594 | 11.145 | 20.275 | 7.04 | 116.4 | 1,164 |
| **Now, engine 5.9, Cinematic, 152 percent** | Frontage and context | 19.801 | 22.233 | 30.449 | 18.41 | 50.5 | 506 |
| | Dense planting | 22.059 | 24.793 | 32.038 | 20.62 | 45.3 | 454 |
| | Block overview | 19.696 | 22.176 | 28.766 | 18.31 | 50.8 | 508 |
| **Now, engine 5.9, Cinematic, 100 percent** | Frontage and context | 11.674 | 13.428 | 21.064 | 10.29 | 85.7 | 857 |
| | Dense planting | 13.911 | 18.572 | 22.399 | 12.09 | 71.9 | 719 |
| | Block overview | 11.613 | 13.979 | 18.957 | 10.22 | 86.1 | 862 |

What this shows:

- **Like for like (Epic, about the same pixel count), 5.9 is not slower than 5.8 on this scene.** Frame means are 10.8, 9.9 and 10.6 ms against 12.7, 11.9 and 12.9 ms in October; graphics-card means are 9.5, 8.6 and 9.3 ms against 10.0, 9.2 and 10.2 ms. The October viewport size is unknown, so this is an indication and not a proof.
- **At Cinematic quality the scene misses 60 frames per second at the pixel count of 2560 by 1440**: 45 to 51 frames per second, with 18 to 21 ms of graphics-card time against a 14.5 ms budget. Cinematic costs about twice Epic here.
- The game thread (the editor's own work each frame) took 5.0 to 6.2 ms in every capture, inside its 8.0 ms budget.
- The render-thread column of the engine's log reads zero throughout in 5.9.0, so the render-thread budget could not be checked from it.

## The fixed exterior path

84 m in 60 seconds along the west sidewalk, eye height 1.60 m, from 45 m south of station S1 to 39 m north of it, the camera turning to keep one point centred.

| Item | Level coordinates (cm) |
|---|---|
| Start | (-11736.7, -3650.0, 158.2) |
| End | (-20136.7, -3650.0, 158.2) |
| Point kept centred | (-16236.7, -5364.8, 303.2): the centre of the street face of the future building, 1 m above its first floor. Provisional, because the level holds no building and so no front door. |

The walking line is 14.0 m west of the front lot line, not the 18 m the plan gives, because 18 m lands inside a building on the west side of the modelled street. See `phase1_results.md`.

| Pass | Frame mean (ms) | 95th percentile (ms) | Worst frame (ms) | Graphics-card mean (ms) | Frames over 16.7 ms | Frames over 33.3 ms | Frames |
|---|---|---|---|---|---|---|---|
| Epic, 100 percent, first walk since the editor started | 8.440 | 11.231 | 106.319 | 6.59 | 90 | 27 | 7,109 |
| **Epic, 100 percent, repeated** | **7.780** | **9.728** | **17.865** | 6.50 | 3 | 0 | 7,712 |
| Epic, 152 percent, first | 10.673 | 13.063 | 18.860 | 9.41 | 8 | 0 | 5,622 |
| **Epic, 152 percent, repeated** | **10.530** | **12.612** | **19.378** | 9.31 | 10 | 0 | 5,699 |
| Cinematic, 152 percent | 20.363 | 22.794 | 30.368 | 19.04 | 2,934 | 0 | 2,947 |

The first walk had 27 frames longer than 33 ms, the worst 106 ms. They did not recur on any later walk. The editor had been restarted 40 minutes earlier with an empty cache, so the first visit to each part of the street paid one-time loading costs. **A profile's path should be walked once before it is recorded.**

Interior paths: none at M0. The scene has no interior.

## Graphics-card time by pass, at the stations

Epic quality. Each figure is the median of three single-frame samples from the editor's per-pass profiler, in milliseconds, set against the plan's proposed budget.

| Render pass | Budget | S1, 100% | S2, 100% | S6, 100% | S1, 152% | S2, 152% | S6, 152% |
|---|---|---|---|---|---|---|---|
| Geometry: Nanite visibility and surface pass | 2.0 | 1.34 | 1.12 | 1.22 | 1.88 | 1.43 | 1.93 |
| Shadows: Virtual Shadow Maps | 2.0 | 0.83 | 0.96 | 0.97 | 0.95 | 1.14 | 1.20 |
| Lumen scene update and its lighting caches | 1.5 | 0.91 | 0.69 | 0.68 | 0.79 | 0.65 | 0.78 |
| Lumen global illumination | 2.5 | 1.40 | 1.40 | 1.66 | **3.42** | **3.72** | **3.81** |
| Lumen reflections, including glass | 1.5 | 0.42 | 0.38 | 0.44 | 0.69 | 0.59 | 0.81 |
| Direct light | 1.0 | 0.37 | 0.31 | 0.47 | 0.68 | 0.72 | **1.19** |
| Sky, atmosphere, clouds and fog | 0.8 | 0.62 | **0.99** | 0.60 | **1.35** | **1.47** | **1.00** |
| Translucent surfaces | 0.8 | 0.10 | 0.09 | 0.11 | 0.12 | 0.10 | 0.13 |
| Foliage wind | 0.4 | 0.20 | 0.20 | 0.20 | 0.20 | 0.21 | 0.20 |
| Temporal upscaling | 1.2 | 0.91 | 0.90 | 0.92 | **1.79** | **1.67** | **2.20** |
| Post-processing and tone mapping | 0.8 | 0.28 | 0.46 | 0.28 | 0.32 | 0.32 | 0.33 |
| Passes not in the budget table | none | 0.55 | 0.31 | 0.31 | 0.37 | 0.36 | 0.36 |
| Sum of the rows above | 14.5 | 7.92 | 7.82 | 7.87 | 12.57 | 12.38 | 13.95 |
| The frame's graphics-card time, as the engine reports it | | 6.30 | 6.40 | 6.65 | 9.45 | 9.08 | 9.40 |
| The editor's own interface, outside the scene | | 0.23 | 0.23 | 0.23 | 0.24 | 0.23 | 0.24 |

Figures in bold exceed the proposed budget for that row.

How to read this table:

- **The rows add up to more than the frame's graphics-card time.** The card runs two queues of work at once, and the profiler reports each pass's own duration. The budget in the plan is a sum of rows, so the sum is the figure to hold against 14.5 ms, and the engine's reported time is the figure to hold against the frame rate.
- At the real-time tier's pixel count (the 100 percent columns) the existing scene uses about 7.9 ms of the 14.5 ms, with every row inside its budget except sky at S2.
- At the full pixel count of 2560 by 1440 (the 152 percent columns) global illumination, sky and upscaling already exceed their rows with no building, no interior and 11 trees. This supports the plan's choice to render the real-time tier at 67 percent.
- The upscaling row at 152 percent is not what the real-time tier will pay: here the upscaler shrinks a larger picture, where the plan has it enlarge a smaller one.
- Shadow projection cannot be separated from direct lighting in the profiler's output and is counted under direct light.

| Station | Level coordinates (cm) | Yaw, pitch (degrees) |
|---|---|---|
| S1 Frontal | (-16236.7, -3650.0, 158.2) | -90, up 12 |
| S2 From the south-west | (-13736.7, -3650.0, 158.2) | -135, up 10 |
| S6 Along the frontage | (-18991.1, -4843.7, 156.8) | 0, level |
| D2 and D5 | Interior design views; they do not exist at M0 | |

All three were taken at the viewport's 90 degree field of view, not at the stations' lens values (24, 35 and 28 mm), because the editor's viewport offers no way to set the field of view by script without placing a camera in the level, and the level is not to be changed.

## Video memory

| Measure | Value |
|---|---|
| Used by the editor, peak, Epic quality | 5,475 MB |
| Used by the editor, peak, Cinematic quality | 6,664 MB |
| Used on the whole card, peak during the Epic path | 7,959 MiB of 16,376 MiB |
| Plan's budget at peak | 13.0 GB |
| October, engine 5.8 | 6,116 MB used by the editor |

## Files in this folder

| File | What it holds |
|---|---|
| `profile.md` | This summary |
| `capture_B_views.json`, `capture_B_views.analysis.json` | The twelve view captures: the record and the reduced figures |
| `capture_C_path.json`, `capture_C_path.analysis.json` | The path, first walk at each setting, with every frame's duration |
| `capture_D_path_warm.json`, `capture_D_path_warm.analysis.json` | The path repeated at Epic |
| `gpu_passes_stations.json`, `gpu_passes_stations.summary.json` | Eighteen per-pass samples and their reduction to budget rows |
| `capture_A_views_epic_sp100.json`, `capture_A_views_epic_sp100.analysis.json` | The first capture, taken under the 120 frames-per-second cap. Kept as a record; not used. |
| `csv\*.csv.gz` | The engine's raw per-frame logs, compressed |

The scripts that made them are in `..\..\tools\`: `wieland_profile.py` (runs in the editor), `analyze_profile_csv.py` and `reduce_gpu_passes.py`.

## To repeat this profile at a later milestone

1. Confirm the level has no unsaved changes.
2. Set Epic quality, texture pool 1,000 MB, `t.MaxFPS 1000`, vertical sync off, Game View on, real-time on, editor interface throttling off (`Slate.bAllowThrottling 0`).
3. Record the viewport's size. If it differs from 2038 by 782, choose the screen percentages that give 1.59 and 3.68 million pixels.
4. Walk the path once without recording, then record it at both screen percentages.
5. Record the three views and the per-pass samples at the stations.
6. Put every setting back.
