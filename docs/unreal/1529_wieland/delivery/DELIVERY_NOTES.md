# 1529 N. Wieland St., Chicago: Unreal Engine scene, delivery of 2026-11-14

This package holds the final pictures, the animation and a program that shows the scene in real time, made in Unreal Engine 5.9 from the owner's Revit model (25-006, 1527 N. Wieland, exported through Datasmith) and from public site data. These notes say what each part is, how it was made, what was measured and what was assumed, which differences are known, what licence each outside asset carries, and how to open and run everything.

Words used the same way throughout:

- **Station** (S1 to S9): a fixed camera position on the street, from the plan's reference views. **Design view** (D1 to D5): a fixed camera position in or on the building. **View** means either.
- **Path-traced**: made by Unreal's Path Tracer, the slow renderer that follows light physically, the way an offline architectural renderer does. **Real-time**: made by the renderer the walk-through uses (Lumen, Unreal's method for bounced light and reflections at interactive speed).
- **Level**: Unreal's word for one saved scene file. **Level sequence**: a saved camera move with a time line.
- **Packaged build**: the scene turned into a Windows program that runs without Unreal. **Frame time**: the time the computer needs to draw one picture, in milliseconds (ms); 16.67 ms is 60 pictures a second.
- **Stand-in**: a simple object that holds the place of something not yet chosen or not yet known; every stand-in is labelled as such.

## 1. What is in the package

| Folder or file | What it is |
|---|---|
| `DELIVERY_NOTES.md` | This file. |
| `LICENCES.csv` | One row for every group of assets in the packaged build, with its source and licence as recorded (section 8). |
| `LICENCES_per_asset.csv` | One row for every one of the 3,543 assets packed in the build, with its group and licence as recorded. |
| `stills\` | Twelve path-traced pictures, 3,840 by 2,160 pixels (section 2). |
| `video\` | The animation: two 30-second moves and the 60-second film that joins them (section 3). |
| `comparison\` | For each move, one frame made path-traced beside the same frame made real-time. |
| `build\` | The packaged build, with three start files (section 4). |
| `profile\` | The final profile of the packaged build on the fixed camera paths (section 5). |
| `MANIFEST_SHA256.txt` | Size and SHA-256 checksum of every file in the package. |

## 2. The stills

Twelve views in the summer afternoon condition (sun bearing 241.72 degrees, height 46.40 degrees above the horizon), path-traced at 3,840 by 2,160 pixels with 1,024 samples per pixel: stations S1, S2, S3, S4, S5, S6 and S9 and design views D1 to D5. All were rendered on 2026-11-13 between 08:35 and 11:57 and show the site as surveyed: the existing buildings and the empty lot at 1520-1528 N. Wells (the proposed hotel studied that afternoon was withdrawn by the owner and removed from the project before this delivery; nothing of it is in these pictures or in the build).

- **Station S7 does not exist.** The plan placed it in an alley behind the lot. The plat of survey shows no alley; the point lies inside the rear neighbour's lot. The rear of the building is shown by design view D5.
- **Trees in the path-traced pictures are coarse.** A Unreal 5.9 setting that lets the Path Tracer follow full-detail geometry (`r.RayTracing.Nanite.Mode` 2) hung the graphics card three times, so it is kept off. The Path Tracer then traces each mesh's simplified fallback copy: buildings and furniture are unchanged to the eye, but tree leaves show as coarse triangles. The real-time pictures and the build draw the full-detail trees.
- No finish-alternative still was made: no alternative has been named.

## 3. The animation

Two continuous camera moves of 30 seconds each, 900 frames each at 30 frames a second, 3,840 by 2,160 pixels, with no cut inside either move:

1. **Triplex** (`W1529_Triplex_30s_3840x2160.mp4`): from the lower level through the north triplex's circulation, every level, and the last 10 seconds on the rear covered and uncovered patios.
2. **Penthouse** (`W1529_Penthouse_30s_3840x2160.mp4`): through the north penthouse, the last 10 seconds on the roof deck.

`W1529_Animation_60s_3840x2160.mp4` is the two moves joined, triplex first, with one cut between them (1,800 frames).

How the frames were made: the real-time renderer (Lumen) at its highest settings with 16 samples per frame, bounced light at "Epic" and reflections and shadows at "Cinematic" quality, the engine's own anti-aliasing (Temporal Super Resolution), a 24 mm lens at f/8, light motion blur, and an exposure written for every frame (outdoors, rooms and the dark lower level each get their own). Each move was rendered as one unbroken run after 1,024 settling frames, so the bounced light is steady from the first frame; an earlier attempt in shorter runs showed a visible brightness step at every join and was discarded. The frames are kept as PNG files beside the package (`D:\Wieland1529_delivery\animation_frames\`), not inside it. Video: H.264, quality setting CRF 16, colour standard BT.709.

Things to know when watching:

- The lower level of the triplex has daylight only through small windows; the camera's exposure is raised there, so it reads brighter than it would to the eye.
- At about 19.9 seconds of the triplex move the camera passes through the plane of the closed glass door onto the patio; reflections in the glass vanish at that moment.
- The `comparison\` folder holds, for one frame of each move, the real-time frame and the same frame path-traced (1,024 samples): triplex frame 180 (the living room looking to the rear patio) and penthouse frame 300 (the living room). The penthouse pair agrees closely, except a slatted panel beside the opening, which the Path Tracer draws dark with a bright green-yellow strip. The triplex path-traced frame is grainier and darker than the stills and draws the living-room floor as a flat light surface instead of wood planks; the likeliest cause is the simplified copy of the floor mesh that the Path Tracer follows (section 2), but it was not proven. The twelve stills, made with the same renderer settings from a fixed camera, show wood floors where floors are visible.

## 4. The packaged build: how to open and run

Copy the `build\` folder anywhere on a Windows 10 or 11 computer (64-bit) and double-click one of the start files:

| Start file | What it does |
|---|---|
| `Run_Walkthrough_2560x1440.bat` | The walk-through, full screen at 2,560 by 1,440, with the real-time settings measured in section 5. |
| `Run_Walkthrough_Window_1920x1080.bat` | The same in a 1,920 by 1,080 window, for a smaller screen. |
| `Run_Profile_FixedPaths.bat` | Plays the fixed camera paths of section 5 in a loop, records 60,000 frames and closes by itself (13 minutes on the computer it was measured on). The record is written to `build\Windows\Wieland1527\Saved\Profiling\CSV\`. |

Controls in the walk-through: the mouse looks around; W, A, S, D move; E or Space rises, Q or C sinks. The viewer flies (no gravity). Alt+F4 closes the program. The walk-through starts on the west sidewalk at station S1, facing the building. The interior level of each of the four apartments is loaded when the viewer enters that apartment and unloaded when the viewer leaves it (Unreal's streaming boxes, set up in Phase 6); from outside, all four are loaded.

Starting `build\Windows\Wieland1527.exe` directly also opens the walk-through (checked: it loads the scene in about one second and reports no errors), but with the project's general settings (full pixel count, frame rate capped at 60), not the measured real-time settings.

What the computer needs: a graphics card for DirectX 12 with hardware ray tracing (for example NVIDIA RTX 30 or 40 series) and preferably 16 GB of video memory, 32 GB of system memory. It was built and measured on an NVIDIA GeForce RTX 4080 (16 GB), an AMD Ryzen 7 7800X3D and 31 GB of memory, Windows 11.

The build is the "Development" kind, not the "Shipping" kind: it keeps the engine's console (key `~`) and the frame-time recorder, which the profile needs. Nothing else differs for the viewer.

The switchable options of the scene (Unreal's Variant Manager lists: "Surroundings", "Revit site objects", "Site ground", "Season", and the Phase 12 material set) cannot be switched in the build; it shows the options that are saved in the levels. They stay switchable in the Unreal project.

## 5. The final profile of the packaged build

The plan's lines for the real-time build: on the fixed camera paths, a 95th-percentile frame time of 16.67 ms or less (60 pictures a second for 95 frames in 100) at 2,560 by 1,440 pixels, and peak video memory of 13.0 GB or less. Both are met.

The fixed paths are those of the plan and of Phase 9: a 60-second walk along the west sidewalk at 1.4 m a second, 1.6 m eye height, keeping the front door in the middle of the picture; 10-second holds at stations S1, S2 and S6; a 30-second walk through the triplex with a 10-second hold at design view D5; a 20-second walk through the penthouse with a hold at D2; and 10 seconds on the roof deck. Each part starts with an 8-second wait at its first point so that the apartment's interior has loaded, and the waits are not counted. The program played the whole 202-second sequence in a loop; the first play warms the program up, and the second play is the profile. Settings: full screen 2,560 by 1,440, 67 % of the pixels computed and enlarged by Temporal Super Resolution, every quality group at "Epic", texture pool 4,000 MB, no frame-rate cap, `r.RayTracing.Nanite.Mode` 0 (all read back from the program's own log).

| Path or hold (second play) | Frames | Mean (ms) | 95th percentile (ms) | Worst (ms) | Graphics card mean (ms) |
|---|---|---|---|---|---|
| Street walk, 60 s | 4,300 | 13.96 | 15.19 | 24.20 | 12.35 |
| Hold S1 | 695 | 14.39 | 15.45 | 23.39 | 12.79 |
| Hold S2 | 725 | 13.78 | 14.94 | 20.56 | 12.13 |
| Hold S6 | 750 | 13.33 | 14.47 | 20.44 | 11.78 |
| Triplex walk, 30 s | 2,485 | 12.07 | 15.47 | 21.87 | 10.57 |
| Hold D5 | 857 | 11.67 | 12.88 | 19.99 | 10.08 |
| Penthouse walk indoors, 20 s | 1,506 | 13.28 | 15.84 | 18.76 | 11.73 |
| Hold D2 | 756 | 13.24 | 14.46 | 17.24 | 11.63 |
| Roof deck walk, 10 s | 757 | 13.21 | 14.71 | 15.94 | 11.66 |
| **All paths and holds** | **12,831** | **13.25** | **15.19** | **24.20** | **11.68** |

No frame of the second play took longer than 33.3 ms; 110 of 12,831 frames took longer than 16.67 ms. The first and third plays agree with the second within 0.1 ms on the 95th percentile. Video memory: the program's own reading peaked at 5,479 MB over the whole run (5,461 MB in the second play); Windows reported 5,527 MB more in use on the card at the peak than before the program started.

Conditions to know: the Unreal editor stayed open during the run, on an empty level and not drawing, because it hosted the agent that ran the measurement; it held 6.3 GB of the card's 16 GB, so the program had about 10 GB of video memory available. The figures are a little higher than the editor's figures of Phase 9 (for example 12.82 ms on the street walk), which computed the same number of pixels in a smaller window; these packaged figures are the ones at the true picture size. The full record (60,000 frames) and the program's log are in `profile\`.

## 6. What is measured, what is assumed, and the known differences

### Measured (with the data behind it)

| Item | Data |
|---|---|
| Lot: 49.50 by 102.20 ft (record rectangle), which governs; the Revit model's property lines are used | Plat of survey, sheet T1.1 of 2025-08-18; county parcel |
| Street right of way 50 ft; no alley behind the lot | Plat of survey |
| Ground heights on a 1 ft grid | 2022 laser survey of the ground, Illinois State Geological Survey |
| Tree positions and crown heights (34 trees, 12.7 to 17.8 m on the lot's street) | 2022 laser survey (top surface minus ground) |
| Neighbours' positions; neighbours' heights | Plat of survey (positions); county building outlines 2022 and the 2022 laser survey (heights) |
| True north, within 0.03 degrees by three independent lines | Parcel lines, building walls, lot front line |
| The building on its lot, within 0.1 to 0.3 mm of the Revit export | Revit export through Datasmith |
| The sun's direction, within 0.05 degrees of the computed position for the summer afternoon | Engine sun against an independent solar calculation |

### Assumed, or held by a labelled stand-in

- **Tree species** are not known; the tree models were chosen by shape (19 ginkgo, 9 Norway maple, 5 English oak, 1 silver birch). Trunk positions are the crown centres.
- **Neighbours' façades** are plain walls in a neutral grey; their parapets and roof edges are finer than the 1 ft laser grid. Street furniture (hydrants, poles, signs, bins), parkway planters, the iron fence, cars, road markings and people are left out.
- **Sidewalk and kerb** are plain concrete; the car park south of 1525 is flat asphalt at the measured ground height. Anything built or planted after spring 2022 is not in the data.
- **The distant city** behind the roof deck (view D1) is a stand-in made from public laser massing. **The lawn** is a green-tinted stand-in that fails the material check closer than 1 m.
- **Furniture** in the four units: 81 grey stand-ins (planters with shrubs, outdoor dining tables, display shelves, outdoor sofas and others), each labelled "grey stand-in; furniture is not approved". Eight Revit markers are kept as exported (manufacturer logos, clearance and warning symbols, camera symbols, Miele connection symbols).
- **Finishes**: 53 of the rebuilt materials carry values only (colour and gloss from the product data, no image); one finish colour is guessed from its object name; one fixture's light output is a generic 800 lumen lamp; four kinds of fixture with no published light-distribution file use generic shapes.

### Known differences (the reality-match review of Phase 10)

Nine differences were listed for the owner to mark "fix" or "accept" (`review\phase10\owner_marks.csv`); none has been marked yet, so none counts as accepted:

| No. | Difference |
|---|---|
| F1 | Neighbours' heights: 3 of 19 buildings near the lot within 0.3 m; overall up to 12.07 m off (the earlier detailed neighbour models are kept as modelled) |
| F2 | Neighbours' walls: 26 of 76 sides near the lot more than 0.5 m from the county outline, largest 3.0 m |
| F3 | The roadway sits 13.1 cm under the laser ground (the kerb was made by lowering the roadway) |
| F4 | S9, real-time against path-traced: 26.2 % brighter; upper windows across the street four stops brighter |
| F5 | D3, real-time against path-traced: 18.0 % brighter; the pendant's glass shade glows in real time |
| F6 | D4 (windowless bath), real-time against path-traced: 42.4 % darker; Lumen carries less bounced lamp light in a small closed room |
| F7 | D5, real-time against path-traced: 11.9 % darker under the covered patio |
| F8 | Sharp edges inside fixtures at D2, D3, D4: 569, 451 and 328 left |
| F9 | S8 plan view from 2 km up, real-time against path-traced: 38.5 % brighter in roofs and ground in shadow |

Other limits: nine of the nineteen tolerances of the reference views could not be checked because no site photographs exist yet (the site visit has not been made); the design views were not checked against Revit views; the soak test of Phase 9 ran 42 of 120 walks.

## 7. Where everything is, and how to check it

- **This package** is delivered as one zip file, `1529_Wieland_UE5.9_Delivery_2026-11-14.zip`. Its size and SHA-256 checksum are written beside it (`.sha256.txt`) on `D:\Wieland1529_delivery\` and in the Google Drive folder `My Drive\Folders\3D Model Workflow\3D Models\1529_Wieland_UE5.9_Delivery_2026-11-14\`. Inside the zip, `MANIFEST_SHA256.txt` lists the size and checksum of every file; on Windows a file can be checked with `certutil -hashfile <file> SHA256`.
- **The Unreal project** is archived separately as `1529_Wieland_UE5.9_Project_Archive_2026-11-14.zip` (the project file, `Config`, `Content` and `ImportStaging`, which holds the Revit/Datasmith exports; not the folders the engine rebuilds by itself: `Saved`, `Intermediate`, `DerivedDataCache`, `Backups`, `Binaries`), in the same two places, with its checksum beside it.
- **The animation frames** (1,800 PNG files, 15.6 GB) stay on `D:\Wieland1529_delivery\animation_frames\`, with the path-traced comparison frames and, set aside, the test frames of the first attempt.
- The working records of this phase (journal, scripts, checks) are in the plan's repository, `docs\unreal\1529_wieland\phase11_results.md` and `review\phase11\`.

## 8. Licences of outside assets in the packaged build

`LICENCES.csv` has one row for every group of outside assets that the packaged build contains, found by reading the build's own list of packed files (Manifest_UFSFiles_Win64.txt) against the project's licence records (`asset_licences.csv`, `asset_licence_groups.csv`, `asset_downloads.csv`, `SOURCES.md` in the plan folder). "Not recorded" means that the project holds no record of where the asset came from or of its terms; those rows are listed for the owner to confirm before the build is shown outside the owner's own office.

The build packs 3,543 assets. Every one of them falls in a group of the project's licence record, or is this project's own work, or is Unreal Engine content. `LICENCES.csv` has one row per group (17 groups); `LICENCES_per_asset.csv` has one row per packed asset with its group and licence as recorded.

| Group | Assets in the build | Licence as recorded |
|---|---|---|
| This project's own work (Phases 6 to 15) | 1,813 | own work |
| Unreal Engine and engine-plugin content | 720 | Unreal Engine licence (Epic Games) |
| Revit export, Phase 3 (the owner's model) | 312 | owner's property; the manufacturers' families inside it carry their makers' terms, not recorded |
| Surroundings, Phase 4 (county footprints and state laser data) | 181 | recorded (footprints "provided as is"; laser data without restriction) |
| Phase 5 materials | 142 | recorded (own work on CC0 texture sets) |
| Poly Haven texture sets | 33 | CC0 (as the earlier project's records state) |
| ambientCG glass imperfection set | 2 | CC0 |
| Earlier project's render settings | 1 | owner's own |
| **Megaplant tree library** (all 34 trees) | 120 | **not recorded** (an earlier note says "UE-only or no-redistribution") |
| **Earlier project's site model** (neighbour buildings) | 98 | **not recorded** (City of Chicago building footprints, terms page not read) |
| **Earlier project's production materials** | 37 | **not recorded** (the records contradict each other) |
| **Revit export images** (Autodesk library 28, other images 28, generated surfaces 16, Indiana limestone 6) | 78 | **not recorded** |
| **Megascans worn brick** | 2 | **not recorded** (tied to the account that took it) |
| **Earlier project's other materials** | 4 | **not recorded** |

339 packed assets in 9 groups have no licence record.

## 9. What still needs the owner

Decisions that stay open; the scene keeps its switchable options and labelled stand-ins as they are until the owner decides:

1. Mark F1 to F9 (section 6) "fix" or "accept".
2. The site visit and site photographs, which would let the remaining nine tolerances be checked.
3. Furniture (the 81 grey stand-ins), the distant city stand-in, the lawn, and up to two finish alternatives per surface (none named yet).
4. Licences: the rows marked "not recorded" in `LICENCES.csv`, in particular the Megaplant tree library (all 34 trees use it), the earlier project's site model and materials, the Megascans brick, and the manufacturers' terms for the light-distribution files and images that came with the Revit families.
5. 1520 N. Wells: a wrecking permit was issued on 1 May 2026, so the existing building shown there (as surveyed in 2022) may be gone.
6. Six Miele appliances (the wall ovens and similar built-ins from the Revit families) use a see-through black glass material on Nanite meshes; Nanite draws only solid materials, so the engine replaces that glass with its default material in real time (the build warns about it on start). A solid black glass material, or turning Nanite off for those six meshes, would fix it; that is a change to imported Revit assets and is left for the owner.
7. The switchable options in the Unreal project: "Surroundings" (earlier detailed buildings or the survey massing), "Revit site objects", "Site ground", "Season" (leaf-on or leaf-off) and the Phase 12 material set; the build shows the saved choice.
