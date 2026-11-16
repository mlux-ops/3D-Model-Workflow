# How to get videos of your own walking paths

Written for the owner (Phase 19, 2026-11-14). It covers drawing a path, asking for its video, where the video appears, and how to run the tool yourself from inside Unreal.

## 1. Draw a path and ask for its video

1. Double-click `Open path editor.bat` in this folder. It opens the path page at http://127.0.0.1:8766/ in your browser. (If the page does not open, the small server behind it is not running; the .bat file starts it.)
2. Choose a plan image (the site, or one floor). On every image north points to the **left** and the street is at the bottom; a north arrow is drawn on each.
3. Click points along the walk. For each point you can set:
   - a **pause** in seconds (the camera stops there, easing in and out);
   - where the camera **looks**: ahead along the path, at a point you click, or in a held direction;
   - on the point **before** a change of floor, "stair" or "lift".
4. Give the path a name (letters, digits, spaces, hyphens and underscores only), set the walking speed (1.2 m/s is an easy walk), and save it.
5. Press **Request videos**. That marks your saved paths as wanted and writes a request file; the supervising program then starts a short session in the editor that makes the videos.

## 2. What the tool does with a path

- The camera walks a smooth curve through your points at your speed, at the eye height you set (1.60 m above the floor unless you changed it). It starts, stops and pauses gently, and turns gently, so the picture never jerks.
- **Stairs:** put a point at the foot and at the head of each flight (and one on each landing), and set "stair" on the point before the climb. The camera goes straight from point to point, rising evenly, at about 60 percent of your walking speed. **Lift:** set "lift" on the point in the lift; the camera rises straight up at 1 m/s, then moves on.
- **Walls:** before anything is rendered, the tool checks that the walk does not pass through a wall, floor, window, cabinet or other solid object. If it does, that path is **not** rendered, and the reason is written down with the object's name and its place (see section 3). Doors and door panels, sliding glass panels, curtains and furniture lower than 0.5 m may be walked through.
- The video is rendered in real time quality (the walk-through's renderer) at the path's picture size and frame rate. Ask for "pathtraced" quality in the path only if you need it: it is many times slower.
- A path whose video is already up to date (made after your last request, from the same saved path) is not rendered again.

## 3. Where the results appear

- Videos: `docs\unreal\1529_wieland\delivery\video_paths\<path name>.mp4` (H.264, plays in any player), with `<path name>.json` beside it (length, frames, render time, and a fingerprint of the path file it was made from).
- `last_render.json` in this folder: when the tool last ran, which paths it rendered, which it refused and why (for example "segment 2 (point 2 to 3) passes through Walls_Basic_Wall_... at x -1386, y -1000, z 1339 cm"), and which were already up to date.
- The picture files of each video are kept in `D:\Wieland1529_delivery\video_paths_frames\`.

Time: a real-time frame at 1,920 by 1,080 takes roughly a second, so a 30-second walk takes about a quarter of an hour, plus a few minutes to prepare.

## 4. Running the tool yourself, from inside Unreal

1. In the Unreal editor, open the working level `L_Site_M4` (it opens with the project) and wait five minutes after opening it before rendering.
2. Open **Window > Output Log**, switch the input box at the bottom from "Cmd" to "Python", and type these three lines, one at a time:

```
import sys; sys.path.insert(0, r"E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\tools")
import wieland_paths as wp
wp.render_requested()
```

3. It answers at once with the paths it has queued, and works through them on its own while the editor runs. To see how far it has got, type `wp.status()`. Leave the editor open until `last_render.json` is written.

Notes: the tool refuses to render if the console setting `r.RayTracing.Nanite.Mode` is not 0 (Nanite ray tracing hung the graphics card in the past). It puts back every setting it changes for a render. It makes a new level sequence for each new version of a path, under `/Game/Wieland1529/Delivery/Paths/`, and never overwrites or deletes one.
