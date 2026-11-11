# Phase 1 results: toolchain setup and first import test in 5.9

Companion to [PLAN.md](PLAN.md). This file is written as each step finishes, so a new session can resume from it.

**Status at 00:40 Central on 2026-11-11: in progress.** Five acceptance lines are measured and pass (agent server, baseline, sun, Path Tracer, light units). The soak is no longer part of Phase 1. The editor was restarted at 00:32 and the workaround variable reads 0. Import attempt 4 is journaled under "Step 1.7" and is being made.

**Nothing in the Unreal project has been saved.** No asset, level or setting was written. The level `L_R15_Production` has no unsaved changes, and the editor's settings and camera were put back after every measurement. The only files this work wrote inside the project folder are the measurement logs the engine itself writes under `Saved\Profiling\CSV\`.

## Acceptance list

| Line | Target | Result | Status |
|---|---|---|---|
| Agent server | 50 consecutive read-only calls with no error | **50 of 50 passed.** Median 14 ms a call, slowest 308 ms. | **Pass** |
| Baseline | The three October views at a recorded viewport size, beside the October means | **Measured at 2038 by 782 pixels.** At the pixel count of 2560 by 1440 and October's settings, frame means are 10.8, 9.9 and 10.6 ms against 12.7, 11.9 and 12.9 ms in 5.8. | **Pass** |
| Import | At least 99.5 percent of 3,562 objects and 587 lights; known dimension within 1 mm | **Two attempts crashed the editor** (23:32, 23:45). No number yet. | Open; attempts are logged under "Step 1.7" |
| Reimport | 20 of 20 assignments survive | Not yet measured | Waits for the import and the owner's second export |
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
| 1.7 | Import the Datasmith file into a scratch level | **First attempt crashed the editor.** See "Step 1.7". |
| 1.8 | Reimport rehearsal | Not started. Waits for 1.7 and the owner's second export. |
| 1.9 | Three path-traced renders of station S1 | **Done.** See "Step 1.9". |
| 1.10 | Sun direction against the NOAA calculator | **Done** for the engine's sun calculation. The same check on a sun placed in a level is added when the scratch level exists. |
| 1.11 | 1,000-lumen light, illuminance at 1 m | **Done.** See "Step 1.11". |
| 1.12 | Lumen World Cache and overlapping glass, on and off | **Part done.** Overlapping glass measured. For Lumen World Cache the owner approved the saved setting and the restart it needs (00:17 on 2026-11-11); it is to be tried after the import's outcome is recorded, with its own restart, so that the two changes are not mixed. See "Step 1.12" and "How to resume". |
| 1.13 | Two-hour soak | **Not run, by the owner's decision; moved to Phase 9, where it runs on the finished scene** (`PLAN.md`, step 9.11). A run was started at 00:02:43 on 2026-11-11 and stopped at 00:09:58 on the owner's instruction, after 7 of 120 walks, with no crash. It is not a result. Its short log is kept in `review\phase1\soak\` as a trial of the soak script. The trial showed two faults in the script, both now corrected and neither re-run; see `PROJECT_MEMORY.md`. |
| 1.14 | Remove the Belmont and beech content | **Done.** The two folders at 00:01 and, with the owner's further approval, the Belmont recovery level at 00:18 on 2026-11-11. See "Step 1.14". |
| 1.15 | This file | In progress. |

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

Not yet covered: this checks the calculation. A sun actually placed in a level also applies a north offset, which is the value Phase 2 measures. That placement is checked in the scratch level once it exists.

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
| 4 | 00:41 | The same import with Epic's workaround in force. The owner restarted the editor at 00:32. Confirmed before the attempt: `r.Material.UseShaderCompilationParameters` reads 0 in the running editor, and this start's log shows "Set CVar [[r.Material.UseShaderCompilationParameters:0]]". Cost of the setting at startup: none measurable. The log shows no shader compiling after the start, no shader compiler process was running five minutes later, and the cache held 2.003 GB, as before (250 files against 235). Any cost during the import is measured from the cache size and the log afterwards. **By the owner's instruction, if this attempt crashes, importing stops and line 43 of `Config\DefaultEngine.ini` is taken out again.** | As attempt 1 otherwise: everything included; lightmap UV generation off; Substrate on; level `/Game/Wieland1529/Scratch/L_P1_DatasmithImport`, assets to `/Game/Wieland1529/Scratch/P1`; record to `review\phase1\datasmith_import_attempt4.json` | ATTEMPT_4_OUTCOME_PENDING: if this line still reads so, the editor crashed during attempt 4 |

### Where the import stands, and the ways forward

The crash is repeatable: both attempts stopped at the same point, when the importer made its first material from Datasmith's Revit parent material, `RevitReference`. The engine then found that the set of shaders it had built for that parent did not include one it expected (`TShadowDepthPSCombined`). An Epic staff member described this assertion for engine 5.8 and named a temporary workaround.

| Option | What it keeps | What it costs | What is known |
|---|---|---|---|
| A. Epic's workaround: one line in `Config\DefaultEngine.ini` and a restart. **Waiting for the owner's yes.** | Everything: reimport, the Revit data on each object, Revit's materials | A project-wide setting; shaders are rebuilt once, and the time and cache growth will be measured | Untested in 5.9. By the owner's instruction, a crash with it set ends the import attempts. |
| B. Import without materials, an option of the importer itself | Geometry, lights, the Revit data on each object, reimport | Revit's materials do not arrive; all 280 would be made in Unreal. The plan's default was to keep them as exported. | Untried. It skips the step that crashes. It is still an import, so it needs the owner's word after a third crash. |
| C. The FBX route, the plan's named fallback | Geometry | Loses reimport and the Revit data on each object; materials are made in Unreal | Worked in October on 5.8 |
| D. Substrate off for the whole project | Possibly everything | Changes how every material in the project is drawn. The owner's decision. | No evidence points to it: the assertion concerns which shadow shaders are built, not Substrate. Not recommended on what is known. |

A caution that follows from the same fault, **not tested**: the project already holds October's Datasmith imports under `/Game/Wieland/Revit1527` (1,720 assets). 356 of their materials use the same parent, `RevitReference`. None is loaded. Opening the two levels there, `L_Wieland_Revit_Integration_r01` and `L_Pilot`, may crash this 5.9.0 editor in the same way. They were not opened.


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

**Lumen World Cache.** The switch is `r.Lumen.WorldCache.Supported`, found by searching the console variables; it has no entry in Project Settings. It is off, and it is read-only while the editor runs ("is read only!"). Trying it means saving a project-wide rendering setting and restarting, which is the owner's decision. **Not tested.**

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


## Findings that bear on the plan

1. **Station S1 as the plan places it is inside a building.** The plan puts the west sidewalk 18 m west of the front lot line, from an assumed 66-foot right-of-way. In the existing model the face of the building on the west side stands about 17.2 m from the front lot line at the lot's centre line, so that point is under its roof. For this baseline the walking line is 14.0 m west of the front lot line, on the modelled sidewalk. Either the model's street is too narrow or the assumption is too wide; Phase 2 measures the real width.
2. **The editor was found at Cinematic quality, not Epic.** Every quality group read 4, and the texture pool read 3,000 MB. The October benchmark used 3 and 1,000 MB. Cinematic costs about twice as much graphics-card time on this scene.
3. **The project is larger than the plan records:** 22.4 GB against 17.2 GB. `Intermediate` holds 5.14 GB of files the engine rebuilds.
4. **Free space on C: moves by gigabytes for reasons outside this work.** C: read 17.05 GB at 21:47, 19.77 GB at 22:12 and 18.87 GB at 22:36 (the plan recorded 20.8). The cause is not known. H: read 233.72 GB and then 230.62 GB; this work wrote nothing to H:. At 22:36, D: had 51.27 GB and E: 66.75 GB.
5. **A correction to this session's first message.** It said the engine cache held 9.2 GB on C:, and gave C:'s small margin as the reason to move the cache before the import. That was wrong. `C:\Users\cowey\AppData\Local\UnrealEngine` is a link to `E:\AppData-Moved\UnrealEngine`, so the cache was on E:. The planning session found this at 22:40 and corrected the plan. What writes to C: during an import is therefore unknown, and C: is watched during step 1.7.
6. **The editor does not slow down when it is in the background** ("Use Less CPU when in Background" is off), so captures taken while the owner works in another window are usable. Each capture records whether the editor was in front.
7. **Two sessions write to the plan's working copy.** While this session was paused, the planning session's commit `644edc7` took in this session's uncommitted files under a message that describes only the cache correction. Nothing was lost. From here this session stages only its own files, by path.

## Waiting on the owner

| # | Step | What | Size on disk | Cost |
|---|---|---|---|---|
| 1 | 1.7 | **Restart the editor**, so that the workaround line takes effect. Close it normally and open `Wieland1527.uproject` again. If it offers to restore anything, decline. | None | None; shaders are rebuilt after the start, and the time is measured |
| 2 | 1.8 | Move one interior wall about a foot in Revit (any one change you can name will do), export the same 3D view as `25-006_1527_N_Wieland-3DView-3D_View_188_r2.udatasmith` into `E:\Claude\3D-Model-Workflow\references\1529 Wieland - Datasmith\`, and say which element changed. Needed only if the import works. | 0.67 GB on E: | None |
| 3 | 1.12 | A second restart later, for the Lumen World Cache trial | None | None |

Answered by the owner at 00:17 on 2026-11-11: yes to the workaround line; yes to deleting the Belmont recovery level; remove the pointer file; yes to trying Lumen World Cache.

## How to resume

Text to give a new session in the editor's panel: "Continue Phase 1 of the 1529 N. Wieland plan. Read `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\phase1_results.md`, section 'How to resume', and the last section of `PROJECT_MEMORY.md` in that working copy, then carry on from step 3 there."

1. Read this file, then the last section of `PROJECT_MEMORY.md`.
2. Confirm the open level has no unsaved changes before doing anything. Never save `L_R15_Production`. Never use "Save All".
3. **Confirm the workaround took.** Read `r.Material.UseShaderCompilationParameters` in the editor. It must read 0. If it reads 1, the section the line sits in was not honoured for this variable: tell the owner before moving the line.
4. **Record what the workaround cost.** Shader compile time: from the editor's log of this start, the `LogShaderCompilers` summary ("Shaders Compiled", "Time at least one job was in flight"), and wait until no `ShaderCompileWorker` process is busy. Cache growth: the size of `D:\UE_DerivedDataCache` against 2.003 GB in 235 files, measured at 00:18:21 on 2026-11-11, just before the line was written.
5. **Journal the import as attempt 4** in the table under "Step 1.7", with a pending marker, and commit. Then load `/Game/Wieland1529/Scratch/L_P1_DatasmithImport` and import with `tools\wieland_datasmith.py` (`start_import`, assets to `/Game/Wieland1529/Scratch/P1`, lightmap UVs off), writing its record to `review\phase1\datasmith_import_attempt4.json`.
6. **If it crashes:** by the owner's instruction, stop importing. Take line 43 out of `Config\DefaultEngine.ini` again, record the plan's fallback (the FBX route) as the workaround for the import line and "re-apply assignments by script" for the reimport line, and report. The ways forward and their costs are under "Step 1.7".
7. **If it works:** count objects and lights with `wieland_datasmith.count_level()` (the file holds 3,562 placed mesh objects and 587 lights; 99.5 percent is 3,545 and 585). Check the known dimension: the top of the object tagged `Revit.Element.Id.12330199` against the top of `Site_GRADE_GRADE`, expected 203.2 cm, within 0.1 cm. Save the scratch level and the assets under `/Game/Wieland1529/Scratch/P1` by name. Then assign 20 materials, save a table of them, and rehearse the reimport with the owner's second export.
8. **Lumen World Cache**, approved by the owner, after the import's outcome is recorded: add `r.Lumen.WorldCache.Supported=True` to the same section of `Config\DefaultEngine.ini`, ask the owner to restart, then capture station S1 with `r.Lumen.WorldCache.Allowed` at 1 and at 0, with timings. Keep the line only if the difference is visible and costs no more than 1.0 ms at S1; otherwise take it out.
9. The soak is not part of Phase 1. It is step 9.11 of the plan.

## What was saved or changed in the project

In `D:\Unreal_Engine_Projects\Wieland1527 5.9\`:

| Item | What |
|---|---|
| `Config\DefaultEngine.ini` | **Changed at 00:18 on 2026-11-11, with the owner's yes:** one line added as line 43, `r.Material.UseShaderCompilationParameters=0`, at the end of the section `[/Script/Engine.RendererSettings]`. To undo: delete that line and restart the editor. No other settings file was changed. |
| `Content\Wieland1529\Scratch\L_P1_DatasmithImport.umap` | New. An empty scratch level for the import. |
| `Content\Wieland1529\Scratch\L_P1_LightUnits.umap` | New. The light-check level: one card, one point light, one hidden reference light, one capture camera. |
| `Content\Wieland1529\Scratch\M_P1_Lambert50.uasset` | New. The matte 50 percent grey material on the card. |
| `Content\Belmont\`, `Content\EuropeanBeech\` | Deleted at 00:01 on 2026-11-11, with the owner's approval. 9.88 GB. |
| `Content\L_Belmont_Production_RECOVERY_20261006.umap` | Deleted at 00:18 on 2026-11-11, with the owner's approval. 1.12 MB. |
| `CLAUDE.md` | Written at 23:29 on 2026-11-10 without explicit approval; removed at 00:18 on 2026-11-11 on the owner's word. Not present now. |
| `Saved\Profiling\CSV\` | 24 measurement logs written by the engine's profiler, named `Profile(2026111...)`. |
| `Saved\Crashes\` | Written by the engine: two crash records (23:32 and 23:45, the import) and two warning records (22:02 and 22:40, harmless, from the viewport's real-time switch). |
| Everything under `Content\Wieland\` and the level `L_R15_Production` | Not changed. Nothing was saved over. |

On H:, with the owner's approval: `H:\Wieland1529_archives\2026-11-10_pre-phase1\Wieland1527 5.9\` (11,657 files, 17.24 GB), the project as it stood before any of the above, including the three deleted items and the settings file without the added line.


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
