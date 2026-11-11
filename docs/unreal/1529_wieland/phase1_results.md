# Phase 1 results: toolchain setup and first import test in 5.9

Companion to [PLAN.md](PLAN.md). This file is written as each step finishes, so a new session can resume from it.

**Status: in progress, paused at the owner's request on 2026-11-10 at about 22:15 Central.** Steps 1.2 and 1.3 are finished. Step 1.6 is part done. No other step has started. Phase 1 is not complete.

**Nothing in the Unreal project was saved.** No asset, level or setting was written. The level `L_R15_Production` has no unsaved changes, and the editor's settings and camera are back as they were found. The only files the work wrote inside the project folder are three measurement files the engine itself writes under `Saved\Profiling\CSV\`.

## Checks made before any work

| Check | Result |
|---|---|
| One read-only call to the editor | Succeeded. `list_toolsets` answered. |
| Model | Fable 5.2 (`claude-fable-5-2`), as pinned by the project's `.claude\settings.json` |
| Permission mode of the panel | Cannot be read from inside the session. The editor log from the panel's start says "tool access mode from host settings: auto", and the project's settings file sets no permission rules, so it is most likely Auto. That mode does not ask before each edit. The owner has not yet confirmed what the selector shows. |
| File access to the `E:` paths | Yes |
| Git | Yes, 2.55.0, with Git LFS 3.7.1. Branch `claude/1529-wieland-scene-plan-e84a03`. |
| Web browser | Partly. Page text can be fetched and searched, which cannot operate the NOAA calculator. A tool that may drive a real browser is connected and untried. |
| Revit and Google Drive connections | Not present. Phase 1 does not need them. |

## Where each step stands

| No. | Step | Status |
|---|---|---|
| 1.1 | Agent server starts with the editor; model confirmed; pointer file | Server and model confirmed. The server started by itself when the editor launched at 21:18 (the log shows "Starting MCP server on port 8000" on the first frame). `bAutoStartServer` is in none of the project's settings files, so whether that came from the engine's default or from a setting stored elsewhere is not established. Pointer file: waiting for the owner's approval. |
| 1.2 | List the tool sets | **Done.** 109 tool sets. See below. |
| 1.3 | Finish the live audit | **Done.** Appended to [SITE_MODEL_AUDIT.md](SITE_MODEL_AUDIT.md). See below. |
| 1.4 | Move the engine cache off C: | Waiting for the owner's action. |
| 1.5 | Archive the project to H: | Waiting for the owner's approval. |
| 1.6 | Baseline profile M0 | **Part done.** Three views captured once at one setting. See below for what is still to capture. |
| 1.7 | Import the Datasmith file into a scratch level | Not started. Waits for 1.5. |
| 1.8 | Reimport rehearsal | Not started. Waits for 1.7 and the owner's second export. |
| 1.9 | Three path-traced renders of station S1 | Not started. |
| 1.10 | Sun direction against the NOAA calculator | Not started. |
| 1.11 | 1,000-lumen light, illuminance at 1 m | Not started. Waits for 1.5. |
| 1.12 | Lumen World Cache and overlapping glass, on and off | Not started. |
| 1.13 | Two-hour soak | Not started. |
| 1.14 | Remove the Belmont and beech content | Waiting for the owner's approval, and for 1.5. |
| 1.15 | This file | In progress. |

## Acceptance list

| Line | Target | Status |
|---|---|---|
| Agent server | 50 consecutive read-only calls with no error | **Not yet run as a test.** In ordinary work this session made 16 calls to the server; 15 succeeded and one failed through a fault in my script, not in the server (logged in `PROJECT_MEMORY.md`). |
| Baseline | The three October views at a recorded viewport size, beside the October means | **Part measured; not final.** See step 1.6 below. |
| Import | At least 99.5 percent of 3,562 objects and 587 lights; known dimension within 1 mm | Not yet measured |
| Reimport | 20 of 20 assignments survive | Not yet measured |
| Path Tracer | Three renders with no crash | Not yet measured |
| Sun | Bearing and height within 0.5 degree of NOAA | Not yet measured |
| Light units | Within 10 percent of 79.6 lux | Not yet measured |
| Soak | Two hours, no crash, video memory growth of 5 percent or less | Not yet measured |

## Step 1.2: tool sets

`list_toolsets` returned **109 tool sets** on 2026-11-10 at about 21:46. The earlier session recorded 115 the same evening. The six that are missing have not been identified. One lead from the editor log: the tool set for Unreal Canvas registered empty when the editor started ("tools/list returned zero tools ... the Unreal Canvas frontend has probably not attached yet"). The tools that trigger Movie Render Graph renders are still offered as top-level tools.

The sets Phase 1 uses were all present: actors, levels, assets, materials, static meshes, scene capture, the three performance sets (frame timings, per-pass GPU profiler, CSV reader), console variables, logs, configuration settings, Python, file system, Fab and project skills.

The editor registers 92 skills (bundles of instructions for an agent), all from the engine and its plugins. None is specific to this project. Those that bear on Phase 1: scene capture diagnostics, Movie Render Graph, Movie Render Queue, outdoor lighting, material basics, placing actors, log triage.

## Step 1.3: live audit

Read from the open level, read-only. Full tables are in [SITE_MODEL_AUDIT.md](SITE_MODEL_AUDIT.md) under "Live audit completed: the material on every part"; the raw record is [site_model_audit_materials.json](site_model_audit_materials.json).

| Measure | Value |
|---|---|
| Parts read | 58: 31 opaque parts drawn with Nanite, 27 glass parts |
| Material slots (one material assignment on a part) | 645, none empty |
| Different materials on the parts | 123, plus 14 used only by the trees and ground plants |
| Instances of the R15 parent materials | 25 materials on 472 slots (73 percent) |
| Stand-alone materials left from the R14 import | 98 materials on 173 slots (27 percent) |
| Glass | 116 slots on 5 materials, all from one parent |
| Materials from the Belmont or beech-tree folders | None |
| Trees and ground plants | 11 and 2,557, matching the October release notes |

## Step 1.6: baseline, as far as it got

### What was captured

The three October views, once each: eight seconds of warm-up, then ten seconds recorded with the engine's CSV profiler (a per-frame log of timings). Settings as in October: every quality group at Epic, screen percentage 100, no frame-rate cap set, vertical sync off, texture pool 1,000 MB, Game View on, real-time on.

**Viewport size: 2038 by 782 pixels** (1.59 million pixels), field of view 90 degrees. The October size was not recorded; that day's release images are 2560 by 1360 (3.48 million pixels), so October most likely drew about 2.2 times as many pixels.

| View | Frame time, mean (ms) | 95th percentile (ms) | Worst frame (ms) | Graphics-card time, mean (ms) | Game-thread time, mean (ms) | Frames | Video memory used by the editor, peak (MB) | October 5.8 frame mean (ms) | October 5.8 graphics-card mean (ms) |
|---|---|---|---|---|---|---|---|---|---|
| Frontage and context | 8.639 | 10.301 | 19.698 | 6.75 | 6.31 | 1,158 | 5,041 | 12.7 | 10.02 |
| Dense planting | 8.422 | 8.675 | 14.796 | 5.80 | 5.50 | 1,188 | 5,101 | 11.9 | 9.22 |
| Block overview | 8.358 | 8.421 | 10.836 | 6.45 | 5.00 | 1,197 | 5,101 | 12.9 | not read |

### Why these numbers are not yet the baseline

1. **The frame time is pinned.** All three means sit at 8.4 to 8.6 ms, which is 120 frames per second. The monitor runs at 239 Hz, so the display is not the limit. The likely cause is the engine's frame-rate smoothing, whose usual upper limit is 120; this has not been checked. Until the cap is lifted, the frame time says only "faster than 8.3 ms". The graphics-card time is not capped and is the number to compare.
2. **The pixel count differs from October.** The comparison needs a second capture at the pixel count of 2560 by 1440, which this viewport reaches at a screen percentage of 152.
3. **The third view was recorded while the editor was not the front window** (foreground share 0.00, against 1.00 for the other two). The editor is set not to slow down in the background, and the numbers look normal, but the capture should be repeated.
4. **Each view was captured once.** No repeat exists to show the spread.

### Still to capture for profile M0

- The three views again with the cap lifted, at 100 percent and at 152 percent.
- The three views at the settings the editor was found in (every quality group at Cinematic, texture pool 3,000 MB), to show what the difference costs.
- The fixed exterior path, 60 seconds.
- Per-pass graphics-card times at stations S1, S2 and S6. Stations D2 and D5 are interior views and do not exist in this scene.
- Peak video memory for the whole card.

### Positions worked out for the profile

The level's axes, confirmed against the live scene: north is negative X, east is negative Y, units are centimetres, grade is Z = 0.

| Item | Level coordinates (cm) | Basis |
|---|---|---|
| Lot centre line | X = -16236.7 | Earlier registration file |
| Front lot line | Y = -5053.7 | Earlier registration file |
| Building's street face | Y = -5364.8 | Earlier registration file |
| West sidewalk walking line | Y = -3650, eye at Z = 158.2 | Traced in the level: the sidewalk surface is at Z = -1.8 along the whole path |
| Station S1 | (-16236.7, -3650, 158.2), yaw -90, pitch up 12 | Walking line at the lot centre line, facing east |
| Station S2 | (-13736.7, -3650, 158.2), yaw -135, pitch up 10 | 25 m south of S1 |
| Station S6 | (-18991.1, -4843.7, ground + 160), yaw 0, level | 20 m north of the lot's north line on the east sidewalk; ground height not yet traced |
| Fixed path | From (-11736.7, -3650, 158.2) to (-20136.7, -3650, 158.2) in 60 s | 45 m south of S1 to 39 m north of it |
| Point the camera keeps centred | (-16236.7, -5364.8, 303.2) | Centre of the street face, 1 m above the first floor. Provisional: the level holds no building and so no front door. |

A true bearing converts to the level's yaw as: yaw = bearing - 180.

## Findings that bear on the plan

1. **Station S1 as the plan places it is inside a building.** The plan puts the west sidewalk 18 m west of the front lot line, from an assumed 66-foot right-of-way. In the existing model the face of the building on the west side stands about 17.2 m from the front lot line at the lot's centre line, so that point is under its roof. For this baseline the walking line is 14.0 m west of the front lot line, on the modelled sidewalk. Either the model's street is too narrow or the assumption is too wide; Phase 2 measures the real width.
2. **The editor was found at Cinematic quality, not Epic.** Every quality group read 4, and the texture pool read 3,000 MB. The October benchmark used 3 and 1,000 MB. Profiles must state which they use.
3. **The project is larger than the plan records:** 22.4 GB against 17.2 GB. `Intermediate` holds 5.14 GB of files the engine rebuilds.
4. **Free space moves by gigabytes for reasons outside this work.** C: read 17.05 GB at 21:47 and 19.77 GB at 22:12 (the plan recorded 20.8). H: read 233.72 GB and then 230.62 GB; this work wrote nothing to H:. D: 52.86 GB, E: 57.49 GB.
5. **The editor does not slow down when it is in the background** ("Use Less CPU when in Background" is off), which makes captures less sensitive to which window is in front.

## Waiting on the owner

| # | Step | What | Size on disk | Cost |
|---|---|---|---|---|
| 1 | 1.5 | Approve copying the project to `H:\Wieland1529_archives\2026-11-10_pre-phase1\`, without `Intermediate` and `DerivedDataCache` | 17.2 GB on H: (22.4 GB for a complete copy) | None |
| 2 | 1.14 | Approve deleting `Content\Belmont` and `Content\EuropeanBeech`, after the archive exists and after a check that no Wieland asset refers to them | Frees 9.88 GB on D: | None |
| 3 | 1.4 | Set the Windows user variable `UE-LocalDataCachePath` to a folder on D:, then restart the Epic launcher and the editor | The cache on C: is 9.2 GB (`Common\DerivedDataCache` 5.91 GB, `Common\Zen` 3.27 GB) | None; the restart ends the session |
| 4 | 1.8 | Change one element in Revit, export the same 3D view to the same folder under a new name ending `_r2`, and say which element changed | 0.67 GB on E: | None |
| 5 | 1.1 | Approve a pointer file `CLAUDE.md` in the project folder | Under 2 KB | None |
| 6 | - | Say what the panel's permission selector shows | None | None |

## How to resume

1. Read this file, then the last section of `PROJECT_MEMORY.md`.
2. Confirm the level has no unsaved changes before doing anything.
3. Finish step 1.6 with the list under "Still to capture". The capture script is `tools\wieland_profile.py`; the analysis script is `tools\analyze_profile_csv.py`. Lift the cap first (set `t.MaxFPS` to a high value for the capture and put it back to 0 afterwards) and check that the frame time then moves with the load.
4. Run the 50-call server test and the engine's side of the sun check. Both are read-only.
5. Everything else waits for the archive on H:.

## Files written so far

In `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\`:

- `docs\unreal\1529_wieland\phase1_results.md` (this file)
- `docs\unreal\1529_wieland\SITE_MODEL_AUDIT.md` (section appended)
- `docs\unreal\1529_wieland\site_model_audit_materials.json`
- `docs\unreal\1529_wieland\tools\wieland_profile.py`
- `docs\unreal\1529_wieland\tools\analyze_profile_csv.py`
- `docs\unreal\1529_wieland\profiles\2026-11-10_M0\capture_A_views_epic_sp100.json`
- `docs\unreal\1529_wieland\profiles\2026-11-10_M0\capture_A_views_epic_sp100.analysis.json`
- `docs\unreal\1529_wieland\profiles\2026-11-10_M0\csv\front_context.csv.gz`
- `docs\unreal\1529_wieland\profiles\2026-11-10_M0\csv\dense_planting.csv.gz`
- `docs\unreal\1529_wieland\profiles\2026-11-10_M0\csv\block_overview.csv.gz`
- `PROJECT_MEMORY.md` (entries appended)

In `D:\Unreal_Engine_Projects\Wieland1527 5.9\Saved\Profiling\CSV\`, written by the engine's profiler: `Profile(20261110_220258).csv`, `Profile(20261110_220318).csv`, `Profile(20261110_220338).csv`.
