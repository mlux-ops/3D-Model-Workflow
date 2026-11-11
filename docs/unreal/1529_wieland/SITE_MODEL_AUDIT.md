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
