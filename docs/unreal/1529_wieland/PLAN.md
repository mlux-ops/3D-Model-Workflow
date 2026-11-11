# Plan: the 1529 N. Wieland St. Unreal Engine scene

Written 2026-11-10. This is a plan. Nothing in it has been built, downloaded or changed.

Companion files, all in `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\`:

- `ENGINE_NOTES.md`: each engine feature the plan relies on, its status, and whether it was read or still needs a test.
- `SOURCES.md`: each real-world data source, its terms, and what the plan uses it for.
- `REFERENCE_VIEWS.md`: the camera stations, tolerances, and the site-visit shot list.
- `OPEN_DECISIONS.md`: the decisions that belong to the owner.
- `SITE_MODEL_AUDIT.md`: the audit of the existing "1527 Wieland" Unreal site model.

## What the plan recommends

1. **Treat the building as new construction.** City records show demolition permits issued in June 2026 and marked complete, street imagery shows the lot cleared by August 2026, and a four-story, four-unit building was permitted on 2026-09-03. The surroundings are matched to reality. The building is matched to the Revit model.
2. **Start from the existing site model, and replace what the audit found wanting.** Keep the project, its performance method, its lot registration and its material parents. Rebuild neighbouring massing from public lidar, re-model the two adjacent buildings from the owner's photographs, and replace every tree and item of street furniture from a site survey.
3. **Decide the engine version at a gate before any content work.** Epic describes 5.9 as an unstable preview. Phase 1 runs a fixed list of tests in both 5.8 and 5.9 and commits to 5.9 only if all pass and 5.9 shows a visible gain. Until then the 5.9 project copy is a test bench.
4. **Use the owner's own photographs as the reference images.** Google does not permit Street View images to be saved, traced or made into textures. Street View is looked at live and cited by link.
5. **Deliver two tiers.** A real-time tier that holds 60 frames per second at 2560 by 1440, and an offline tier that trades nothing away. The differences are listed below.

## Rules for every phase

A session that builds one phase should read this block along with that phase's section.

- **Words.** "Agent" means Claude working through the Unreal editor's agent server (Epic calls it Unreal MCP) or through Python. "Owner" means the owner working by hand. A "station" is a fixed camera position defined in `REFERENCE_VIEWS.md`. A "profile" is a saved set of performance measurements.
- **One writer.** Only one session or person changes the Unreal project at a time. Never use "Save All". A command that times out has an unknown result; inspect before repeating it.
- **Ask first.** Ask the owner before installing or updating anything, downloading any dataset or asset, getting anything from a store, creating an account or key, changing anything in Revit, writing files outside this repository, or pushing to the remote. Name the action, its size on disk and its cost.
- **Street View is for looking.** No saved copies, no traced positions, no textures, no measurements entered as data.
- **Evidence over habit.** Where a fact about the block is missing, the scene shows a neutral placeholder and the gap is listed. Nothing is filled in with what is typical for the neighbourhood.
- **Materials.** This repository's rules apply: no visible seams, no recognizable repeats at the intended viewing distance, relief judged under grazing light.
- **Errors.** Every error and its solution is logged in `PROJECT_MEMORY.md` at the repository root in the same session.
- **Profiles.** Every phase that changes the scene ends by running the fixed camera path and saving a profile (defined under "Budgets").
- **The installed Unreal skills.** The owner installed the Claude Code plugin `unreal-engine-skills-for-claude-code` (version 3.1.2) on 2026-11-10. Every session that touches the editor uses its `unreal-mcp` skill: check for skills registered in the project first, find tools with `list_toolsets` and `describe_toolsets`, run them with `call_tool`, read each result before the next call, make dependent changes one at a time, and save the named assets before and after any bulk change. In engine 5.9 the describing tools are named `describe_toolsets` and `describe_tools`; the skill's text uses the older singular name.

## How the build sessions run

The owner intends to run later sessions from the terminal inside the Unreal editor that connects to Claude Code. Epic documents that the editor starts the agent as a local program and connects it to that editor's own agent server, so no connection file is needed. This was read, not yet tried; step 1.1 confirms it. It has these consequences for every phase:

- **Where files are.** Such a session starts in the Unreal project folder. Paths in this file that begin `docs\unreal\1529_wieland\` are inside this repository, whose main checkout is `E:\Claude\3D-Model-Workflow\`. This plan was written on the branch `claude/1529-wieland-scene-plan-e84a03`, in the working copy `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\`; until that branch is merged, the files are only there. Give the session the full path.
- **Rules do not load by themselves.** This repository's `AGENTS.md`, `WORKFLOW.md` and `PROJECT_MEMORY.md` are not read automatically by a session that starts in the Unreal project folder. Step 1.1 places a short pointer file in the project folder, after approval, that names them and this plan.
- **One editor, one session, one writer.** A session inside the 5.9 editor drives only that editor. Phase 1 therefore runs twice, once from each engine's editor, and both write to the same profiles folder.
- **A session ends when the editor closes or crashes.** Every step writes its result to a file before the next step starts, so a new session can resume from the files. Steps that need an editor restart (engine update, cache move, enabling a plugin) are the owner's and end the session. Long jobs (the two-hour soak, the 45-hour animation render) are started so that they resume from the last finished frame.
- **Scripts run on the editor's main thread.** Keep each call short and split large jobs, or the editor freezes while it runs.
- **Permission mode.** The approvals in this plan are instructions; the terminal does not enforce them. Run sessions in a mode that asks before edits and commands, not in a bypass mode.
- **Connections.** A session in the editor's terminal has the editor's tools. It may not have a web browser, the Revit connection or the Google Drive connection that the desktop app has. Each session checks the connections its phase needs before starting and reports any that are missing.

| Phase | Editor | Revit (read-only) | Web browser | Google Drive | Can run from the editor's terminal |
|---|---|---|---|---|---|
| 1 Toolchain | yes | no | yes, for the NOAA check | no | Yes, apart from the NOAA check |
| 2 Site data | yes | no | yes, for downloads | no | Partly; downloads and photograph handling need file and web access |
| 3 Revit import | yes | yes | no | no | Yes, if the Revit connection is present; otherwise the owner reads the values from Revit |
| 4 to 9 | yes | no | no | no | Yes |
| 10 Review | yes | no | yes, for the owner's live look at street imagery | no | Yes; the owner does the browser part |
| 11 Delivery | yes | no | no | yes | Yes, apart from the upload if the Drive connection is missing |

## Terms used in this file

| Term | Meaning |
|---|---|
| PIN | Cook County's parcel index number, the county's identifier for a tax parcel |
| Lidar | Aerial laser survey that yields a cloud of measured points on ground, roofs and trees |
| Datasmith | Epic's translator that carries a Revit model into Unreal with its objects, materials and data |
| Nanite | The engine's system for drawing very dense geometry at a cost that depends on screen size |
| Lumen | The engine's real-time system for bounced light and reflections |
| Path Tracer | The engine's slow, physically complete renderer, used here as ground truth |
| Virtual Shadow Maps | The engine's high-resolution real-time shadow system |
| MegaLights | The engine's system for many shadow-casting lights at once |
| Substrate | The engine's newer material system, which layers coatings and glass more accurately |
| Movie Render Graph | The engine's batch renderer for stills and animation. It is in beta; the older Movie Render Queue is the fallback. |
| DLSS | NVIDIA's image upscaler, an alternative to the engine's own temporal upscaler |
| Texel density | Texture pixels per metre of real surface |
| CIEDE2000 | A standard measure of the visible difference between two colours; 1 is barely visible, 5 is clearly visible side by side |

## Facts every phase relies on

| Fact | Value | Source |
|---|---|---|
| Site | Two adjacent parcels, PINs 17-04-203-010-0000 (1529) and 17-04-203-011-0000 (1527). Records also use 1531. | `SOURCES.md` |
| Lot | 49.50 ft by 102.20 ft on record; survey measured 50.18 ft at the front and 50.50 ft at the rear. Front setback 10 ft 2.5 in; rear setback 20 ft. | Owner's drawing set 25-006, sheets T1.1 and T1.4, as quoted in the earlier project's registration file |
| Lot centre | Latitude 41.910215, longitude -87.635389 (within about 3 m) | County parcel centres |
| Building | 13.208 m wide; floors at 2.032, 5.283, 8.534 and 11.786 m; four stories with basement, roof decks, pergolas and a two-car garage | Earlier registration file; city permit 101086781 |
| Street | The building faces west onto Wieland. The street runs roughly one degree west of true north; Phase 2 measures it. | `SOURCES.md` |
| Workstation | NVIDIA RTX 4080 (16 GB), Ryzen 7 7800X3D, 32 GB memory, Windows 11 | Owner |
| Engines installed | 5.8.3 at `D:\Games\Unreal Engine\UE_5.8`; 5.9.0 at `D:\Games\UE_5.9` | Measured 2026-11-10 |
| Projects | 5.8 original: `D:\Unreal_Engine_Projects\Wieland1527\`. 5.9 copy: `D:\Unreal_Engine_Projects\Wieland1527 5.9\`. Production level in both: `/Game/Wieland/R15_Landscape/L_R15_Production` | Measured 2026-11-10 |
| Agent server | Address `http://127.0.0.1:8000/mcp`. Not listening when first checked on 2026-11-10; answering after the owner restarted the editor at 19:23 that evening (engine 5.9.0, project `Wieland1527 5.9`, 115 tool sets). It does not start by itself unless the per-user setting is on. Start command: `ModelContextProtocol.StartServer 8000` in the editor's Output Log. | Observed; `ENGINE_NOTES.md` |
| Existing sun | The existing model's sun is at the engine's template values: latitude 45.0, longitude -73.0, north offset 35 degrees, 12 December 2019, 10:00, 50,000 lux. It has never been set for this site. | Read live from the editor, 2026-11-10 |
| Revit | Revit 2025.4 is installed. The model's location is to be given by the owner. | Measured; owner |

## Two tiers

The real-time tier is what runs interactively. The offline tier is what renders stills and animation. Both use the same scene, materials and lights.

| Setting | Real-time tier | Offline tier |
|---|---|---|
| Output | 2560 by 1440, 60 frames per second | Stills 3840 by 2160; animation 3840 by 2160 at 30 frames per second, 60 seconds (1,800 frames) |
| Internal resolution | 67 percent (1715 by 965), upscaled by the engine's temporal upscaler | 100 percent, with extra samples per frame |
| Global illumination and reflections | Lumen with hardware ray tracing | Path Tracer for stills. For animation, the owner chooses per shot between the Path Tracer and Lumen at its highest settings with many samples per frame. |
| Shadows | Virtual Shadow Maps | Ray-traced by the Path Tracer |
| Glass | Thin translucent glass with ray-traced reflections | Refracting glass with true double reflections |
| Relief | Normal maps, with displacement only on surfaces within 5 m of a station. Displacement is an experimental engine feature with no crack-free guarantee; where it cracks, the surface stays on normal maps. | Displacement wherever a station sees relief, with the same fallback |
| Foliage | Reduced leaf count beyond 30 m; wind simplified or off beyond 50 m | Full leaf count; wind on |
| Textures | Limited by a 4.0 GB streaming pool | Full resolution |
| Exposure, sun, sky, fixtures | Identical in both tiers: fixed exposure, physical units, manufacturer photometric files | Identical |

**What the real-time tier visibly gives up:**

- Fine detail at distance (mortar joints, railings, overhead wires, small leaves) is softer and can shimmer in motion, because the image is rendered at two thirds resolution and upscaled.
- Reflections in windows are coarser, and things outside the camera's view are reflected from a simplified copy of the scene.
- Glass does not bend light, casts no tinted shadow, and shows one reflection where real double glazing shows two.
- Indirect light is less detailed in small recesses such as under sills and inside arcades, and interior light bounced several times is dimmer and noisier.
- Shadow edges are less accurate in softness, and distant small foliage casts simplified shadow.
- Relief on distant brick and stone is shading only; its silhouette stays flat.
- Clouds are lower in resolution. Depth of field and motion blur are off.

## Budgets

### Frame time, real-time tier, 2560 by 1440 output

The limit is 16.67 ms. The budget is 14.5 ms of graphics-card time, which leaves 2.17 ms (13 percent) in reserve. These figures are proposals. Phase 1 measures the existing scene by pass and Phase 9 holds the totals.

| Render pass | Budget (ms) |
|---|---|
| Geometry: Nanite visibility and surface pass | 2.0 |
| Shadows: Virtual Shadow Maps, including foliage | 2.0 |
| Lumen scene update, including its lighting caches | 1.5 |
| Lumen global illumination | 2.5 |
| Lumen reflections, including glass | 1.5 |
| Direct light: sun, and fixtures at dusk | 1.0 |
| Sky, atmosphere, clouds and fog | 0.8 |
| Translucent surfaces | 0.8 |
| Foliage wind | 0.4 |
| Temporal upscaling | 1.2 |
| Post-processing and tone mapping | 0.8 |
| **Total** | **14.5** |

Processor budget: 8.0 ms for the game thread and 8.0 ms for the render thread.

Baseline for comparison: the existing site model measured mean total frame times of 12.7, 11.9 and 12.9 ms at three views in October 2026 (79, 84 and 77 frames per second) at 100 percent resolution, with 58 building parts and 11 trees and without the building's interior. The viewport size was not recorded; the release images from that day are 2560 by 1360. The scene this plan describes is much heavier, which is why the real-time tier renders at 67 percent.

Offline time budget, to be confirmed by the first timed render: 10 minutes or less per path-traced 3840 by 2160 still; 90 seconds or less per path-traced animation frame (45 hours for 1,800 frames) or 15 seconds or less per Lumen animation frame (7.5 hours).

### Video memory, real-time tier

The card has 16 GB. The budget is 13.0 GB at peak, which leaves 3.0 GB for Windows and other programs.

| Use | Budget (GB) |
|---|---|
| Texture streaming pool | 4.0 |
| Ray-tracing scene structures, including foliage | 2.5 |
| Lumen caches | 1.5 |
| Screen buffers and upscaler history at 2560 by 1440 | 1.5 |
| Nanite geometry streaming | 1.0 |
| Virtual Shadow Map pages | 1.0 |
| Virtual texture pools | 0.5 |
| Foliage wind and animation buffers | 0.5 |
| Reserve inside the budget | 0.5 |
| **Total** | **13.0** |

The offline tier may use up to 15.0 GB with nothing else open. If a path-traced still exceeds that, it is rendered in tiles. System memory budget for the editor: 24 GB of the 32 GB.

### Disk space by drive

Free space was measured on 2026-11-10. Caps are proposals; every download behind them needs approval.

| Drive | Free now (GB) | Planned change (GB) | Free afterwards (GB) | Floor to keep free (GB) |
|---|---|---|---|---|
| C: | 20.8 | Nothing new is written here. The engine keeps 10.5 GB of data under the user profile on C:. Step 1.4 tests whether Epic's documented variable moves it; if it does, up to 10.5 is freed. | 20.8, or up to about 31 if the move works | 15 |
| D: | 61.0 | Working project grows by up to 20. Unrelated content removed from the working copy (frees 10). | 51.0 | 25 |
| E: | 57.2 | Site data 6 (lidar up to 4, county extracts 1.5, other 0.5); owner's photographs 5; texture sources 10; profiles, evidence and review renders 10. Total 31. | 26.2 | 25 |
| H: | 233.7 | Engine cache capped at 40; the latest two project archives at up to 30 each, 60; offline frames 45 (1,800 frames at about 25 MB); packaged builds 15. Total 160. | 73.7 | 50 |

Already on D: and counted in "free now": engine 5.9 (33.5 GB), the 5.8 project (22.1 GB) and the 5.9 copy (17.2 GB). Once the engine is chosen, the unused project copy moves to an H: archive.

### The fixed camera path and the profile

- **Exterior path:** 60 seconds at walking pace (1.4 m per second, 84 m) along the west sidewalk at 1.60 m eye height, from 45 m south of station S1 to 39 m north of it, the camera turning to keep the building's front door centred.
- **Interior path:** 30 seconds from the entry of the unit used for the interior views to its main living space, ending at the windows.
- **A profile** is: the frame-time record for both paths (mean, 95th percentile, worst frame), the per-pass graphics-card times at stations S1, S2, S6, D2 and D5, peak video memory, the output and internal resolution, the engine version and the date.
- **Where:** `docs\unreal\1529_wieland\profiles\<date>_<milestone>\` in this repository.
- **Milestones:** M0 existing scene (Phase 1), M1 building imported (Phase 3), M2 surroundings (Phase 4), M3 materials (Phase 5), M4 interiors (Phase 6), M5 vegetation (Phase 7), M6 lighting (Phase 8), M7 optimized (Phase 9).

## Approvals this plan will ask for

Each is asked at the step that needs it. None has been asked or done yet.

| Action | Who acts | Size on disk | Cost |
|---|---|---|---|
| Start the editor's agent server | Owner | none | none |
| Update engine 5.8.3 to 5.8.4 through the launcher | Owner | not published; ask the launcher | none |
| Set `UE-LocalDataCachePath` so the engine cache leaves C: | Owner | moves about 10.5 GB | none |
| Remove the 651 Belmont and beech-tree content from the working project copy | Agent, after approval | frees 10 GB | none |
| Download 2022 lidar tiles for the block | Agent, after approval | estimated 4 GB or less; confirmed on the tile page first | none |
| Download county parcel, 2022 footprint and 2025 aerial extracts for the block | Agent, after approval | 1.5 GB or less | none |
| Export a Datasmith file from the Revit model | Owner, or Agent after approval | not known until exported; the earlier import was about 1 GB in Unreal | none |
| Download public-domain textures | Agent, after approval, per set | 10 GB cap in total | none |
| Download fixture photometric files from manufacturers | Agent, after approval | under 50 MB | none |
| Get tree models and interior furniture from Fab or another licensed library | Agent, after approval, per item | asked per item | asked per item |
| Google's 3D city tiles, only if the owner chooses them | Owner creates the account | none on disk | See `OPEN_DECISIONS.md`, decision 6 |
| Delete the Street View captures held in this session's cache | Agent, after approval | frees a few MB | none |
| Write render frames, packaged builds and project archives to H: | Agent, after approval | up to 160 GB in total, as budgeted | none |
| Install a Python library if a needed one is missing (map projection, point-cloud reading, image comparison) | Agent, after approval, per library | asked per library | none |
| Place a short pointer file in the Unreal project folder naming this repository's rules and this plan, so sessions started from the editor's terminal load them | Agent, after approval | under 2 KB | none |
| Register a project skill in the Unreal project that carries this plan's rules for any agent working in the editor | Agent, after approval | one small asset | none |
| Push the branch or merge to main | Agent, after approval | none | none |

---

## Phase 1: Toolchain setup, engine decision and first import test

**Goal.** A working link between the Agent and the editor, a baseline profile, and a recorded decision on the engine version, before any content is made.

**Inputs.**

- The two projects and two engines listed under "Facts every phase relies on".
- `ENGINE_NOTES.md`, which marks every feature that still needs a test.
- `SITE_MODEL_AUDIT.md`, whose live audit is partial: the material on each part and the site marker are still to be read.
- A small test view of the Revit model, chosen by the owner (one room or one facade bay).

**Steps.**

| No. | Step | Tool | Who |
|---|---|---|---|
| 1.1 | Make the agent server start with the editor (the per-user setting `bAutoStartServer`), give the 5.8 project and the 5.9 copy different ports so both can be open, open Claude Code in the editor's terminal and confirm it reaches the editor's tools, and, after approval, place the pointer file in the project folder. The server was started by hand on 2026-11-10 and answered. | Editor Preferences; the editor's terminal; text editor | Owner sets; Agent confirms a read-only tool call succeeds |
| 1.2 | List the tool sets the server offers and record them. On 2026-11-10 it listed 115, including tools for actors, levels, materials, textures, meshes, scene capture, performance capture, console variables, Python, the vegetation editor, source control and Fab. | `unreal-mcp` skill: `list_toolsets` | Agent |
| 1.3 | Finish the live audit. Sun, sky, lights and exposure were read on 2026-11-10 and are in `SITE_MODEL_AUDIT.md`. Still to do: the material on every part, and the object that marks the building's site, which the owner points out because no object carries a site name. | `unreal-mcp` skill, read-only | Agent; Owner points out the site object |
| 1.4 | Try to move the engine cache off C: by setting `UE-LocalDataCachePath`; restart editor and launcher; measure whether the 10.5 GB under the user profile shrinks and new cache files land on the chosen drive | Windows environment variable; folder sizes | Owner sets; Agent measures |
| 1.5 | Update 5.8.3 to 5.8.4 | Epic launcher | Owner |
| 1.6 | Run the existing three-view timing and the fixed exterior path in 5.8 and in 5.9; save profile M0 for each under `docs\unreal\1529_wieland\profiles\` | Editor's performance tools through the agent server | Agent |
| 1.7 | Export the test view from Revit as a Datasmith file into the project's `ImportStaging` folder | Revit 2025.4, Export to Datasmith | Owner |
| 1.8 | Import the test file into a scratch level in 5.8 and in 5.9; count objects and check one known dimension | Datasmith importer through Python | Agent |
| 1.9 | Assign 20 library materials in Unreal, change one wall in the Revit test view, re-export, reimport, and count surviving assignments | Revit; Datasmith reimport | Owner exports; Agent tests |
| 1.10 | Render station S1 with the Path Tracer at 3840 by 2160 three times in each engine, into `docs\unreal\1529_wieland\review\phase1\` | Movie Render Graph; if it fails, the older Movie Render Queue | Agent |
| 1.11 | Compare the engine's sun direction with the NOAA calculator for 15 August, 15:30 Central Daylight Time at the lot centre | Sun Position plugin; NOAA Solar Calculator in a browser | Agent |
| 1.12 | Place a 1,000-lumen point light in a dark scratch level and read the illuminance at 1 m | Editor's lighting visualization | Agent |
| 1.13 | In 5.9 only: find and switch on Lumen World Cache and the new handling of overlapping glass; capture S1 with each on and off, with timings | Project settings; scene capture | Agent |
| 1.14 | Run the fixed exterior path in a loop for two hours in each engine | Editor's performance tools | Agent |
| 1.15 | Remove the unrelated Belmont and beech content from the working copy, after approval | Editor content browser through the agent server | Agent |
| 1.16 | Write the gate result and the engine decision into `OPEN_DECISIONS.md` | Text editor | Agent drafts; Owner decides |

**Acceptance.** Every line is a number.

- Agent server: 50 consecutive read-only calls with no error.
- Baseline, 5.8 only: the three October views are within 10 percent of their October means (12.7, 11.9 and 12.9 ms) at the same viewport size, which is recorded this time.
- Import: at least 99.5 percent of the Revit test view's elements arrive, and the known dimension is within 1 mm.
- Reimport: 20 of 20 Unreal-side assignments survive.
- Path Tracer: three renders complete with no crash.
- Sun: bearing and height within 0.5 degree of the NOAA values.
- Light units: the reading is within 10 percent of 79.6 lux.
- Soak: two hours with no crash and video memory growing by no more than 5 percent.
- **Engine gate.** Each engine is scored separately on the agent server, import, reimport, Path Tracer, sun, light units and soak lines. Commit to 5.9 only if 5.9 passes all seven and step 1.13 shows a difference visible in a side-by-side of S1 while adding no more than 1.0 ms to 5.9's own graphics-card frame time at S1. Otherwise commit to 5.8.4, provided 5.8.4 passes all seven. If neither engine passes, stop and report to the owner.

**Main risks.**

- The agent server is experimental and does not start by itself in 5.9 unless set to (Epic lists a known issue with its defaults). Fallback: 5.8, where the earlier work's notes (`E:\Games\Claude\1527 Wieland\UNREAL_MCP.md`) record it running on the same address; that is to be confirmed in step 1.1.
- The Datasmith file from Revit 2025 is written at an older engine level than either engine expects. Fallback: the FBX route the earlier work used, which loses reimport and metadata.
- The cache does not move, or the move is skipped, and C: fills during shader compilation.
- Preview defects appear only after the gate. Mitigation: archive the project to H: at every milestone.

**Leaves behind.** Profile M0 for both engines; the completed live audit appended to `SITE_MODEL_AUDIT.md`; the engine decision; a tested import and reimport method.

---

## Phase 2: Site data and georeferencing

**Goal.** One coordinate frame for the lot, the street and the neighbours, tied to the survey, with true north measured, and the site visit done.

**Inputs.**

- `SOURCES.md` for each dataset, its terms and what it can prove.
- `REFERENCE_VIEWS.md` for the stations, tolerances and the site-visit shot list.
- The owner's survey (sheet T1.1) and site plan (sheet T1.4) of drawing set 25-006.
- The existing model's anchor: longitude -87.6355370, latitude 41.9102814, stated error 1.5 m, with model north assumed to be true north.

**Steps.**

| No. | Step | Tool | Who |
|---|---|---|---|
| 2.1 | Make the site visit and work through the shot list and measurement list | Camera, tape or laser, grey card | Owner |
| 2.2 | Ask approval, then download the 2022 lidar tile or tiles covering the block, the county parcel outlines, the county 2022 building footprints and the 2025 aerial photograph for a 300 m square around the lot | Web browser or `curl`, into `E:\` | Agent, after approval |
| 2.3 | Read each file's coordinate system from its header and record it; convert everything to one system (Illinois State Plane East, 2011 adjustment, metres for use in the engine) | Python with a projection library, after checking that the library is installed | Agent |
| 2.4 | Measure the bearing of the lot's side lines from the parcel outlines and from the survey; record true north for the site | Python; the survey drawing | Agent; Owner confirms against the survey's north arrow |
| 2.5 | Choose the level origin at the surveyed south-west lot corner; record the level-to-map transform and the sun tool's north offset | Georeferencing plugin through the agent server | Agent |
| 2.6 | Re-anchor the existing site model to the new origin and north, and measure how far its buildings sit from the lidar and parcel positions | Editor's agent server; Python | Agent |
| 2.7 | From lidar, extract the ground surface, kerb and sidewalk levels, each neighbour's roof heights and roof shape, and each tree's crown height and spread | Python point-cloud processing | Agent |
| 2.8 | Enter the site-visit measurements: station points, trees, poles, hydrant, signs, fences, street and alley widths | A table in this repository, `docs\unreal\1529_wieland\site_survey.csv` | Owner supplies; Agent enters |
| 2.9 | Name each tree's species from the owner's bark, bud, form and leaf photographs, with a stated confidence | Looking; a regional tree key | Agent proposes; Owner confirms |
| 2.10 | List every gap: anything a station can see for which no evidence was gathered | `docs\unreal\1529_wieland\site_gaps.md` | Agent |

**Acceptance.**

- Three surveyed lot corners convert from map coordinates to level coordinates and back within 0.05 m.
- True north is recorded to 0.2 degree, with the two methods (parcel outline and survey arrow) agreeing within 0.3 degree.
- A top-down render of the lot outline and the neighbours' footprints laid over the county aerial photograph (station S8) shows every kerb line and building corner within 1.0 m.
- Every tree and every item of street furniture visible from a station has a row in the survey table, or a row in the gaps list.

**Main risks.**

- The survey and the record lot width disagree by 0.21 m; the owner states which governs (`OPEN_DECISIONS.md`, decision 7).
- The 2022 lidar predates the 2026 demolition and may catch 1526 N. Wieland under construction. The 2017 lidar and site photographs cover those cases.
- County data publish no horizontal accuracy, so the absolute tolerance stays at 1.0 m.
- A November visit cannot settle leaf-on appearance, and species named from bark and buds carry lower confidence.
- Construction on the lot may block stations or change the sidewalk.

**Leaves behind.** The coordinate transform and north offset; lidar-derived ground, heights and crowns; the survey table; the gaps list; the owner's photograph set filed by station.

---

## Phase 3: Revit export and Datasmith import

**Goal.** The whole building in the Unreal level at the surveyed position, with a repeatable path from Revit that keeps every Unreal-side material assignment and edit.

**Inputs.**

- The engine chosen at the Phase 1 gate and the import method tested there.
- The level origin, true north and lot corners from Phase 2.
- The Revit model, opened by the owner. Its project location and true-north angle are read from it.
- The existing project already holds an earlier import at `Content\Wieland\Revit1527\Datasmith\MAIN_r01` with no recorded source; it is kept for comparison and not built on.

**Steps.**

| No. | Step | Tool | Who |
|---|---|---|---|
| 3.1 | Read the model's project base point, survey point, true-north angle, levels and material list | Read-only queries to the open Revit model | Agent |
| 3.2 | Prepare one 3D export view per part: shell and structure, exterior envelope, each floor's interior, site elements. Hide everything Unreal will replace (Revit's own site context and planting) | Revit view settings | Owner |
| 3.3 | Export each view to a Datasmith file in the project's `ImportStaging` folder, with the file name carrying the date and the Revit model's save time | Revit 2025.4, Export to Datasmith | Owner |
| 3.4 | Import into its own sub-level per part, under `/Game/Wieland1529/Building/` | Datasmith importer through Python | Agent |
| 3.5 | Place the import by matching the Revit survey point to the level origin and applying the true-north angle | Editor's agent server | Agent |
| 3.6 | Write the material mapping table: one row per Revit material name, naming the library material that replaces it | `docs\unreal\1529_wieland\material_map.csv` | Agent drafts; Owner reviews |
| 3.7 | Apply the mapping by script as actor-level overrides. Never edit an asset that Datasmith created; where a mesh must change, duplicate it and record the swap in `docs\unreal\1529_wieland\mesh_swaps.csv` | Python in the editor | Agent |
| 3.8 | Rehearse a change: the owner moves one element in Revit, re-exports, and the Agent reimports and re-runs the mapping script | Revit; Datasmith reimport; Python | Owner and Agent |
| 3.9 | Convert opaque building meshes to Nanite; keep glass separate | Editor's agent server | Agent |
| 3.10 | Run the fixed camera path and save profile M1 | Editor's performance tools | Agent |

**Acceptance.**

- Element count: the number of Revit elements in the export views equals the number of imported objects within 0.5 percent, with every difference listed.
- Position: the four building corners at grade are within 0.05 m of the governing lot lines (`OPEN_DECISIONS.md`, decision 7) plus setbacks, and the floor levels are within 5 mm of 2.032, 5.283, 8.534 and 11.786 m above the Revit ground datum.
- Rehearsal: after the reimport, 100 percent of rows in the mapping table and the swap table are still in force, and the moved element is in its new place.
- No building surface is left on a default or placeholder material.

**Main risks.**

- The exporter built into Revit 2025 may write a file at an older engine level than the chosen engine expects. Phase 1 (steps 1.7 to 1.9) tests this pairing; this phase does not start until that test has passed.
- Datasmith recreates its own material assets on every reimport, so any edit made to them directly is lost. The mapping table exists to prevent that.
- Revit families with very dense geometry (fixtures, hardware) inflate the import; they are swapped for lighter meshes through the swap table.
- The owner's Revit session must not be saved, synchronized or reloaded by the Agent. Export is done by the owner unless the owner approves otherwise.

**Leaves behind.** The building in place; the mapping and swap tables; a rehearsed re-export procedure; profile M1.

---

## Phase 4: Surroundings

**Goal.** The block and its setting, built from evidence, with detail spent where the stations look.

**Inputs.**

- From Phase 2: ground surface, kerb and sidewalk levels, neighbours' footprints, heights and roof shapes, the survey table, the gaps list, and the owner's photographs.
- `SITE_MODEL_AUDIT.md`, findings A1 to A13.
- `REFERENCE_VIEWS.md` for the stations.
- The existing site model's 58 building parts.

**Zones, set by what the stations see.**

| Zone | What it covers | How it is built |
|---|---|---|
| 1 | Anything inside a station's frame within 40 m: the two adjacent buildings (1533 and 1525), the houses directly opposite, the street, kerbs, parkways and sidewalks in front, the alley behind the lot | Modelled from the owner's photographs and measurements on lidar massing: openings, reveals, sills, trim, stoops, railings, fences |
| 2 | The rest of both sides of the block visible in stations S4 and S5 | Lidar massing with correct openings and roof forms; materials from the library |
| 3 | One block further in each direction | Lidar massing with simple materials; no openings modelled |
| 4 | The city beyond | Simplified lidar massing merged into a few meshes, plus the sky. The alternative is in `OPEN_DECISIONS.md`, decision 6. |

**Steps.**

| No. | Step | Tool | Who |
|---|---|---|---|
| 4.1 | Test every existing building part against lidar and the 2022 footprints; mark each "keep", "correct" or "rebuild" | Python; editor's agent server | Agent |
| 4.2 | Build the ground: roadway with its crown, kerbs, parkways, sidewalks with joints, driveway aprons, the alley | Editor's geometry tools; Python | Agent |
| 4.3 | Rebuild or correct the two adjacent buildings from the owner's photographs and measurements | Editor's geometry tools, or Blender if the owner approves its use | Agent |
| 4.4 | Rebuild or correct the houses opposite the lot in the same way | Same | Agent |
| 4.5 | Generate Zone 2, 3 and 4 massing from lidar | Python | Agent |
| 4.6 | Place street furniture from the survey table: light poles with their fixture type, the hydrant, the utility pole with its transformers and overhead lines, signs, refuse carts, fences | Editor's agent server | Agent |
| 4.7 | Remove the placeholder lot and anything the survey does not support (for example the cedar fence), or mark it as a neutral placeholder and list it | Editor's agent server | Agent |
| 4.8 | Render every exterior station in a plain grey material beside the owner's photograph | Scene capture; Python for the side-by-side sheets | Agent |
| 4.9 | Run the fixed camera path and save profile M2 | Editor's performance tools | Agent |

**Acceptance.**

- Station S8 (plan): every Zone 1 building corner, kerb line, pole and hydrant is within 0.3 m of its surveyed or lidar position relative to the lot.
- Heights: every Zone 1 and Zone 2 parapet, eave and ridge is within 0.3 m of lidar.
- Side-by-side sheets for S1 to S7 and S9, grey render beside photograph, with the camera solved from the photograph: fixed edges align within 1.5 percent of image width (38 pixels at 2560).
- No station shows the edge of the world or a blank box inside Zone 1 or Zone 2.
- The gaps list is either empty or each remaining gap is visible in the sheets as a labelled placeholder.

**Main risks.**

- Without the site visit, Zone 1 falls back to lidar accuracy (about 0.5 m) and has no facade detail source.
- The alley has not been seen in any imagery.
- Neighbours may change during construction (scaffolding, new fences).
- Hand-modelling the adjacent buildings is the largest single block of work in the plan.

**Leaves behind.** Zoned surroundings in sub-levels under `/Game/Wieland1529/Surroundings/`; the grey side-by-side sheets; profile M2.

---

## Phase 5: Materials

**Goal.** A small library of parent materials at a stated texel density, with every visible surface carrying the weathering it has on site, passing this repository's material rules.

**Inputs.**

- The owner's material photographs with grey card and scale, from Phase 2.
- The mapping table from Phase 3 and the existing material parents (`M_R15_World_Metric`, `M_R15_UV_Metric`).
- This repository's material packages under `output\` (colour and 16-bit height maps) for interior finishes.
- The material rules in `AGENTS.md` and `WORKFLOW.md` at the repository root.
- `SITE_MODEL_AUDIT.md`, findings ML1 to ML9.

**The library.** Seven parent materials; everything else is an instance of one of them.

| Parent | Used for |
|---|---|
| Opaque surface | Brick, stone, concrete, siding, asphalt, roofing, plaster, timber. World-scaled mapping, large-scale variation, and layers for dirt at wall bases, streaks under sills, edge wear and moss. |
| Window glass | Tint, reflection, surface dirt; a refracting version for the offline tier |
| Metal | Painted, galvanized, anodized and cast |
| Fabric and soft surfaces | Interior furnishings |
| Foliage | Leaves and bark |
| Ground blend | Soil, mulch, turf and the edges where paving meets planting |
| Decal | Stains, cracks, asphalt patches, pavement markings |

**Texel density.** At 2560 pixels across a 24 mm view, one pixel covers 1.17 mm at 2 m and 11.7 mm at 20 m. The zones in the table are the surroundings zones of Phase 4: Zone 1 is anything a station sees within 40 m, Zone 2 is the rest of the block, Zone 3 is one block further, and Zone 4 is the city beyond.

| Where | Density |
|---|---|
| Interior surfaces and exterior surfaces that a station sees from within 3 m | 1,024 pixels per metre |
| Other Zone 1 surfaces | 512 pixels per metre |
| Zone 2 | 256 pixels per metre |
| Zone 3 and Zone 4 | 64 pixels per metre |

**Steps.**

| No. | Step | Tool | Who |
|---|---|---|---|
| 5.1 | Record a licence line for every texture and asset already in the project; remove any without one | `docs\unreal\1529_wieland\asset_licences.csv` | Agent |
| 5.2 | Build the seven parents, starting from the existing world-scaled parents | Material editor through the agent server | Agent |
| 5.3 | Make surface maps from the owner's photographs: correct perspective and lighting, balance on the grey card, build a field large enough to pass the repeat test | Python image processing, following `WORKFLOW.md` | Agent |
| 5.4 | Where photographs do not suffice, ask approval and take a public-domain set, then match its colour to the photograph | Web download after approval | Agent |
| 5.5 | Bring in this repository's material packages for interior finishes, keeping their physical scale | Python import | Agent |
| 5.6 | Author weathering per surface from the photographs: where dirt, streaks, stains and patches actually are | Material layers and decals | Agent |
| 5.7 | Build window assemblies: frame depth, glazing, and what is behind the glass | Editor's geometry tools | Agent |
| 5.8 | Test each material: a 3 by 3 tiling check, the largest uninterrupted surface it covers, and a grazing-light view; record relief in millimetres for any sculpted tile | Scene capture; Python | Agent |
| 5.9 | Render stations S1, S3 and S6 beside the owner's photographs | Scene capture | Agent |
| 5.10 | Run the fixed camera path and save profile M3 | Editor's performance tools | Agent |

**Acceptance.**

- Every material has a filled row in a test table: source, licence, physical size of its field, tested surface size, tiling result, grazing-light result. Every row passes.
- Colour: for the principal materials of 1533, 1525 and the paving, the difference from the grey-card-balanced photograph is 5 or less (CIEDE2000).
- Side-by-side sheets for S1, S3 and S6 show no recognizable repeat and no visible seam.
- Measured texel density of 20 sampled surfaces is within 25 percent of the table above.
- Sculpted tiles: pattern relief, grout step and clearance are recorded in millimetres and the pattern reads under grazing light.

**Main risks.**

- Photographs taken in flat November light carry weaker relief information.
- The repeat rule is hardest on the large blank brick side wall of 1533, which the existing model fails.
- Substrate is switched on in the existing project's settings file and is only in beta in the Path Tracer; a material may differ between the real-time and offline tiers.
- The 4.0 GB texture pool limits how many 1,024-pixel-per-metre surfaces can be in view.

**Leaves behind.** The parent library and instances under `/Game/Wieland1529/Materials/`; the licence table; the material test table; profile M3.

---

## Phase 6: Interiors

**Goal.** The Revit interior refined in detail, furniture, geometry and materials to the standard of the interior design views. The owner put interiors in scope on 2026-11-10.

**Inputs.**

- The imported building from Phase 3 and the material library from Phase 5.
- Design views D2 to D5 in `REFERENCE_VIEWS.md`; the owner names the unit and rooms.
- This repository's Revit families and material packages, which define the specified fixtures and finishes.

**Steps.**

| No. | Step | Tool | Who |
|---|---|---|---|
| 6.1 | List, room by room, what the Revit geometry lacks at camera distance: rounded edges, reveals, gaps between cabinet doors, grout joints, hardware, baseboards, switch plates | Looking at grey renders of D2 to D4 | Agent proposes; Owner prioritizes |
| 6.2 | Replace coarse or over-dense Revit family geometry with render-quality meshes, recording each swap in the swap table `docs\unreal\1529_wieland\mesh_swaps.csv` so that it is re-applied after every Revit re-export | Editor's geometry tools; Python | Agent |
| 6.3 | Apply finishes from this repository's material packages at their recorded physical scale | Material instances | Agent |
| 6.4 | Propose furniture and accessories per room with source, size and cost; acquire only what the owner approves | Licensed library, after approval | Agent proposes; Owner approves |
| 6.5 | Add the small things that make a room read as lived in: soft furnishings, window treatments, books and tableware | Editor placement | Agent |
| 6.6 | Render D2 to D4 in grey and in full material beside the matching Revit views | Scene capture | Agent |
| 6.7 | Run the fixed interior path and save profile M4 | Editor's performance tools | Agent |

**Acceptance.**

- Side-by-side sheets for D2, D3 and D4 beside the Revit view of the same camera: every fixture and finish in the Revit view is present, in the same place within 10 mm, in the specified finish.
- D4 under grazing light: tile relief reads, with relief recorded in millimetres as this repository's rules require.
- Edges: a count of sharp, unrounded edges within 2 m of the camera in D2, D3 and D4 is zero.
- Interior path: within the frame budget once Phase 9 is complete; recorded now.

**Main risks.**

- Interior detail multiplies object count and texture memory faster than anything outside.
- Furniture is a design choice; without the owner's selection the rooms stay sparsely furnished.
- Every mesh swap must survive a Revit re-export, which depends on the swap table being kept current.

**Leaves behind.** Refined rooms; the furniture list with licences; profile M4.

---

## Phase 7: Vegetation

**Goal.** Every tree where it really stands, at its real size and species, with the planting that the photographs show.

**Inputs.**

- The survey table from Phase 2: position, trunk circumference, height, crown spread and species with confidence for each tree.
- Lidar crown heights and spreads from Phase 2.
- `SITE_MODEL_AUDIT.md`, finding A7: the existing eleven trees are not evidenced and are removed.
- `ENGINE_NOTES.md`: Nanite Foliage, Dynamic Wind and the Procedural Vegetation Editor are all experimental.

**Steps.**

| No. | Step | Tool | Who |
|---|---|---|---|
| 7.1 | Remove the eleven existing trees and the generic ground planting from the working level; keep them in an archived sub-level | Editor's agent server | Agent |
| 7.2 | For each species named in the survey, propose a source: built in the engine's vegetation editor, or a licensed model, with size and cost | Procedural Vegetation Editor; store search | Agent proposes; Owner approves |
| 7.3 | Build or acquire one tree per species and fit each instance to its measured trunk diameter, height and crown spread | Vegetation editor; scaling by script | Agent |
| 7.4 | Place each tree at its surveyed position; build its pit, grate or parkway soil as photographed | Editor's agent server | Agent |
| 7.5 | Plant shrubs, hedges, lawn and weeds only where photographs show them, by type | Procedural placement inside drawn outlines | Agent |
| 7.6 | Make a leaf-off state for each tree for the November comparison | Vegetation editor | Agent |
| 7.7 | Test one tree near and far with Nanite Foliage and wind on and off; choose per zone | Scene capture; performance tools | Agent |
| 7.8 | Render S2, S3, S4 and S5 leaf-off beside the owner's photographs, and leaf-on for viewing beside the August 2026 Street View in a browser | Scene capture | Agent renders; Owner judges the leaf-on look |
| 7.9 | Run the fixed camera path and save profile M5 | Editor's performance tools | Agent |

**Acceptance.**

- Every surveyed tree is present: trunk position within 0.3 m, trunk diameter within 2 cm, height and crown spread within 1.0 m.
- Each tree's species matches the survey table. Trees whose species was named with low confidence are listed.
- Leaf-off side-by-side sheets for S2 to S5, with the camera solved from the photograph: trunk bases align within 1.5 percent of image width.
- No plant stands where the photographs show paving.
- Vegetation's cost: mean graphics-card frame time on the exterior path with all vegetation shown, minus the same with all vegetation hidden, is 3.0 ms or less.

**Main risks.**

- No public record of these trees exists; without the site visit this phase cannot meet its acceptance.
- Species named in November carry lower confidence until summer.
- The foliage features are experimental and may be unstable or slow; the fallback is conventional card-based foliage.
- The large tree at the rear of the lot may be removed by construction.
- A species may not exist in any library.

**Leaves behind.** Surveyed trees and planting under `/Game/Wieland1529/Vegetation/`, each with leaf-on and leaf-off states; profile M5.

---

## Phase 8: Lighting and atmosphere

**Goal.** Physically set light for each lighting condition, fixed exposure, and a path-traced ground truth for every reference view that the real-time lighting is measured against.

**Inputs.**

- True north and the lot centre (latitude 41.910215, longitude -87.635389) from Phase 2.
- The four lighting conditions and their dates and times in `REFERENCE_VIEWS.md`.
- Fixture types and positions from the Revit model, and each fixture's manufacturer and model from this repository's families.
- `SITE_MODEL_AUDIT.md`, findings A2 and ML1: the existing scene's sun is at the engine's template values (latitude 45.0, longitude -73.0, north offset 35 degrees, 12 December 2019, 10:00, 50,000 lux), and it uses automatic exposure with a +1.26 stop bias.

**Steps.**

| No. | Step | Tool | Who |
|---|---|---|---|
| 8.1 | Set the sun from latitude, longitude, time zone, north offset, date and time for each condition; check each against the NOAA calculator | Sun Position plugin; browser | Agent |
| 8.2 | Set sun and sky brightness in physical units so that a white card in open sun reads a daylight value appropriate to the date and time (about 80,000 to 100,000 lux for the summer afternoon) | Sky atmosphere and light settings | Agent |
| 8.3 | Turn automatic exposure off. Fix exposure per condition from camera settings: about 14 to 15 exposure value outdoors in sun, 7 to 9 indoors by day, 3 to 5 at dusk | Post-process settings | Agent |
| 8.4 | Ask approval, then download each fixture's photometric file from its manufacturer; set each light's output in lumens and its colour temperature from the data sheet | Web download after approval; light settings | Agent |
| 8.5 | Set street lights from the site visit's notes on fixture type and colour | Light settings | Agent |
| 8.6 | Add sky detail: clouds that match the reference condition, haze and distance fog | Volumetric clouds; fog | Agent |
| 8.7 | Render every station and design view with the Path Tracer at 3840 by 2160 for each condition it applies to. These are the ground truth. | Movie Render Graph | Agent |
| 8.8 | Render the same views with the real-time tier and compute the difference from the ground truth | Scene capture; Python image comparison | Agent |
| 8.9 | Adjust real-time lighting settings only (never the lights themselves) until the difference is within tolerance, or record what cannot be closed | Lumen and reflection settings | Agent |
| 8.10 | Compare shadow edges in the site-visit-match condition with the owner's photographs | Side-by-side sheets | Agent |
| 8.11 | Run both camera paths and save profile M6 | Editor's performance tools | Agent |

**Acceptance.**

- Sun: bearing and height within 0.5 degree of NOAA for every condition.
- Shadows: edges on the ground within 0.3 m of the owner's photograph taken at the same time.
- Exposure: sunlit sidewalk concrete within one third of a stop of the grey-card-balanced photograph.
- Fixtures: every interior and exterior fixture has a photometric file and a lumen value traceable to a data sheet, listed in a table.
- Real-time against ground truth: mean brightness difference of 10 percent or less over facade and ground at each view, and no region larger than 2 percent of the frame off by more than one stop. Regions that fail are listed with the cause.
- A side-by-side sheet of ground truth and real-time for every view.

**Main risks.**

- Epic's physical light units page could not be read; step 1.12 in Phase 1 is the check.
- Volumetric clouds are only partly supported by the Path Tracer, so skies may differ between tiers.
- Some fixtures may have no published photometric file; those use a generic distribution and are listed.
- A path-traced still may exceed the 10-minute budget at an acceptable noise level.
- The 10 percent tolerance is a proposal until the first pair is measured.

**Leaves behind.** One lighting sub-level per condition; the fixture table; ground-truth renders and comparison sheets; profile M6.

---

## Phase 9: Optimization

**Goal.** The real-time tier inside its frame-time and video-memory budgets on the fixed camera paths, with every change shown as a measured cost or saving, and no change to the offline tier's result.

**Inputs.**

- The budgets in this file and profiles M0 to M6.
- The list headed "What the real-time tier visibly gives up" under "Two tiers" in this file. Nothing outside that list may be traded away.
- The ground-truth renders from Phase 8.

**Steps.**

| No. | Step | Tool | Who |
|---|---|---|---|
| 9.1 | Compare profile M6 with the budget pass by pass; rank the overruns | Profile tables | Agent |
| 9.2 | Geometry: confirm every opaque mesh is Nanite, merge glass by facade, instance repeated objects, give Zones 3 and 4 merged stand-ins | Editor's agent server | Agent |
| 9.3 | Shadows: limit which objects cast shadow at distance, set the update rate for far shadows, cap the shadow page pool | Shadow settings | Agent |
| 9.4 | Lumen: tune gather and reflection quality; use the 5.9 lighting cache if the Phase 1 gate adopted 5.9 | Lumen settings | Agent |
| 9.5 | Foliage: set leaf reduction and wind cut-off distances; choose Nanite or card foliage per zone | Vegetation settings | Agent |
| 9.6 | Textures: confirm densities against the table in Phase 5, use virtual textures for the largest unique surfaces, hold the 4.0 GB pool | Texture settings | Agent |
| 9.7 | Lights at dusk: confirm MegaLights holds the direct-light share of the budget with every fixture on | Light settings | Agent |
| 9.8 | Upscaling: confirm 67 percent internal resolution; compare 60 and 75 percent on foliage and brick | Scene capture | Agent |
| 9.9 | After each change, run the paths, save the timing, and re-render S1 and D2 to compare with ground truth | Performance tools; image comparison | Agent |
| 9.10 | Save profile M7 and a change log listing each change with its measured effect in milliseconds and megabytes | `docs\unreal\1529_wieland\profiles\` | Agent |

**Acceptance.**

- Exterior path and interior path: 95th-percentile frame time 16.67 ms or less; no frame over 33.3 ms; graphics-card time 14.5 ms or less on average.
- Each render pass within its budget, or the overrun is offset by a named pass that is under.
- Peak video memory 13.0 GB or less.
- The Phase 8 real-time tolerance still holds at every view.
- Every change in the log has a before and an after measurement.

**Main risks.**

- The budget is tight: the existing, much lighter scene already used about 12 to 13 ms at full resolution.
- Hardware ray tracing with dense foliage can dominate video memory.
- No DLSS on 5.9; the engine's own upscaler is the only choice there.
- A setting that saves time may break the Phase 8 match; step 9.9 exists to catch that.

**Leaves behind.** Profile M7; the change log; the real-time settings recorded as a named configuration.

---

## Phase 10: Reality-match review

**Goal.** A scored comparison of every station against its reference, and an honest list of what matches, what does not, and what could not be checked.

**Inputs.**

- `REFERENCE_VIEWS.md`: stations, tolerances and conditions.
- The owner's photographs by station; the county aerial photograph for S8.
- The gaps list from Phase 2 (`docs\unreal\1529_wieland\site_gaps.md`) and the ground-truth renders from Phase 8.

**Steps.**

| No. | Step | Tool | Who |
|---|---|---|---|
| 10.1 | Solve each owner photograph's camera from its taped station point and its recorded focal length; set the engine camera to match | Python; editor camera | Agent |
| 10.2 | Render each exterior station in the site-visit-match condition, in both tiers, at the photograph's size | Movie Render Graph; scene capture | Agent |
| 10.3 | Build a sheet per station: photograph, offline render, real-time render, and an edge overlay | Python | Agent |
| 10.4 | Score each row of the tolerance table: positions, heights, overlay alignment, shadows, colour, brightness | Python measurement on the sheets and in the scene | Agent |
| 10.5 | Render the summer afternoon condition for every station, for the owner to view beside the August 2026 Street View in a browser | Movie Render Graph | Agent renders; Owner judges |
| 10.6 | Score the design views D1 to D5 against the Revit views and the ground truth | Sheets | Agent |
| 10.7 | Write the review: a table of pass, fail and "could not be checked" per station and per tolerance, each failure with a cause and a proposed fix | `docs\unreal\1529_wieland\REVIEW.md` | Agent |
| 10.8 | The owner reviews the sheets and marks each failure "fix" or "accept" | Looking | Owner |
| 10.9 | Fix what is marked, then re-render and re-score only the affected stations | The phase that owns the fix | Agent |

**Acceptance.**

- Every exterior station S1 to S9 has a side-by-side sheet and a score against every tolerance that applies.
- Every "could not be checked" entry names the missing evidence.
- No tolerance is reported as met without a measurement.
- The owner has marked every failure.

**Main risks.**

- The building did not exist when the photographs were taken, and the lot is a construction site. The comparison covers the surroundings and uses a mask over the lot.
- Leaf-off photographs cannot score the agreed summer condition. That part rests on the owner's judgment until a summer visit.
- Street View can be looked at beside a render and cannot be placed in a saved sheet.
- Camera solving from a phone photograph depends on its recorded focal length being right.

**Leaves behind.** The review file; the sheets; the owner's marks; a final list of accepted differences.

---

## Phase 11: Packaging and delivery

**Goal.** The stills, the animation, a packaged real-time build and an archived project, delivered and verified.

**Inputs.**

- The reviewed scene from Phase 10 and the real-time configuration from Phase 9.
- This repository's delivery rule in `AGENTS.md`: final packages go to Google Drive under "3D Model Workflow", folder "3D Models", and upload is verified from Drive's own file records.
- The owner's choices in `OPEN_DECISIONS.md`, decision 12.

**Steps.**

| No. | Step | Tool | Who |
|---|---|---|---|
| 11.1 | Render the final stills at 3840 by 2160 in the offline tier. The delivery list is: stations S1 to S7 and S9 and design views D1 to D4 in the summer afternoon condition; S1, S6 and D5 at dusk; S1 in the summer morning condition. That is 16 stills. | Movie Render Graph; if it fails, the older Movie Render Queue | Agent, after approval to write to H: |
| 11.2 | Render the 60-second animation, 1,800 frames at 3840 by 2160, to H:, by the method the owner chose per shot (`OPEN_DECISIONS.md`, decision 13), set up so that an interrupted run resumes from the last finished frame | Movie Render Graph; if it fails, the older Movie Render Queue | Agent, after approval to write to H: |
| 11.3 | Encode the animation | An encoder already installed; otherwise ask approval to install one | Agent |
| 11.4 | Package the real-time scene for Windows with the real-time configuration | Engine packaging | Agent |
| 11.5 | Run the packaged build on the fixed paths and save a final profile | Packaged build with timing capture | Agent |
| 11.6 | Write the delivery notes: what is measured, what is assumed, the accepted differences, every asset's licence, how to open and run | A file inside the package | Agent |
| 11.7 | Zip the package, record its size and checksum, and verify the zip | Python | Agent |
| 11.8 | Upload to Google Drive "3D Models"; confirm name, size and location from Drive's records; report the link | Google Drive connector | Agent |
| 11.9 | Archive the Unreal project to H: and record the archive's checksum. This repository's delivery rule asks for native files in the uploaded package, so the archive (about 30 GB) is also uploaded to Drive unless the owner waives that in decision 12. | File copy; Google Drive connector | Agent, after approval to write to H: |

**Acceptance.**

- Packaged build on the fixed paths: 95th-percentile frame time 16.67 ms or less at 2560 by 1440, and peak video memory 13.0 GB or less.
- The animation has 1,800 frames, none dropped or duplicated.
- All 16 stills of the delivery list in step 11.1 exist at 3840 by 2160.
- Drive's records show each uploaded file at the expected size in the expected folder.
- The licence table has a row for every third-party asset in the package.

**Main risks.**

- A packaged build can behave differently from the editor; it is profiled separately for that reason.
- Movie Render Graph is a beta feature and carries every still and the animation. The older Movie Render Queue is the fallback, and Phase 1 step 1.10 is the early test.
- Path-traced animation at 90 seconds a frame takes 45 hours; a crash mid-run must resume from the last finished frame.
- Free space on H: is consumed by frames and archives together.
- If Google's 3D city tiles were chosen, they cannot be packaged for offline use and limit what video may be published.
- Asset licences may restrict redistribution inside a packaged build.

**Leaves behind.** The delivered package and its Drive link; the archived project; the final profile; the delivery notes.

---

## Open risks, in order of how much each could change the plan

1. **The engine.** 5.9 is an unstable preview with no DLSS or Cesium plugin, and its experimental agent server had to be started by hand here. The Phase 1 gate may send the whole project to 5.8.
2. **The Revit-to-Unreal path.** No source confirms that Revit 2025's exporter suits either engine. If it fails, reimport and the mapping table fall back to a weaker FBX route.
3. **Evidence for the block.** No public record exists for trees, poles, hydrants or signs. The site visit is the only source, and it happens in November on a construction site.
4. **The season.** The agreed summer condition cannot be scored against the owner's own photographs until summer 2027.
5. **Frame budget.** The lighter existing scene already used three quarters of the frame at full resolution.
6. **Imagery terms.** Street View cannot be saved or traced. Earlier work on this project did fetch Street View images, and that practice stops.
7. **Disk space.** C: has 20.8 GB free and holds the engine cache until the owner moves it.
8. **The live audit is partial.** Sun, lights and exposure were read from the open editor. The materials on each part and the object that marks the building's site were not, and no object in the level carries a site name.
9. **Sessions in the editor's terminal.** That way of working was read about, not tried. A session there ends with the editor and may lack the browser, Revit and Drive connections.
