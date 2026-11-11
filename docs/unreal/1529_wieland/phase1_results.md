# Phase 1 results: toolchain setup and first import test in 5.9

Companion to [PLAN.md](PLAN.md). This file is written as each step finishes, so a new session can resume from it.

**Status at 23:10 Central on 2026-11-10: in progress.** Three of the eight acceptance lines are measured and pass (agent server, baseline, sun). The other five need the project to be archived to H: first, which waits for the owner's approval. Phase 1 is not complete.

**Nothing in the Unreal project has been saved.** No asset, level or setting was written. The level `L_R15_Production` has no unsaved changes, and the editor's settings and camera were put back after every measurement. The only files this work wrote inside the project folder are the measurement logs the engine itself writes under `Saved\Profiling\CSV\`.

## Acceptance list

| Line | Target | Result | Status |
|---|---|---|---|
| Agent server | 50 consecutive read-only calls with no error | **50 of 50 passed.** Median 14 ms a call, slowest 308 ms. | **Pass** |
| Baseline | The three October views at a recorded viewport size, beside the October means | **Measured at 2038 by 782 pixels.** At the pixel count of 2560 by 1440 and October's settings, frame means are 10.8, 9.9 and 10.6 ms against 12.7, 11.9 and 12.9 ms in 5.8. | **Pass** |
| Import | At least 99.5 percent of 3,562 objects and 587 lights; known dimension within 1 mm | Not yet measured | Waits for the archive |
| Reimport | 20 of 20 assignments survive | Not yet measured | Waits for the import and the owner's second export |
| Path Tracer | Three renders with no crash | Not yet measured | Next |
| Sun | Bearing and height within 0.5 degree of NOAA | **Bearing differs by 0.05 degree, height by 0.06 degree.** | **Pass** |
| Light units | Within 10 percent of 79.6 lux | Not yet measured | Waits for the archive |
| Soak | Two hours, no crash, video memory growth of 5 percent or less | Not yet measured | Last, because it occupies the editor for two hours |

## Where each step stands

| No. | Step | Status |
|---|---|---|
| 1.1 | Agent server starts with the editor; model confirmed; pointer file | Server and model confirmed. The server started by itself at both editor launches this evening (21:18 and 22:08). `bAutoStartServer` is in none of the project's settings files, so whether that comes from the engine's default or from a setting stored elsewhere is not established. Pointer file: waiting for the owner's approval. |
| 1.2 | List the tool sets | **Done.** 109 tool sets, listed at the end of this file. |
| 1.3 | Finish the live audit | **Done.** Appended to [SITE_MODEL_AUDIT.md](SITE_MODEL_AUDIT.md). |
| 1.4 | Move the engine cache to D: | **Done by the planning session at 22:05**, with the editor restarted at 22:08. Confirmed by this session at 22:37: `D:\UE_DerivedDataCache` held 1.57 GB in 92 files and was still being written. The plan's cap is 20 GB. |
| 1.5 | Archive the project to H: | Waiting for the owner's approval. |
| 1.6 | Baseline profile M0 | **Done.** [profiles/2026-11-10_M0/profile.md](profiles/2026-11-10_M0/profile.md). |
| 1.7 | Import the Datasmith file into a scratch level | Not started. Waits for 1.5. |
| 1.8 | Reimport rehearsal | Not started. Waits for 1.7 and the owner's second export. |
| 1.9 | Three path-traced renders of station S1 | Not started. |
| 1.10 | Sun direction against the NOAA calculator | **Done** for the engine's sun calculation. The same check on a sun placed in a level is added when the scratch level exists. |
| 1.11 | 1,000-lumen light, illuminance at 1 m | Not started. Waits for 1.5. |
| 1.12 | Lumen World Cache and overlapping glass, on and off | Not started. |
| 1.13 | Two-hour soak | Not started. |
| 1.14 | Remove the Belmont and beech content | Waiting for the owner's approval, and for 1.5. |
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
| 1 | 1.5 | Approve copying the project to `H:\Wieland1529_archives\2026-11-10_pre-phase1\`, without `Intermediate` and `DerivedDataCache`, which the engine rebuilds | 17.2 GB on H: (22.4 GB for a complete copy); H: has 230.6 GB free | None |
| 2 | 1.14 | Approve deleting `Content\Belmont` and `Content\EuropeanBeech`, after the archive exists and after a check that no Wieland asset refers to them | Frees 9.88 GB on D: | None |
| 3 | 1.8 | Change one element in Revit, export the same 3D view to the same folder under a new name ending `_r2`, and say which element changed | 0.67 GB on E: | None |
| 4 | 1.1 | Approve a pointer file `CLAUDE.md` in the project folder | Under 2 KB | None |
| 5 | - | Say what the panel's permission selector shows | None | None |

## How to resume

1. Read this file, then the last section of `PROJECT_MEMORY.md`.
2. Confirm the level has no unsaved changes before doing anything.
3. Steps that need no approval and are still open: 1.9 (path-traced renders), 1.12 (find the two new settings and compare them through console variables, without saving), 1.13 (soak).
4. Everything else waits for the archive on H:.

## Files written so far

In `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\`:

- `docs\unreal\1529_wieland\phase1_results.md` (this file)
- `docs\unreal\1529_wieland\SITE_MODEL_AUDIT.md` (section appended)
- `docs\unreal\1529_wieland\site_model_audit_materials.json`
- `docs\unreal\1529_wieland\profiles\2026-11-10_M0\profile.md`, and beside it the capture records `capture_A_views_epic_sp100`, `capture_B_views`, `capture_C_path`, `capture_D_path_warm` (each a `.json` and a `.analysis.json`), `gpu_passes_stations.json`, `gpu_passes_stations.summary.json`, and 20 compressed logs in `csv\`
- `docs\unreal\1529_wieland\review\phase1\agent_server_50_calls.json`
- `docs\unreal\1529_wieland\review\phase1\sun_check.json`
- `docs\unreal\1529_wieland\tools\wieland_profile.py` (runs in the editor; drives the camera and the engine's profiler)
- `docs\unreal\1529_wieland\tools\analyze_profile_csv.py`
- `docs\unreal\1529_wieland\tools\reduce_gpu_passes.py`
- `docs\unreal\1529_wieland\tools\mcp_readonly_calls_test.py`
- `PROJECT_MEMORY.md` (entries appended)

In `D:\Unreal_Engine_Projects\Wieland1527 5.9\Saved\Profiling\CSV\`, written by the engine's profiler: 20 files named `Profile(20261110_22....).csv`.

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
