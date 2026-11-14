Status: DONE 2026-11-14 12:35

# Phase 18: plan images for the owner's path-drawing page

## What was made

Nine top views, each 2,048 x 2,048 pixels, PNG. They are listed in `owner_review\paths\plans\manifest.json`, and the drawing page at http://127.0.0.1:8766/ shows them as nine tabs.

| id | What it shows | Floor level (cm) | Cut height (cm) | Scale |
|---|---|---|---|---|
| site | Site plan with roofs on: the lot, the street (both kerbs and the crown line), the neighbours and the trees | 0 (grade) | none, roofs on | 4.88 cm per pixel, 100 m across |
| lower_level | Lower level | -150 | -30 | 1.75 cm per pixel, 35.84 m across |
| entry | Entry hall at grade: the front passage from the street door back to the lift (the lower-level rooms show darker below it) | 10 | 130 | 1.75 |
| first_floor | 1st floor | 203 | 323 | 1.75 |
| rear_deck | Rear deck over the garages. It is at 1st-floor level, so it uses the same cut as the 1st floor with the deck outlined in green | 203 | 323 | 1.75 |
| second_floor | 2nd floor | 528 | 648 | 1.75 |
| third_floor | 3rd floor | 853 | 973 | 1.75 |
| fourth_floor | 4th floor, including the rear terrace | 1179 | 1299 | 1.75 |
| roof_deck | Penthouse roof deck | 1523 | 1643 | 1.75 |

The floor levels are the tops of the Revit floor slabs as they sit in the level. They agree with the plan's figures of 2.032, 5.283, 8.534 and 11.786 m above grade. The lower-level slab is at -1.47 m at the front and -1.52 m at the rear; -1.50 m is used. The shared entry hall has its own slab at +0.10 m, with a lift stop there, so it has its own plan. Without it, a point clicked in the hall would get the 1st floor's height, about 1.9 m too high.

Every floor plan uses the same window and scale, so the building does not move when you switch floors.

### How the images look

- Floor and ground: light grey.
- Below the floor (stairs going down, yards): slightly darker grey.
- Furniture and counters: mid grey, getting darker the taller they are.
- Walls cut by the plane: charcoal.
- Doors: tan.
- Windows: blue.
- Stairs: each tread shows as a line.
- Lift: a blue box with a cross, marked LIFT.
- One stair on each floor is marked STAIR.
- Lot line: red dashes.
- Each image also has a title, a north arrow and a scale bar.

## North is to the LEFT, not up

The brief asked for north up and gave a fixed formula: world X = left + u/width x (right - left), world Y = top + v/height x (bottom - top). This level's north is the -X axis (the level frame in PLAN.md: origin at the south-west lot corner, north -X, east -Y). The formula ties X to the horizontal pixel direction. To put north up, X would have to run vertically, which means turning the image a quarter turn. Choosing different corner values can only flip an axis; it cannot turn the image.

The drawing page (`index.html`, lines 137 to 142) converts clicks with exactly that formula. I kept the formula exact, because a quietly swapped axis would put every Phase 19 camera in the wrong place. So, on every image:

- the street (Wieland, west, +Y) is at the bottom;
- the rear of the lot (east, -Y) is at the top;
- north (-X) is to the left;
- south (+X) is to the right.

Each image has a large north arrow pointing left. In Revit terms the plans are shown at project north, with the street at the bottom. The image is not mirrored: the check below uses two diagonally opposite lot corners, and a mirrored image would have failed it.

The manifest says this outright:

- `"north_up": false`
- `"up_axis": "-Y (east, the rear of the lot)"`
- `"right_axis": "+X (south)"`
- `"north_direction_on_image": "left (-X)"`
- an `orientation_note`

Level north is 1.18 degrees west of true north. The arrow shows level north.

Note for Phase 19 and the supervisor: on the page's "Hold a direction" setting, the arrow for 0° points to the TOP of the image, clockwise. On these plans the top is east. So the direction the owner sets by eye converts as Unreal yaw = yaw_deg - 90:

- 0 = east (the rear);
- 90 = south;
- 180 = west (the street);
- 270 = north.

The label "° from north" does not fit these images. This is written into the manifest as `page_yaw_note`. I did not change the page.

The brief mentioned "the alley side". There is no alley behind the lot (PLAN.md, Phase 4). The site plan shows the neighbours behind the lot instead.

## Mapping (from manifest.json)

| id | world_x_at_left_cm | world_x_at_right_cm | world_y_at_top_cm | world_y_at_bottom_cm |
|---|---|---|---|---|
| site | -5754.4 | 4245.6 | -6000.0 | 4000.0 |
| all eight floor plans | -2546.4 | 1037.6 | -3349.6 | 234.4 |

Every image has `width_px` = `height_px` = 2048 and `default_eye_height_cm` 160. Measure u and v from the top-left corner of the image; pixel number i covers u from i to i+1.

## Check

On each plan I placed three temporary 24 cm marker cubes, at 40 cm above the floor:

- the south-west lot corner (0, 0);
- the north-east lot corner (-1508.8, -3115.1);
- the centre of a stair run on that floor.

The engine rendered the cubes with the plan's own camera. I then found the cube centres in the rendered picture and compared them with where the page's formula puts those world points.

| id | SW corner error (px) | NE corner error (px) | Stair centre error (px) | Stair used (x, y cm) | Result |
|---|---|---|---|---|---|
| site | 0.30 | 0.33 | 0.28 | rear yard stair (-1055.5, -3069.0) | pass |
| lower_level | 0.10 | 0.09 | 0.35 | (-629.0, -1981.0) | pass |
| entry | 0.10 | 0.09 | 0.14 | (-703.0, -770.0) | pass |
| first_floor | 0.10 | 0.09 | 0.41 | (-694.5, -2635.0) | pass |
| rear_deck | 0.10 | 0.09 | 0.41 | (-694.5, -2635.0) | pass |
| second_floor | 0.10 | 0.09 | 0.18 | (-703.0, -888.0) | pass |
| third_floor | 0.10 | 0.09 | 0.13 | (-816.5, -2365.0) | pass |
| fourth_floor | 0.10 | 0.09 | 0.13 | (-816.5, -2365.0) | pass |
| roof_deck | 0.10 | 0.09 | 0.34 | (-692.0, -2363.5) | pass |

- Every point is within 0.41 pixels, against the 3-pixel limit.
- In the check images, the magenta cross is where the formula puts the point and the green square is where the engine drew the marker.
- The full numbers are in `review\phase18\checks.json`.
- The rendered geometry also agrees with the drawings: the building sits inside the red lot line, with its front wall about 3.1 m behind the front lot line, which is the drawn 10 ft 2 1/2 in.

The page check:

- `path_server.py` was already running on port 8766.
- `/api/plans` returns all nine plans.
- Each `/plan/<id>.png` returns 200 as image/png.
- A headless-browser screenshot shows the page with plan tabs (taken before the entry plan was added; `/api/plans` was read again afterwards and returns nine) and the site plan loaded: `review\phase18\page_check.png`.

## Editor state afterwards

- Nothing was saved, and Save All was not used.
- The capture camera and the marker cubes were temporary actors I placed myself. I removed them again, so these were my own unsaved additions being undone, not deletions of project content. The actor count is back to 3,040, the same as before.
- The viewport camera was never moved; I read it back unchanged.
- r.RayTracing.Nanite.Mode is 0 throughout.
- No level visibility was changed, because all levels were already visible.
- Free memory at the start: 31.4 GB of free commit, above the 30 GB limit, so the editor was not restarted.
- The editor lists three levels with unsaved changes:
  - `L_Site_M4`, from the temporary actors;
  - `L_W1529_NorthPenthouse` and `L_W1529_SouthPenthouse`. My scripts placed nothing in these two. I did not read the unsaved-changes list at the start, so I cannot tell whether they were already changed before this session.
  - Do not save any of the three.

## How it was made

- `tools\phase18_capture.py` makes orthographic depth captures with a temporary SceneCapture2D. For a floor, the camera sits at the cut height looking straight down, and its near clip plane hides everything above.
- `tools\phase18_plans.py` builds the picture in three steps:
  1. **Floors, furniture and stairs:** from the cut capture.
  2. **Walls:** a cut wall shows its open inside to the camera and would vanish. Instead, walls that stand on this floor and rise through the cut are captured from below, and a wall is drawn wherever its underside is below the cut. Because the wall above a door head is higher than the cut, doors stay open. Walls running through several floors are drawn from their outline seen from above.
  3. **Doors and windows that cross the cut:** drawn on top, from their outlines.
- Labels, the lot line, the street, the north arrow and the scale bar come from the known lot coordinates.
- Large scratch files, mostly depth EXRs, are in `review\phase18\scratch\` (31 MB) and are not committed.

## Files

- E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\owner_review\paths\plans\manifest.json
- E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\owner_review\paths\plans\site.png
- E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\owner_review\paths\plans\lower_level.png
- E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\owner_review\paths\plans\entry.png
- E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\owner_review\paths\plans\first_floor.png
- E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\owner_review\paths\plans\rear_deck.png
- E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\owner_review\paths\plans\second_floor.png
- E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\owner_review\paths\plans\third_floor.png
- E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\owner_review\paths\plans\fourth_floor.png
- E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\owner_review\paths\plans\roof_deck.png
- E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\owner_review\paths\plans\check_site.png
- E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\owner_review\paths\plans\check_lower_level.png
- E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\owner_review\paths\plans\check_entry.png
- E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\owner_review\paths\plans\check_first_floor.png
- E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\owner_review\paths\plans\check_rear_deck.png
- E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\owner_review\paths\plans\check_second_floor.png
- E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\owner_review\paths\plans\check_third_floor.png
- E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\owner_review\paths\plans\check_fourth_floor.png
- E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\owner_review\paths\plans\check_roof_deck.png
- E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\review\phase18\checks.json
- E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\review\phase18\page_check.png
- E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\tools\phase18_capture.py
- E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\tools\phase18_plans.py
