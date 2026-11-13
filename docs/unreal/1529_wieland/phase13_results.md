# Phase 13 results: the proposed hotel at 1520-1528 N. Wells ("The Duke of Wells")

Status: DONE at 16:03 on 2026-11-13 (Central). The proposed hotel, its garage and three homes are built in `/Game/Wieland1529/Site/L_ProposedHotel`, switchable by the Variant Manager list "Neighbour development" (default "Duke of Wells (proposed)"), measured, compared with the renderings, and its effect on the views, the shadow and the frame time recorded. Phase 11 resumes: re-render S1, S2, S3, S4, S5, S6, D1 and D5. Nothing is pushed.

Project: `D:\Unreal_Engine_Projects\Wieland1527 5.9\Wieland1527.uproject` (Unreal Engine 5.9).
Plan: `PLAN.md`, Phase 13. This file is the journal of the phase. A line marked PENDING is written and committed before its step starts; it is replaced by the outcome when the step ends.

Everything this phase builds is **proposed, modelled from published renderings and records, not a survey**.

Words used the same way throughout this file:

- "Level" is Unreal's word for one saved scene file. The "top level" `L_Site_M4` loads the others. The "hotel level" is the new level `/Game/Wieland1529/Site/L_ProposedHotel`.
- "Object" is one placed thing in a level (Unreal calls it an actor). "Mesh" is the stored shape an object shows. "Material" is the surface finish on a mesh.
- "Station" is a fixed camera position on the street (S1 to S9, `REFERENCE_VIEWS.md`). "Design view" is a fixed camera position in or on the building (D1 to D5). "View" means either.
- "Variant Manager" is the engine's tool that holds lists of named options; choosing one option changes a set of objects in one action. "List" means one such list; "option" means one choice in it.
- "Earlier detailed buildings" are the copies of the October 2026 neighbourhood model in the level `L_Surroundings_R15` (Phase 7). "Phase 4 survey massing" is the set of blocks built from the 2022 laser scan in `L_Surroundings`. "Revit neighbour massing" is the block of neighbours that came with the Revit export.
- "Console variable" is a named engine setting that can be changed while the editor runs.
- "Path-traced" means made by Unreal's Path Tracer, the slow renderer that follows light physically. "Real-time" means made by the renderer the walk-through uses.
- "Frame time" is the time the computer needs to draw one picture, in milliseconds (ms).
- "Parcel" is one lot of land as the county's map draws it, with its 14-digit number (PIN).

## How to resume

1. Read the journal below from the bottom up. The last line that is not PENDING is the last step known to be finished. A PENDING line means the step was started and its result is unknown: look at what exists (files in `review\phase13\`, `E:\Wieland1529_site_data\proposed_hotel\`, assets under `/Game/Wieland1529/Site/ProposedHotel/`, the level `/Game/Wieland1529/Site/L_ProposedHotel`, and the editor's unsaved packages) before repeating anything.
2. Editor: top level `/Game/Wieland1529/L_Site_M4`. After a restart the editor opens `L_R15_Production` and may show a window "Restore Packages" that blocks every tool until it is closed without restoring (`tools\close_restore_window.ps1`); then open the top level with `review\phase11\scripts\open_m4.py`. Never save `/Game/Wieland/R15_Landscape/L_R15_Production`, never use "Save All", save named assets only, never edit an asset Datasmith created.
3. Calls go through `tools\ue_call.py` (`python -B tools\ue_call.py py <script file> [timeout seconds]`). A script returns the value of its last expression. Scripts of this phase are in `review\phase13\scripts\`; the status reading is `review\phase13\scripts\status.py`.
4. `r.RayTracing.Nanite.Mode` stays 0 at all times, path-traced pictures included, and is never set to 2. One picture at a time; a freshly opened level settles five minutes first.
5. Before any heavy step read free commit memory; under 30 GB, unload and wait (see Phase 11's J3 for the lowered line of 26 GB when the 30 GB line cannot be reached). The memory log of this phase is `review\phase13\memory_log_phase13.csv` (started by `tools\memory_log.ps1`).
6. The journal helper `review\phase13\scripts\journal.py` writes every time from the clock: `python -B review/phase13/scripts/journal.py outcome.txt [next.txt]`, run from the plan folder.
7. Commit by explicit path on branch `claude/1529-wieland-scene-plan-e84a03`. Do not push.

## Checks made before work (2026-11-13 12:30 Central)

| Check | Reading |
|---|---|
| `phase13_results.md` | did not exist: this is a fresh start, not a resume |
| Editor | process 42444, started 11:09:44, agent server answers, holds 19.8 GB of commit |
| Open world | `/Game/Wieland1529/L_Site_M4`, 12 levels, 3,059 objects |
| Unsaved packages | one, `L_Site_M4`, as Phase 11 left it (temporary camera placed and removed; no content change) |
| `r.RayTracing.Nanite.Mode` | 0 |
| `r.Material.UseShaderCompilationParameters` | 0 |
| Free commit memory | 26.3 of 79.1 GB (under the 30 GB line; the same state Phase 11's J3 describes); free physical 6.6 GB |
| Working copy | branch `claude/1529-wieland-scene-plan-e84a03`, last commit `cb4bf6af` (Phase 13 inserted) |
| Advisor tool | none in the first session; the resumed session (15:31) had it and used it for the closing review (see J9) |

## Journal

| No. | Time (Central) | Step | Outcome |
|---|---|---|---|
| J1 | 12:33 | Step 13.1, read-only and off line: the parcels of 1520 to 1528 N. Wells and of any other lot the hotel uses, from the county parcel file `E:\Wieland1529_site_data\county_parcels_2025.json` (Phase 2), with their outlines in the project's coordinates; whether the project's rear lot line faces a public alley and Wells Street lies behind it; and which objects of the present site model stand on those parcels (earlier detailed buildings, Phase 4 survey massing, Revit neighbour massing, trees, ground). In parallel, step 13.2: reading the article, the developer's and architect's pages, the city's permit records and planning documents, and saving reference pictures under `E:\Wieland1529_site_data\proposed_hotel\`. Nothing is changed in the Unreal project. | DONE 12:47. 13.1 and 13.2 done: proposed_hotel.md written. No alley exists in the block; the development land (PD 1335) is site north -149.55..0, east 0..204.5 and abuts the project lot's south line; the PD has three homes (press says two). Hide list for the proposed option: SB_782868, R15_PART_opaque_xm04_yp01_part01, R15_PART_glass_xm04_yp01_part01. Written heights from the PD elevations; plan dimensions scaled (2 ft). Four rows appended to asset_downloads.csv (53 MB of 500 MB). |
| J2 | 12:47 | 13.3 Materials for the hotel (new instances of the project's own parents, own generated maps), the off-line mesh generator, new level L_ProposedHotel inside L_Site_M4, and the tower's lowest storeys (floors 1-2), then a look at them before anything else is built | DONE 12:58. 13.3 done. Own images made (two bricks of 2,048 different bricks each, planted roof, metal panel) and imported; seven new material instances of the project's parents under /Game/Wieland1529/Site/ProposedHotel/Materials; generator tools/phase13_hotel_meshes.py and editor module tools/wieland_hotel.py; level /Game/Wieland1529/Site/L_ProposedHotel made inside L_Site_M4. Lowest storeys (group Base, 9 objects) built first and looked at from Wells Street (scratch/base_wells.jpg, base_close.jpg): walls, shopfronts, garage door, entrance and second-floor windows stand right; then the rest built: 56 objects in 7 groups, 61,168 triangles, no triangle lost. Hotel level, top level and materials saved by name. Top of the hotel read back at 152.33 ft above the level's zero = 151.33 ft above its first floor. |
| J3 | 12:58 | 13.4 Look at the whole hotel, garage and homes from several sides, also under grazing light; correct what is wrong; then the Variant Manager list "Neighbour development" with both options tested both ways, and the recorded hide list | DONE 13:04. 13.4 done. Whole development looked at from six sides (scratch/all_*.jpg): tower with its setbacks, top storey and plant room, planted roof over the garage, the three homes; nothing out of place, nothing corrected. List "Neighbour development" added to /Game/Wieland1529/Surroundings/LVS_W1529_Surroundings (118 recorded values: 56 hotel objects and 3 existing objects in each of two options). Tested existing -> proposed -> existing -> proposed, read back each time: 0/56 hotel and 3/3 existing visible, then 56/56 and 0/3, twice; pictures scratch/var1..var4. Left on "Duke of Wells (proposed)". Hide record review/phase13/hidden_for_proposed_hotel.csv. Levels L_ProposedHotel, L_Surroundings and L_Surroundings_R15 saved by name so that the default opens as proposed. Note: two of the three hidden objects are also driven by the list "Surroundings"; after changing that list, put the wanted option of "Neighbour development" on again. |
| J4 | 13:04 | 13.5 Measure height, storeys, setbacks and footprint against the recorded numbers; side-by-side sheets of the model against each published rendering under review/phase13 | DONE 15:32. 13.5 done (finished by the session resumed at 15:31 after the usage-limit stop). Measured in the editor with straight-line probes (review/phase13/measure_traces.json, script measure_traces.py): every roof and terrace height, every wall position and the home outlines agree with proposed_hotel.md to 0.1 ft or better; top of the mechanical penthouse 151.33 ft above the first floor (PD 151 ft 4 in); 12 storeys counted up the window lines (8 runs on the north wing below its 9th-floor terrace roof, 3 more on the tower, 1 at the 12th floor); windows 7.5 ft high. Ten side-by-side sheets, rendering left and model right, review/phase13/compare_r1..r8, r11, r12 .jpg and compare_all.jpg (script side_by_side.py), each labelled proposed / not a survey. Massing, setbacks, colour split and window rhythm match; differences listed under Findings. The sheets hold copies of the publishers' renderings, so they are kept on disk and not committed, like the renderings themselves. |
| J5 | 15:32 | 13.6 Views from the project that see the hotel: real-time pictures of S1-S9 and D1-D5, the rear of 1529 and its roof deck, and the side yard toward the hotel (there is no alley), each with the option "Duke of Wells (proposed)" and compared with the same view under "Existing buildings (as surveyed)", to list which views change for Phase 11 | DONE 15:42. 13.6 done. 16 views rendered twice with the real-time renderer at 1920 x 1080 (review/phase13/views/existing and proposed; scripts views_rt.py and views_diff.py), Phase 8 cameras and fixed exposure, r.RayTracing.Nanite.Mode read back 0 after each set. Changed pixels (over 40/255) existing -> proposed: S1 17.4 %, S2 25.1 %, S3 10.7 %, S4 13.4 %, S5 2.5 %, S6 10.1 %, S8 16.6 %, S9 0.0 %, D1 6.7 %, D2 0.01 %, D3 0.0 %, D4 0.0 %, D5 11.4 %, roof deck RD 33.3 %, rear patio RP 9.2 %, south side yard SY 27.6 %. Phase 11 re-renders S1, S2, S3, S4, S5, S6, D1, D5; S9, D2, D3, D4 stay. Sheets review/phase13/views/sheet_<view>.jpg, table views/changes.csv. Left on "Duke of Wells (proposed)", 56/56 shown, 0/3 existing shown. |
| J6 | 15:42 | 13.7 Shadow of the hotel on 1529: plan view and roof deck view at the review condition (15 August, 15:30) and in the morning (15 August, 09:00), each with both options; sun turned with the project's own sun tools and put back to the review condition and read back | DONE 15:46. 13.7 done (numbers superseded by J9: the corrected test leaves out 181 points that land inside 1529; see Findings). Line tests over the project lot (820 points every 2.5 ft on the first surface met from above; review/phase13/shadow/shadow_traces.json, script shadow_traces.py), 15 August 2026, 07:00-19:00 CDT: the hotel adds shade to 0.0 % of the lot at 07:00-08:00, 0.2 % at 09:00, 1.3 % at 10:00, 4.3 % at 11:00, 7.9 % at 12:00, 8.2 % at 13:00, 0.5 % at 14:00, 0.1 % at 15:00-16:00 (review condition 15:30: 0.1 %), 0 % after 17:00. The roof deck level (517 points at 45 ft and above) gets new shade only at 12:00 (3.1 %) and 13:00 (0.4 %). The hotel stands south and south-east of 1529 (not east), so its shadow reaches the lot only around midday, on the south side yard and the lower south face. Pictures: plan view from 80 m at 09:00, 12:30 and 15:30, both options, review/phase13/shadow/shadow_sheet.jpg (script shadow_pics.py, shadow_sheet.py). Sun put back to 15 August 15:30 and read back (bearing 241.72, height 46.40); option left on proposed; Nanite mode read back 0. |
| J7 | 15:46 | 13.8 Cost of the new level: the exterior part of Phase 11's camera path played once with the hotel level unloaded-equivalent (option existing, hotel objects hidden) and once with the proposed option, frame time and video memory recorded each time with the project's own profiling tool | DONE 15:51. 13.8 done. Exterior path (60 s) and holds S1, S2, S6 recorded under Phase 9 tier conditions (tools/phase9_profile_m7.py, first walk skipped as in state C2; script review/phase13/scripts/profile_exterior.py; records and frame tables profiles/2026-11-13_P13/existing and /proposed). Existing -> proposed: exterior path frame mean 11.10 -> 11.02 ms, 95th percentile 12.64 -> 12.38 ms, worst 22.40 -> 19.60 ms, graphics card 9.98 -> 9.90 ms, frames over 33.3 ms 0 -> 0, over 16.67 ms 4 -> 2 of about 5,400, video memory peak 6,351 -> 6,320 MB, editor in front 100 % both times. The difference is inside the run-to-run spread; the hotel level costs nothing measurable. Settings put back and read back by the tool (settings_put_back true); option left on proposed. |
| J8 | 15:51 | 13.9 Close the phase: findings, list of views for Phase 11, before-and-after numbers and owner items into this file; errors into PROJECT_MEMORY.md (new Phase 13 section); Status line DONE; commit by explicit path; no push | DONE 15:54. 13.9 done. Findings, the list of views for Phase 11 (re-render S1-S6, D1, D5; keep S9, D2-D4), before-and-after numbers, how to switch, owner items and the file list written below; Phase 13 section added to PROJECT_MEMORY.md; committed by explicit path, not pushed. |
| J9 | 15:58 | Closing review (advisor, about 15:57) and corrections, recorded after the step: shadow-test points chosen with the same filter as the shadow test and indoor points left out; Revit neighbour massing tested on the land; grazing-light check of the hotel materials; cost wording; memory logger stopped | DONE 16:03. Shadow numbers corrected (peak new shade 4.9 % of outdoor points at 13:00; 0.3 % at 09:00; 0.2 % at 15:30). The massing has a block on the land, switched off for drawing. Grazing-light check made; sun and exposure put back and read back (bearing 241.72, height 46.40, EV 14.644). Nothing saved in the project. |

## Findings

Everything below is **proposed, modelled from published renderings and records, not a survey**. Every dimension, its source or its estimate and its uncertainty is in `proposed_hotel.md`; the short form is here.

### Where the hotel stands

- **There is no alley.** The kickoff's premise (the hotel across a public alley behind 1529) does not hold: the county parcels and the planned development's boundary map show block 17-04-203 without an alley; the Wieland lots back straight onto the Wells lots.
- The development land of City of Chicago Planned Development No. 1335 (as amended 9 Sept 2020) is 149.55 ft north-south by 204.50 ft east-west, from Wieland to Wells, and its **north line is 1529's south lot line**. So the hotel is the project's **south and south-east neighbour**, not its east (rear) neighbour.
- It uses more parcels than "1520-1528 N. Wells": 1520, 1522, 1524, 1528 and 1530 N. Wells and the rear parts of 1513-1523 N. Wieland (sub-area A, the hotel and garage); the homes stand on the Wieland fronts (sub-area B), one of them on 1525 N. Wieland, right next to 1529. 1532 N. Wells stays (sub-area C).
- In the project's coordinates (feet north and east of 1529's south-west lot corner): tower floors 3-11 north -137.15 to -36.75, east 77.15 to 178.05 (about 37 ft south of 1529's south lot line); garage west wall at east 28.75; Home 3 north -22.3 to -1.7, east 2.6 to 59.8 (its north wall about 1.7 ft from 1529's lot line).
- Existing objects on the land, hidden by the proposed option: `SB_782868` (the block of the 3-storey building 1520 N. Wells, `L_Surroundings`) and the two parts of the detailed house 1525 N. Wieland (`R15_PART_opaque_xm04_yp01_part01`, `R15_PART_glass_xm04_yp01_part01`, `L_Surroundings_R15`). The Revit neighbour massing (`Generic_Models_SURROUNDING_BUILDINGS_SURROUNDING_BUILDINGS`, level `L_W1529_Shell`) is one combined mesh, and it **does have geometry on the land**: 133 of its 221 triangles, a block at north -26.9 to -1.9, east 10.2 to 84.2, 0 to 30 ft high, which is the house 1525 N. Wieland where Home 3 now stands (`review\phase13\scripts\dump_massing.py`). Its mesh component is switched off for drawing (`visible` false, read back) in the saved scene, as is the Revit grade, so it is never drawn in the editor, the renders or the walk-through and does not visibly overlap the hotel; the variant list cannot hide a part of one mesh and does not need to. Its collision is still there (see the shadow test). Record: `review\phase13\hidden_for_proposed_hotel.csv`.
- Three single-family homes, not two: the PD (the legal record) has three; the press writes "a pair", counting only those that screen the garage.
- State of the real project: the PD was extended to 9 Sept 2027 (letter of 8 Oct 2026); the 3-storey building at 1520 N. Wells got a wrecking permit on 1 May 2026; a foreclosure suit over the land was reported in April 2025. The hotel was not under construction in October 2026.

### What was built (in `/Game/Wieland1529/Site/L_ProposedHotel`, streamed into `L_Site_M4`)

56 objects in 7 groups, 61,168 triangles: the 12-storey tower with its terraced setbacks (3rd-floor terraces north and south, 7th-floor terrace on the south wing, 9th on the north wing, 11th on the dark grey projecting part, 12th-floor terrace with glass guard), the 12th floor in dark grey brick, the mechanical penthouse in metal panel, the 3-storey garage with planted roof, the three homes. Red and dark grey brick, recessed windows of 7.5 by 7.5 ft with frames and glass, stone bands, copings and parapets, shopfront, entrance canopy and garage door on Wells. Meshes were generated by the project's own tool (`tools\phase13_hotel_meshes.py`, editor module `tools\wieland_hotel.py`); seven new material instances of the project's own parents under `/Game/Wieland1529/Site/ProposedHotel/Materials`, with colour maps made for this phase (two bricks of 2,048 different bricks each, planted roof, metal panel). No downloaded picture is used as a texture.

### Measured on the model (J4, line probes in the editor) against the recorded numbers

| Item | Recorded (`proposed_hotel.md`) | Measured on the model |
|---|---|---|
| Top of the mechanical penthouse above the first floor | 151 ft 4 in (PD, written) | 151.33 ft |
| 12th-floor roof / 12th-floor terrace | 142.0 / 127.67 ft (PD, written; terrace finish +0.5 ft) | 142.0 / 128.17 ft |
| 11th, 9th, 7th-floor terraces | 114.67, 93.67, 72.67 ft (PD, written) | 114.67, 93.67, 72.67 ft |
| 3rd-floor terraces, garage roof | 32.33 ft (PD written; garage roof estimated, 3 ft) | 32.33 ft |
| 2nd-floor terrace on Wells | 17.0 ft (PD, written) | 17.0 ft |
| Storeys | 12 | 12 window rows counted |
| Tower walls (a = ft east, b = ft south of sub-area A's north-west corner) | west 48.4, east 149.3, north 12.0, south 112.4 (scaled, 2 ft) | 48.4, 149.3, 12.0, 112.4 |
| Wings on Wells | north wing b 0-41.0, south wing b 84.5-124.8, front at a 175.75 (scaled, 2 ft) | 0-41.0, 84.5-124.8, 175.7 |
| Dark grey projecting part | east face at a 158.3 (scaled, 1.5 ft) | 158.3 |
| 12th floor | a 64-132.5, b 24.6-88.5 / 103.8 (scaled, 2-4 ft) | 64.0-132.5, 24.6-88.5 / 103.8 |
| Penthouse | a 66-114.2, b 42.6-82.5 (scaled, 2 ft) | the same |
| Homes 1, 2, 3 | outlines scaled (2 ft), heights estimated (4 ft) | outlines as recorded; roofs 36.5, 36.5, 34.25 ft above level zero, plus parapets |
| Windows | about 8 ft (press); 7.5 by 7.5 ft read off renderings (1 ft) | 7.5 ft high on every row |

The model reproduces the recorded numbers to 0.1 ft. Every height is written in the PD; every plan dimension is scaled from small drawings (uncertainty 2 ft, homes 4 ft).

### Model against the published renderings (J4)

Ten side-by-side sheets: `review\phase13\compare_r1.jpg` to `compare_r8.jpg`, `compare_r11.jpg` (Urbanize), `compare_r12.jpg` (architect's page) and `compare_all.jpg`. **These sheets hold copies of the publishers' renderings and are kept on disk only, not committed**, like the renderings themselves. What matches: the massing and every setback, the split of red and dark grey brick (dark middle bay on the west face, dark projecting part on Wells, dark 12th floor), the window rhythm, the planted garage roof, the homes in front of the garage. Differences: the renderings show steel pergolas and furniture on the 12th-floor terrace, furniture and planters on the other terraces, gas lanterns, blade signs, the street clock and street trees, none of which is modelled; the 12th-floor cornice reads lighter and deeper on the model; the renderings' homes have more façade detail (bays, entrances); on two sheets (r2, r4) the model's viewpoint is higher and farther than the rendering's.

### Views that change: the list for Phase 11 (J5)

Each view was rendered with both options with the real-time renderer at the same camera and exposure; the share of the picture that changes is the share of pixels differing by more than 40 of 255 (an unchanged view reads 0.0 %). Sheets `review\phase13\views\sheet_<view>.jpg`, table `review\phase13\views\changes.csv`.

| View | Changed | Changes? | Phase 11 action |
|---|---|---|---|
| S1 | 17.4 % | yes | **re-render** |
| S2 | 25.1 % | yes | **re-render** |
| S3 | 10.7 % | yes | **re-render** |
| S4 | 13.4 % | yes | **re-render** |
| S5 | 2.5 % | yes (tower above the street's trees) | **re-render** |
| S6 | 10.1 % | yes | **re-render** |
| S7 | - | cannot exist (no alley) | none |
| S8 (plan) | 16.6 % | yes | not a Phase 11 still; re-render if the plan picture is delivered |
| S9 | 0.0 % | no | keep |
| D1 (roof deck) | 6.7 % | yes | **re-render** |
| D2 | 0.01 % | no | keep |
| D3 | 0.0 % | no | keep |
| D4 | 0.0 % | no | keep |
| D5 (rear patio) | 11.4 % | yes | **re-render** |
| Roof deck looking south (RD, Phase 14's camera) | 33.3 % | yes | new view; picture `views\proposed\RD_realtime.0000.png` |
| Rear patio looking south (RP, Phase 14's camera) | 9.2 % | yes | new view |
| South side yard from Wieland Street (SY) | 27.6 % | yes | new view |

**Phase 11 re-renders S1, S2, S3, S4, S5, S6, D1 and D5 (eight stills); S9, D2, D3 and D4 stay.** The animation (Phase 11 J5) is to be made with the option "Duke of Wells (proposed)" on: the hotel is visible from the roof deck and along Wieland. Path-traced stills trace each mesh's simplified fallback copy (`r.RayTracing.Nanite.Mode` 0).

### Shadow on 1529 (J6, corrected in J9)

The hotel stands south and south-east of 1529, not east. Line tests toward the sun on 15 August 2026 from a grid of points every 2.5 ft over 1529's lot, each on the first drawn surface met from above (`review\phase13\shadow\shadow_traces.json`, script `shadow_traces.py`). 181 of the 820 grid points land on surfaces inside 1529 (ceilings, furniture, interior partitions, a lower floor: the 1529 model has roof parts that are not drawn and have no collision, which also shows in the plan pictures, where 1529 looks open from above); they are left out, so the shares are of the **639 outdoor points** (roofs, roof decks, terraces, stairs, the yard). "New shade" counts points in sun with the existing buildings and in shade with the hotel; "hotel on the line" counts points whose line to the sun passes through the hotel, whatever else also shades them.

| Clock (CDT) | Sun bearing / height (degrees) | New shade from the hotel (outdoor points) | Hotel on the line | New shade on the roof-deck level (439 points, 45 ft and up) |
|---|---|---|---|---|
| 07:00-08:00 | 80-90 / 10-21 | 0 % | 0 % | 0 % |
| 09:00 (morning) | 101 / 32 | 0.3 % | 6.6 % | 0 % |
| 10:00 | 113 / 43 | 0.6 % | 11.6 % | 0 % |
| 11:00 | 130 / 53 | 1.1 % | 15.0 % | 0 % |
| 12:00 | 153 / 60 | 4.7 % | 15.0 % | 3.6 % |
| 13:00 | 183 / 62 | 4.9 % | 10.3 % | 0.5 % |
| 14:00 | 212 / 59 | 0.6 % | 4.7 % | 0 % |
| 15:30 (review condition) | 242 / 46 | 0.2 % | 5.3 % | 0 % |
| 17:00 | 261 / 31 | 0 % | 5.2 % | 0 % |
| 18:00-19:00 | 272-281 / 19-8 | 0 % | 0 % | 0 % |

On a mid-August day the hotel adds noticeable shade to 1529 only from about 11:00 to 14:00 (at most about 5 % of the outdoor surfaces), mainly on the south side yard and the lower south face; the roof deck gets new shade only around noon, at its south edge (3.6 %). In the morning (09:00) and at the review condition (15:30) the added shade is negligible (0.3 % and 0.2 %): the hotel is on the line to the sun for 5-7 % of the points then, but those points are already shaded by something nearer (1529's own parapets, stairs and pergola, the existing neighbours, or Home 3 in place of the existing house 1525). Picture: `review\phase13\shadow\shadow_sheet.jpg` (plan view from 80 m at 09:00, 12:30 and 15:30, both options). In winter, with the sun low in the south, the shadow is far longer and will cover much more of 1529 around midday; Phase 14's 21 December roof-deck video (made with the hotel on) shows it; it was not measured here.

### Materials under grazing light (J9)

The rule for every material (seamless, non-repeating, with a colour map, checked under grazing light) was checked for the hotel's new materials in close views of the red brick and the dark grey brick (Wells face and west face), the planted roof and the metal panel, each with the sun 8 degrees above the horizon raking along the face (exposure lowered to EV 11.5 for those pictures only, put back to 14.644 and read back) and with the review sun: `review\phase13\grazing\grazing_sheet.jpg`, figures `grazing_detail.json`, script `grazing.py`. Result: no seam and no repeated block is visible on any of them; the bricks vary one by one; the metal panel joints read under grazing light. **The brick's mortar joints read mainly by colour; their relief is shallow under grazing light.** At the distances the hotel is seen from 1529 (37 ft and more) this does not show; a deeper joint would need a stronger normal map. Listed for the owner. The project's material table was not changed in this phase.

### Cost of the new level (J7): before and after

Exterior path of the M4/M6/M7 profiles (60 s) and holds S1, S2, S6, Phase 9 tier conditions, editor in front 100 % of the time; records `profiles\2026-11-13_P13\`.

| Recording | Option | Frame mean (ms) | 95th percentile | Worst | Over 33.3 ms | Over 16.67 ms | Graphics card mean | Video memory peak (MB) |
|---|---|---|---|---|---|---|---|---|
| Exterior path | Existing buildings (before) | 11.10 | 12.64 | 22.40 | 0 of 5,407 | 4 | 9.98 | 6,351 |
| Exterior path | Duke of Wells (after) | 11.02 | 12.38 | 19.60 | 0 of 5,444 | 2 | 9.90 | 6,320 |
| Hold S1 | before / after | 11.09 / 11.10 | 12.39 / 12.47 | 15.76 / 14.88 | 0 / 0 | 0 / 0 | 9.96 / 9.97 | 6,319 / 6,320 |
| Hold S2 | before / after | 11.20 / 10.75 | 12.59 / 12.05 | 16.76 / 19.79 | 0 / 0 | 1 / 1 | 10.08 / 9.65 | 6,319 / 6,320 |
| Hold S6 | before / after | 10.42 / 10.64 | 11.79 / 11.80 | 14.41 / 14.25 | 0 / 0 | 0 / 0 | 9.31 / 9.54 | 6,319 / 6,320 |

The cost of **drawing** the hotel is inside the spread between two runs. This method does not separate the **memory** the loaded hotel level holds: both runs had the level loaded (the existing option only hides its objects). As a stand-in for that memory, the hotel's assets take 72 MB on disk (`Content\Wieland1529\Site\ProposedHotel\`: textures 70 MB, meshes 1.8 MB, materials 84 KB; the level file 0.14 MB). Video memory is compared within this session only; between sessions it varied from 6.3 to 8.9 GB. Phase 9's final recording (M7, before the hotel existed) read 11.50 ms mean and 12.82 ms 95th percentile on the same path.

### What was saved or changed in the project (whole phase)

- Saved by name in J2-J3: the new level `/Game/Wieland1529/Site/L_ProposedHotel`; meshes, textures and seven material instances under `/Game/Wieland1529/Site/ProposedHotel/`; the top level `/Game/Wieland1529/L_Site_M4` (now streams the hotel level); the variant asset `/Game/Wieland1529/Surroundings/LVS_W1529_Surroundings` (new list "Neighbour development"); `L_Surroundings` and `L_Surroundings_R15` (saved so that the three existing objects open hidden, matching the default option). No Datasmith asset was edited, nothing was deleted, `L_R15_Production` was not saved, "Save All" was not used.
- Nothing was saved in J4-J8. At the end the editor holds five levels marked unsaved (`L_Site_M4`, `L_ProposedHotel`, `L_Light_SummerAfternoon`, `L_Surroundings_R15`, `L_Surroundings`) only from Phase 14's sun moves, the option switches and the temporary camera; their content equals what is saved (sun at 15 August 15:30, read back bearing 241.72, height 46.40; option "Duke of Wells (proposed)" on, 56 of 56 hotel objects shown, 0 of 3 existing shown). They need not be saved.
- `r.RayTracing.Nanite.Mode` was 0 throughout and is read back 0; `r.RayTracing.Nanite.MaxAppendInstances` read back 10,000; the profiling tool put back every setting it changed and read them back equal.

### How to switch between the hotel and the existing buildings

In the editor: Window > Variant Manager, open `LVS_W1529_Surroundings` (the object `W1529_Surroundings` in the level), list **Neighbour development**, double-click **Duke of Wells (proposed)** or **Existing buildings (as surveyed)**. The first shows the 56 hotel objects and hides the three existing objects on its land; the second does the reverse. Nothing is deleted either way. Two of the three hidden objects also belong to the older list "Surroundings"; after choosing an option there, choose the wanted option of "Neighbour development" again. From a script: `wieland_hotel.switch(wieland_hotel.OPTION_PROPOSED)`.

## For the owner

1. The kickoff said the hotel is the rear neighbour across an alley. It is not: there is no alley, and the hotel's land adjoins 1529's south lot line (Home 3 stands 1.7 ft from it). Please confirm from your own knowledge of the site.
2. Every plan dimension of the hotel and the homes is scaled from small public drawings (2 ft; homes 4 ft); the homes' design is not final in the PD; the garage roof height is estimated (3 ft). Dimensioned permit drawings are not public; getting them needs an account or a records request, which is not approved here.
3. The press says two homes, the PD three; three are modelled.
4. Whether the hotel will be built as drawn is uncertain (PD extended to Sept 2027, foreclosure suit, an unpublished 2024 change "adding a few rooms"). 12 vs 13 storeys and 151 ft 4 in vs 152 ft differ between sources; the PD's 12 storeys and 151 ft 4 in are modelled.
5. The ten comparison sheets contain copies of copyrighted renderings and are not committed; decide whether they may go into any delivery.
6. The existing building 1520 N. Wells may already be demolished (wrecking permit 1 May 2026); the option "Existing buildings (as surveyed)" still shows it as in 2022.
7. Phase 11 must re-render S1-S6, D1 and D5, and render the animation with the hotel on.
8. The brick's mortar joints have shallow relief under grazing light (the colour maps pass); a stronger normal map would deepen them if the hotel is ever seen close up.
9. The 1529 model has roof parts that are not drawn and have no collision (plan views show 1529 open from above). This was so before this phase; it affects plan pictures (S8) and line tests, not the street and deck views.
10. The Revit neighbour massing has a 30 ft block where Home 3 stands; it is switched off for drawing and never shows, so nothing was changed.
11. `PROJECT_MEMORY.md` had been rewritten with Windows line endings and an uncommitted Phase 14 section by the Phase 14 session; its line endings were put back and the Phase 14 section committed together with this phase's.

## Files written by this phase

Plan folder `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\`:

- `phase13_results.md`, `proposed_hotel.md`, four rows in `asset_downloads.csv`
- `tools\phase13_hotel_meshes.py`, `tools\wieland_hotel.py`
- `review\phase13\scripts\`: journal.py, status.py, parcels_block.py, objects_on_site.py, r15_parts_by_north.py, dump_r15_parts.py, ground_heights.py, list_materials.py, make_textures.py, append_downloads.py, crop.py, wh.py, measure_traces.py, side_by_side.py, views_rt.py, views_diff.py, shadow_traces.py, shadow_pics.py, shadow_sheet.py, profile_exterior.py
- `review\phase13\parcels_block.csv`, `parcels_block.png`, `objects_on_site.json`, `hidden_for_proposed_hotel.csv`, `measure_traces.json`, `memory_log_phase13.csv`
- `review\phase13\model_views\m1..m8_*.png`; `review\phase13\compare_r1..r8.jpg`, `compare_r11.jpg`, `compare_r12.jpg`, `compare_all.jpg` (on disk, not committed)
- `review\phase13\views\existing\` and `views\proposed\` (16 pictures each, about 95 MB, not committed for size; the sheets show them), `views\sheet_*.jpg`, `views\changes.csv`, `views\job.json`
- `review\phase13\grazing\grazing_sheet.jpg`, `grazing_detail.json` (the ten pictures not committed); scripts `grazing.py`, `grazing_sheet.py`, `dump_massing.py`
- `review\phase13\shadow\shadow_traces.json`, `shadow_sheet.jpg`, `shadow\existing\` and `shadow\proposed\` (3 pictures each, not committed)
- `profiles\2026-11-13_P13\existing\` and `profiles\2026-11-13_P13\proposed\`
- `review\phase13\scratch\` (working pictures and meshes)

Reference downloads: `E:\Wieland1529_site_data\proposed_hotel\` (53 MB of the 500 MB allowed; listed in `manifest.csv` there and in `asset_downloads.csv`).
