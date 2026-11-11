# Phase 1 results: toolchain setup and first import test in 5.9

Companion to [PLAN.md](PLAN.md). This file is written as each step finishes, so a new session can resume from it.

**Status at 13:25 Central on 2026-11-11: Phase 1 is complete.** All seven acceptance lines that belong to Phase 1 are measured and pass (agent server, baseline, import, reimport, Path Tracer, sun, light units). The soak is no longer part of Phase 1. Every step in the table below is done.

**Three of the passes carry a condition.** The import needs one workaround line in the project's settings file. The Path Tracer needs one ray-tracing setting changed for the length of each render. The reimport needs a rule of use: in 5.9.0, let the editor finish preparing a level's assets before a reimport is started.

**The reimport rehearsal** (step 1.8): 20 of 20 Unreal-side assignments survived the reimport from the owner's second export, and that export's changes arrived (reimport R3, 13:19). A first try at 11:21 (R2) had crashed the editor, with nothing lost, because it began 0.6 seconds after the level finished loading, while the level's meshes were still being prepared. The owner chose to repeat it with that one thing changed, and it worked.

**The Lumen World Cache trial is done** (step 1.12): the difference is visible, the feature is about 0.4 ms cheaper and not dearer, and the setting does not stay, because it moves the picture away from the path-traced render. Its line was taken out of the settings file at 12:59.

**Nothing in Phase 1 waits on the owner except restarting the editor,** which the owner has said will be done. Phase 1's rules and findings were carried into `PLAN.md`, `ENGINE_NOTES.md` and `OPEN_DECISIONS.md` on 2026-11-11, so that a later session finds them without being told; see "Waiting on the owner".

A new session took over at 12:38 on 2026-11-11 from the one that ran out of credit at 11:18. Earlier, the editor crashed at 00:55 when Windows ran out of virtual memory; nothing was lost then either.

**What has been saved in the Unreal project** is listed under "What was saved or changed in the project": three scratch levels' worth of test content under `/Game/Wieland1529/Scratch/`, one line in `Config\DefaultEngine.ini` (a second was added for the World Cache trial and taken out again after it), and three deletions the owner approved. The level `L_R15_Production` and everything under `Content\Wieland\` are unchanged and were never saved over.

## Acceptance list

| Line | Target | Result | Status |
|---|---|---|---|
| Agent server | 50 consecutive read-only calls with no error | **50 of 50 passed.** Median 14 ms a call, slowest 308 ms. | **Pass** |
| Baseline | The three October views at a recorded viewport size, beside the October means | **Measured at 2038 by 782 pixels.** At the pixel count of 2560 by 1440 and October's settings, frame means are 10.8, 9.9 and 10.6 ms against 12.7, 11.9 and 12.9 ms in 5.8. | **Pass** |
| Import | At least 99.5 percent of 3,562 objects and 587 lights; known dimension within 1 mm | **3,562 of 3,562 placed objects and 587 of 587 lights (100 percent each). First floor 2,032.00 mm above grade, against 2,032 mm.** On the fourth attempt, with one settings line added as a workaround for an engine fault. | **Pass, with a condition** |
| Reimport | 20 of 20 assignments survive | **20 of 20 survived the reimport from the owner's second export** (R3, 13:19 on 2026-11-11): 10 of 10 on placed objects and 10 of 10 on meshes. **The export's changes arrived:** 571 lights against 587, 57 accent fixtures against 62, 8 rugs against 1, and 22 meshes imported again. A first try (R2) had crashed the editor because it began 0.6 seconds after the level load; R3 waited until the editor had finished preparing the level's assets. See "Step 1.8". | **Pass, with a rule of use** |
| Path Tracer | Three renders with no crash | **Three 3840 by 2160 renders completed, 48 to 50 seconds each, no crash.** They are correct only with one ray-tracing setting changed; see "Step 1.9". | **Pass, with a condition** |
| Sun | Bearing and height within 0.5 degree of NOAA | **Bearing differs by 0.05 degree, height by 0.06 degree.** | **Pass** |
| Light units | Within 10 percent of 79.6 lux | **79.5 lux** read against a 1,000-lux reference light (0.15 percent low); 76.6 lux if the test card is taken as an ideal matte surface (3.8 percent low) | **Pass** |
| Soak | Two hours, no crash, video memory growth of 5 percent or less | Not run, by the owner's decision; moved to Phase 9, where it runs on the finished scene | **Not part of Phase 1** |

## Where each step stands

| No. | Step | Status |
|---|---|---|
| 1.1 | Agent server starts with the editor; model confirmed; pointer file | Server and model confirmed. The server started by itself at every editor launch. `bAutoStartServer` is in none of the project's settings files, so where that comes from is not established. The pointer file `CLAUDE.md` was written at 23:29 on 2026-11-10 without the owner's explicit approval and **removed at 00:18 on 2026-11-11 on the owner's word**. A session started in the project folder therefore does not load the plan's rules by itself; give it the resume text under "How to resume". |
| 1.2 | List the tool sets | **Done.** 109 tool sets, listed at the end of this file. |
| 1.3 | Finish the live audit | **Done.** Appended to [SITE_MODEL_AUDIT.md](SITE_MODEL_AUDIT.md). |
| 1.4 | Move the engine cache to D: | **Done by the planning session at 22:05**, with the editor restarted at 22:08. Confirmed by this session at 22:37: `D:\UE_DerivedDataCache` held 1.57 GB in 92 files and was still being written. The plan's cap is 20 GB. |
| 1.5 | Archive the project to H: | **Done at 23:28**, approved by the owner. See "Step 1.5". |
| 1.6 | Baseline profile M0 | **Done.** [profiles/2026-11-10_M0/profile.md](profiles/2026-11-10_M0/profile.md). |
| 1.7 | Import the Datasmith file into a scratch level | **Done** on the fourth attempt, at 00:39 on 2026-11-11. See "Step 1.7". |
| 1.8 | Reimport rehearsal | **Done.** Reimport R1 from the unchanged file kept 20 of 20 assignments. Reimport R2 from the owner's second export crashed the editor at 11:22:20 on 2026-11-11, with nothing lost; its cause is recorded. Reimport R3 at 13:19, the same reimport made after the editor had finished preparing the level's assets, worked: 20 of 20 survived and the export's changes arrived. Saved by name at 13:21. See "Step 1.8". |
| 1.9 | Three path-traced renders of station S1 | **Done.** See "Step 1.9". |
| 1.10 | Sun direction against the NOAA calculator | **Done**, for the engine's sun calculation and for a sun placed in a level. See "Step 1.10". |
| 1.11 | 1,000-lumen light, illuminance at 1 m | **Done.** See "Step 1.11". |
| 1.12 | Lumen World Cache and overlapping glass, on and off | **Done.** Overlapping glass: 0.3 ms, no visible difference at S1, not kept for now. Lumen World Cache, tried at 12:47 to 12:58 on 2026-11-11: visible difference, about 0.4 ms cheaper, not kept, because it moves the picture away from the path-traced render; its settings line was taken out at 12:59. See "Step 1.12". |
| 1.13 | Two-hour soak | **Not run, by the owner's decision; moved to Phase 9, where it runs on the finished scene** (`PLAN.md`, step 9.11). A run was started at 00:02:43 on 2026-11-11 and stopped at 00:09:58 on the owner's instruction, after 7 of 120 walks, with no crash. It is not a result. Its short log is kept in `review\phase1\soak\` as a trial of the soak script. The trial showed two faults in the script, both now corrected and neither re-run; see `PROJECT_MEMORY.md`. |
| 1.14 | Remove the Belmont and beech content | **Done.** The two folders at 00:01 and, with the owner's further approval, the Belmont recovery level at 00:18 on 2026-11-11. See "Step 1.14". |
| 1.15 | This file | **Done.** |

## Checks made before any work

| Check | Result |
|---|---|
| One read-only call to the editor | Succeeded. `list_toolsets` answered. |
| Model | Fable 5.2 (`claude-fable-5-2`), as pinned by the project's `.claude\settings.json` |
| Permission mode of the panel | Cannot be read from inside the session. The editor log from the panel's start says "tool access mode from host settings: auto", and the project's settings file sets no permission rules, so it is most likely Auto. That mode does not ask before each edit. The owner has not yet said what the selector shows. |
| File access to the `E:` paths | Yes |
| Git | Yes, 2.55.0, with Git LFS 3.7.1. Branch `claude/1529-wieland-scene-plan-e84a03`. |
| Web browser | Yes, as it turned out. A connected tool drives a real browser without a window; it read the NOAA calculator in step 1.10. |
| Revit and Google Drive connections | Not present. Phase 1 does not need them. |

## Acceptance: agent server

A script outside the panel opened its own session with the editor's server at `http://127.0.0.1:8000/mcp` and made 50 calls one after another at 22:55, rotating through ten tools that the server itself marks as read-only (level, camera, viewport, console variable, frame timings, selection, skills, and the listing tools).

| Measure | Value |
|---|---|
| Calls | 50 |
| Passed | 50 |
| Failed | 0 |
| Time per call | fastest 7.6 ms, median 14.1 ms, mean 22.9 ms, slowest 307.7 ms (the skills list, 52,000 characters) |
| Server | `unreal-mcp`, version 5.9.0-60351404 |

Record: `review\phase1\agent_server_50_calls.json`. Script: `tools\mcp_readonly_calls_test.py`.

Separately, this session's own work through the panel made 34 calls to the server by 23:10. One returned an error, caused by a fault in the script I sent and not by the server. Two more scripts met an error inside themselves and reported it back normally. All three are logged in `PROJECT_MEMORY.md`.

## Step 1.2: tool sets

The server offers **109 tool sets** and 70 top-level tools, counted at 21:46 and again after the 22:08 restart. The earlier figure of 115 is reproduced exactly by also counting six lines of description text ("Graph", "Node" and "Pin", twice each) that look like entries, so 109 is the count and nothing went missing.

The sets Phase 1 uses are all present: actors, levels, assets, materials, static meshes, scene capture, the three performance sets (frame timings, per-pass GPU profiler, CSV reader), console variables, logs, configuration settings, Python, file system, Fab and project skills. The top-level tools include the ones that trigger Movie Render Graph renders.

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

## Step 1.6: baseline profile M0

The full profile, with its conditions and method, is [profiles/2026-11-10_M0/profile.md](profiles/2026-11-10_M0/profile.md). The main figures:

**Viewport size: 2038 by 782 pixels**, field of view 90 degrees. "152 percent" means the scene is drawn at 3098 by 1189, which is the pixel count of 2560 by 1440. "Epic" is the October benchmark's quality level; "Cinematic" is the level the editor was found at.

| View | October, 5.8, Epic: frame mean (ms) | Now, 5.9, Epic, 152 percent: frame mean (ms) | 95th percentile (ms) | Graphics-card mean (ms) | Now, Cinematic, 152 percent: frame mean (ms) |
|---|---|---|---|---|---|
| Frontage and context | 12.7 | 10.8 | 13.2 | 9.5 | 19.8 |
| Dense planting | 11.9 | 9.9 | 12.0 | 8.6 | 22.1 |
| Block overview | 12.9 | 10.6 | 12.7 | 9.3 | 19.7 |

| Fixed exterior path, 60 seconds | Frame mean (ms) | 95th percentile (ms) | Worst frame (ms) |
|---|---|---|---|
| Epic, 100 percent (about the real-time tier's pixel count) | 7.8 | 9.7 | 17.9 |
| Epic, 152 percent | 10.5 | 12.6 | 19.4 |
| Cinematic, 152 percent | 20.4 | 22.8 | 30.4 |

| Other measures | Value |
|---|---|
| Sum of the graphics-card budget rows at stations S1, S2 and S6, Epic, 100 percent | 7.9, 7.8 and 7.9 ms of the 14.5 ms budget |
| The same at 152 percent | 12.6, 12.4 and 13.9 ms; global illumination, sky and upscaling exceed their rows |
| Video memory used by the editor, peak | 5.5 GB at Epic, 6.7 GB at Cinematic |
| Video memory used on the whole card, peak | 8.0 GB of 16 GB, against a 13.0 GB budget |
| Game thread | 5.0 to 6.2 ms, inside its 8.0 ms budget |

What it means for the plan:

1. **5.9 is not slower than 5.8 on this scene.** At October's settings and about the same pixel count, 5.9 is 15 to 18 percent quicker per frame. The October viewport size is unknown, so this is an indication.
2. **At Cinematic quality the existing scene already misses 60 frames per second** at the pixel count of 2560 by 1440 (45 to 51 frames per second). The editor is set to Cinematic. The plan's real-time tier needs a stated quality level; this baseline uses Epic.
3. **At the full pixel count, three budget rows are already exceeded** with no building, no interior and 11 trees. This supports rendering the real-time tier at 67 percent.
4. **The editor caps itself at 120 frames per second when no cap is set.** Every profile must lift the cap (`t.MaxFPS 1000`) or light scenes all read 8.3 ms.
5. **The path must be walked once before it is recorded.** The first walk after the editor restart had 27 frames longer than 33 ms, the worst 106 ms; none recurred.

### Positions used, in level coordinates

The level's axes, confirmed against the live scene: north is negative X, east is negative Y, units are centimetres, grade is Z = 0. A true bearing converts to the level's yaw as: yaw = bearing - 180.

| Item | Level coordinates (cm) | Basis |
|---|---|---|
| Lot centre line | X = -16236.7 | Earlier registration file |
| Front lot line | Y = -5053.7 | Earlier registration file |
| Building's street face | Y = -5364.8 | Earlier registration file |
| West sidewalk walking line | Y = -3650, eye at Z = 158.2 | Traced in the level: the sidewalk surface is at Z = -1.8 along the whole path |
| Station S1 | (-16236.7, -3650, 158.2), yaw -90, pitch up 12 | Walking line at the lot centre line, facing east |
| Station S2 | (-13736.7, -3650, 158.2), yaw -135, pitch up 10 | 25 m south of S1 |
| Station S6 | (-18991.1, -4843.7, 156.8), yaw 0, level | 20 m north of the lot's north line on the east sidewalk; ground traced at Z = -3.2 |
| Fixed path | From (-11736.7, -3650, 158.2) to (-20136.7, -3650, 158.2) in 60 s | 45 m south of S1 to 39 m north of it |
| Point the camera keeps centred | (-16236.7, -5364.8, 303.2) | Centre of the street face, 1 m above the first floor. Provisional: the level holds no building and so no front door. |

## Step 1.10: sun direction

Case: 15 August 2026, 15:30:00 Central Daylight Time, lot centre (latitude 41.910215, longitude -87.635389).

| Source | Bearing (degrees from true north) | Height above the horizon (degrees) |
|---|---|---|
| Engine 5.9.0: the Sun Position plugin's calculation | 241.72 | 46.40 with atmospheric bending; 46.38 without |
| NOAA Solar Calculator page, read on 2026-11-10 | 241.67 | 46.34 (the page includes atmospheric bending) |
| Difference | **0.05** | **0.06** |
| Tolerance | 0.5 | 0.5 |

How it was done:

- The engine's value came from the plugin's own function, called with the site's inputs. The function returns the height plus 180 degrees (226.40); that offset is the plugin's convention and is removed here. Giving the time as "zone -6, daylight saving on" or as "zone -5, daylight saving off" returns identical values, so the plugin's daylight-saving switch works as expected. West longitude is negative.
- The NOAA page was opened in a browser without a window, the inputs were entered, and the results were read from the page's own fields. The page showed time zone America/Chicago, offset -05:00, 15 August 2026, 15:30:00; it also gave solar noon at 12:55:06, sunrise 05:59 and sunset 19:51.
- As a third check, NOAA's published equations run separately reproduce the page to two decimals (241.667 and 46.340).

The plan's hand-calculated figures (about 46 degrees, bearing about 242) agree.

**The same check on a sun placed in a level**, made on 2026-11-11 in the scratch level `L_P1_LightUnits` with the engine's sun-and-sky actor, which was removed again afterwards:

| Reading | Bearing (degrees) | Height (degrees) |
|---|---|---|
| The placed sun, read from the direction of its light | 241.80 | 46.48 |
| NOAA for 2026 | 241.67 | 46.34 |
| Difference | 0.13 | 0.14 |

Three things this showed, all for Phase 8:

1. **The actor's north setting must be 180 in this project.** With its north offset at 0 the actor takes the level's +X as north. This project's levels have north at -X. At 180 the light comes from the right direction. Whatever Phase 2 measures for the street's turn from true north is added to that. The existing production level has 35, the engine's template value.
2. **The actor's year cannot be set on a placed sun.** It is fixed at 2019 inside the actor's Blueprint (its editable definition), and the editor refuses a change on the placed copy. That is why the placed sun is 0.13 degree from NOAA where the bare calculation is 0.05. Either the Blueprint's default is changed, or 0.15 degree is accepted.
3. The actor's daylight-saving dates are also 2019's (10 March to 3 November). For 15 August that makes no difference.

Record: `review\phase1\sun_check.json`.

## Step 1.5: archive

Copied at 23:23 to 23:28 to `H:\Wieland1529_archives\2026-11-10_pre-phase1\Wieland1527 5.9\`, leaving out `Intermediate` and `DerivedDataCache`, which the engine rebuilds.

| Measure | Value |
|---|---|
| Files copied | 11,657 of 11,658 |
| Size | 17.24 GB |
| `Content`, `Config`, `Backups`, `ImportStaging`, `.claude` and the four files at the root | Identical to the source in file count and bytes |
| The one file not copied | `Saved\AgentBridge\writer.lock`, 1 byte, held open by the running editor. It is not project content. |
| Log | `review\phase1\archive_2026-11-10_pre-phase1.robocopy.log` |

The lock belongs to `shb_agent_bridge`, a helper the earlier R15 work left in `Content\Python\`. It starts with the editor and runs jobs that another program drops into `Saved\AgentBridge\pending\`. It was idle all evening. It is a second way into this editor, so the one-writer rule covers it too.

## Step 1.7: Datasmith import

What the file holds, counted from the file itself: 1,294 meshes, 3,562 placed mesh objects, 587 point lights, 155 empty holder objects, 1 camera, 94 textures, and **280 materials**. The plan's "2,072 materials" is the number of material slots on the meshes. The file uses the same coordinates as the existing level, in centimetres: floor element 12330199 sits at Z = 161.61 with a thickness of 41.59, so its top is at 203.20, which is the plan's 2.032 m. The file is not strict XML (nine texture paths hold a bare "&").

The known-dimension check is therefore: after import, the top of element 12330199 should be 203.2 cm above the top of the site element `Site_GRADE_GRADE`, within 0.1 cm.

### Attempts

Each attempt is written here before it is made.

| No. | Time | What was tried | Settings | Outcome |
|---|---|---|---|---|
| 1 | 23:32 | Import into the empty scratch level `/Game/Wieland1529/Scratch/L_P1_DatasmithImport`, assets to `/Game/Wieland1529/Scratch/P1` | Everything included; lightmap UV generation off; engine cache emptied 85 minutes before; Substrate on | **Editor crashed** on the assertion `ShaderMapId.ContainsShaderType(ShaderType, kUniqueShaderPermutationId)` in `MaterialShader.cpp` line 2653, naming the material shader map `RevitReference`. Nothing was left on disk except the empty level. Crash record: `Saved\Crashes\UECC-Windows-7B156D5548BE86A0C033DDA1C171F70E_0001\`. |
| 2 | 23:45 | The same import, repeated unchanged, after the editor restart. Before it: the Datasmith parent material `/DatasmithContent/Materials/RevitReference` was loaded in the scratch level and no shader compiler process was running. Purpose: learn whether the crash repeats once shaders are no longer compiling. | As attempt 1: everything included; lightmap UV generation off; Substrate on; same level and asset folder | **Editor crashed** at 23:45:18, about 20 seconds into the import, on the same assertion and the same material (`Metal_-_Stainless_Steel`, parent `RevitReference`, "is missing expected shader type TShadowDepthPSCombined"). So the crash repeats and does not depend on shaders compiling in the background. Nothing was left on disk. Crash record: `Saved\Crashes\UECC-Windows-4B47E20049E2F30ADC524CB84F0C1600_0000\`. |
| 3 | 23:58 | The same import with one console variable changed for this editor run only, not saved: `r.Material.UseShaderCompilationParameters` from 1 to 0. This is the temporary workaround an Epic staff member gave for this assertion in engine 5.8 (https://forums.unrealengine.com/t/cooking-crash-materials/2738422, post of 12 June 2026; lead supplied by the owner). It makes the engine decide which shaders to compile from the material's conservative data, at the cost of compiling some shaders that are not needed. Untested in 5.9. Procedure: set the variable in the running editor and read it back; if the editor refuses, make no import and ask the owner; otherwise wait for any shader compiling to stop, then import. Shader compile time and cache growth are recorded. **By the owner's instruction, if this attempt crashes, importing stops and the variable is put back.** | As attempt 1 otherwise: everything included; lightmap UV generation off; Substrate on; same level and asset folder | **Not made.** At 23:53 the running editor refused the change ("r.Material.UseShaderCompilationParameters is read only!") and the value stayed 1, so the variable applies only at startup. No import was started and nothing was changed. Proposed to the owner: add the line `r.Material.UseShaderCompilationParameters=0` at the end of the section `[/Script/Engine.RendererSettings]` in `Config\DefaultEngine.ini`, then restart the editor. **The owner said yes at 00:17 on 2026-11-11, and the line was written at 00:18** as line 43 of `Config\DefaultEngine.ini` (2,468 bytes before, 2,513 after). It takes effect at the next editor start. The import itself is journaled as attempt 4 once the variable reads 0. |
| 4 | 00:41 | The same import with Epic's workaround in force. The owner restarted the editor at 00:32. Confirmed before the attempt: `r.Material.UseShaderCompilationParameters` reads 0 in the running editor, and this start's log shows "Set CVar [[r.Material.UseShaderCompilationParameters:0]]". Cost of the setting at startup: none measurable. The log shows no shader compiling after the start, no shader compiler process was running five minutes later, and the cache held 2.003 GB, as before (250 files against 235). Any cost during the import is measured from the cache size and the log afterwards. **By the owner's instruction, if this attempt crashes, importing stops and line 43 of `Config\DefaultEngine.ini` is taken out again.** | As attempt 1 otherwise: everything included; lightmap UV generation off; Substrate on; level `/Game/Wieland1529/Scratch/L_P1_DatasmithImport`, assets to `/Game/Wieland1529/Scratch/P1`; record to `review\phase1\datasmith_import_attempt4.json` | **No crash. The import call returned success at 00:39 after 28.2 seconds**, reporting 1,294 meshes and 2,602 actors. Counts against the file, the dimension check, the saves and the cost in shader compiling are recorded below under "Result of attempt 4" as each is made. |

### Result of attempt 4

The import ran at 00:39 on 2026-11-11 in the scratch level `/Game/Wieland1529/Scratch/L_P1_DatasmithImport` and took 28.2 seconds. The editor did not crash. Record: `review\phase1\datasmith_import_attempt4.json`.

| Measure | In the file | Arrived | Share |
|---|---|---|---|
| Placed mesh objects | 3,562 | 3,562 | 100 percent |
| Lights | 587 | 587 | 100 percent |
| Meshes | 1,294 | 1,294 | 100 percent |
| Materials | 280 | 280 | 100 percent |
| Textures | 94 named | 72 (65 images and 7 light-distribution files) | 9 image files named in the file are not in the export folder; see below |
| Camera | 1 | 1 | |

How the objects arrive: Unreal makes 2,602 actors (its word for objects placed in a level) from them. 1,935 of those carry the 3,562 meshes and 557 carry the 587 lights, because Datasmith attaches the parts of some Revit families to one actor. A count of actors alone would read 1,935 and 557 and look like a shortfall; the count must be of mesh and light parts.

**Known dimension.** The floor with Revit element ID 12330199 (type `Floor Generic - 1'-2"`, on the level 1ST FLOOR) has its top at Z = 203.2000 cm. The site element `Site_GRADE_GRADE` has its top at Z = 0.0000 cm. The first floor is therefore 2,032.00 mm above grade, against 2,032 mm in the drawings: a difference under 0.01 mm. The same floor measures 1,320.80 cm across, the building's 13.208 m width.

**Position.** The import sits in the existing level's coordinates with no adjustment: its floor lies at the level coordinates the earlier registration file gives for the lot. Phase 3 can place the building by importing it, without re-registering.

**Saved.** The imported assets (1,647 files, 0.71 GB, under `Content\Wieland1529\Scratch\P1\`) and the scratch level (12.2 MB) were saved by name at 00:40. Nothing else was saved.

**What the workaround cost.**

| Measure | Value |
|---|---|
| At editor start, with the line in force | Nothing measurable: no shader compiling in the log, cache unchanged at 2.003 GB |
| During and after the import | 82 shaders compiled; 45 seconds with a compile job running; 314 seconds of processor time over 8 workers |
| Cache growth | 2 MB (2.003 GB to 2.005 GB) |
| Of 21,702 shader requests | 77 percent were already in the cache and 21 percent in memory |

Most of the shaders the import needed were already in the cache, left there by the two crashed attempts. An import into an empty cache will take longer; that is the import's own cost, not the workaround's. The workaround's own share is the 82 extra shaders.

**The condition on this pass.** The import works only with the line `r.Material.UseShaderCompilationParameters=0` in `Config\DefaultEngine.ini`. It is a temporary workaround for an engine fault that Epic described for 5.8. It stays in the project until an engine update fixes the fault; each engine update should be tested by taking the line out and importing once.

**Found in the import, for later phases.**

1. **Nine image files are missing from the export.** The file names them, and Revit did not write them into the export folder, so the materials that use them arrive without those images: `Bandalux_9920.png`, `Bandalux_OpennessFactor_Simulator.png`, `diffuse_Oak Veneered MDF Staggered 51.2 x 78 inches (NG7H6O) (5).jpeg`, `Endicott SN-8 Black Glazed Thinbrick Modular Stack 11.3 x 24.5 inches bump.jpg`, `Endicott SN-8 Black Glazed Thinbrick Modular Stack 11.3 x 24.5 inches texture.jpg`, `ETH_Teak_NaturalOutdoor.jpg`, `Material_Leaf_N2D.png`, `RS10242_Wall_BoothBayBlue_BW.jpg`, `White Aluminum.jpg`. In Revit these are materials whose image paths do not resolve on the exporting computer.
2. **One object lies about 865 m from the building.** A generic model, Revit element ID 18049581, about 0.6 by 2.9 by 2.7 m, at 441 m north and 885 m east of the model's origin. Every other mesh object is within 60 m of the building. It is probably a stray element in the Revit view.
3. **The lights carry no physical units.** All 587 arrive as point lights with unitless intensity (9.3 to 6,870, median 100). 60 carry a light-distribution file. All cast shadows. Phase 8, which wants every fixture at its real output, has to convert them.
4. **No imported mesh is set to Nanite** (checked on 60). Phase 3 decides that.
5. **The editor held 24.4 GB of memory after the import**, just over the plan's 24 GB budget for it, with the production level's content still in memory from earlier in the run.
6. **1,301 warnings "Missing actor referenced in metadata"** were logged. They are Revit data blocks in the file that name no placed object (the file holds 5,589 such blocks, and 4,288 of them name a placed object). No placed object lacks its data: all 2,600 imported actors and all 1,657 parts attached to another actor carry their Revit data (category, family, type and the rest), checked one by one.


### The ways forward that were weighed before attempt 4

Option A below was taken on 2026-11-11 with the owner's yes, and it worked. The others were not needed. The table is kept as the record of what each would have cost.

The crash is repeatable: both attempts stopped at the same point, when the importer made its first material from Datasmith's Revit parent material, `RevitReference`. The engine then found that the set of shaders it had built for that parent did not include one it expected (`TShadowDepthPSCombined`). An Epic staff member described this assertion for engine 5.8 and named a temporary workaround.

| Option | What it keeps | What it costs | What is known |
|---|---|---|---|
| A. Epic's workaround: one line in `Config\DefaultEngine.ini` and a restart. **Taken; it worked (attempt 4).** | Everything: reimport, the Revit data on each object, Revit's materials | A project-wide setting; shaders are rebuilt once, and the time and cache growth will be measured | Untested in 5.9. By the owner's instruction, a crash with it set ends the import attempts. |
| B. Import without materials, an option of the importer itself | Geometry, lights, the Revit data on each object, reimport | Revit's materials do not arrive; all 280 would be made in Unreal. The plan's default was to keep them as exported. | Untried. It skips the step that crashes. It is still an import, so it needs the owner's word after a third crash. |
| C. The FBX route, the plan's named fallback | Geometry | Loses reimport and the Revit data on each object; materials are made in Unreal | Worked in October on 5.8 |
| D. Substrate off for the whole project | Possibly everything | Changes how every material in the project is drawn. The owner's decision. | No evidence points to it: the assertion concerns which shadow shaders are built, not Substrate. Not recommended on what is known. |

A caution that follows from the same fault, **not tested**: the project already holds October's Datasmith imports under `/Game/Wieland/Revit1527` (1,720 assets). 356 of their materials use the same parent, `RevitReference`. None is loaded. Opening the two levels there, `L_Wieland_Revit_Integration_r01` and `L_Pilot`, may crash this 5.9.0 editor in the same way. They were not opened.


## Step 1.8: reimport rehearsal

The question: when the Revit model changes and is exported again, does work done in Unreal on the imported building survive the reimport?

**The 20 Unreal-side assignments**, made at 00:47 on 2026-11-11 in `/Game/Wieland1529/Scratch/L_P1_DatasmithImport` and saved. They are of two kinds, because Unreal keeps them in two different places. The table with full paths is `review\phase1\reimport_assignments.json`.

Ten on placed objects. Each replaces the first material of one object in the level with the marker material `M_P1_Marker_OnObject` (magenta). The change is stored in the level.

| No. | Revit category | Object | Revit element ID | Material it replaced |
|---|---|---|---|---|
| 1 | Walls | `Walls_Basic_Wall_B2010_Exterior_Wall_Havord_block_w__1_GYP_14` | 10534415 | `Concrete_Masonry_Units` |
| 2 | Floors | `Floors_Floor_Wood_Joist_16__-_Wood_Finish` | 10534437 | `Calacatta_Vena_None_86_6_x_43_4_inches__M4W6HI_` |
| 3 | Doors | `Doors_Door-Garage-Flush_Panel_-_Copy_16__X_7_` | 10663660 | `Acrylic_-_Waterworks_-_White` |
| 4 | Windows | `Windows_Window-Single_Hung-Marvin-Essential_3_4__x_8_8_` | 10765950 | `Ultrex-Marvin-Pebblegray` |
| 5 | Casework | `Casework_Countertop146_Countertop` | 11998145 | `Countertop_1_` |
| 6 | Ceilings | `Ceilings_Compound_Ceiling_GWB_58` | 15744361 | `Gypsum_Wall_Board` |
| 7 | Furniture | `Furniture_Bed_simpleBoxFrame_Queen_Pillow_double_1900x1385w_11` | 12017319 | `Textile_-_White` |
| 8 | Plumbing Fixtures | `Plumbing_Fixtures_Washer_PW_6080_Miele_Drain_Pump_5` | 12459707 | `Finish_-_Black` |
| 9 | Structural Columns | `Structural_Columns_Timber-Column_6x6_3` | 11210177 | `Cedar` |
| 10 | Lighting Devices | `Lighting_Devices_Lighting_Switch_3_Way` | 15597595 | `RNT_Material` |

Ten on meshes. Each replaces the first material of one imported mesh with the marker material `M_P1_Marker_OnMesh` (cyan). The change is stored in the mesh, so every object that uses that mesh shows it.

| No. | Revit category | Mesh | Material it replaced |
|---|---|---|---|
| 11 | Generic Models | `Generic_Models_SURROUNDING_BUILDINGS_SURROUNDING_BUILDINGS` | `00_Soffit_2_Color_White` |
| 12 | Lighting Fixtures | `Lighting_Fixtures_Recessed_Can_Light_18377_2_Recessed_Can_Light_18377` | `LIGHT_BULB_BRASS` |
| 13 | Specialty Equipment | `Specialty_Equipment_Display-LG_Electronics-US340C_Free_Standing_-_65”_UHD_Signa` | `Metal_-_LG_Electronics_-_Black` |
| 14 | Structural Framing | `Structural_Framing_Structural_Framing_6_Structural_Framing_1` | `Cedar` |
| 15 | Roofs | `Roofs_Basic_Roof_Generic_-_8___w_TPO` | `white_plastic` |
| 16 | Railings | `Railings_Railing_Fence_-_Regular` | `Wood` |
| 17 | Supports | `Supports_Stringer_Stringer_-_2__Width_8` | `09_23_00_Gypsum_Wall_Board` |
| 18 | Landings | `Landings_Non-Monolithic_Landing_Non-Monolithic_Landing` | `Finishes_-_Flooring__Oak` |
| 19 | Runs | `Runs_Non-Monolithic_Run_2__Tread_1__Nosing_1_4__Riser_2` | `Finishes_-_Flooring__Oak` |
| 20 | Electrical Fixtures | `Electrical_Fixtures_33816_33815_PUNT_Black_ceiling_fan_with_DC_motor` | `FARO_Black` |

**An extra check, outside the 20.** Because a reimport rewrites every imported material, three imported materials were also edited directly at 00:49, to learn whether such edits survive: `00_Soffit_2_Color_White`, `KM3054_Grate_Finish` and `z_Miele_Design_Zinc_Steel` each had their colour set to (0.123, 0.456, 0.789) and their glossiness to 0.321, and were saved. Their earlier values are in `review\phase1\reimport_assignments.json`. The next reimport shows whether the edits hold.

### Reimports

Each reimport is written here before it is made, as with the import.

| No. | Time | What was tried | Outcome |
|---|---|---|---|
| R1 | 00:50 | Reimport of the imported scene from the **same, unchanged file**, with the importer's defaults (update the placed objects; do not bring back deleted ones). Purpose: prove the reimport route works in 5.9.0 with the workaround in force, and see whether the 20 assignments survive a reimport in which nothing changed. It does not replace the rehearsal with the owner's changed export. | **No crash; success in 24.5 seconds at 00:47.** No mesh was imported again, because none had changed. **20 of 20 assignments survived**: 10 of 10 on objects and 10 of 10 on meshes. The level still holds 3,562 mesh objects and 587 lights. The reimport did rewrite all 280 imported materials, 22 textures and 7 light-distribution files, although nothing had changed in the file; they and the level were saved again by name afterwards. Record: `review\phase1\datasmith_reimport_R1.json`. |
| R2 | 11:22 on 2026-11-11 | **The rehearsal proper:** reimport from the owner's second export, `25-006_1527_N_Wieland-3DView-3D_View_188_r2.udatasmith`, written 11:08. The owner swapped some light fixtures. Compared with the first file it holds 571 lights against 587, 1,288 meshes against 1,294, 284 materials against 280; 22 placed objects are gone and 14 are new; 13 meshes keep their name with changed content. Method: point the imported scene's recorded source file at the second export, then reimport with the importer's defaults. Workaround line in force. | **The editor crashed at 11:22:20, 28 seconds into the reimport.** Engine assertion (a built-in self-check that stops the program) `StaticMeshDescriptionBulkData != nullptr`, `StaticMeshSourceData.cpp` line 326, with `DatasmithSceneElement.ReimportScene` on the script stack. Not a memory failure. Nothing reached disk, so R2 gives no count of surviving assignments. Found at 12:38 by the session that took over; see "Reimport R2: the crash and its cause" below. Crash record: `Saved\Crashes\UECC-Windows-86D475F047311BC81EFD42A667941506_0001`. |
| R3 | 13:18 on 2026-11-11 | **Way forward A, chosen by the owner** in answer to the 13:06 report ("proceed with your recommendations": A, then B if A crashes, then C). The same reimport as R2 with one change: the level is loaded in one call; in a separate call the editor is made to finish preparing every asset (`finish_all_asset_compilation()`), and the counts and the 20 assignments are read as the "before" state; only then is the scene asset pointed at the second export and reimported with the importer's defaults. Workaround line in force. Free physical memory 7.8 of 31.1 GB, free commit 24.5 of 79.1 GB, Revit closed, editor at 15.5 GB. | **No crash; success in 36.2 seconds, 13:19:56 to 13:20:32. 20 of 20 assignments survived** (10 of 10 on objects, 10 of 10 on meshes), and the three materials edited directly kept their edits. **The second export's changes arrived:** 571 lights against 587, 22 meshes imported again (the 13 changed and the 9 new). The level had been loaded for 52 seconds and asset preparation had finished when the reimport began. Saved by name at 13:21. See "Reimport R3: result" below. Records: `review\phase1\datasmith_reimport_R3.json`, `_R3_before.json` and `_R3_after.json`. |

### Reimport R3: result

**20 of 20 Unreal-side assignments survived a reimport from the owner's second export, and the changes in that export arrived.** The acceptance line passes, with one rule of use: in 5.9.0, let the editor finish preparing a level's assets before starting a reimport.

What was done, in order, each in its own call to the editor: the scratch level was loaded (13:18:56 to 13:19:03); the editor was made to finish preparing every asset, which returned at once, six seconds after the load (`tools\wieland_datasmith.py`, `finish_asset_compilation()`); the "before" state was read; the scene asset's recorded source file was pointed at the second export; the reimport ran with the importer's defaults (13:19:56 to 13:20:32). The same reimport, started 0.6 seconds after the level load, had crashed the editor as R2. So the reading of the cause under "Reimport R2" held, and waiting is enough. Way forward B was not needed.

| Measure | Before R3 | After R3 | The second export holds |
|---|---|---|---|
| Assignments on placed objects still in place | 10 of 10 | **10 of 10** | - |
| Assignments on meshes still in place | 10 of 10 | **10 of 10** | - |
| Imported materials edited directly, edit still in place | 3 of 3 | **3 of 3** | - |
| Light components in the level | 587 | 571 | 571 |
| Imported mesh components in the level | 3,562 | 3,562 | 3,562 |
| Different imported meshes in use | 1,294 | 1,288 | 1,288 |
| Mesh components of the Focal Point accent fixture | 62 | 57 | 57 |
| Mesh components of the Fritz Hansen rug | 1 | 8 | 8 |
| Meshes imported again | - | 22 | 13 changed and 9 new |

The level also holds one mesh component that is not from the import, the editor's own marker on the imported camera `3D_View_188`; it is left out of the counts above. The counts are of components, read with `count_components()`, and the assignments with `check_assignments()`, both in `tools\wieland_datasmith.py`. The same two functions gave the "before" and the "after" figures.

**Three things the rehearsal shows for Phase 3:**

1. **Both kinds of Unreal-side work survive a reimport that changes the model:** a material put on one placed object (stored in the level), and a material slot changed on an imported mesh (stored in the mesh). So do colour and glossiness set directly on an imported material, although the reimport rewrote all 284 materials. This held for objects and meshes the export did not change; an assignment on a mesh that the export changes was not tested, because none of the 20 sat on one.
2. **Labels are not stable across a reimport; Revit element IDs are.** The marked ceiling kept its marker material and its Revit element ID 15744361, but its label changed from `Ceilings_Compound_Ceiling_GWB_58` to `Ceilings_Compound_Ceiling_GWB_57`, because the owner had removed one ceiling and Unreal numbers same-named objects in order. Another ceiling now carries the label `_58`. A script that finds objects by label would have picked the wrong one. Every later script must find objects by Revit element ID.
3. **A reimport does not delete what the new export no longer has.** The removed objects left the level, but the mesh files of 10 removed meshes and the file of 1 removed material are still in the folder, unused. Over many reimports the folder will collect such files; clearing them is a deletion and needs the owner's approval.

**On disk after saving** (13:21, the level and the 374 changed assets, each by name; nothing else): `L_P1_DatasmithImport.umap` 12.7 MB; `Content\Wieland1529\Scratch\P1\` 1,670 files and 0.96 GB, against 1,647 files and 0.71 GB before. The growth of 0.25 GB is larger than the "few MB" estimated in the table of ways forward, and nearly all of it is one texture: the second export's folder holds 76 image files against the first's 64, among them a 16,000-pixel Indiana limestone image (`...Tranche-2-001-COLOR-16K`, 211 MB in the project) that the first export named but did not contain. Its companion (`...Tranche-1...`, 631 MB) was already there. Those two textures are 0.84 GB of the folder's 0.96 GB, which matters for the video-memory budget in Phase 5. The scene asset now records the second export as its source file. No error was logged and no crash record was written.

**Eight texture files that the export names were not in its folder,** so the materials that use them came in without them. These are for the owner to look at in Revit, where the material's image path probably points at a file Revit could not find at export: `RS10242_Wall_BoothBayBlue_BW.jpg`, `ETH_Teak_NaturalOutdoor.jpg`, `Endicott SN-8 Black Glazed Thinbrick Modular Stack 11.3 x 24.5 inches texture.jpg` and its `bump.jpg`, `Material_Leaf_N2D.png`, `White Aluminum.jpg`, `Bandalux_9920.png` and `Bandalux_OpennessFactor_Simulator.png`. Three more entries name only `generic`. Checked afterwards: the first export names the same eight files and its folder lacks them too, and none of the eight is on drive C:, D: or E:.

### Reimport R2: the crash and its cause

Found at 12:38 on 2026-11-11 by the session that took over from the one that journaled R2. Sources: the editor's log of that run (`Saved\Logs\Wieland1527-backup-2026.11.11-17.22.45.log`; its clock is UTC, six hours ahead of Central), the crash record, and the engine's source files under `D:\Games\UE_5.9\Engine\`. No reimport was repeated to find this.

| Time | What the log shows |
|---|---|
| 11:21:44 | The scratch level `L_P1_DatasmithImport` starts to load |
| 11:21:52.07 | The level has finished loading |
| 11:21:52.67 | The reimport from the second export is already running: it reads the file, then brings in its textures |
| 11:22:20.85 | Assertion `StaticMeshDescriptionBulkData != nullptr`, `StaticMeshSourceData.cpp` line 326. The editor stops. |

**The state of the project after the crash: as reimport R1 left it.** Checked at 12:38 without loading anything. `L_P1_DatasmithImport.umap` was last written at 00:48:49. All 1,647 files under `Content\Wieland1529\Scratch\P1\` were last written between 00:39 and 00:48. The asset list holds 1 Datasmith scene, 1,294 meshes, 280 materials, 65 textures and 7 light-distribution files there. The Datasmith scene asset still records the first export as its source file (`25-006_1527_N_Wieland-3DView-3D_View_188.udatasmith`). The 20 assignments are therefore still in place as saved at 00:47, and reimport R1's result (20 of 20) stands.

**The cause, read from the engine's 5.9.0 source.** After a level loads, the editor goes on preparing each of its meshes for drawing in the background; Epic calls this asset compilation. Four facts, each read in the source:

1. When a mesh in the new file has changed and already exists in the project, the reimport makes a copy of the existing mesh, and before copying it takes the mesh's source geometry out of it (`DuplicateStaticMesh`, `DatasmithImporterUtils.cpp` line 1354).
2. Copying a mesh that is still being prepared in the background forces that preparation to finish first (`UStaticMesh::Serialize`, `StaticMesh.cpp` lines 7689 to 7704).
3. When preparation of a mesh finishes, the engine tells the Content Browser to refresh what it knows about that mesh (`StaticMeshCompiler.cpp` line 436).
4. That refresh asks the mesh whether its source geometry is valid. The check at line 326 stops the editor if the geometry is not there, and because of fact 1 it is not.

The crash record's call stack lists the same parts of the engine in the same order: Datasmith importer, object copy, engine, Content Browser, engine. It carries no function names, because the engine's debug files are not installed. So this reading fits everything observed, but it is not proven.

**Why this reimport and not the earlier work.** R2 began 0.6 seconds after the level finished loading, so the level's 1,294 meshes were still being prepared. Reimport R1 ran with the level already open for eight minutes, and it copied no mesh, because no mesh had changed. The first import had no existing mesh to copy. R2 is the first time this project asked 5.9.0 to replace a mesh that was still being prepared. Whether the reimport of a changed mesh works once preparation has finished is not yet known.

**This is a fault in engine 5.9.0, not in the export or the project.** It can be met in real use: reimporting straight after opening a level.

### What the second export changes, and what a reimport should show

Made at 13:00 on 2026-11-11 with `tools\compare_udatasmith.py`, which reads the two export files only; the editor is not involved. Full lists: `review\phase1\datasmith_export_r1_vs_r2.json`.

| Kind | First export | Second export | Gone | New | Changed |
|---|---|---|---|---|---|
| Meshes | 1,294 | 1,288 | 15 | 9 | 13 (same name, new content) |
| Placed mesh objects | 3,562 | 3,562 | 15 | 14 | 28 (17 moved; 11 given another mesh, one of those also moved) |
| Lights | 587 | 571 | 16 fewer | - | - |
| Materials | 280 | 284 | 1 | 5 | not comparable: every material that names a texture differs, because the textures' folder name changed |

The counts of gone, new and changed objects are by the name Datasmith gives each object; 15 or 16 objects in each file share a name with another, which is why 15 gone and 14 new still leave the total at 3,562. Lights share names between copies of one fixture, so only their totals are given. The earlier session's journal line says "22 placed objects are gone and 14 are new"; how it counted the 22 is not recorded, and this table does not reproduce that figure. The totals of meshes, lights and materials, and the 13 changed meshes, agree with it.

What changed, in words: five Focal Point adjustable accent fixtures and one Lumenwerx cylinder are gone; the mesh of a recessed Lumenwerx Via fixture is new; seven Fritz Hansen rugs, two Barrow lounge chairs, a side table, a coffee table, a dining chair, a seating pad and a one-seat sofa are new; one interior partition, two primary vanities, a countertop, a footstool, an end-seat sofa, a top rail, a ceiling and a terrace reveal are gone; the 13 changed meshes are niches, Kohler Purist sconces, a ceiling, casework and AXOR bathroom fittings.

**None of the 20 assignments sits on anything that changed.** For each of the 20, the object it marks is in the second export with the same name and the same mesh, and that mesh is not one of the 13 changed or 15 removed. So a reimport that works can be expected to keep 20 of 20, and anything less would be a real loss, not an effect of the owner's edits.

**Signs that the changes arrived**, to check after a reimport: 571 light components in the level, against 587 now; 57 mesh components whose label begins `Lighting_Fixtures_Lighting_Fixture-Focal_Point-ID-3_5_Adjustable_Accent`, against 62 now; 8 labelled `Furniture_Furniture_Other-Furniture_Fritz-Hansen_Rug-Dots_Default`, against 1 now; the 13 changed mesh files under `Scratch\P1\` with a new write time, and 9 new mesh files.

### Ways forward for the reimport line

By the owner's instruction a reimport that crashed the editor is not repeated unchanged, and the owner chooses how to go on. No reimport has been made since the crash.

| | Way forward | Size on disk | Cost | What it settles |
|---|---|---|---|---|
| A | **Repeat the reimport with one change: wait first.** Load the scratch level; in a separate call, wait until the editor has finished preparing every asset (`unreal.AutomationUtilsBlueprintLibrary.finish_all_asset_compilation()`); only then point the scene asset at the second export and reimport. This removes the condition the crash needed. It is also what a person does by hand: open the level, let it settle, reimport. | The 0.71 GB under `Scratch\P1\` is rewritten in place and grows by a few MB (9 new meshes, 4 more materials), and only if the result is saved | About 2 minutes. If the reading of the cause is wrong, the editor crashes again: nothing is lost, but the editor and the chat have to be started again | The acceptance line as written: how many of 20 survive, and whether the changes arrive |
| B | **As A, with background mesh preparation switched off for the length of the reimport** (`Editor.AsyncStaticMeshCompilation 0`, a console setting put back afterwards). A second change, kept for use only if A crashes. | As A | As A | As A |
| C | **The plan's fallback: no reimport.** Import the second export fresh into a new folder `/Game/Wieland1529/Scratch/P1_r2` in a new scratch level, and put the 20 assignments back by script from `review\phase1\reimport_assignments.json`. A fresh import is the route that worked in attempt 4. | About 0.7 GB new on D:, which has 59 GB free | About 2 minutes | Whether the changes arrive, and whether assignments can be put back by script. Not whether they survive a reimport |
| D | **Close the line as it stands** and carry it to Phase 3 as an open risk: a reimport of an unchanged file keeps 20 of 20; a reimport that replaces meshes crashes 5.9.0 when started while a level's meshes are still being prepared; untested otherwise. | None | None now; the question comes back in Phase 3 with the real model | Nothing new |

Recommended: A. If A crashes, B. If B crashes, C. Whichever is chosen is journaled in the table under "Reimports" as R3 and committed before it is made, and the memory reading is taken first.

**Outcome:** the owner chose the recommendation ("proceed with your recommendations"). A was made as reimport R3 at 13:19 on 2026-11-11 and worked, so B, C and D were not needed. One figure in the table proved wrong: the saved result is 0.25 GB larger than before, not a few MB.


## Step 1.9: path-traced renders

Station S1, 3840 by 2160, 1,024 samples per pixel, through Movie Render Graph's Quick Render with one-off settings, so no asset was created. Record: `review\phase1\pathtracer\pathtracer_runs.json`.

| Run | Time (s) | Video memory on the whole card, peak (MiB) |
|---|---|---|
| 1 | 49.8 | 11,888 |
| 2 | 48.2 | 11,921 |
| 3 | 48.3 | 11,849 |

The three pictures agree: mean difference 0.07 to 0.09 of 255. The plan allows 10 minutes and 15.0 GB for such a still.

**The condition.** Nanite parts carry a crude stand-in mesh for ray tracing. The console variable `r.RayTracing.Nanite.Mode` chooses what the Path Tracer sees:

| Value | Meaning | Result in a 1280 by 720 trial |
|---|---|---|
| 0 (as found) | Stand-in meshes | Walls and ground with holes and spikes; arcade and fence missing (`trial1_...png`) |
| 1 | Full meshes, streamed out | Every solid part missing; only glass and trees drawn; the log reports a staging buffer overflow (`trial2_...png`) |
| 2 | Full meshes, cluster method | Correct (`trial4_...png`) |

The three 4K renders used 2, and the variable was put back to 0 afterwards. **The Path Tracer is usable as ground truth only with value 2.** The same stand-in meshes are why reflections in the real-time view look blocky (audit finding ML4); whether value 2 is affordable in real time is for Phase 8.

## Step 1.11: light units

A 1,000-lumen point light should give 1000 / (4 x pi) = 79.58 lux on a surface 1 m away that faces it.

The editor's view options in 5.9.0 offer no read-out of illuminance in lux for a point light (the only one is for the sky light). So the reading was taken another way, in the saved scratch level `/Game/Wieland1529/Scratch/L_P1_LightUnits`: a matte card of 50 percent reflectance lies 1 m under the light in an otherwise empty, black level, and a capture camera reads the card's brightness in the engine's physical units at the point directly under the light. A second light of known strength, a 1,000-lux directional light pointing straight down, is read on the same card through the same camera as a reference.

| Reading | Value (lux) | Against expected |
|---|---|---|
| Point light at 1 m, read against the reference light | **79.46** | 0.15 percent low |
| Point light at 2 m, read against the reference light | 19.81 | 0.4 percent low (expected 19.89) |
| Point light at 1 m, taking the card as an ideal matte surface | 76.58 | 3.8 percent low |
| Reference light, taking the card as an ideal matte surface | 963.7 | 3.6 percent low (set to 1,000) |
| Every light off | 0 | |

Both lights read about 3.7 percent low when the card is taken as ideal. The shortfall is the same for both, so it belongs to the card and not to the lights: this project draws rough matte surfaces with a model that is a little darker than the ideal at the camera's angle. The engine's lumens and lux agree with each other to 0.15 percent, and the fall-off with distance follows the inverse-square law to 0.3 percent.

Record: `review\phase1\light_units_check.json`.


## Step 1.12: the two new 5.9 settings

**Overlapping glass** (Epic's name: AVBOIT). Switched by `r.OIT.Method 1`; its shaders are already built. By default it acts only on Nanite glass, and this level's glass is not Nanite, so `r.AVBOIT.NonNanite 1` is needed as well. At S1, Epic quality, 2038 by 782:

| State | Graphics-card time (ms) |
|---|---|
| Off | 6.28, and 6.24 on repeat |
| On, defaults | 6.30 |
| On, all glass | 6.60 |

Cost: 0.3 ms, inside the plan's 1.0 ms limit. Visible difference: none that can be told from the scene's own movement. Inside the windows of 1533 the pictures differ by 2 to 5 levels of 255 with the setting on, against 1 to 3 between two captures with nothing changed (clouds reflected in the glass move). S1 in this scene has no glass behind glass. **Not kept for now**, by the plan's rule; to be judged again where glass overlaps (the Revit building's railings and windows). Captures: `review\phase1\oit_S1_*`.

**Lumen World Cache.** The switch is `r.Lumen.WorldCache.Supported`, found by searching the console variables; it has no entry in Project Settings. It is off, and it is read-only while the editor runs ("is read only!"), so it needs a line in the settings file and a restart. The owner approved both at 00:17 on 2026-11-11.

**The trial was made on 2026-11-11 between 12:47 and 12:58 and is written up under "World Cache: results" below. The line was then taken out.** What existed before the trial:

| Item | State |
|---|---|
| The setting line | Written at 10:03 on 2026-11-11: `r.Lumen.WorldCache.Supported=True`, line 44 of `Config\DefaultEngine.ini`. No effect until the editor is restarted. |
| Reference at S1 without the feature | Captured at 09:59, Epic quality, 2038 by 782: **6.11 and 6.06 ms** of graphics-card time (two 10-second captures), with a picture, `review\phase1\worldcache_reference_lit_S1.png` |
| Captures with the feature on | None yet |

**Two captures taken at 00:52 are not usable and are kept only as a record** (`worldcache_before_capture.*`). They read 2.0 and 2.1 ms because the viewport was in Unlit view mode, which draws flat colours with no light, shadow or sky (`worldcache_invalid_unlit_view_S1.png`). The editor had come back from its 00:32 restart in that mode: its saved layout holds Unlit for the perspective viewport. The view mode was set back to Lit before the reference above. Every capture script must now check the view mode first.

After the restart: confirm `r.Lumen.WorldCache.Supported` reads true, confirm the view mode is Lit, record free memory, then capture S1 with `r.Lumen.WorldCache.Allowed` at 1 and at 0, with timings and pictures. Keep the line only if the difference is visible and costs no more than 1.0 ms; otherwise take it out.

### The World Cache trial

Written before the trial is made, as with the import and the reimports.

**Checked at 12:46 on 2026-11-11, after the editor's 11:39 restart:** `r.Lumen.WorldCache.Supported` reads true, set by the project's settings file, so line 44 took effect. `r.Lumen.WorldCache.Allowed` reads true, so the feature has been in use since that restart. `r.Lumen.HardwareRayTracing` reads 1; the feature's own help text says it acts only there ("Lumen hardware ray tracing samples the world cache instead of the surface cache"). The view mode is Lit. The open level is `L_R15_Production`, with nothing unsaved. No shader compiler process is running. The editor had come up at Cinematic quality (every quality group at 4, texture pool 3,000 MB, Game View off); the trial sets the reference's Epic settings and puts the found values back afterwards.

| No. | Time | What is tried | Outcome |
|---|---|---|---|
| W1 | 12:47 on 2026-11-11 | At S1 in `L_R15_Production`, with the reference's settings (Epic quality, texture pool 1,000 MB, 100 percent screen percentage, `t.MaxFPS 1000`, Game View on): four 10-second captures, each after 15 seconds of settling, with `r.Lumen.WorldCache.Allowed` at 1, 0, 1 and 0 in turn, then one picture in each state. Free physical memory 8.4 of 31.1 GB, free commit 26.5 of 79.1 GB, video memory 7.8 of 16.4 GB in use. Every console setting is put back afterwards and nothing is saved. | **No crash; four captures, four pictures and a per-pass check made, 12:47 to 12:52.** Graphics-card time on 5.64, off 5.98, on 5.99, off 6.43 ms. The readings rose through the run whichever state was set, so W2 repeats them in the opposite order. Written up under "World Cache: results". |
| W2 | 12:52 on 2026-11-11 | The same four captures in the opposite order (`r.Lumen.WorldCache.Allowed` at 0, 1, 0, 1), with no other call made to the editor while they run, to separate the feature's effect from the upward drift seen in W1. Memory as for W1. | **No crash; four captures, 12:52 to 12:54, with the editor in front.** Graphics-card time off 6.26, on 5.91, off 6.28, on 5.84 ms. No drift this time. All console settings were put back at 12:55 and read back; nothing is unsaved. |
| W3 | 12:57 on 2026-11-11 | One extra pair of pictures at S1, on and off, with `r.RayTracing.Nanite.Mode` at 2 for the length of the check (its found value is 0; the path-traced renders of step 1.9 needed 2 to draw the walls correctly). Reason: with the World Cache on, the shaded front of the frame house turns from warm beige to grey-blue, and the path-traced render shows it warm beige; this checks whether the reduced stand-in meshes that ray tracing uses at value 0 are the cause. Epic settings as in W1. Everything is put back afterwards; nothing is saved. | **No crash; two pictures and a per-pass timing, 12:57 to 12:58.** The stand-in meshes are not the cause: with the World Cache on, the house front reads grey at value 2 as well. All console settings were put back and read back (`r.RayTracing.Nanite.Mode` 0, `r.Lumen.WorldCache.Allowed` true, Cinematic quality, Game View off); nothing is unsaved. |

### World Cache: results

**The difference is visible. The feature costs nothing: it is about 0.4 ms cheaper and uses about 0.4 GB less video memory. The setting does not stay,** because the visible difference is a loss when measured against the path-traced render. Line 44 was taken out of `Config\DefaultEngine.ini` at 12:59 on 2026-11-11.

Lumen is Unreal's real-time system for light that bounces between surfaces. Until 5.9 it kept that light in a store called the Surface Cache; the World Cache is the new store that replaces it when the setting is on.

**Cost.** Ten-second captures at S1, Epic quality, 2038 by 782 pixels, 15 seconds of settling before each. W1 ran with the editor behind another window, W2 with it in front.

| Run, in the order captured | World Cache | Graphics-card time (ms) | Frame time (ms) | Peak video memory (MB) |
|---|---|---|---|---|
| W1 | on | 5.64 | 6.70 | 4,456 |
| W1 | off | 5.98 | 7.11 | 4,915 |
| W1 | on | 5.99 | 7.29 | 4,531 |
| W1 | off | 6.43 | 7.83 | 4,920 |
| W2 | off | 6.26 | 8.52 | 5,022 |
| W2 | on | 5.91 | 8.37 | 4,662 |
| W2 | off | 6.28 | 8.52 | 5,022 |
| W2 | on | 5.84 | 8.54 | 4,667 |

In each of the four neighbouring pairs, the capture with the World Cache on is cheaper, by 0.34 to 0.44 ms of graphics-card time (0.39 ms on average), and it holds 355 to 459 MB less video memory. W1's readings rose through the run in both states; W2, in the opposite order and with no other call made to the editor, shows no such drift and the same difference. The morning's reference from before the setting was in force read 6.11 and 6.06 ms, the same as "off" here, so switching the feature off by console gives the lighting the project had before.

Why it is cheaper, from a per-pass reading of four frames in each state (`review\phase1\worldcache_trial_W1_gpu_passes.json`): with the feature on, a pass named `LumenWorldCache` appears and takes 0.06 ms, and the Surface Cache's passes stop (`LumenSceneLighting`, 0.28 ms, and `LumenSceneUpdate`, about 0.2 ms). This also proves the feature really ran.

**Visible difference.** Yes. In `review\phase1\worldcache_W1_off_above_on_S1.png` (off above, on below) the shaded front of the frame house on the right turns from warm beige to grey-blue, the shaded brick on the left darkens, and the window glass reflects darker. Two pictures of a moving scene never match pixel for pixel (clouds, leaves), so the measure used is the mean brightness of each cell of a 3 by 4 grid over the frame, on a scale of 0 to 255 (`tools\image_levels.py`):

| Pair | Largest change in a cell | Average change over the 12 cells |
|---|---|---|
| Off against off, 26 seconds apart (nothing changed) | 1.7 | 0.8 |
| Off against the morning's reference, three hours apart (nothing changed) | 3.4 | 1.2 |
| On against off | 8.4 | 3.4 |
| The second "on" picture against the same "off" | 8.1 | 3.3 |

**Which is nearer the truth.** The path-traced render of step 1.9 is the plan's measure of correct light. The mean colour of the house front, in a box of each picture (the path-traced render has a different frame shape, so its box was placed by eye on the same wall):

| Picture | Red | Green | Blue | Red minus blue | Brightness |
|---|---|---|---|---|---|
| Path-traced render of 10 November | 151.6 | 140.7 | 125.7 | +25.9 | 139.3 |
| World Cache off, as the project stands | 157.2 | 153.0 | 145.8 | +11.4 | 152.0 |
| World Cache on, as the project stands | 135.5 | 144.4 | 147.0 | -11.4 | 142.3 |
| World Cache off, `r.RayTracing.Nanite.Mode 2` (check W3) | 155.7 | 142.3 | 126.2 | +29.5 | 141.4 |
| World Cache on, `r.RayTracing.Nanite.Mode 2` (check W3) | 122.2 | 125.3 | 122.6 | -0.4 | 123.4 |

"Red minus blue" above zero is a warm wall, below zero a cool one. The path-traced wall is warm. With the World Cache off the wall is warm; with it on the wall is cool or grey, in both ray-tracing modes. Check W3 was made because ray tracing in this project draws each Nanite part as a reduced stand-in mesh (value 0), which had spoiled the first path-traced trials; it shows that the stand-in meshes are not what turns the wall grey. Why the World Cache does so in this scene is not established.

**Decision.** The earlier rule was "keep the line only if the difference is visible and costs no more than 1.0 ms". Both hold. The line is taken out all the same, for three reasons. First, the visible difference moves the picture away from the path-traced render, and the plan's aim is a match with reality. Second, the line does not merely make the feature available: `r.Lumen.WorldCache.Allowed` is on by default, so with the line in place every level of the project is lit by the World Cache. Third, the baseline profile M0 and the six acceptance lines were measured without it. Taking the line out is what the record of 10:03 said would happen if the trial did not justify it. To put it back: add `r.Lumen.WorldCache.Supported=True` at the end of `[/Script/Engine.RendererSettings]` and restart the editor. The removal takes effect at the next editor start; until then the running editor still has the feature on, as it was found.

**Two things this leaves for Phase 8,** neither acted on here:

1. The World Cache is cheaper by 0.4 ms and 0.4 GB. It is worth trying again on the finished scene and after each engine update, judged against a path-traced render of the same view.
2. With the World Cache off, `r.RayTracing.Nanite.Mode 2` brings the real-time picture closer to the path-traced one at this wall (red minus blue +29.5 against +25.9, where the project's present value 0 gives +11.4). From four single frames in each state it costs roughly 0.5 ms on the graphics card (6.84 against 6.29 ms); that figure is rough. This is the same setting step 1.9 found the Path Tracer needs.

Records: `review\phase1\worldcache_trial_W1_capture.json` and `_W2_capture.json` with their `.analysis.json`, the eight engine logs in `review\phase1\csv\worldcache_W*.csv.gz`, and the pictures `worldcache_W1_*.png`, `worldcache_W3_*.png` and `worldcache_house_front_W1off_W1on_W3off_W3on.png`.

## Step 1.14: content removal

Approved by the owner for the two folders `Content\Belmont` and `Content\EuropeanBeech`.

Checks made immediately before deleting, all read-only:

| Check | Result |
|---|---|
| Assets in the two folders | 5,872 and 258 |
| Wieland assets that refer to them | None |
| Assets outside the two folders that refer to them | One: the level `/Game/L_Belmont_Production_RECOVERY_20261006` at the content root (792 references). It is Belmont's own. |
| Assets from the two folders loaded in the editor | None |
| Settings files that name the folders | None |
| Archive copies on H: | Identical in file count and bytes (5,872 files, 3.19 GB; 258 files, 7.41 GB) |
| Links inside the folders | None |

Because nothing from the folders was loaded, the files were removed directly from disk at 00:01 and the editor's asset list was then rescanned. Deleting through the editor would have loaded all 6,130 assets first, including old Datasmith materials, which is the kind of load that crashes the import.

| Outcome | Value |
|---|---|
| Space freed on D: | 9.88 GB (50.70 GB free before, 60.58 GB after) |
| Assets the editor lists under the two folders | 0 |
| Assets left under `/Game` | 2,918 |
| Assets that still point at the deleted folders | One: `/Game/L_Belmont_Production_RECOVERY_20261006` (1.12 MB). **Left in place**: deleting it is not covered by the approval. It will show missing content if opened. |

**The recovery level.** With the owner's approval of 00:17, `Content\L_Belmont_Production_RECOVERY_20261006.umap` (1,178,422 bytes) was deleted at 00:18. Checked first: it was not loaded, nothing referred to it, every one of its 797 references pointed at Belmont or engine content, and the archive holds an identical copy. The editor's asset list now shows 2,917 assets under `/Game` and nothing that points at the deleted folders.

To restore any of this: copy it back from `H:\Wieland1529_archives\2026-11-10_pre-phase1\Wieland1527 5.9\Content\`.


## Memory before heavy steps

By the owner's instruction of 2026-11-11: before an import, a reimport, a path-traced render or a lighting trial, free physical memory and free commit (the virtual memory Windows can still hand out) are read and written here. Under 12 GB of free commit the step is not started and the owner is told.

| Time | Step about to start | Free physical memory (GB) | Free commit (GB) | Started |
|---|---|---|---|---|
| 09:57 on 2026-11-11 | Lighting captures at S1 (reference for the World Cache trial) | 12.3 of 31.1 | 30.0 of 79.1 | Yes |
| 11:17 on 2026-11-11 | Reimport R2 from the second export (Revit open at 6.5 GB, editor at 15.5 GB) | 6.2 of 31.1 | 18.4 of 79.1 | Yes |
| 12:38 on 2026-11-11 | None yet: the state check of the session that took over (Revit closed, editor at 14.9 GB, started 11:39) | 8.3 of 31.1 | 26.6 of 79.1 | - |
| 12:46 on 2026-11-11 | Lumen World Cache trial W1 at S1 (Revit closed, editor at 15.0 GB, video memory 7.8 of 16.4 GB in use) | 8.4 of 31.1 | 26.5 of 79.1 | Yes |
| 12:56 on 2026-11-11 | World Cache check W3 at S1, with Nanite ray tracing at 2 for its length (video memory 8.0 of 16.4 GB in use) | 8.4 of 31.1 | 25.5 of 79.1 | Yes |
| 13:17 on 2026-11-11 | Reimport R3 from the second export, way forward A (Revit closed, editor at 15.5 GB, video memory 8.0 of 16.4 GB in use) | 7.8 of 31.1 | 24.5 of 79.1 | Yes |
| 13:25 on 2026-11-11 | None: the reading after reimport R3, with the editor back on `L_R15_Production`. The editor now holds 23.4 GB, because it keeps both levels in memory; a restart frees it. | 8.8 of 31.1 | 18.3 of 79.1 | - |

For the record, readings taken before the rule existed: at 00:46, just before reimport R1, 4.5 GB physical and 8.2 GB commit were free, with the editor at 20.5 GB and Revit at 12.5 GB. At 00:51 commit free was 6.0 GB. The editor crashed at 00:55.


## Findings that bear on the plan

1. **Station S1 as the plan places it is inside a building.** The plan puts the west sidewalk 18 m west of the front lot line, from an assumed 66-foot right-of-way. In the existing model the face of the building on the west side stands about 17.2 m from the front lot line at the lot's centre line, so that point is under its roof. For this baseline the walking line is 14.0 m west of the front lot line, on the modelled sidewalk. Either the model's street is too narrow or the assumption is too wide; Phase 2 measures the real width.
2. **The editor was found at Cinematic quality, not Epic.** Every quality group read 4, and the texture pool read 3,000 MB. The October benchmark used 3 and 1,000 MB. Cinematic costs about twice as much graphics-card time on this scene.
3. **The project is larger than the plan records:** 22.4 GB against 17.2 GB. `Intermediate` holds 5.14 GB of files the engine rebuilds.
4. **Free space on C: moves by gigabytes for reasons outside this work.** C: read 17.05 GB at 21:47, 19.77 GB at 22:12 and 18.87 GB at 22:36 (the plan recorded 20.8). The cause is not known. H: read 233.72 GB and then 230.62 GB; this work wrote nothing to H:. At 22:36, D: had 51.27 GB and E: 66.75 GB. **The cause was looked for on 2026-11-11, when C: had fallen to 12.8 GB, under the plan's 15 GB floor.** A read-only scan listed every file on C: written since 2026-11-10, 14.6 GB in all, by folder. The writers are: a Windows update being staged, about 3.5 GB (`C:\Windows\SoftwareDistribution\Download` 1.0 GB, `C:\$WinREAgent\Scratch` 0.9 GB, new components under `C:\Windows\WinSxS` about 0.8 GB, and its logs); program updates (the Epic launcher and its online services 1.3 GB, two versions of the Claude desktop app 1.6 GB, Unreal Canvas's Python packages 0.6 GB, Node packages 0.4 GB); and caches (Google Drive 0.7 GB, browsers 0.5 GB). Claude's own chat records came to 0.26 GB. None of it is this project: the engine's cache and the page file are on D:. Written bytes are not the same as lost space, since an update replaces files, but they show who writes. A staged Windows update is normally cleared after Windows installs it.
5. **A correction to this session's first message.** It said the engine cache held 9.2 GB on C:, and gave C:'s small margin as the reason to move the cache before the import. That was wrong. `C:\Users\cowey\AppData\Local\UnrealEngine` is a link to `E:\AppData-Moved\UnrealEngine`, so the cache was on E:. The planning session found this at 22:40 and corrected the plan. What writes to C: during an import is therefore unknown, and C: is watched during step 1.7.
6. **The editor does not slow down when it is in the background** ("Use Less CPU when in Background" is off), so captures taken while the owner works in another window are usable. Each capture records whether the editor was in front.
7. **Two sessions write to the plan's working copy.** While this session was paused, the planning session's commit `644edc7` took in this session's uncommitted files under a message that describes only the cache correction. Nothing was lost. From here this session stages only its own files, by path.
8. **In 5.9.0 a Datasmith reimport must not be started straight after a level is opened.** A reimport that replaces a changed mesh crashes the editor if that mesh is still being prepared in the background, as it is for some seconds after the level loads (reimport R2, "Step 1.8"). Until an engine update fixes it, every reimport in Phase 3 and later waits for asset preparation to finish first. Reimport R3 showed that this is enough.
9. **The Lumen World Cache is cheaper but, in this scene, less true.** It saves about 0.4 ms and 0.4 GB of video memory at S1 and turns shaded walls grey where the path-traced render shows them warm ("Step 1.12"). It is off again; Phase 8 should try it once more on the finished scene.
10. **`r.RayTracing.Nanite.Mode 2` brings the real-time picture closer to the path-traced one,** at roughly 0.5 ms (a rough figure). The project runs at 0. Step 1.9 found the Path Tracer needs 2. A project-wide choice for Phase 8.
11. **Find imported objects by Revit element ID, never by label.** A reimport renumbers the labels of same-named objects when one of them is removed; in reimport R3 a marked ceiling went from `_58` to `_57` and another ceiling took `_58` ("Reimport R3: result").
12. **A reimport keeps Unreal-side material work but leaves unused files behind.** Assignments on placed objects, on meshes and edits to imported materials all survived; 10 mesh files and 1 material file that the second export no longer has stayed in the folder.
13. **Two 16,000-pixel limestone textures are 0.84 GB of the 0.96 GB import,** and eight texture files the export names are missing from its folder. Both are for Phase 5 and for the owner's Revit materials.

## Waiting on the owner

| # | Step | What | Size on disk | Cost |
|---|---|---|---|---|
| 1 | 1.12 | **Restart the editor.** The owner said on 2026-11-11 that this will be done. Two reasons for it: the removal of the World Cache line takes effect only at a restart, and the editor held 23.4 GB after the reimport. | None | None |

**Nothing else in Phase 1 waits on the owner.** On 2026-11-11, after the report that Phase 1 was complete, the owner wrote: "i will restart but i need you to complete all other required steps i dont want to interact with this workflow anymore". What that left, and what was done with each item between 13:30 and 13:42:

| Item | What was done |
|---|---|
| The eight texture files that the export names and does not contain | Checked: both exports name them and neither contains them, so this is a standing condition of the Revit materials, not something the second export introduced. A search of C:, D: and E: by file name (finished at 13:41) found none of the eight, so they are not on this workstation's drives and cannot be copied in. It is now a task for Phases 3 and 5 (`PLAN.md`, end of the Phase 1 section) with a default that needs nothing from the owner (`OPEN_DECISIONS.md`, decision 15). |
| C: under the plan's 15 GB floor | The cause was looked for with a read-only scan, as the plan's risk list asks. It is not this work. See finding 4, which now names the writers. |
| Revit closed during heavy work, and the memory reading | Now a rule of every phase in `PLAN.md`, so it does not depend on anyone remembering it. |
| The check that the World Cache removal took effect | Cannot be made before the restart. It is the first check of the next session, written at the end of the Phase 1 section of `PLAN.md`. |
| Phase 1's findings | Carried into the files later sessions read: four rules in `PLAN.md` under "Rules for every phase", a table of carry-over items at the end of its Phase 1 section, the test results in `ENGINE_NOTES.md`, and the choices that come later in `OPEN_DECISIONS.md`, decision 15. |
| An archive at the milestone | What Phase 1 added to the project was copied to `H:\Wieland1529_archives\2026-11-11_phase1-complete\` and verified; see "What was saved or changed in the project". |
| The two resume prompts | Marked at their top as used and not to be pasted again. |

Done earlier: the owner made the second export at 11:08 on 2026-11-11, restarted the editor at 11:25 and 11:39, and chose the way forward for the reimport.

Answered by the owner at 00:17 on 2026-11-11: yes to the workaround line; yes to deleting the Belmont recovery level; remove the pointer file; yes to trying Lumen World Cache.

## How to resume

Text to give a new session in the editor's panel: "Continue Phase 1 of the 1529 N. Wieland plan. Read `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\phase1_results.md`, section 'How to resume', and the last section of `PROJECT_MEMORY.md` in that working copy, then carry on from step 3 there."

**As of 13:25 on 2026-11-11 nothing is left: Phase 1 is complete.** The next work is Phase 2 of `PLAN.md`. Everything below is kept as history and as the method for later reimports. Steps 3 to 8 of the numbered list are done or overtaken. The reimport was made at 13:19 as reimport R3 in the following way, which is the way to make every reimport in 5.9.0:

- Read the memory figures and write them under "Memory before heavy steps"; under 12 GB of free commit, stop and tell the owner.
- Add a row R3 to the table under "Reimports" with a pending marker, and commit it.
- Load `/Game/Wieland1529/Scratch/L_P1_DatasmithImport`. In a **separate** call, run `unreal.AutomationUtilsBlueprintLibrary.finish_all_asset_compilation()` and let it return. Never start a reimport in the call that loads the level.
- Point the scene asset `/Game/Wieland1529/Scratch/P1/25-006_1527_N_Wieland-3DView-3D_View_188/25-006_1527_N_Wieland-3DView-3D_View_188` at the second export (its `asset_import_data`, with `scripted_add_filename(<file>, 0, "")`), then reimport with `tools\wieland_datasmith.py`, `start_reimport(<scene asset>, <result file>)`, writing `review\phase1\datasmith_reimport_R3.json`.
- Count what survived against `review\phase1\reimport_assignments.json` (10 on objects, 10 on meshes, and the three edited materials), and check the signs listed under "What the second export changes". Count components, not actors.
- Save the level and the assets under `/Game/Wieland1529/Scratch/P1` by name, write the result into the acceptance list, the step table and the status block, and commit.

1. Read this file, then the last section of `PROJECT_MEMORY.md`.
2. Confirm the open level has no unsaved changes before doing anything. Never save `L_R15_Production`. Never use "Save All".
3. **Confirm the workaround took.** Read `r.Material.UseShaderCompilationParameters` in the editor. It must read 0. If it reads 1, the section the line sits in was not honoured for this variable: tell the owner before moving the line.
4. **Record what the workaround cost.** Shader compile time: from the editor's log of this start, the `LogShaderCompilers` summary ("Shaders Compiled", "Time at least one job was in flight"), and wait until no `ShaderCompileWorker` process is busy. Cache growth: the size of `D:\UE_DerivedDataCache` against 2.003 GB in 235 files, measured at 00:18:21 on 2026-11-11, just before the line was written.
5. **Journal the import as attempt 4** in the table under "Step 1.7", with a pending marker, and commit. Then load `/Game/Wieland1529/Scratch/L_P1_DatasmithImport` and import with `tools\wieland_datasmith.py` (`start_import`, assets to `/Game/Wieland1529/Scratch/P1`, lightmap UVs off), writing its record to `review\phase1\datasmith_import_attempt4.json`.
6. **If it crashes:** by the owner's instruction, stop importing. Take line 43 out of `Config\DefaultEngine.ini` again, record the plan's fallback (the FBX route) as the workaround for the import line and "re-apply assignments by script" for the reimport line, and report. The ways forward and their costs are under "Step 1.7".
7. **If it works:** count objects and lights with `wieland_datasmith.count_level()` (the file holds 3,562 placed mesh objects and 587 lights; 99.5 percent is 3,545 and 585). Check the known dimension: the top of the object tagged `Revit.Element.Id.12330199` against the top of `Site_GRADE_GRADE`, expected 203.2 cm, within 0.1 cm. Save the scratch level and the assets under `/Game/Wieland1529/Scratch/P1` by name. Then assign 20 materials, save a table of them, and rehearse the reimport with the owner's second export.
8. **Lumen World Cache.** The line is written. After the owner's restart, follow the last paragraph of "Step 1.12".
9. The soak is not part of Phase 1. It is step 9.11 of the plan.

## What was saved or changed in the project

In `D:\Unreal_Engine_Projects\Wieland1527 5.9\`:

| Item | What |
|---|---|
| `Config\DefaultEngine.ini` | **One line added at the end of `[/Script/Engine.RendererSettings]`, with the owner's yes.** Line 43, at 00:18 on 2026-11-11: `r.Material.UseShaderCompilationParameters=0`, the workaround the import needs. It stays; to undo it, delete the line and restart. A second line, `r.Lumen.WorldCache.Supported=True`, was added as line 44 at 10:03 with the owner's yes for the World Cache trial and **taken out again at 12:59**, because the trial did not justify it; the file is back at 2,513 bytes, its size before that line. The removal takes effect at the next editor start; the editor that was running at 12:59 still has the feature on. No other settings file was changed. |
| `Content\Wieland1529\Scratch\L_P1_DatasmithImport.umap` | New. The scratch level that holds the imported building (12.7 MB). **Since reimport R3 it holds the owner's second export;** last saved at 13:21 on 2026-11-11. |
| `Content\Wieland1529\Scratch\P1\` | New. The imported assets. **Since reimport R3: 1,670 files, 0.96 GB** (1,298 meshes, 285 materials, 86 textures and light-distribution files, 1 Datasmith scene), last saved at 13:21 on 2026-11-11. Before R3 it held 1,647 files and 0.71 GB. Ten mesh files and one material file belong to things the second export no longer has; a reimport leaves such files in place. |
| `Content\Wieland1529\Scratch\M_P1_Marker_OnObject.uasset`, `M_P1_Marker_OnMesh.uasset` | New at 00:45 on 2026-11-11. The magenta and cyan marker materials used for the 20 assignments. |
| `Content\Wieland1529\Scratch\L_P1_LightUnits.umap` | New. The light-check level: one card, one point light, one hidden reference light, one capture camera. |
| `Content\Wieland1529\Scratch\M_P1_Lambert50.uasset` | New. The matte 50 percent grey material on the card. |
| `Content\Belmont\`, `Content\EuropeanBeech\` | Deleted at 00:01 on 2026-11-11, with the owner's approval. 9.88 GB. |
| `Content\L_Belmont_Production_RECOVERY_20261006.umap` | Deleted at 00:18 on 2026-11-11, with the owner's approval. 1.12 MB. |
| `CLAUDE.md` | Written at 23:29 on 2026-11-10 without explicit approval; removed at 00:18 on 2026-11-11 on the owner's word. Not present now. |
| `Saved\Profiling\CSV\` | 63 measurement logs written by the engine's profiler, named `Profile(2026111...)`; the last eight are the World Cache trial's. |
| `Saved\Screenshots\P1_worldcache\` | New at 12:50 on 2026-11-11: six pictures from the World Cache trial, 14.9 MB. Copies are in the plan's working copy. |
| `Saved\Crashes\` | Written by the engine during this work: four crash records (23:32 and 23:45, the import; 00:55, out of virtual memory; 11:22 on 2026-11-11, reimport R2) and five warning records (22:02, 22:40, 00:53, 09:57 and 12:47). The warnings at 22:02, 22:40 and 12:47 were read: each is the harmless one from the viewport's real-time switch at the first capture of an editor run. The other two were written at the first capture of their editor runs and were not read. |
| Everything under `Content\Wieland\` and the level `L_R15_Production` | Not changed. Nothing was saved over. |

On H:, with the owner's approval: `H:\Wieland1529_archives\2026-11-10_pre-phase1\Wieland1527 5.9\` (11,657 files, 17.24 GB), the project as it stood before any of the above, including the three deleted items and the settings file without the added line.

Also on H:, written at 13:34 on 2026-11-11 at the close of Phase 1, as the plan's risk list asks for an archive at every milestone: `H:\Wieland1529_archives\2026-11-11_phase1-complete\Wieland1527 5.9\`, holding the project's `Config` folder (32 files) and `Content\Wieland1529\` (1,675 files), 0.97 GB in all. It is a copy of what Phase 1 added or changed, not of the whole project; with the first archive beside it, it restores the project as Phase 1 left it. Every file matched its source in count and bytes. Log: `review\phase1\archive_2026-11-11_phase1-complete.robocopy.log`.


## Files written in the plan's working copy

In `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\`. Changed: `PROJECT_MEMORY.md` (entries appended), `docs\unreal\1529_wieland\SITE_MODEL_AUDIT.md` (section appended), `docs\unreal\1529_wieland\PLAN.md` (the soak moved from Phase 1 to Phase 9). New:

- `docs\unreal\1529_wieland\phase1_results.md`
- `docs\unreal\1529_wieland\profiles\2026-11-10_M0\capture_A_views_epic_sp100.analysis.json`
- `docs\unreal\1529_wieland\profiles\2026-11-10_M0\capture_A_views_epic_sp100.json`
- `docs\unreal\1529_wieland\profiles\2026-11-10_M0\capture_B_views.analysis.json`
- `docs\unreal\1529_wieland\profiles\2026-11-10_M0\capture_B_views.json`
- `docs\unreal\1529_wieland\profiles\2026-11-10_M0\capture_C_path.analysis.json`
- `docs\unreal\1529_wieland\profiles\2026-11-10_M0\capture_C_path.json`
- `docs\unreal\1529_wieland\profiles\2026-11-10_M0\capture_D_path_warm.analysis.json`
- `docs\unreal\1529_wieland\profiles\2026-11-10_M0\capture_D_path_warm.json`
- `docs\unreal\1529_wieland\profiles\2026-11-10_M0\csv\block_overview.csv.gz`
- `docs\unreal\1529_wieland\profiles\2026-11-10_M0\csv\cinematic_sp100_block_overview.csv.gz`
- `docs\unreal\1529_wieland\profiles\2026-11-10_M0\csv\cinematic_sp100_dense_planting.csv.gz`
- `docs\unreal\1529_wieland\profiles\2026-11-10_M0\csv\cinematic_sp100_front_context.csv.gz`
- `docs\unreal\1529_wieland\profiles\2026-11-10_M0\csv\cinematic_sp152_block_overview.csv.gz`
- `docs\unreal\1529_wieland\profiles\2026-11-10_M0\csv\cinematic_sp152_dense_planting.csv.gz`
- `docs\unreal\1529_wieland\profiles\2026-11-10_M0\csv\cinematic_sp152_front_context.csv.gz`
- `docs\unreal\1529_wieland\profiles\2026-11-10_M0\csv\dense_planting.csv.gz`
- `docs\unreal\1529_wieland\profiles\2026-11-10_M0\csv\epic_sp100_block_overview.csv.gz`
- `docs\unreal\1529_wieland\profiles\2026-11-10_M0\csv\epic_sp100_dense_planting.csv.gz`
- `docs\unreal\1529_wieland\profiles\2026-11-10_M0\csv\epic_sp100_front_context.csv.gz`
- `docs\unreal\1529_wieland\profiles\2026-11-10_M0\csv\epic_sp152_block_overview.csv.gz`
- `docs\unreal\1529_wieland\profiles\2026-11-10_M0\csv\epic_sp152_dense_planting.csv.gz`
- `docs\unreal\1529_wieland\profiles\2026-11-10_M0\csv\epic_sp152_front_context.csv.gz`
- `docs\unreal\1529_wieland\profiles\2026-11-10_M0\csv\front_context.csv.gz`
- `docs\unreal\1529_wieland\profiles\2026-11-10_M0\csv\path_cinematic_sp152.csv.gz`
- `docs\unreal\1529_wieland\profiles\2026-11-10_M0\csv\path_epic_sp100.csv.gz`
- `docs\unreal\1529_wieland\profiles\2026-11-10_M0\csv\path_epic_sp100_warm.csv.gz`
- `docs\unreal\1529_wieland\profiles\2026-11-10_M0\csv\path_epic_sp152.csv.gz`
- `docs\unreal\1529_wieland\profiles\2026-11-10_M0\csv\path_epic_sp152_warm.csv.gz`
- `docs\unreal\1529_wieland\profiles\2026-11-10_M0\gpu_passes_stations.json`
- `docs\unreal\1529_wieland\profiles\2026-11-10_M0\gpu_passes_stations.summary.json`
- `docs\unreal\1529_wieland\profiles\2026-11-10_M0\profile.md`
- `docs\unreal\1529_wieland\review\phase1\agent_server_50_calls.json`
- `docs\unreal\1529_wieland\review\phase1\archive_2026-11-10_pre-phase1.robocopy.log`
- `docs\unreal\1529_wieland\review\phase1\csv\oit_off_S1.csv.gz`
- `docs\unreal\1529_wieland\review\phase1\csv\oit_off_again_S1.csv.gz`
- `docs\unreal\1529_wieland\review\phase1\csv\oit_on_all_glass_S1.csv.gz`
- `docs\unreal\1529_wieland\review\phase1\csv\oit_on_default_S1.csv.gz`
- `docs\unreal\1529_wieland\review\phase1\light_units_check.json`
- `docs\unreal\1529_wieland\review\phase1\oit_S1_capture.analysis.json`
- `docs\unreal\1529_wieland\review\phase1\oit_S1_capture.json`
- `docs\unreal\1529_wieland\review\phase1\oit_S1_difference_x8.png`
- `docs\unreal\1529_wieland\review\phase1\oit_S1_off_1.png`
- `docs\unreal\1529_wieland\review\phase1\oit_S1_off_2.png`
- `docs\unreal\1529_wieland\review\phase1\oit_S1_on_all_glass.png`
- `docs\unreal\1529_wieland\review\phase1\oit_S1_windows_off_left_on_right.png`
- `docs\unreal\1529_wieland\review\phase1\pathtracer\S1_pathtraced_4k_run1.0000.png`
- `docs\unreal\1529_wieland\review\phase1\pathtracer\S1_pathtraced_4k_run2.0000.png`
- `docs\unreal\1529_wieland\review\phase1\pathtracer\S1_pathtraced_4k_run3.0000.png`
- `docs\unreal\1529_wieland\review\phase1\pathtracer\S1_pathtraced_run1_preview_1600.png`
- `docs\unreal\1529_wieland\review\phase1\pathtracer\pathtracer_runs.json`
- `docs\unreal\1529_wieland\review\phase1\pathtracer\trial1_720p_16spp_nanite_mode0_fallback_meshes.png`
- `docs\unreal\1529_wieland\review\phase1\pathtracer\trial2_720p_16spp_nanite_mode1_walls_missing.png`
- `docs\unreal\1529_wieland\review\phase1\pathtracer\trial4_720p_16spp_nanite_mode2_correct.png`
- `docs\unreal\1529_wieland\review\phase1\soak\soak_loops.jsonl`
- `docs\unreal\1529_wieland\review\phase1\soak\soak_loops.jsonl.summary.json`
- `docs\unreal\1529_wieland\review\phase1\soak\soak_system_log.csv`
- `docs\unreal\1529_wieland\review\phase1\sun_check.json`
- `docs\unreal\1529_wieland\site_model_audit_materials.json`
- `docs\unreal\1529_wieland\tools\analyze_profile_csv.py`
- `docs\unreal\1529_wieland\tools\compare_images.py`
- `docs\unreal\1529_wieland\tools\mcp_readonly_calls_test.py`
- `docs\unreal\1529_wieland\tools\reduce_gpu_passes.py`
- `docs\unreal\1529_wieland\tools\wieland_datasmith.py`
- `docs\unreal\1529_wieland\tools\wieland_profile.py`
- `docs\unreal\1529_wieland\tools\wieland_render.py`

Written between 00:39 and 09:58 on 2026-11-11 by the earlier session and not listed above until now:

- `docs\unreal\1529_wieland\review\phase1\csv\worldcache_not_supported_S1_a.csv.gz`
- `docs\unreal\1529_wieland\review\phase1\csv\worldcache_not_supported_S1_b.csv.gz`
- `docs\unreal\1529_wieland\review\phase1\csv\worldcache_reference_lit_S1_a.csv.gz`
- `docs\unreal\1529_wieland\review\phase1\csv\worldcache_reference_lit_S1_b.csv.gz`
- `docs\unreal\1529_wieland\review\phase1\datasmith_import_attempt4.json`
- `docs\unreal\1529_wieland\review\phase1\datasmith_import_check.json`
- `docs\unreal\1529_wieland\review\phase1\datasmith_reimport_R1.json`
- `docs\unreal\1529_wieland\review\phase1\reimport_assignments.json`
- `docs\unreal\1529_wieland\review\phase1\worldcache_before_capture.analysis.json`
- `docs\unreal\1529_wieland\review\phase1\worldcache_before_capture.json`
- `docs\unreal\1529_wieland\review\phase1\worldcache_invalid_unlit_view_S1.png`
- `docs\unreal\1529_wieland\review\phase1\worldcache_reference_lit_capture.analysis.json`
- `docs\unreal\1529_wieland\review\phase1\worldcache_reference_lit_capture.json`
- `docs\unreal\1529_wieland\review\phase1\worldcache_reference_lit_S1.png`

Written between 12:45 and 13:06 on 2026-11-11 by the session that took over at 12:38 (it also changed this file and `PROJECT_MEMORY.md`):

- `docs\unreal\1529_wieland\review\phase1\csv\worldcache_W1_off_S1_a.csv.gz`
- `docs\unreal\1529_wieland\review\phase1\csv\worldcache_W1_off_S1_b.csv.gz`
- `docs\unreal\1529_wieland\review\phase1\csv\worldcache_W1_on_S1_a.csv.gz`
- `docs\unreal\1529_wieland\review\phase1\csv\worldcache_W1_on_S1_b.csv.gz`
- `docs\unreal\1529_wieland\review\phase1\csv\worldcache_W2_off_S1_a.csv.gz`
- `docs\unreal\1529_wieland\review\phase1\csv\worldcache_W2_off_S1_b.csv.gz`
- `docs\unreal\1529_wieland\review\phase1\csv\worldcache_W2_on_S1_a.csv.gz`
- `docs\unreal\1529_wieland\review\phase1\csv\worldcache_W2_on_S1_b.csv.gz`
- `docs\unreal\1529_wieland\review\phase1\datasmith_export_r1_vs_r2.json`
- `docs\unreal\1529_wieland\review\phase1\worldcache_house_front_W1off_W1on_W3off_W3on.png`
- `docs\unreal\1529_wieland\review\phase1\worldcache_trial_W1_capture.analysis.json`
- `docs\unreal\1529_wieland\review\phase1\worldcache_trial_W1_capture.json`
- `docs\unreal\1529_wieland\review\phase1\worldcache_trial_W1_gpu_passes.json`
- `docs\unreal\1529_wieland\review\phase1\worldcache_trial_W2_capture.analysis.json`
- `docs\unreal\1529_wieland\review\phase1\worldcache_trial_W2_capture.json`
- `docs\unreal\1529_wieland\review\phase1\worldcache_W1_difference_off_on_x8.png`
- `docs\unreal\1529_wieland\review\phase1\worldcache_W1_off_1_S1.png`
- `docs\unreal\1529_wieland\review\phase1\worldcache_W1_off_2_S1.png`
- `docs\unreal\1529_wieland\review\phase1\worldcache_W1_off_above_on_S1.png`
- `docs\unreal\1529_wieland\review\phase1\worldcache_W1_on_1_S1.png`
- `docs\unreal\1529_wieland\review\phase1\worldcache_W1_on_2_S1.png`
- `docs\unreal\1529_wieland\review\phase1\worldcache_W3_nanite2_off_S1.png`
- `docs\unreal\1529_wieland\review\phase1\worldcache_W3_nanite2_on_S1.png`
- `docs\unreal\1529_wieland\tools\compare_udatasmith.py`
- `docs\unreal\1529_wieland\tools\image_levels.py`

Written between 13:17 and 13:25 on 2026-11-11 by the same session, for reimport R3 (it also added four functions to `docs\unreal\1529_wieland\tools\wieland_datasmith.py`):

- `docs\unreal\1529_wieland\review\phase1\datasmith_reimport_R3.json`
- `docs\unreal\1529_wieland\review\phase1\datasmith_reimport_R3_after.json`
- `docs\unreal\1529_wieland\review\phase1\datasmith_reimport_R3_before.json`

Written between 13:30 and 13:42 on 2026-11-11 by the same session, to close the phase. New: `docs\unreal\1529_wieland\review\phase1\archive_2026-11-11_phase1-complete.robocopy.log`. Changed, so that later sessions find Phase 1's rules and findings where they read:

- `docs\unreal\1529_wieland\PLAN.md` (four rules added under "Rules for every phase"; a status line and a table of carry-over items in the Phase 1 section)
- `docs\unreal\1529_wieland\ENGINE_NOTES.md` (a section "Phase 1 test results" and a note pointing to it)
- `docs\unreal\1529_wieland\OPEN_DECISIONS.md` (decision 15, none of it needed now)
- `docs\unreal\1529_wieland\RESUME_PHASE1.md` and `docs\unreal\1529_wieland\RESUME_PHASE1_2026-11-11.md` (a note at the top that they are used and not to be pasted again)


## Appendix: the 109 tool sets

| Owner | Sets | Names |
|---|---|---|
| `SequencerScriptingEditor` | 1 | SequencerToolsFunctionLibrary |
| `SequencerScripting` | 13 | MovieSceneTimeWarpExtensions, MovieSceneDoubleVectorTrackExtensions, MovieSceneFloatVectorTrackExtensions, MovieSceneBindingExtensions, MovieSceneSequenceExtensions, MovieSceneSectionEasingExtensions, MovieSceneSectionExtensions, MovieSceneBindingTagExtensions, MovieScenePropertyTrackExtensions, MovieSceneTrackExtensions, MovieSceneFolderExtensions, MovieSceneEventTrackExtensions, MovieSceneConditionExtensions |
| `SequencerAnimTools` | 1 | SequencerAnimToolsEditorLibrary |
| `PCGEditor` | 1 | PCGEditorSubsystem |
| `UMGEditor` | 2 | UMGDebuggerSubsystem, WidgetBlueprintEditorSubsystem |
| `ProceduralVegetationEditor` | 1 | ProceduralVegetationEditorSubsystem |
| `WidgetFinder` | 1 | WidgetFinderSubsystem |
| `BlueprintToolsets` | 2 | BlueprintToolset, BlueprintDslToolset |
| `FabToolset` | 1 | FabToolset |
| `ToolsetRegistry` | 1 | AgentSkillToolset |
| `DataflowEditor` | 1 | DataflowScriptingSubsystem |
| `AIAssistantEditor` | 1 | AIAssistantToolset |
| `SourceControl` | 1 | SourceControlHelpers |
| `LevelSequenceEditor` | 2 | LevelSequenceEditorBlueprintLibrary, LevelSequenceEditorSubsystem |
| `TemplateSequenceEditor` | 1 | TemplateSequenceEditorSubsystem |
| `SequenceValidator` | 1 | SequenceValidatorSubsystem |
| `ControlRigEditor` | 1 | ControlRigSequencerEditorLibrary |
| `OptimusScripting` | 1 | DeformerGraphScriptingSubsystem |
| `SlateDebugger` | 1 | SlateDebuggerSubsystem |
| `AgentPluginToolset` | 1 | AgentPluginToolset |
| `AIModuleToolset` | 2 | BehaviorTreeToolset, EnvironmentQueryToolset |
| `AnimationAssistantToolset` | 1 | SequencerDirectorToolset |
| `AutomationTestToolset` | 1 | AutomationTestToolset |
| `ChaosClothAssetToolset` | 1 | ChaosClothAssetToolset |
| `CheatsToolset` | 1 | CheatsToolset |
| `ConfigSettingsToolset` | 1 | ConfigSettingsToolset |
| `ConsoleToolset` | 2 | ConsoleToolset, LogsToolset |
| `DataflowAgent` | 1 | DataflowAgentToolset |
| `DataRegistryToolset` | 1 | DataRegistryTools |
| `GameFeaturesToolset` | 1 | GameFeaturesToolset |
| `EditorToolset` | 20 | ActorToolset, AssetToolset, CurveAtlasToolset, CurveTableToolset, DataAssetToolset, DataTableToolset, EditorAppToolset, LevelToolset, MaterialInstanceToolset, MaterialToolset, ObjectToolset, PrimitiveToolset, SkeletalMeshToolset, SoundWaveToolset, StaticMeshToolset, StringTableToolset, TextureToolset, UndoHistoryToolset, UserDefinedEnumToolset, UserDefinedStructToolset |
| `GameplayTagsToolset` | 1 | GameplayTagsToolset |
| `GASToolsets` | 4 | GameplayAbilityToolset, GameplayCueToolset, AttributeSetToolset, AbilitySystemInspectorToolset |
| `FileSystemToolset` | 1 | FileSystemToolset |
| `InputToolset` | 1 | InputToolset |
| `LiveCodingToolset` | 1 | LiveCodingToolset |
| `MediaToolset` | 1 | MediaToolset |
| `MetaSoundToolset` | 3 | MetaSoundDiscoveryToolset, MetaSoundInspectionToolset, MetaSoundAuthoringToolset |
| `NavMeshToolset` | 1 | NavMeshToolset |
| `MVVMToolset` | 1 | MVVMToolset |
| `NiagaraToolsets` | 5 | NiagaraToolset_Info, NiagaraToolset_Component, NiagaraToolset_Blueprint, NiagaraToolset_System, NiagaraToolset_Assets |
| `PCGToolset` | 2 | PCGToolset, PCGSpatialToolset |
| `PerfToolset` | 3 | CsvProfilerToolset, StatsToolset, GpuProfilerToolset |
| `PhysicsToolsets` | 1 | PhysicsAssetToolset |
| `RewindDebuggerToolset` | 1 | RewindDebuggerToolset |
| `WorldConditionsToolset` | 1 | WorldConditionTools |
| `PluginToolset` | 1 | PluginToolset |
| `SceneCaptureToolset` | 1 | SceneCaptureToolset |
| `SlateInspectorToolset` | 1 | SlateInspectorToolset |
| `TextureGraphToolset` | 1 | TextureGraphTools |
| `WidgetStaticAnalysisToolset` | 1 | WidgetStaticAnalysisToolset |
| `WidgetAnimationToolset` | 1 | WidgetAnimationToolset |
| `CommonUIToolset` | 1 | CommonUIToolset |
| `UnrealCanvasAnnotationsEditor` | 2 | UnrealCanvasSpatialAnnotationEditorSubsystem, UnrealCanvasSpatialAnnotationToolset |
| `state_tree_toolset.state_tree` | 1 | StateTreeToolset |
| `editor_toolset.toolsets.blueprint` | 1 | BlueprintDslTools |
| `editor_toolset.toolsets.blueprint_diff` | 1 | BlueprintDiffTools |
| `editor_toolset.toolsets.python_scripting` | 1 | PythonScriptingTools |
| `conversation_toolset.toolsets.conversation` | 1 | ConversationTools |
| `animation_toolset.toolsets.controlrig` | 1 | ControlRigTools |
