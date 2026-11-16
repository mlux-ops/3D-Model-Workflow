Phase 14 (sun-path timelapse videos from the two decks) of the 1529 N. Wieland scene plan, unattended, quick

What this session is for

The owner wants four short timelapse videos, made now, quickly. Picture quality is not important; getting the sun and shadows right is. You are working in the Unreal Engine 5.9 project `D:\Unreal_Engine_Projects\Wieland1527 5.9\Wieland1527.uproject` through the editor's agent server (unreal-mcp). The plan folder is `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\`. You have no memory of earlier sessions. Nobody will answer questions; decide and keep going. Keep it short: aim to finish within about an hour, and do not research, redesign or polish.

The four videos

| File | Deck | Day |
|---|---|---|
| `timelapse_roofdeck_summer.mp4` | The penthouse roof deck (design view D1's deck) | 21 June, sunrise to sunset |
| `timelapse_roofdeck_winter.mp4` | The penthouse roof deck | 21 December, sunrise to sunset |
| `timelapse_reardeck_summer.mp4` | The lower outdoor deck at the rear of the building | 21 June, sunrise to sunset |
| `timelapse_reardeck_winter.mp4` | The lower outdoor deck at the rear | 21 December, sunrise to sunset |

- Each is 10 seconds long, 1920 by 1080, 24 frames a second (240 frames), H.264 MP4, in `review\phase14\` in the plan folder.
- One fixed camera per deck, the same for summer and winter, at standing eye height (1.6 m), wide (about 100 degrees across), placed so the deck floor, its railings or walls, and as much of the southern sky as possible are in view, so the sun's arc and the moving shadows on the deck can both be seen. Find the rear deck from the building levels (it is outdoors, at the rear, on a lower floor); D1's camera in `REFERENCE_VIEWS.md` shows where the roof deck is.
- The sun moves evenly from sunrise to sunset, using the project's sun (the Sun Position settings from Phase 8: latitude 41.910215, longitude -87.635389, the correct time zone and daylight-saving time for each date, the north offset already set). Read the sunrise and sunset times from the Sun Position calculation for each date and record them.
- Burn a small caption into a corner of every frame: the deck, the date, the clock time, and "proposed hotel shown".
- Scene state: the default site as it now stands, including the proposed hotel at 1520-1528 N. Wells (Variant Manager list `Neighbour development`, option "Duke of Wells (proposed)"), because its shadow matters here. Real-time rendering, not path tracing.
- Brightness: the project uses fixed exposure for daylight, which makes dawn and dusk nearly black. For these videos only, let exposure follow the light (automatic exposure, or exposure stepped with the sun's height) so every frame is readable, and say so in the notes. Put it back afterwards.

How (keep it simple)

- Step the sun's time in Python, let each frame settle a few ticks (Lumen needs a moment after the sun moves), and take a high-resolution screenshot or a Movie Render Graph real-time frame; then join the frames into MP4 with whatever is already available (the Python packages in `E:\Wieland1529_site_data\_python_packages\`, OpenCV or imageio if present, or ffmpeg if installed). Do not install software; if nothing can write MP4, write an animated sequence of PNG frames plus the same frames as an AVI or a GIF and say so.
- Make one video first and look at a few of its frames before making the other three.
- Delete nothing; leave intermediate frames in `review\phase14\frames\` (they are not committed).

Rules

- Nanite ray tracing stays OFF: keep the console variable r.RayTracing.Nanite.Mode at 0; it has hung the graphics card three times.
- Never save `/Game/Wieland/R15_Landscape/L_R15_Production`, never use "Save All", and do not save any level for this job: everything you change (sun time, exposure, camera) is temporary. Put the sun back to the plan's review condition (15 August, 15:30 daylight time) and the exposure back to fixed when you finish, and read both back to confirm.
- Memory: read free commit memory before starting; if it is under 30 GB, close and reopen the editor first (nothing unsaved matters).
- Another job (Phase 13, the proposed hotel's checks) is paused and resumes after you. Do not touch `phase13_results.md` or `phase11_results.md`.

Done means

- The four MP4 files exist in `review\phase14\` and play; a short `phase14_results.md` in the plan folder gives the camera positions, the sunrise and sunset times used for each date, the exposure method, what the videos show (for example when the rear deck goes into the hotel's shadow), and the full path of every file. Its first line reads `Status: DONE` with the time.
- Any error is logged in `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\PROJECT_MEMORY.md` with cause, fix and status.
- Commit `phase14_results.md`, the four MP4 files and any script you wrote, by explicit path, on the current branch. Do not push. Then stop.

Write for the owner in plain words: they know Revit and construction well and Unreal less well.
