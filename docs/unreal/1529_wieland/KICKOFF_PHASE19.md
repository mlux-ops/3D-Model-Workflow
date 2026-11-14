Phase 19 (the owner's own walking paths: the path-to-video tool and the videos) of the 1529 N. Wieland scene plan, unattended

What this session is for

The owner wants to draw the walk-through paths for the videos themselves, and have the editor make the videos from them. The supervising session has built a drawing page for the owner (`docs\unreal\1529_wieland\owner_review\paths\index.html`, served by `path_server.py` at http://127.0.0.1:8766/). It shows plan images of the site and of each floor, lets the owner click a path onto them, and saves each path as a JSON file. Phase 18 already made the plan images the page shows, and Phase 17 rebuilt the surroundings and the downtown skyline. Your job is the tool that turns a saved path into a video, and then the videos of the paths the owner has drawn. You work in the Unreal Engine 5.9 project `D:\Unreal_Engine_Projects\Wieland1527 5.9\Wieland1527.uproject` through the editor's agent server (unreal-mcp). The plan folder is `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\`. You have no memory of earlier sessions; their records are in the plan folder.

You are running from a terminal and nobody will answer questions. Decide what you can and put anything that needs the owner in the final report. A supervisor checks your progress every 5 minutes.

If `phase19_results.md` already exists in the plan folder, read its "How to resume" section and journal from the bottom up, and continue from the first unfinished line.

The file formats (fixed; the page already uses them)

`owner_review\paths\plans\manifest.json` (Phase 18 wrote it; read it, do not change it unless a mapping is wrong):

```
{ "plans": [ { "id": "site", "label": "Site plan (roofs)", "image": "site.png",
               "width_px": 2048, "height_px": 2048,
               "world_x_at_left_cm": ..., "world_x_at_right_cm": ...,
               "world_y_at_top_cm": ..., "world_y_at_bottom_cm": ...,
               "floor_z_cm": <ground level>, "default_eye_height_cm": 160 },
             { "id": "L1", "label": "Level 1 (ground floor)", ... "floor_z_cm": ... }, ... ],
  "north_up": true, "units": "Unreal centimetres, level axes" }
```

The mapping must be exact: a pixel (u, v) on a plan maps to world X = left + u/width x (right - left) and world Y = top + v/height x (bottom - top). Make north point up on every image, and state in the manifest which world axis that is. If north up needs the image rotated relative to the level axes, keep the mapping linear by choosing the corners accordingly and say how.

`owner_review\paths\<name>.json` (the page writes it):

```
{ "name": "Roof deck sunset", "version": 1,
  "speed_m_per_s": 1.2, "fps": 30, "resolution": [1920, 1080], "quality": "realtime",
  "points": [ { "plan": "L5", "x_cm": ..., "y_cm": ..., "z_cm": <floor_z + eye height>,
                "pause_s": 0, "look": { "mode": "forward" } },
              { ..., "look": { "mode": "target", "x_cm": ..., "y_cm": ..., "z_cm": ... } },
              { ..., "look": { "mode": "yaw", "yaw_deg": 135, "pitch_deg": 0 } },
              { ..., "segment": "stair" } ],
  "render_requested_at": "2026-11-14T15:00:00" }
```

A path may change floors between points; the point before the change carries `"segment": "stair"` or `"segment": "lift"`, and z changes between those points. Path names contain only letters, digits, spaces, hyphens and underscores; refuse any other name.

What to build

1. **Plan images.** Already made by Phase 18. If Phase 17 changed the site, re-make only the "site" image so it shows the new surroundings, keeping the same mapping.
2. **The path tool** `tools\wieland_paths.py`. It reads a path JSON and makes the video:
   - a camera that follows a smooth curve through the points at constant walking speed, pausing where asked, at the eye height given;
   - looking ahead along the path ("forward"), turning smoothly towards a target, or holding a direction ("yaw"), with turns eased so the picture never jerks;
   - a line-of-sight check: if a segment passes through a wall, floor or other solid object, report which one and where, and do not render that path. Doors and door panels, glass sliding panels, curtains and furniture smaller than 0.5 m high are passable (the camera may pass through them). A segment whose start point has `"segment": "stair"` (or "lift") changes floors: it follows the nearest stair run (or rises vertically in the lift shaft) and is not checked against slabs;
   - rendered through Movie Render Graph in real time at the path's resolution and frame rate (path-traced quality only if the JSON asks for "pathtraced"), encoded to H.264 MP4 with ffmpeg, into `delivery\video_paths\<name>.mp4`, with a small JSON beside it listing duration, frames, the path file's checksum and the render time.
   It skips a path whose video is newer than its `render_requested_at` and whose checksum matches.
3. **A test path** of your own, `owner_review\paths\_test_roofdeck.json`, a short walk across the roof deck; render it and look at the video before doing any of the owner's.
4. **Render the owner's paths.** Render every path JSON in `owner_review\paths\` (not starting with `_`) that has `render_requested_at` set and no up-to-date video.
5. **Re-rendering on request.** The page's "Request videos" button sets `render_requested_at` in the path files and writes `owner_review\paths\RENDER_REQUEST`; the supervisor's watcher then starts a short session that runs your tool. Make the tool runnable as one call, `wieland_paths.render_requested()`, which renders every requested path that has no up-to-date video and writes `owner_review\paths\last_render.json` (time, paths rendered, refused, with reasons). Write `owner_review\paths\RENDER_HOW.md`: how the owner asks for new videos, and how to run the tool by hand from the editor's Python.
6. **A new delivery revision.** Once the videos are done: copy the Phase 17 re-rendered stills, the new videos and updated delivery notes into a new dated package `D:\Wieland1529_delivery\package\1529_Wieland_UE5.9_Delivery_<date>\` and into Google Drive `F:\My Drive\Folders\3D Model Workflow\3D Models\1529_Wieland_UE5.9_Delivery_<date>\`, checked by size and SHA-256, and mark the 2026-11-14 package as superseded in both places (a SUPERSEDED.md note in its folder; delete nothing).

Done means

- `phase19_results.md` in the plan folder:
  - a journal (a line marked PENDING before each step, committed before you start it, and a "How to resume" section);
  - the mapping check for each plan;
  - the test video;
  - every owner path rendered, or why not;
  - a first `Status:` line that says DONE, with the time.
- Every error is logged in `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\PROJECT_MEMORY.md` with cause, fix and status, in a new section for Phase 19.
- Commit the tool, notes and results by explicit path; the videos stay uncommitted under `delivery\`. Do not push. Then stop.

Read these first, and only these

1. `phase11_results.md`: how J7 made the animation (camera, sequences, Movie Render Graph settings, encoding, the brightness lesson: one run per camera move, with long warm-up). Reuse its scripts.
2. `phase17_results.md` and `phase18_results.md`: their status, what levels make up the site now, and the plan images.
3. `REFERENCE_VIEWS.md`, for stations and design views.
4. The last three sections of `PROJECT_MEMORY.md`.

Rules that apply throughout

- Nanite ray tracing stays OFF: keep the console variable r.RayTracing.Nanite.Mode at 0; it has hung the graphics card three times. Render one video at a time, and let a freshly opened level settle five minutes first.
- Never save `/Game/Wieland/R15_Landscape/L_R15_Production`, never use "Save All", save named assets only, never edit a Datasmith asset.
- Memory: read free commit before each render; under 30 GB, close and reopen the editor or wait.
- Put back any console or quality setting you change, and read it back to confirm.
- Not approved: anything with a price, an account or key, any deletion, software installation, any push or merge.

Keep going until the done list is met; treat errors and failing tools as ordinary obstacles. Write for the owner in plain words: they know Revit and construction well and Unreal less well.
