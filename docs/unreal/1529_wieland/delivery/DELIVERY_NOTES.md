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
| `LICENCES.csv` | One row for every outside asset group in the packaged build, with its source and licence as recorded (section 8). |
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
- The `comparison\` folder holds, for one frame of each move, the real-time frame and the same frame path-traced (1,024 samples): triplex frame 180 (the living room looking to the rear patio) and penthouse frame 300 (the living room). The penthouse pair agrees closely, except a slatted panel beside the opening, which the Path Tracer draws dark with a bright green-yellow strip. The triplex path-traced frame is grainier and darker than the stills and draws the living-room floor as a flat light surface instead of wood planks; the likeliest cause is the simplified copy of the floor mesh that the Path Tracer follows (section 2), but it was not proven. The twelve stills, made the same way from a fixed camera, show wood floors where floors are visible.

## 4. The packaged build: how to open and run

Copy the `build\` folder anywhere on a Windows 10 or 11 computer (64-bit) and double-click one of the start files:

| Start file | What it does |
|---|---|
| `Run_Walkthrough_2560x1440.bat` | The walk-through, full screen at 2,560 by 1,440, with the real-time settings measured in section 5. |
| `Run_Walkthrough_Window_1920x1080.bat` | The same in a 1,920 by 1,080 window, for a smaller screen. |
| `Run_Profile_FixedPaths.bat` | Plays the fixed camera paths of section 5 in a loop, records the frame times and closes by itself after about ten minutes. The record is written to `build\Windows\Wieland1527\Saved\Profiling\CSV\`. |

Controls in the walk-through: the mouse looks around; W, A, S, D move; E or Space rises, Q or C sinks. The viewer flies (no gravity). Alt+F4 closes the program. The walk-through starts on the west sidewalk at station S1, facing the building. The interior level of each of the four apartments is loaded when the viewer enters that apartment and unloaded when the viewer leaves it (Unreal's streaming boxes, set up in Phase 6); from outside, all four are loaded.

Starting `build\Windows\Wieland1527.exe` directly also opens the walk-through, but with the project's general settings (full pixel count, frame rate capped at 60), not the measured real-time settings.

What the computer needs: a graphics card for DirectX 12 with hardware ray tracing (for example NVIDIA RTX 30 or 40 series) and preferably 16 GB of video memory, 32 GB of system memory. It was built and measured on an NVIDIA GeForce RTX 4080 (16 GB), an AMD Ryzen 7 7800X3D and 31 GB of memory, Windows 11.

The build is the "Development" kind, not the "Shipping" kind: it keeps the engine's console (key `~`) and the frame-time recorder, which the profile needs. Nothing else differs for the viewer.

The switchable options of the scene (Unreal's Variant Manager lists: "Surroundings", "Revit site objects", "Site ground", "Season", and the Phase 12 material set) cannot be switched in the build; it shows the options that are saved in the levels. They stay switchable in the Unreal project.

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

## 8. Licences of outside assets in the packaged build

`LICENCES.csv` has one row for every group of outside assets that the packaged build contains, found by listing the cooked asset folders of the build against the project's licence records (`asset_licences.csv`, `asset_licence_groups.csv`, `asset_downloads.csv`, `SOURCES.md` in the plan folder). "Not recorded" means that the project holds no record of where the asset came from or of its terms; those rows are listed for the owner to confirm before the build is shown outside the owner's own office.

## 9. What still needs the owner

Decisions that stay open; the scene keeps its switchable options and labelled stand-ins as they are until the owner decides:

1. Mark F1 to F9 (section 6) "fix" or "accept".
2. The site visit and site photographs, which would let the remaining nine tolerances be checked.
3. Furniture (the 81 grey stand-ins), the distant city stand-in, the lawn, and up to two finish alternatives per surface (none named yet).
4. Licences: the rows marked "not recorded" in `LICENCES.csv`, in particular the Megaplant tree library (all 34 trees use it), Fab and Megascans content, and the manufacturers' terms for the light-distribution files and images that came with the Revit families.
5. 1520 N. Wells: a wrecking permit was issued on 1 May 2026, so the existing building shown there (as surveyed in 2022) may be gone.
6. The switchable options in the Unreal project: "Surroundings" (earlier detailed buildings or the survey massing), "Revit site objects", "Site ground", "Season" (leaf-on or leaf-off) and the Phase 12 material set; the build shows the saved choice.
