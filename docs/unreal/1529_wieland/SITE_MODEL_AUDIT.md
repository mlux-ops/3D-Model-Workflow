# Audit of the existing "1527 Wieland" Unreal site model

Audited 2026-11-10. Companion to [PLAN.md](PLAN.md). The audit was read-only: nothing in the Unreal project, its evidence folder or Revit was changed.

## Verdict

The existing model is a competent, well-documented real-time scene, and it does not yet meet the standard this project sets. Its surroundings were built from an old city footprint layer with estimated heights, its trees and street furniture are not based on evidence, its light is not physically set, and several materials fail this repository's rules on repeats and relief. The plan keeps its project shell, its measured performance method, its survey-based lot registration and its world-scaled material parents, and replaces or corrects the rest.

## What was audited, and what could not be

| Item | Status |
|---|---|
| The project on disk: `D:\Unreal_Engine_Projects\Wieland1527 5.9\` (a copy made 2026-11-10 18:59 of the Unreal Engine 5.8 project `D:\Unreal_Engine_Projects\Wieland1527\`) | Read: project file, settings, content listing, release notes, manifest |
| The earlier work's evidence: `E:\Games\Claude\1527 Wieland\fbx_walkthrough\qa\unreal_r15\` | Read: scene snapshot of 2026-10-04, review reports, incident log, three review images |
| The earlier work's source records: `E:\Games\Claude\1527 Wieland\fbx_walkthrough\` | Read: source register, registration files, project configuration |
| The live scene in the open editor (engine 5.9.0, level `L_R15_Production`) | **Partly audited, read-only.** The editor's agent server was not listening at first. After the owner restarted the editor at 19:23 it answered, and two read-only scripts were run through the installed `unreal-mcp` skill's flow. Read live: the object list, the sun and sky settings, every light, the exposure settings, and which parts lie on the lot. Not read live: the material on every part, and anything that needs a rendered image. The review images compared below are still the October ones. |
| The site of the new building as designated in the model | **No object in the level marks it.** The level's 64 objects are 58 grid-cell mesh parts, the sun and sky, fog, a post-process volume, a start point and two planting holders; none has "site", "subject", "lot", "proposed", "1527" or "1529" in its name apart from two tree labels. The lot's white slab is part of one merged cell (`R15_PART_opaque_xm04_yp01_part01`, which spans 96 m by 59 m). The designation exists only in the registration file: a lot 49.50 ft wide by 102.20 ft deep, with the building 13.208 m wide and floors at 2.032, 5.283, 8.534 and 11.786 m. If the owner means a different marker, the owner needs to point to it. |

Street imagery used for comparison was looked at live in a browser and is cited by link in [SOURCES.md](SOURCES.md). The comparisons below are by eye. They are leads for the site visit, not measurements.

## What the model is

- A context model made in Blender (revision "R14"), exported as FBX (30.8 MB) and imported to Unreal, then given a material, planting and performance pass (release "R15", 2026-10-04).
- 64 objects: 58 building parts (31 opaque parts drawn with Nanite, 27 glass parts), one sun-and-sky object, one fog volume, one post-process volume, one start point, and two holders for 11 trees and 2,557 ground plants.
- Extent about 204 m north to south and 184 m east to west, up to 21.8 m high.
- Units and axes: imported at 0.3048 m per unit; north is the negative X axis; the Wieland frontage is toward negative Y.
- Georeference: one anchor, longitude -87.6355370, latitude 41.9102814, with a stated error of 1.5 m. Model north is taken as true north.
- Settings: Lumen for global illumination and reflections, hardware ray tracing on, Virtual Shadow Maps, Substrate materials on, Nanite foliage on, DirectX 12.
- Measured in October on this workstation at three views: mean frame times of 12.7, 11.9 and 12.9 ms (79, 84 and 77 frames per second), 95th percentile 14.4 to 15.3 ms. The viewport size was not recorded; the release images are 2560 by 1360.
- Read live on 2026-11-10: the sun-and-sky object is at the engine's template values (latitude 45.0, longitude -73.0, time zone -5, north offset 35 degrees, 12 December 2019, 10:00, daylight saving on). The sun stands 17.9 degrees above the horizon at 50,000 lux. The sky light has intensity 1.0 and captures the scene in real time. Sky atmosphere and volumetric clouds are present. One unbounded post-process volume sets histogram automatic exposure with a +1.263 bias and leaves the brightness limits at project defaults.
- The project also holds an earlier Datasmith import of the owner's Revit model: `Content\Wieland\Revit1527\Datasmith\MAIN_r01` (1,498 files, 1.04 GB) and a pilot import (929 MB). No Datasmith source file was found beside it; the staged sources are FBX files, including `25-0061527NWieland-3DView-ExteriorRendering.fbx` (88.4 MB, 2026-10-02).

## Findings on accuracy

Severity: **High** changes what a reference view shows. **Medium** is visible on inspection. **Low** is housekeeping.

| No. | Finding | Evidence | Severity | Correction (plan phase) |
|---|---|---|---|---|
| A1 | The lot is shown in a condition that no longer exists: a white slab with a cedar fence, short iron fences and sunken steps. | August 2026 street view shows a cleared lot behind a green-screened chain-link fence. City permits show demolition complete in June 2026 and a new-construction permit issued 2026-09-03. | High | Replace with the building from Revit (Phase 3). |
| A2 | **The sun has never been set for this site.** It is at the engine's template values: latitude 45.0, longitude -73.0 (near Montreal), a 35 degree north offset, 12 December 2019 at 10:00. Every shadow and the whole light balance in the model are those of a winter morning somewhere else. Separately, model north is assumed to be true north, and the anchor error is 1.5 m. | Read live from the sun-and-sky object on 2026-11-10. Registration file: "geographicnorth=-X", "estimated_error_m 1.5". The street grid is reported to lie about one degree west of true north. One degree of error moves a 20 m shadow edge by about 0.35 m. | High | Set the sun from the site's latitude, longitude, true north, date and time (Phase 8); measure true north from the survey and parcel outlines and re-anchor on surveyed lot corners (Phase 2). |
| A3 | Neighbouring buildings' heights and roofs are estimates. | Source register: built on the city's 2015 footprint layer, with entries such as "7.0 m estimated height". No lidar was used. The county's 2022 footprints carry lidar heights, and the 2022 lidar has 9 cm vertical error. | High | Rebuild massing from lidar and the 2022 footprints (Phase 4). |
| A4 | The frame house south of the site (1525) does not match the real house. | Model: grey siding, three upper windows, one lower window and two doors, no attic window. August 2026 view: cream siding, a gable with an attic window and brackets, dark-trimmed windows, an entry stair on the north side. The earlier review itself notes "weaker retained provenance" for this house. | High | Re-model from site photographs (Phase 4). |
| A5 | The house's siding is built as separate slats with gaps; the sky shows through the gable. Its steps carry a pebble texture. | Review image `final_r15_visual_01\W1525_front.jpg`. | High | Solid wall with lap-siding relief; correct step material (Phases 4 and 5). |
| A6 | The brick apartment building north of the site (1533) differs in detail. | Model: six arches, two-pane sliding windows, low shrubs. August 2026 view suggests seven openings including the entry, three-part windows, and a tall evergreen screen behind the iron fence. Counts need confirming on site. | Medium | Correct from site photographs (Phase 4). |
| A7 | The eleven trees are not based on evidence. Species are whatever the tree library offered: three English oaks, three ginkgos, three Norway maples, two silver birches, all at their library size. Two maples stand in the parkway in front of the site. | Snapshot tree list. August 2026 view shows no tree in the parkway in front of the site, one parkway tree in front of 1533, a large mature tree south of 1525 beside a street light, and a large tree at the rear of the cleared lot. No species or trunk record exists publicly. | High | Survey on site; place and size each tree from measurements and lidar (Phases 2 and 7). |
| A8 | Street furniture is missing. | August 2026 views show a fire hydrant on the west sidewalk opposite the site, galvanized street-light poles with curved arms on the east side north and south of the site, a timber utility pole with three transformers and overhead lines on the west side, and parking signs. The model shows two overhead wires and refuse carts only. | High | Survey and place (Phases 2 and 4). |
| A9 | The parkway and paving in front of the site are generic. | Model: concrete with a small bright lawn rectangle. August 2026 view: a continuous unpaved, weedy strip between kerb and walk, patched asphalt, driveway aprons opposite. | Medium | Rebuild the ground from lidar, aerial photography and site measurements (Phase 4). |
| A10 | The world ends in view. A flat blue plane shows at the horizon, background buildings are blank boxes, and there is no skyline. | Review images `front_context.jpg` and `W1525_front.jpg`. The real views show towers to the south and east. | High | Zoned surroundings and a distant-city stand-in (Phase 4). |
| A11 | Buildings opposite the site may be out of date. | The 2015 footprint layer predates 1526 N. Wieland (new building permitted 2021) and 1532 (2016). Reflections in the model's glass show the classical houses opposite, so some of the west side was modelled from photographs. | Medium | Check each west-side building against 2022 lidar and site photographs (Phase 4). |
| A12 | The Revit import inside the project has no recorded source file, date or exporter version, and the staged building source is an FBX. | Content listing; no Datasmith file found. | Medium | Fresh, recorded export and import (Phase 3). |
| A13 | The project carries 10 GB of unrelated content: 3.0 GB from the 651 Belmont project and 7.0 GB of a beech tree pack. | Content listing. | Low | Remove from the working copy with the owner's approval (Phase 1). |

## Findings on materials and light

| No. | Finding | Evidence | Severity | Correction (plan phase) |
|---|---|---|---|---|
| ML1 | Exposure is automatic, with a +1.26 stop bias and an open range. Asphalt and concrete wash out, and the same brick reads brown in one view and salmon in another. The sun is a round 50,000 lux and the sky light a default 1.0; neither is derived from a date, time or measurement. | Read live on 2026-11-10; diagnostic file `native\glass_diagnostic.json`; review images. | High | Fixed exposure from camera settings; sun and sky in physical units (Phase 8). |
| ML2 | The blank brick side wall of 1533 shows repeating bands at street distance. | `final_release_clean_01\front_context.jpg`. This fails the repository rule against recognizable repeats at the intended viewing distance. | High | Larger varied brick field or per-brick variation, tested at the full wall size (Phase 5). |
| ML3 | Stone bands and trim are flat and featureless: no joints, no staining. The earlier release notes call the stone "appearance-matched", with no known specification. | `W1533_glass_pilot.jpg`; release notes. | Medium | Jointed, weathered stone from site photographs (Phase 5). |
| ML4 | Glass reflections are coarse and blocky, rooms behind the glass are empty, and reflected windows read as bright flat rectangles. | `W1533_glass_pilot.jpg`. | High | Window assemblies with depth, double reflections and rooms or blinds behind; ray-traced reflections checked against a path-traced frame (Phases 5 and 8). |
| ML5 | Nothing is weathered: no dirt at wall bases, no streaks under sills, no stains or cracks in paving, no patches in asphalt. | All three review images. | High | Weathering layers per surface from site photographs (Phase 5). |
| ML6 | The cedar fence is saturated orange with a repeating plank pattern, and the fence itself is not evidenced on site today. | `front_context.jpg`. | Medium | Remove or replace per site photographs (Phase 4). |
| ML7 | Tree foliage is sparse with oversized leaves; the lawn patch reads as artificial turf. | `front_context.jpg`, `W1525_front.jpg`. | Medium | Species-true trees and planting (Phase 7). |
| ML8 | No texel density is stated, and relief has not been judged under grazing light as the repository rule requires. | No record in the review reports. | Medium | State density per material class; grazing-light test (Phase 5). |
| ML9 | Texture licences are incompletely recorded. Poly Haven and ShareTextures sets are noted as CC0. The Megascans brick, the Fab items and the tree library have no licence record, and the grass source is recorded two different ways. | Source report and content listing. | Medium | One licence line per asset before it stays in the project (Phase 5). |

## Findings on records

| No. | Finding | Action |
|---|---|---|
| R1 | The earlier work fetched Google Street View images through Google's programming interface for 1500 to 1516 N. Wieland, and the log of those requests stores the access key in plain text: `E:\Games\Claude\1527 Wieland\fbx_walkthrough\05_context\candidates\buildings_detail_A_r01\evidence\reference_fetches.jsonl`. The key was not opened or copied during this audit. Google's terms bar storing Street View images and building content from them. | Owner: restrict or replace that key. The new plan does not fetch Street View images. |
| R2 | One reference photograph of 1533 comes from the building owner's web page with an unknown capture date. | Replace with the owner's own photographs. |
| R3 | The frame performance figures were taken at an unrecorded pixel size. | The plan's profile records resolution with every capture. |
| R4 | The level's building parts are merged grid cells, each mixing several buildings and materials (one cell holds the 1525 house, its roof and paving together). A single building cannot be selected, hidden, replaced or measured by itself. | Phase 4 rebuilds the surroundings as one object per building and per ground element. |

## Worth keeping

- The split of the architecture into Nanite parts with separate glass, which removed the earlier section-count stall.
- The world-scaled material parents (`M_R15_World_Metric`, `M_R15_UV_Metric`), which make a stated texel density easy to enforce.
- The timed performance captures (eight seconds of warm-up, ten seconds of capture, three views), which become the first entries of the plan's fixed-path profile.
- The lot registration against the survey and site plan, including its honest note of the 0.68 ft disagreement between measured and record frontage.
- The incident log and its operating rules: one writer to the Unreal project at a time, never "save all", treat a timed-out command as an unknown outcome.

## Live audit completed: the material on every part

Read on 2026-11-10 from the open level `/Game/Wieland/R15_Landscape/L_R15_Production` in engine 5.9.0, through the editor's agent server, as step 1.3 of the plan. The reading was read-only: nothing in the project was changed or saved. It closes the gap recorded above under "What was audited". The raw record, which also holds every slot's name and each part's bounding box, is [site_model_audit_materials.json](site_model_audit_materials.json).

Two terms. A **slot** is one material assignment on a part; a part has one slot for each material it carries. An **instance** is a material that takes its logic from a parent material and changes only values and textures; a **base material** stands alone.

### Totals

| Measure | Value |
|---|---|
| Parts read | 58: 31 opaque parts drawn with Nanite, 27 glass parts |
| Material slots | 645, none empty |
| Different materials on the parts | 123 (a further 14 are used only by the trees and ground plants) |
| Instances | 25 materials on 472 slots (73 percent of slots) |
| Base materials | 98 materials on 173 slots (27 percent of slots), all in `/Game/Wieland/R14` |
| Opaque slots | 529 |
| Glass slots | 116, on 5 glass materials |
| Most materials on one part | 22, on each of two parts: `R15_PART_opaque_xm04_yp01_part01` (the merged cell that holds the lot; 32 slots) and `R15_PART_opaque_xm03_yp00_part01` (29 slots) |
| Materials from the 651 Belmont or beech-tree content | None |
| Engine placeholder materials (the grey grid) | None |

### What this adds to the findings

| No. | Finding | Evidence | Severity | Correction (plan phase) |
|---|---|---|---|---|
| ML10 | 98 of the 123 materials on the parts are stand-alone base materials left from the R14 import. They do not use the world-scaled parents, so no texel density can be stated or enforced for them. | Table below: every material in `/Game/Wieland/R14` has no parent. They carry 173 of 645 slots. | Medium | Replaced when the surroundings are rebuilt one object per building (Phase 4) and re-materialled (Phase 5). |
| ML11 | All glass in the level comes from one parent, `M_MS_Glass`, through 5 instances. | Table below. | Low | The window assemblies in Phase 5 replace it. |
| R5 | The cell that holds the lot, `R15_PART_opaque_xm04_yp01_part01`, carries 22 different materials on 32 slots of one part, which confirms finding R4: a single building or surface cannot be re-materialled by itself. | Table of parts below. | Medium | Phase 4. |
| A14 | No part of the level uses a material from the 651 Belmont or beech-tree folders. This supports removing that content (finding A13); a full check of references from every Wieland asset is made in step 1.14 before anything is deleted. | Table below; no material path lies under `/Game/Belmont` or `/Game/EuropeanBeech`. | Low | Phase 1, step 1.14. |

### Materials on the parts

Sorted by the number of slots that use each one.

| Material | Kind | Parent | Blend | Parts | Slots | Folder |
|---|---|---|---|---|---|---|
| `MI_R15_concrete_floor_03_World` | instance | `M_R15_World_Metric` | opaque | 21 | 79 | `/Game/Wieland/R15_Materials/Production` |
| `MI_R15_limestone_continuous_World` | instance | `M_R15_World_Metric` | opaque | 27 | 68 | `/Game/Wieland/R15_Materials/Production` |
| `MI_R15_sexkaitb_UV` | instance | `M_R15_UV_Metric` | opaque | 28 | 66 | `/Game/Wieland/R15_Materials/Production` |
| `MI_R15_Glass_Blue` | instance | `M_MS_Glass` | translucent glass | 10 | 52 | `/Game/Wieland/R15_Materials` |
| `MI_R15_Glass_Clear` | instance | `M_MS_Glass` | translucent glass | 21 | 46 | `/Game/Wieland/R15_Materials` |
| `MI_R15_bitumen_UV` | instance | `M_R15_UV_Metric` | opaque | 23 | 39 | `/Game/Wieland/R15_Materials/Production` |
| `MI_R15_concrete_floor_03_UV` | instance | `M_R15_UV_Metric` | opaque | 25 | 36 | `/Game/Wieland/R15_Materials/Production` |
| `WLD_CTX_BLDG_metal` | base material | none | opaque | 13 | 13 | `/Game/Wieland/R14` |
| `MI_R15_wood_chips_World` | instance | `M_R15_World_Metric` | opaque | 12 | 12 | `/Game/Wieland/R15_Materials/Production` |
| `B_MAT_Joint_recess` | base material | none | opaque | 10 | 10 | `/Game/Wieland/R14` |
| `MI_R15_asphalt_03_World` | instance | `M_R15_World_Metric` | opaque | 7 | 9 | `/Game/Wieland/R15_Materials/Production` |
| `MI_R15_Glass_Smoke` | instance | `M_MS_Glass` | translucent glass | 5 | 8 | `/Game/Wieland/R15_Materials` |
| `MI_R15_AsphaltShingle_Courses` | instance | `M_R15_RoofCourse_Metric` | opaque | 5 | 6 | `/Game/Wieland/R15_Materials/Production` |
| `MI_R15_turf_World` | instance | `M_R15_World_Metric` | opaque | 6 | 6 | `/Game/Wieland/R15_Materials/Production` |
| `MI_R15_Glass_Dim` | instance | `M_MS_Glass` | translucent glass | 5 | 5 | `/Game/Wieland/R15_Materials` |
| `MI_R15_W1533_Glass` | instance | `MI_R15_Glass_Blue` | translucent glass | 1 | 5 | `/Game/Wieland/R15_Materials/Production` |
| `MI_R15_factory_brick_UV` | instance | `M_R15_UV_Metric` | opaque | 4 | 5 | `/Game/Wieland/R15_Materials/Production` |
| `MI_R15_galvanized_World` | instance | `M_R15_World_Metric` | opaque | 5 | 5 | `/Game/Wieland/R15_Materials/Production` |
| `MI_R15_yellow_brick_UV` | instance | `M_R15_UV_Metric` | opaque | 5 | 5 | `/Game/Wieland/R15_Materials/Production` |
| `WLD_CTX_BLDG_garage_001` | base material | none | opaque | 5 | 5 | `/Game/Wieland/R14` |
| `A4_wells_1535_305867_0_metal` | base material | none | opaque | 4 | 4 | `/Game/Wieland/R14` |
| `A_wells_1549_304564_0_metal` | base material | none | opaque | 4 | 4 | `/Game/Wieland/R14` |
| `A_wells_1561_815207_0_metal` | base material | none | opaque | 4 | 4 | `/Game/Wieland/R14` |
| `B_MAT_Wells_ornamental_iron` | base material | none | opaque | 4 | 4 | `/Game/Wieland/R14` |
| `MI_R15_brown_planks_09_UV` | instance | `M_R15_UV_Metric` | opaque | 4 | 4 | `/Game/Wieland/R15_Materials/Production` |
| `MI_R15_japanese_cedar_planks_World` | instance | `M_R15_World_Metric` | opaque | 4 | 4 | `/Game/Wieland/R15_Materials/Production` |
| `SS_R01_BlackPaintedIron_001` | base material | none | opaque | 4 | 4 | `/Game/Wieland/R14` |
| `SS_R01_FadedParkingPaint_001` | base material | none | opaque | 4 | 4 | `/Game/Wieland/R14` |
| `MI_R15_brick_wall_08_UV` | instance | `M_R15_UV_Metric` | opaque | 3 | 3 | `/Game/Wieland/R15_Materials/Production` |
| `MI_R15_brown_planks_09_World` | instance | `M_R15_World_Metric` | opaque | 3 | 3 | `/Game/Wieland/R15_Materials/Production` |
| `SS_R01_BlackRubber_002` | base material | none | opaque | 3 | 3 | `/Game/Wieland/R14` |
| `SS_R01_LuminaireLens_001` | base material | none | opaque | 3 | 3 | `/Game/Wieland/R14` |
| `A4_wells_1511_815257_0_metal` | base material | none | opaque | 2 | 2 | `/Game/Wieland/R14` |
| `A4_wells_1511_815257_0_wells_white_trim` | base material | none | opaque | 2 | 2 | `/Game/Wieland/R14` |
| `A4_wells_1533_306029_0_metal` | base material | none | opaque | 2 | 2 | `/Game/Wieland/R14` |
| `A4_wells_1535_305867_0_wells_white_trim` | base material | none | opaque | 2 | 2 | `/Game/Wieland/R14` |
| `A4_wells_1539_815224_0_metal` | base material | none | opaque | 2 | 2 | `/Game/Wieland/R14` |
| `A4_wells_1541_815223_0_metal` | base material | none | opaque | 2 | 2 | `/Game/Wieland/R14` |
| `A_E1510_metal` | base material | none | opaque | 2 | 2 | `/Game/Wieland/R14` |
| `A_E1553_1555_metal` | base material | none | opaque | 2 | 2 | `/Game/Wieland/R14` |
| `A_E1562_metal` | base material | none | opaque | 2 | 2 | `/Game/Wieland/R14` |
| `A_W1525_siding_pale` | base material | none | opaque | 2 | 2 | `/Game/Wieland/R14` |
| `A_W1550_MONTAUK_a1_pale_panel` | base material | none | opaque | 2 | 2 | `/Game/Wieland/R14` |
| `A_W1550_MONTAUK_door_paint` | base material | none | opaque | 2 | 2 | `/Game/Wieland/R14` |
| `A_W1550_MONTAUK_metal` | base material | none | opaque | 2 | 2 | `/Game/Wieland/R14` |
| `A_wells_1543_815222_0_metal` | base material | none | opaque | 2 | 2 | `/Game/Wieland/R14` |
| `A_wells_1547_815221_0_metal` | base material | none | opaque | 2 | 2 | `/Game/Wieland/R14` |
| `A_wells_1548_304917_0_metal` | base material | none | opaque | 2 | 2 | `/Game/Wieland/R14` |
| `A_wells_1548_304917_0_wells_paint_gray` | base material | none | opaque | 2 | 2 | `/Game/Wieland/R14` |
| `A_wells_1549_304564_0_wells_awning` | base material | none | opaque | 2 | 2 | `/Game/Wieland/R14` |
| `A_wells_1559_815208_0_metal` | base material | none | opaque | 2 | 2 | `/Game/Wieland/R14` |
| `A_wells_1561_815207_0_wells_awning` | base material | none | opaque | 2 | 2 | `/Game/Wieland/R14` |
| `A_wieland_1503_307872_0_a2_dark` | base material | none | opaque | 2 | 2 | `/Game/Wieland/R14` |
| `A_wieland_1503_307872_0_metal` | base material | none | opaque | 2 | 2 | `/Game/Wieland/R14` |
| `A_wieland_1504_307698_0_a2_gray_siding` | base material | none | opaque | 2 | 2 | `/Game/Wieland/R14` |
| `B_MAT_Wells_opal_globe` | base material | none | opaque | 2 | 2 | `/Game/Wieland/R14` |
| `B_MAT_Wells_ornamental_iron_001` | base material | none | opaque | 2 | 2 | `/Game/Wieland/R14` |
| `MI_R15_bitumen_World` | instance | `M_R15_World_Metric` | opaque | 2 | 2 | `/Game/Wieland/R15_Materials/Production` |
| `MI_R15_dirt_floor_World` | instance | `M_R15_World_Metric` | opaque | 2 | 2 | `/Game/Wieland/R15_Materials/Production` |
| `SS_R01_BlackRubber_001` | base material | none | opaque | 2 | 2 | `/Game/Wieland/R14` |
| `SS_R01_RecyclingPlastic_001` | base material | none | opaque | 2 | 2 | `/Game/Wieland/R14` |
| `SS_R01_RefusePlastic_001` | base material | none | opaque | 2 | 2 | `/Game/Wieland/R14` |
| `A4_wells_1504_308303_0_metal` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |
| `A4_wells_1504_308303_0_wells_white_trim` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |
| `A4_wells_1512_815266_0_metal` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |
| `A4_wells_1514_307361_0_metal` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |
| `A4_wells_1514_307361_0_wells_white_trim` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |
| `A4_wells_1533_306029_0_wells_white_trim` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |
| `A4_wells_1541_815223_0_wells_awning` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |
| `A_E1500_a2_dark` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |
| `A_E1500_a2_store` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |
| `A_E1500_metal` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |
| `A_E1510_a2_dark` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |
| `A_E1510_a2_store` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |
| `A_E1539_REAR2026_door_paint` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |
| `A_E1539_REAR2026_metal` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |
| `A_E1562_door_paint` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |
| `A_W1512_a2_dark` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |
| `A_W1512_a2_store` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |
| `A_W1512_door_paint` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |
| `A_W1512_metal` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |
| `A_W1525_door_paint` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |
| `A_W1525_metal` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |
| `A_W1525_paint_trim` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |
| `A_W1533_1537_metal` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |
| `A_W1533_1537_reveal_dark` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |
| `A_W1533_1537_stone_joint` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |
| `A_W1536_door_paint` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |
| `A_W1536_metal` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |
| `A_W1544_door_paint` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |
| `A_W1544_metal` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |
| `A_wells_1543_815222_0_wells_awning` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |
| `A_wells_1544_815228_0_metal` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |
| `A_wells_1544_815228_0_wells_siding` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |
| `A_wells_1544_815228_0_wells_siding_trim` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |
| `A_wells_1547_815221_0_wells_awning` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |
| `A_wells_1550_815219_0_metal` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |
| `A_wells_1550_815219_0_wells_paint_gray` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |
| `A_wells_1552_304450_0_metal` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |
| `A_wells_1552_304450_0_wells_awning` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |
| `A_wells_1559_815208_0_wells_awning_red` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |
| `A_wells_1559_815208_0_wells_store_base` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |
| `A_wieland_1501_877871_0_a2_dark` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |
| `A_wieland_1501_877871_0_door_paint` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |
| `A_wieland_1501_877871_0_metal` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |
| `A_wieland_1504_307698_0_a2_dark` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |
| `A_wieland_1504_307698_0_a2_pale` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |
| `A_wieland_1504_307698_0_door_paint` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |
| `A_wieland_1507_307490_0_a2_dark` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |
| `A_wieland_1507_307490_0_a2_pale` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |
| `A_wieland_1507_307490_0_door_paint` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |
| `A_wieland_1507_307490_0_metal` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |
| `A_wieland_1508_858637_0_a2_dark` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |
| `A_wieland_1508_858637_0_door_paint` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |
| `A_wieland_1508_858637_0_metal` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |
| `A_wieland_1511_307299_0_a2_dark` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |
| `A_wieland_1511_307299_0_door_paint` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |
| `A_wieland_1511_307299_0_metal` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |
| `B_MAT_Limestone_gravel` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |
| `MI_R15_W1533_Brick` | instance | `MI_R15_sexkaitb_UV` | opaque | 1 | 1 | `/Game/Wieland/R15_Materials/Production` |
| `MI_R15_W1533_Limestone` | instance | `MI_R15_limestone_continuous_World` | opaque | 1 | 1 | `/Game/Wieland/R15_Materials/Production` |
| `R14_W1525_PAINTED_METAL` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |
| `SS_R01_BlackPaintedIron_002` | base material | none | opaque | 1 | 1 | `/Game/Wieland/R14` |

### Each part and its materials

Sizes are the part's bounding box. A number after a material is how many of the part's slots use it.

| Part | Kind | Size north-south by east-west by height (m) | Slots | Materials |
|---|---|---|---|---|
| `R15_PART_glass_xm02_yp00_part01` | glass | 5.3 by 30.0 by 11.8 | 1 | `MI_R15_Glass_Clear` |
| `R15_PART_glass_xm02_yp01_part01` | glass | 6.8 by 3.9 by 11.0 | 2 | `MI_R15_Glass_Clear` x2 |
| `R15_PART_glass_xm02_yp02_part01` | glass | 20.6 by 0.5 by 11.7 | 4 | `MI_R15_Glass_Blue` x2, `MI_R15_Glass_Clear`, `MI_R15_Glass_Smoke` |
| `R15_PART_glass_xm03_yp00_part01` | glass | 38.4 by 29.6 by 11.3 | 4 | `MI_R15_Glass_Clear` x4 |
| `R15_PART_glass_xm03_yp01_part01` | glass | 28.6 by 23.8 by 11.1 | 4 | `MI_R15_Glass_Clear` x4 |
| `R15_PART_glass_xm03_yp02_part01` | glass | 23.2 by 32.1 by 8.7 | 7 | `MI_R15_Glass_Clear` x3, `MI_R15_Glass_Blue` x2, `MI_R15_Glass_Smoke` x2 |
| `R15_PART_glass_xm03_yp03_part01` | glass | 18.4 by 0.5 by 20.8 | 4 | `MI_R15_Glass_Blue` x3, `MI_R15_Glass_Smoke` |
| `R15_PART_glass_xm03_yp04_part01` | glass | 19.4 by 0.4 by 19.1 | 1 | `MI_R15_Glass_Clear` |
| `R15_PART_glass_xm04_yp00_part01` | glass | 38.8 by 28.9 by 14.2 | 1 | `MI_R15_Glass_Clear` |
| `R15_PART_glass_xm04_yp01_part01` | glass | 4.7 by 15.1 by 5.0 | 2 | `MI_R15_Glass_Blue` x2 |
| `R15_PART_glass_xm04_yp02_part01` | glass | 11.4 by 24.5 by 8.5 | 1 | `MI_R15_Glass_Clear` |
| `R15_PART_glass_xm04_yp03_part01` | glass | 10.8 by 1.9 by 5.6 | 6 | `MI_R15_Glass_Blue` x4, `MI_R15_Glass_Smoke` x2 |
| `R15_PART_glass_xm04_yp04_part01` | glass | 7.4 by 24.7 by 2.8 | 2 | `MI_R15_Glass_Clear` x2 |
| `R15_PART_glass_xm05_yp00_part01` | glass | 40.2 by 26.5 by 14.2 | 3 | `MI_R15_Glass_Clear` x2, `MI_R15_Glass_Dim` |
| `R15_PART_glass_xm05_yp01_part01` | glass | 30.1 by 17.4 by 13.6 | 6 | `MI_R15_W1533_Glass` x5, `MI_R15_Glass_Dim` |
| `R15_PART_glass_xm05_yp02_part01` | glass | 40.9 by 31.7 by 14.8 | 7 | `MI_R15_Glass_Blue` x5, `MI_R15_Glass_Clear` x2 |
| `R15_PART_glass_xm05_yp03_part01` | glass | 38.8 by 4.3 by 14.3 | 18 | `MI_R15_Glass_Blue` x16, `MI_R15_Glass_Smoke` x2 |
| `R15_PART_glass_xm05_yp04_part01` | glass | 39.2 by 25.2 by 15.5 | 7 | `MI_R15_Glass_Clear` x7 |
| `R15_PART_glass_xm06_yp00_part01` | glass | 38.0 by 22.0 by 20.1 | 4 | `MI_R15_Glass_Clear` x3, `MI_R15_Glass_Dim` |
| `R15_PART_glass_xm06_yp01_part01` | glass | 7.4 by 0.3 by 15.1 | 2 | `MI_R15_Glass_Clear`, `MI_R15_Glass_Dim` |
| `R15_PART_glass_xm06_yp02_part01` | glass | 39.3 by 31.6 by 14.8 | 9 | `MI_R15_Glass_Blue` x5, `MI_R15_Glass_Clear` x4 |
| `R15_PART_glass_xm06_yp03_part01` | glass | 40.7 by 3.1 by 18.8 | 10 | `MI_R15_Glass_Blue` x9, `MI_R15_Glass_Clear` |
| `R15_PART_glass_xm06_yp04_part01` | glass | 34.4 by 3.9 by 7.8 | 3 | `MI_R15_Glass_Clear` x3 |
| `R15_PART_glass_xm07_yp00_part01` | glass | 12.4 by 27.0 by 20.1 | 1 | `MI_R15_Glass_Clear` |
| `R15_PART_glass_xm07_yp02_part01` | glass | 12.2 by 0.2 by 3.3 | 2 | `MI_R15_Glass_Clear`, `MI_R15_Glass_Dim` |
| `R15_PART_glass_xm07_yp03_part01` | glass | 2.8 by 0.1 by 8.9 | 4 | `MI_R15_Glass_Blue` x4 |
| `R15_PART_glass_xm07_yp04_part01` | glass | 4.5 by 0.6 by 7.8 | 1 | `MI_R15_Glass_Clear` |
| `R15_PART_opaque_xm02_yp00_part01` | opaque, Nanite | 9.7 by 34.2 by 14.4 | 9 | `MI_R15_concrete_floor_03_World` x3, `MI_R15_bitumen_UV`, `MI_R15_brick_wall_08_UV`, `MI_R15_concrete_floor_03_UV`, `MI_R15_limestone_continuous_World`, `MI_R15_sexkaitb_UV`, `WLD_CTX_BLDG_metal` |
| `R15_PART_opaque_xm02_yp01_part01` | opaque, Nanite | 9.8 by 35.8 by 13.0 | 20 | `MI_R15_sexkaitb_UV` x4, `MI_R15_concrete_floor_03_World` x3, `MI_R15_limestone_continuous_World` x2, `A_wieland_1501_877871_0_a2_dark`, `A_wieland_1501_877871_0_door_paint`, `A_wieland_1501_877871_0_metal`, `A_wieland_1503_307872_0_a2_dark`, `A_wieland_1503_307872_0_metal`, `B_MAT_Joint_recess`, `MI_R15_asphalt_03_World`, `MI_R15_bitumen_UV`, `MI_R15_concrete_floor_03_UV`, `MI_R15_turf_World`, `MI_R15_wood_chips_World` |
| `R15_PART_opaque_xm02_yp02_part01` | opaque, Nanite | 30.8 by 31.6 by 12.7 | 17 | `MI_R15_sexkaitb_UV` x5, `MI_R15_bitumen_UV` x2, `MI_R15_concrete_floor_03_UV` x2, `MI_R15_limestone_continuous_World` x2, `A4_wells_1504_308303_0_metal`, `A4_wells_1504_308303_0_wells_white_trim`, `A_E1500_a2_dark`, `A_E1500_a2_store`, `A_E1500_metal`, `A_E1510_metal` |
| `R15_PART_opaque_xm03_yp00_part01` | opaque, Nanite | 41.2 by 34.4 by 15.6 | 29 | `MI_R15_concrete_floor_03_World` x3, `MI_R15_limestone_continuous_World` x3, `MI_R15_bitumen_UV` x2, `MI_R15_factory_brick_UV` x2, `MI_R15_sexkaitb_UV` x2, `A_W1512_a2_dark`, `A_W1512_a2_store`, `A_W1512_door_paint`, `A_W1512_metal`, `A_wieland_1504_307698_0_a2_dark`, `A_wieland_1504_307698_0_a2_gray_siding`, `A_wieland_1504_307698_0_a2_pale`, `A_wieland_1504_307698_0_door_paint`, `A_wieland_1508_858637_0_a2_dark`, `A_wieland_1508_858637_0_door_paint`, `A_wieland_1508_858637_0_metal`, `MI_R15_AsphaltShingle_Courses`, `MI_R15_brown_planks_09_World`, `MI_R15_concrete_floor_03_UV`, `MI_R15_galvanized_World`, `SS_R01_BlackRubber_002`, `SS_R01_LuminaireLens_001` |
| `R15_PART_opaque_xm03_yp00_part02` | opaque, Nanite | 43.1 by 29.9 by 9.6 | 5 | `MI_R15_bitumen_UV`, `MI_R15_concrete_floor_03_UV`, `MI_R15_limestone_continuous_World`, `MI_R15_sexkaitb_UV`, `WLD_CTX_BLDG_metal` |
| `R15_PART_opaque_xm03_yp01_part01` | opaque, Nanite | 41.7 by 59.2 by 13.0 | 30 | `MI_R15_concrete_floor_03_World` x4, `MI_R15_sexkaitb_UV` x4, `MI_R15_bitumen_UV` x3, `MI_R15_limestone_continuous_World` x3, `MI_R15_asphalt_03_World` x2, `A_wieland_1503_307872_0_a2_dark`, `A_wieland_1503_307872_0_metal`, `A_wieland_1507_307490_0_a2_dark`, `A_wieland_1507_307490_0_a2_pale`, `A_wieland_1507_307490_0_door_paint`, `A_wieland_1507_307490_0_metal`, `A_wieland_1511_307299_0_a2_dark`, `A_wieland_1511_307299_0_door_paint`, `A_wieland_1511_307299_0_metal`, `B_MAT_Joint_recess`, `MI_R15_concrete_floor_03_UV`, `MI_R15_turf_World`, `MI_R15_wood_chips_World`, `SS_R01_FadedParkingPaint_001` |
| `R15_PART_opaque_xm03_yp01_part02` | opaque, Nanite | 5.6 by 21.5 by 6.6 | 5 | `MI_R15_bitumen_UV`, `MI_R15_concrete_floor_03_UV`, `MI_R15_limestone_continuous_World`, `MI_R15_sexkaitb_UV`, `WLD_CTX_BLDG_metal` |
| `R15_PART_opaque_xm03_yp02_part01` | opaque, Nanite | 40.5 by 37.8 by 9.9 | 24 | `MI_R15_limestone_continuous_World` x5, `MI_R15_sexkaitb_UV` x4, `MI_R15_bitumen_UV` x3, `MI_R15_concrete_floor_03_UV` x2, `MI_R15_concrete_floor_03_World` x2, `A4_wells_1512_815266_0_metal`, `A4_wells_1514_307361_0_metal`, `A4_wells_1514_307361_0_wells_white_trim`, `A_E1510_a2_dark`, `A_E1510_a2_store`, `A_E1510_metal`, `MI_R15_brown_planks_09_UV`, `SS_R01_FadedParkingPaint_001` |
| `R15_PART_opaque_xm03_yp03_part01` | opaque, Nanite | 31.5 by 44.5 by 22.1 | 8 | `MI_R15_concrete_floor_03_World` x2, `A4_wells_1511_815257_0_metal`, `A4_wells_1511_815257_0_wells_white_trim`, `MI_R15_asphalt_03_World`, `MI_R15_concrete_floor_03_UV`, `MI_R15_limestone_continuous_World`, `MI_R15_sexkaitb_UV` |
| `R15_PART_opaque_xm03_yp04_part01` | opaque, Nanite | 31.5 by 49.4 by 22.0 | 7 | `A4_wells_1511_815257_0_metal`, `A4_wells_1511_815257_0_wells_white_trim`, `MI_R15_bitumen_UV`, `MI_R15_concrete_floor_03_UV`, `MI_R15_concrete_floor_03_World`, `MI_R15_limestone_continuous_World`, `MI_R15_sexkaitb_UV` |
| `R15_PART_opaque_xm04_yp00_part01` | opaque, Nanite | 45.7 by 35.4 by 18.1 | 21 | `MI_R15_concrete_floor_03_World` x4, `MI_R15_sexkaitb_UV` x2, `A_wieland_1504_307698_0_a2_gray_siding`, `B_MAT_Joint_recess`, `MI_R15_AsphaltShingle_Courses`, `MI_R15_bitumen_UV`, `MI_R15_brown_planks_09_World`, `MI_R15_concrete_floor_03_UV`, `MI_R15_factory_brick_UV`, `MI_R15_galvanized_World`, `MI_R15_limestone_continuous_World`, `MI_R15_turf_World`, `MI_R15_wood_chips_World`, `SS_R01_BlackRubber_002`, `SS_R01_LuminaireLens_001`, `WLD_CTX_BLDG_garage_001`, `WLD_CTX_BLDG_metal` |
| `R15_PART_opaque_xm04_yp01_part01` | opaque, Nanite | 96.1 by 59.2 by 10.4 | 32 | `MI_R15_concrete_floor_03_World` x10, `MI_R15_asphalt_03_World` x2, `A_W1525_door_paint`, `A_W1525_metal`, `A_W1525_paint_trim`, `A_W1525_siding_pale`, `B_MAT_Joint_recess`, `MI_R15_AsphaltShingle_Courses`, `MI_R15_brown_planks_09_UV`, `MI_R15_concrete_floor_03_UV`, `MI_R15_dirt_floor_World`, `MI_R15_galvanized_World`, `MI_R15_japanese_cedar_planks_World`, `MI_R15_turf_World`, `MI_R15_wood_chips_World`, `R14_W1525_PAINTED_METAL`, `SS_R01_BlackPaintedIron_001`, `SS_R01_BlackPaintedIron_002`, `SS_R01_BlackRubber_001`, `SS_R01_FadedParkingPaint_001`, `SS_R01_RecyclingPlastic_001`, `SS_R01_RefusePlastic_001` |
| `R15_PART_opaque_xm04_yp02_part01` | opaque, Nanite | 43.7 by 37.7 by 11.2 | 16 | `MI_R15_concrete_floor_03_World` x5, `B_MAT_Joint_recess`, `B_MAT_Wells_ornamental_iron`, `MI_R15_bitumen_UV`, `MI_R15_concrete_floor_03_UV`, `MI_R15_japanese_cedar_planks_World`, `MI_R15_limestone_continuous_World`, `MI_R15_sexkaitb_UV`, `MI_R15_wood_chips_World`, `SS_R01_BlackPaintedIron_001`, `SS_R01_FadedParkingPaint_001`, `WLD_CTX_BLDG_metal` |
| `R15_PART_opaque_xm04_yp03_part01` | opaque, Nanite | 40.0 by 46.2 by 6.8 | 18 | `MI_R15_concrete_floor_03_World` x4, `MI_R15_limestone_continuous_World` x2, `MI_R15_sexkaitb_UV` x2, `A4_wells_1533_306029_0_metal`, `A4_wells_1533_306029_0_wells_white_trim`, `A4_wells_1535_305867_0_metal`, `A4_wells_1535_305867_0_wells_white_trim`, `B_MAT_Wells_opal_globe`, `B_MAT_Wells_ornamental_iron`, `B_MAT_Wells_ornamental_iron_001`, `MI_R15_asphalt_03_World`, `MI_R15_brown_planks_09_UV`, `MI_R15_wood_chips_World` |
| `R15_PART_opaque_xm04_yp04_part01` | opaque, Nanite | 39.9 by 50.2 by 6.7 | 12 | `MI_R15_sexkaitb_UV` x3, `MI_R15_concrete_floor_03_UV` x2, `MI_R15_limestone_continuous_World` x2, `A4_wells_1533_306029_0_metal`, `A4_wells_1535_305867_0_metal`, `MI_R15_bitumen_UV`, `MI_R15_concrete_floor_03_World`, `WLD_CTX_BLDG_metal` |
| `R15_PART_opaque_xm05_yp00_part01` | opaque, Nanite | 41.2 by 33.5 by 16.1 | 25 | `MI_R15_concrete_floor_03_World` x4, `MI_R15_AsphaltShingle_Courses` x2, `MI_R15_concrete_floor_03_UV` x2, `MI_R15_limestone_continuous_World` x2, `A_W1536_door_paint`, `A_W1536_metal`, `B_MAT_Joint_recess`, `MI_R15_bitumen_UV`, `MI_R15_brown_planks_09_World`, `MI_R15_factory_brick_UV`, `MI_R15_galvanized_World`, `MI_R15_sexkaitb_UV`, `MI_R15_turf_World`, `MI_R15_wood_chips_World`, `MI_R15_yellow_brick_UV`, `SS_R01_BlackRubber_002`, `SS_R01_LuminaireLens_001`, `WLD_CTX_BLDG_garage_001`, `WLD_CTX_BLDG_metal` |
| `R15_PART_opaque_xm05_yp01_part01` | opaque, Nanite | 41.5 by 37.0 by 17.4 | 31 | `MI_R15_concrete_floor_03_World` x9, `MI_R15_concrete_floor_03_UV` x2, `A_W1533_1537_metal`, `A_W1533_1537_reveal_dark`, `A_W1533_1537_stone_joint`, `B_MAT_Joint_recess`, `MI_R15_W1533_Brick`, `MI_R15_W1533_Limestone`, `MI_R15_bitumen_UV`, `MI_R15_dirt_floor_World`, `MI_R15_galvanized_World`, `MI_R15_japanese_cedar_planks_World`, `MI_R15_sexkaitb_UV`, `MI_R15_turf_World`, `MI_R15_wood_chips_World`, `MI_R15_yellow_brick_UV`, `SS_R01_BlackPaintedIron_001`, `SS_R01_BlackRubber_001`, `SS_R01_RecyclingPlastic_001`, `SS_R01_RefusePlastic_001`, `WLD_CTX_BLDG_garage_001`, `WLD_CTX_BLDG_metal` |
| `R15_PART_opaque_xm05_yp02_part01` | opaque, Nanite | 46.3 by 44.8 by 16.3 | 30 | `MI_R15_concrete_floor_03_World` x7, `MI_R15_limestone_continuous_World` x3, `MI_R15_bitumen_UV` x2, `MI_R15_concrete_floor_03_UV` x2, `MI_R15_sexkaitb_UV` x2, `A_W1525_siding_pale`, `A_wells_1544_815228_0_metal`, `A_wells_1544_815228_0_wells_siding`, `A_wells_1544_815228_0_wells_siding_trim`, `A_wells_1548_304917_0_metal`, `A_wells_1548_304917_0_wells_paint_gray`, `B_MAT_Joint_recess`, `B_MAT_Wells_ornamental_iron`, `MI_R15_AsphaltShingle_Courses`, `MI_R15_japanese_cedar_planks_World`, `MI_R15_wood_chips_World`, `MI_R15_yellow_brick_UV`, `SS_R01_BlackPaintedIron_001`, `WLD_CTX_BLDG_metal` |
| `R15_PART_opaque_xm05_yp03_part01` | opaque, Nanite | 41.6 by 46.2 by 15.8 | 30 | `MI_R15_limestone_continuous_World` x8, `MI_R15_sexkaitb_UV` x5, `MI_R15_bitumen_UV` x4, `MI_R15_concrete_floor_03_UV` x2, `A4_wells_1535_305867_0_metal`, `A4_wells_1535_305867_0_wells_white_trim`, `A4_wells_1539_815224_0_metal`, `A4_wells_1541_815223_0_metal`, `A4_wells_1541_815223_0_wells_awning`, `A_wells_1543_815222_0_metal`, `A_wells_1543_815222_0_wells_awning`, `A_wells_1547_815221_0_metal`, `A_wells_1547_815221_0_wells_awning`, `MI_R15_bitumen_World`, `MI_R15_brown_planks_09_UV` |
| `R15_PART_opaque_xm05_yp03_part02` | opaque, Nanite | 40.1 by 50.5 by 9.9 | 14 | `MI_R15_concrete_floor_03_World` x4, `MI_R15_sexkaitb_UV` x2, `A_wells_1549_304564_0_metal`, `A_wells_1549_304564_0_wells_awning`, `B_MAT_Wells_opal_globe`, `B_MAT_Wells_ornamental_iron`, `B_MAT_Wells_ornamental_iron_001`, `MI_R15_asphalt_03_World`, `MI_R15_limestone_continuous_World`, `MI_R15_wood_chips_World` |
| `R15_PART_opaque_xm05_yp04_part01` | opaque, Nanite | 41.4 by 47.8 by 18.2 | 30 | `MI_R15_limestone_continuous_World` x8, `MI_R15_sexkaitb_UV` x5, `MI_R15_bitumen_UV` x2, `MI_R15_concrete_floor_03_UV` x2, `A4_wells_1535_305867_0_metal`, `A4_wells_1539_815224_0_metal`, `A4_wells_1541_815223_0_metal`, `A_E1539_REAR2026_door_paint`, `A_E1539_REAR2026_metal`, `A_wells_1543_815222_0_metal`, `A_wells_1547_815221_0_metal`, `A_wells_1549_304564_0_metal`, `MI_R15_bitumen_World`, `MI_R15_brick_wall_08_UV`, `MI_R15_concrete_floor_03_World`, `WLD_CTX_BLDG_garage_001`, `WLD_CTX_BLDG_metal` |
| `R15_PART_opaque_xm06_yp00_part01` | opaque, Nanite | 53.0 by 32.8 by 21.2 | 23 | `MI_R15_concrete_floor_03_World` x4, `MI_R15_bitumen_UV` x3, `MI_R15_concrete_floor_03_UV` x2, `MI_R15_limestone_continuous_World` x2, `MI_R15_sexkaitb_UV` x2, `A_W1544_door_paint`, `A_W1544_metal`, `A_W1550_MONTAUK_a1_pale_panel`, `A_W1550_MONTAUK_door_paint`, `A_W1550_MONTAUK_metal`, `B_MAT_Joint_recess`, `MI_R15_factory_brick_UV`, `MI_R15_wood_chips_World`, `WLD_CTX_BLDG_garage_001`, `WLD_CTX_BLDG_metal` |
| `R15_PART_opaque_xm06_yp01_part01` | opaque, Nanite | 58.1 by 41.5 by 18.6 | 13 | `MI_R15_concrete_floor_03_World` x3, `B_MAT_Joint_recess`, `B_MAT_Limestone_gravel`, `MI_R15_asphalt_03_World`, `MI_R15_bitumen_UV`, `MI_R15_brick_wall_08_UV`, `MI_R15_concrete_floor_03_UV`, `MI_R15_limestone_continuous_World`, `MI_R15_wood_chips_World`, `MI_R15_yellow_brick_UV`, `WLD_CTX_BLDG_metal` |
| `R15_PART_opaque_xm06_yp02_part01` | opaque, Nanite | 44.1 by 32.8 by 16.1 | 23 | `MI_R15_limestone_continuous_World` x7, `MI_R15_sexkaitb_UV` x3, `MI_R15_bitumen_UV` x2, `MI_R15_concrete_floor_03_UV` x2, `A_E1562_metal`, `A_wells_1548_304917_0_metal`, `A_wells_1548_304917_0_wells_paint_gray`, `A_wells_1550_815219_0_metal`, `A_wells_1550_815219_0_wells_paint_gray`, `A_wells_1552_304450_0_metal`, `A_wells_1552_304450_0_wells_awning`, `MI_R15_yellow_brick_UV`, `WLD_CTX_BLDG_metal` |
| `R15_PART_opaque_xm06_yp03_part01` | opaque, Nanite | 41.3 by 31.0 by 20.0 | 22 | `MI_R15_sexkaitb_UV` x5, `MI_R15_limestone_continuous_World` x4, `MI_R15_bitumen_UV` x3, `MI_R15_concrete_floor_03_UV` x2, `A_E1553_1555_metal`, `A_wells_1549_304564_0_metal`, `A_wells_1549_304564_0_wells_awning`, `A_wells_1559_815208_0_metal`, `A_wells_1559_815208_0_wells_awning_red`, `A_wells_1559_815208_0_wells_store_base`, `A_wells_1561_815207_0_metal`, `A_wells_1561_815207_0_wells_awning` |
| `R15_PART_opaque_xm06_yp04_part01` | opaque, Nanite | 40.8 by 4.3 by 19.5 | 11 | `MI_R15_sexkaitb_UV` x4, `MI_R15_limestone_continuous_World` x3, `A_E1553_1555_metal`, `A_wells_1549_304564_0_metal`, `A_wells_1559_815208_0_metal`, `A_wells_1561_815207_0_metal` |
| `R15_PART_opaque_xm07_yp00_part01` | opaque, Nanite | 13.9 by 32.4 by 21.2 | 7 | `MI_R15_concrete_floor_03_World` x3, `A_W1550_MONTAUK_a1_pale_panel`, `A_W1550_MONTAUK_door_paint`, `A_W1550_MONTAUK_metal`, `MI_R15_sexkaitb_UV` |
| `R15_PART_opaque_xm07_yp01_part01` | opaque, Nanite | 13.7 by 4.0 by 0.3 | 2 | `MI_R15_concrete_floor_03_World` x2 |
| `R15_PART_opaque_xm07_yp02_part01` | opaque, Nanite | 13.8 by 27.9 by 4.0 | 6 | `A_E1562_door_paint`, `A_E1562_metal`, `MI_R15_bitumen_UV`, `MI_R15_concrete_floor_03_UV`, `MI_R15_limestone_continuous_World`, `MI_R15_sexkaitb_UV` |
| `R15_PART_opaque_xm07_yp03_part01` | opaque, Nanite | 7.6 by 27.4 by 10.3 | 6 | `A_wells_1561_815207_0_metal`, `A_wells_1561_815207_0_wells_awning`, `MI_R15_bitumen_UV`, `MI_R15_concrete_floor_03_UV`, `MI_R15_limestone_continuous_World`, `MI_R15_sexkaitb_UV` |
| `R15_PART_opaque_xm07_yp04_part01` | opaque, Nanite | 7.2 by 1.1 by 10.3 | 3 | `A_wells_1561_815207_0_metal`, `MI_R15_limestone_continuous_World`, `MI_R15_sexkaitb_UV` |

### Trees and ground plants

The two holders carry no building material. Each row is one group of identical plants drawn together.

| Holder | Mesh | Plants in the group | Materials |
|---|---|---|---|
| `R15_InstancedTrees` | `Tree_English_Oak_Forest_01_A` | 1 | `MI_English_Oak_Bark_01`, `MI_English_Oak_Foliage_01` |
| `R15_InstancedTrees` | `Tree_English_Oak_Forest_01_B` | 1 | `MI_English_Oak_Bark_01`, `MI_English_Oak_Foliage_01` |
| `R15_InstancedTrees` | `Tree_English_Oak_Forest_01_C` | 1 | `MI_English_Oak_Bark_01`, `MI_English_Oak_Foliage_01` |
| `R15_InstancedTrees` | `Tree_Ginkgo_01_A` | 1 | `MI_Ginkgo_Bark_01`, `MI_Ginkgo_Foliage_01` |
| `R15_InstancedTrees` | `Tree_Ginkgo_01_B` | 1 | `MI_Ginkgo_Bark_01`, `MI_Ginkgo_Foliage_01` |
| `R15_InstancedTrees` | `Tree_Ginkgo_01_C` | 1 | `MI_Ginkgo_Bark_01`, `MI_Ginkgo_Foliage_01` |
| `R15_InstancedTrees` | `Tree_Norway_Maple_Forest_01_A` | 1 | `MI_Norway_Maple_Bark_01`, `MI_Norway_Maple_Foliage_01` |
| `R15_InstancedTrees` | `Tree_Norway_Maple_Forest_01_B` | 1 | `MI_Norway_Maple_Bark_01`, `MI_Norway_Maple_Foliage_01` |
| `R15_InstancedTrees` | `Tree_Norway_Maple_Forest_01_C` | 1 | `MI_Norway_Maple_Bark_01`, `MI_Norway_Maple_Foliage_01` |
| `R15_InstancedTrees` | `Tree_Silver_Birch_01_A` | 1 | `MI_Silver_Birch_01_Bark_Blend`, `MI_Silver_Birch_01_Foliage`, `MI_Silver_Birch_01_Bark` |
| `R15_InstancedTrees` | `Tree_Silver_Birch_01_B` | 1 | `MI_Silver_Birch_01_Bark_Blend`, `MI_Silver_Birch_01_Foliage`, `MI_Silver_Birch_01_Bark` |
| `R15_InstancedLandscape` | `SM_R15_weed_plant_02_00` | 90 | `MI_R15_weed_plant_02` |
| `R15_InstancedLandscape` | `SM_R15_weed_plant_02_01` | 90 | `MI_R15_weed_plant_02` |
| `R15_InstancedLandscape` | `SM_R15_moss_01_02` | 45 | `MI_R15_moss_01` |
| `R15_InstancedLandscape` | `SM_R15_grass_medium_02_04` | 23 | `MI_R15_grass_medium_02` |
| `R15_InstancedLandscape` | `SM_R15_shrub_04_00` | 182 | `MI_R15_shrub_04` |
| `R15_InstancedLandscape` | `SM_R15_shrub_04_01` | 182 | `MI_R15_shrub_04` |
| `R15_InstancedLandscape` | `SM_R15_shrub_04_02` | 182 | `MI_R15_shrub_04` |
| `R15_InstancedLandscape` | `SM_R15_shrub_04_03` | 182 | `MI_R15_shrub_04` |
| `R15_InstancedLandscape` | `SM_R15_grass_medium_02_00` | 527 | `MI_R15_Lawn` |
| `R15_InstancedLandscape` | `SM_R15_grass_medium_02_01` | 527 | `MI_R15_Lawn` |
| `R15_InstancedLandscape` | `SM_R15_grass_medium_02_02` | 527 | `MI_R15_Lawn` |

Totals: `R15_InstancedTrees` 11; `R15_InstancedLandscape` 2557. These match the 11 trees and 2,557 ground plants in the October release notes.
