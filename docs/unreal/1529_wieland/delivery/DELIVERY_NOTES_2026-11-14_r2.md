# 1529 N. Wieland St., Chicago: Unreal Engine scene, delivery revision r2 of 2026-11-14

This revision adds what changed after the delivery of earlier the same day (`1529_Wieland_UE5.9_Delivery_2026-11-14`): the surroundings and the downtown skyline rebuilt from the 2022 Illinois laser scan (Phase 17), their materials refined from freely licensed photographs (Phase 20), new pictures of every station and design view, and the tool that turns the owner's own drawn walking paths into videos (Phase 19). It stands on its own; section 6 says what stays in the earlier package.

Words used the same way throughout:

- **Station** (S1 to S9; S7 cannot exist): a fixed camera position on the street. **Design view** (D1 to D5): a fixed camera position in or on the building; D1 is the penthouse roof deck. **D1S**: D1 moved onto the south penthouse deck, 10.9 m south, the same height, from where the skyline is not behind the pergola.
- **Real time**: made by the renderer the walk-through uses (Lumen, Unreal's method for bounced light at interactive speed). **Path traced**: made by Unreal's Path Tracer, the slow renderer that follows light physically.
- **Laser scan**: the Illinois Height Modernization airborne lidar of Cook County, spring 2022. **Clean built form**: a building shape made of flat or planar roofs, straight walls, parapets, setbacks and simple shapes for crowns, masts and rooftop plant, sized from the scan but never following its raw points.
- **Level**: one saved Unreal scene file. **Variant Manager**: Unreal's list of named options that show some objects and hide others.

## 1. What is in this package

| Folder or file | What it is |
|---|---|
| `DELIVERY_NOTES.md` | This file. |
| `stills\` | Twelve real-time pictures (S1 to S6, S9, D1 to D5) and D1 path traced, 3,840 by 2,160 pixels, with the new surroundings and materials (section 3). |
| `skyline\` | The labelled skyline panoramas from D1S and D1, every tower of 90 m or more beyond 1 km named with its modelled height (section 2). |
| `comparison\` | `p11_vs_p17_<view>.jpg`: each view in the earlier delivery's path-traced still beside the same view with the laser-scan surroundings (Phase 17); `p17_vs_p20_<view>.jpg`: the Phase 17 picture beside the Phase 20 one, showing the material changes; `skyline_p17_vs_p20_<deck>.jpg` the same for the skyline sheets. |
| `video_paths\` | Videos made from drawn walking paths, each with a small file giving its length, frames, render time and the fingerprint of the path it came from (section 4). |
| `RENDER_HOW.md` | How the owner draws a path and asks for its video, and how to run the tool by hand. |
| `LICENCES.csv` | The licence table of the earlier package's build, unchanged, plus section 7 below for what this revision adds. |
| `MANIFEST_SHA256.txt` | Size and SHA-256 checksum of every file in this package. |

## 2. The surroundings and the skyline (Phase 17)

The owner chose a model built from public laser-scan data: our own geometry, usable offline. Google's 3D tiles, Maps, Earth and Street View were not used in any way.

- **What is modelled.** A viewshed (what each station and deck can really see, cast over the scan's surface model) picked 418 buildings beyond 150 m that show from the roof decks, out to 4.3 km (the Loop), and the 144 county buildings of Zones 1 and 2 within the 300 m square around the lot. All are clean built forms; the ground beyond the square, with the lake and river, is one mesh with colours from the scan's ground classes.
- **How accurate** (measured against the 2022 point cloud, on the clean forms): Zone 1 (the 23 buildings within 40 m of the lot): main roof within 0.3 m for 23 of 23 (median 0.03 m); free walls within 0.3 m for 19 of 22. Skyline towers (beyond 1 km, 60 m or taller, 104 with scan returns): main roof within 1 m for 96 of 104; masts and spires within 1 m for 37 of 37; plan within 2 m for 97 of 105. The misses are named in the project's `phase17_tables.md`.
- **Against photographs**: tower tops lined up with two freely licensed skyline photographs from North Avenue Beach agree within 0.1 degree for the towers whose top is the photograph's sky line (median 0.07 degree in the 2023 photograph), except 900 N Michigan, whose thin lantern tops the photograph's edge finder does not register.
- **Switching**: in the working level `L_Site_M4`, the Variant Manager list `Surroundings` (asset `/Game/Wieland1529/Surroundings/LVS_W1529_Surroundings`) offers "Laser-scan model (Phase 17)" (the default), "Earlier detailed buildings" and "Phase 4 survey massing".
- **Frame time** of the real-time walk-through with the new surroundings (measured in the editor at the plan's real-time conditions): exterior path 95th percentile 14.96 ms, roof-deck path 14.27 ms, against 16.67 ms (60 pictures a second); graphics card 10.9 and 10.1 ms against 14.5; video memory 8.8 GB against 13.0. Inside the budget.

## 3. Materials (Phase 20) and the stills

- **Skyline towers**: the 40 most visible from the roof deck were checked against freely licensed photographs (Wikimedia Commons). 20 were settled by them: 17 changed (among them the Waldorf Astoria, which is warm-grey stone, not glass; Two Prudential Plaza, granite and blue-grey glass; One Chicago, light blue glass with silver fins; the Merchandise Mart, darker tan) and 3 confirmed. The rest keep materials from public descriptions or, labelled as assumptions, from their building type.
- **Neighbours (Zones 1 and 2)**: no open photograph shows their facades, so their wall materials come from the Cook County Assessor's records where they exist (94 of 144), brick otherwise, and every colour is an assumption. The owner's own photographs would settle them.
- **Stills**: real time, summer afternoon (sun bearing 241.72 degrees, 46.40 degrees above the horizon), 3,840 by 2,160. D1 is also path traced (1,024 samples). Path-traced pictures trace each mesh's simplified fallback copy (Nanite ray tracing is kept off: it hung the graphics card three times). These are real-time pictures, so they are not a like-for-like replacement of the earlier package's path-traced stills; the comparison sheets set them side by side.

## 4. Videos of drawn walking paths (Phase 19)

The owner draws walking paths on top views of the site and of each floor (the path page, `Open path editor.bat`), presses "Request videos", and the tool renders each path to an MP4 at its own speed, frame rate and picture size, after checking that the walk does not pass through a wall or other solid object (a path that does is refused, with the object and the place). See `RENDER_HOW.md`.

At the time of this revision the owner had not saved a path yet. `video_paths\` therefore holds the agent's test walk across the penthouse roof deck (`_test_roofdeck.mp4`, 15.2 s, 1,920 by 1,080, 30 frames a second), made to prove the tool. Two further test paths were correctly refused, with the object and its place: one through the penthouse's north exterior wall, and one from the sidewalk into the north neighbour, 1533 N Wieland (a laser-scan building, which the check treats as solid).

## 5. Known differences and assumptions

- The surroundings beyond the work list keep Phase 17's materials by building type: 357 of the 418 skyline buildings rest on such assumptions (371 in Phase 17, less the 14 that Phase 20's photographs settled; the project's `tower_materials.csv` holds Phase 17's labels, and `review\phase20\building_table.csv` overrides them for the towers it settled).
- One county footprint (773890) has no building in the 2022 scan (ground and trees only); it is modelled as the low structure the scan shows.
- Rooftop items under 1.5 m or 4 square metres are left out by rule; crowns are simplified shapes.

## 6. What stays in the earlier package

`1529_Wieland_UE5.9_Delivery_2026-11-14` still holds the packaged build (the walk-through program), the 60-second animation, the comparison frames and the build's profile. They were made before Phase 17 and show the earlier surroundings (the generic far-city blocks and the earlier neighbour massing). That package is marked superseded for its surroundings and stills; nothing in it was deleted.

## 7. Sources and licences added by this revision

- Laser scan: Illinois State Geological Survey, Illinois Height Modernization Program, Cook County 2022 lidar (surface and ground models, classified point cloud); cite "Illinois State Geological Survey".
- Building footprints: Cook County 2022 building footprints; City of Chicago building footprints (Chicago Data Portal).
- Wall materials of Zones 1 and 2: Cook County Assessor, residential characteristics, tax year 2025 (public records).
- Tower names, shapes and some materials: OpenStreetMap, © OpenStreetMap contributors, Open Database License (ODbL). The derived names and shapes carry the ODbL; share-alike applies if the model is ever published.
- Photographs from Wikimedia Commons (CC0, public domain, CC BY, CC BY-SA, each with its author recorded in the project's `review\phase20\commons_index.csv`) were looked at only, to judge colours and window grids; none is included in this package, used as a texture or traced.
- Materials of the new buildings are procedural (no photographic texture).
