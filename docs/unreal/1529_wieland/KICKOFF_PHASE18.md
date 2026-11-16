Phase 18 (plan images for the owner's path-drawing page) of the 1529 N. Wieland scene plan, unattended, short

What this session is for

The owner wants to draw the walk-through paths for the videos themselves. The supervising session built a drawing page (`docs\unreal\1529_wieland\owner_review\paths\index.html`, served by `path_server.py` at http://127.0.0.1:8766/) that shows plan images and lets the owner click a path onto them. Your only job is to make those plan images, with an exact mapping from pixels to the level's coordinates, so the owner can start drawing. A later phase (19) writes the tool that turns the drawn paths into videos. You work in the Unreal Engine 5.9 project `D:\Unreal_Engine_Projects\Wieland1527 5.9\Wieland1527.uproject` through the editor's agent server (unreal-mcp). The plan folder is `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\`. You have no memory of earlier sessions. Nobody will answer questions; decide and keep going. Aim to finish within about an hour.

If `phase18_results.md` already exists in the plan folder, read it and continue from the first unfinished line.

What to make

Orthographic top views, 2,048 by 2,048 pixels, PNG, plain and legible: light grey ground, darker walls, doors and openings visible, stairs and the lift shown, the street and the lot line drawn.

- `site`: the lot, the street, the alley side and the neighbours, roofs on.
- One per floor of 1529, including the lowest level, each floor, the rear deck and the penthouse roof deck. Cut each one 1.2 m above its floor, so that walls, doors, stairs and furniture read as a floor plan. Hide everything above the cut.

Write the images and `manifest.json` to `owner_review\paths\plans\` in exactly this form, because the page reads it:

```
{ "plans": [ { "id": "site", "label": "Site plan (roofs)", "image": "site.png",
               "width_px": 2048, "height_px": 2048,
               "world_x_at_left_cm": ..., "world_x_at_right_cm": ...,
               "world_y_at_top_cm": ..., "world_y_at_bottom_cm": ...,
               "floor_z_cm": <floor level>, "default_eye_height_cm": 160 }, ... ],
  "north_up": true, "units": "Unreal centimetres, level axes" }
```

A pixel (u, v) must map to world X = left + u/width x (right - left) and world Y = top + v/height x (bottom - top). Put north up on every image. If the level axes are turned against north, choose the corner values so the mapping stays linear, and state in the manifest which world axis points up. Use one scale for all floor plans, so the building does not jump between floors.

Check

Mark three known points on each image: two lot corners and the centre of a stair. Confirm they land within 3 pixels of where the mapping puts them, and save the marked copies as `check_<id>.png` beside the images. Then open http://127.0.0.1:8766/ (the server may not be running: start it with `python -I path_server.py` in `owner_review\paths\`) and confirm the page lists the plans.

Rules

- Nanite ray tracing stays OFF: keep the console variable r.RayTracing.Nanite.Mode at 0; it has hung the graphics card three times.
- Do not save any level. Every camera and visibility change is temporary; put it back afterwards and read it back.
- Never save `/Game/Wieland/R15_Landscape/L_R15_Production`, never use "Save All".
- Memory: read free commit first; under 30 GB, close and reopen the editor.
- Not approved: anything with a price, an account or key, any deletion, software installation, any push or merge.

Done means

- The images, the check images and `manifest.json` exist.
- `phase18_results.md` in the plan folder: its first line is `Status: DONE` with the time; then the plans made, their mapping, the check results, and the full path of each file.
- Any error is logged in `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\PROJECT_MEMORY.md` with cause, fix and status.
- Everything is committed by explicit path on the current branch. Do not push.
- Then stop. Phase 17, the site model, starts next in its own session.

Write for the owner in plain words: they know Revit and construction well and Unreal less well.
