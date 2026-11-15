# Phase 19 results: the owner's walking paths, from drawn path to video

Companion to [PLAN.md](PLAN.md), section "Phases 18 and 19", and to `KICKOFF_PHASE19.md`. Written as each step finishes, so a new session can resume from it.

Status: IN PROGRESS (started 20:16 Central on 2026-11-14, editor panel session, Opus).

## Words used here

- **Path**: a walk the owner draws on a plan image on the path page (`owner_review\paths\index.html`, served at http://127.0.0.1:8766/), saved as `owner_review\paths\<name>.json`.
- **Plan image**: a top view of the site or of one floor, with an exact rule that turns a pixel into a position in the level (`owner_review\paths\plans\manifest.json`).
- **Level sequence**: Unreal's saved camera move with a time line; the tool makes one per path version. **Movie Render Graph**: Unreal's tool that renders a level sequence to picture files.
- **Real time**: the renderer the walk-through uses (Lumen). **Path traced**: the slow, physically exact renderer.
- **Line-of-sight check**: a test, before rendering, that the camera's walk does not pass through a wall, floor or other solid object.

## How to resume, if this chat ends

1. Read the journal below from the bottom up; a PENDING line marks the step that was running.
2. The tool is `tools\wieland_paths.py`; `RENDER_HOW.md` in `owner_review\paths\` says how to run it. Frames go to `D:\Wieland1529_delivery\video_paths_frames\<name>_<checksum>\`, videos to `delivery\video_paths\`.
3. Never save `L_R15_Production`, never "Save All", keep `r.RayTracing.Nanite.Mode` at 0 (the tool refuses to render otherwise), keep the ground object's shadow off, and set `MSYS_NO_PATHCONV=1` when passing `/Game/...` paths from Git Bash.

## Journal

| No. | Time | What is done | Outcome |
|---|---|---|---|
| J1 | 20:16 | Checks before work, read-only: saved paths in `owner_review\paths\`, the page, the editor's state, ffmpeg. | DONE 20:17. No path saved by the owner yet: `owner_review\paths\` holds only the agent's two test paths (`_test_roofdeck.json`, `_test_wall.json`, written at 20:05 for J3 and J4), so no owner video can be made in this session; the page answers at http://127.0.0.1:8766/ (code 200). Editor: `L_Site_M4` open, `r.RayTracing.Nanite.Mode` 0, the Phase 17 surroundings shown. ffmpeg 9.0.2 installed (nothing new installed). |
| J2 | 20:17 | Step 1: the site plan image made again so it shows the Phase 17 surroundings, with the same mapping (`tools\phase18_plans.make_plan("site")`, then `check_plan("site")`, the three known points); the Phase 18 images kept beside it as `site_phase18.png` and `check_site_phase18.png`. | DONE 20:17. `owner_review\paths\plans\site.png` now shows the laser-scan buildings of Phase 17 (clean outlines, rooftop structures) where Phase 18 showed the earlier detailed massing; same window and mapping, so the manifest is unchanged. Mapping check (three temporary marker cubes, removed again): lot corner SW 0.30 px, lot corner NE 0.33 px, rear yard stair centre about 0.3 px, against the 3 px limit; `check_site.png` made again. The eight floor plans are unchanged by Phase 17 (the building itself did not change), so their Phase 18 checks stand: every point within 0.41 px (`phase18_results.md`). |
| J3 | 20:18 | Step 2: the path tool `tools\wieland_paths.py` (smooth constant-speed camera with eased starts, stops and pauses; look modes; line-of-sight check; level sequence; Movie Render Graph; ffmpeg; `render_requested()`). Planned outside the editor on the test path, then the line-of-sight check run in the editor on the test path (must pass) and on `_test_wall.json` (straight north from the penthouse living room through the party wall; must be refused with its place). | DONE 20:24. Planned (outside the editor and again inside): `_test_roofdeck` 10.54 m in 15.2 s, 456 frames at 30 a second, 3.33 cm a frame at walking speed and at most 3.35 cm (eased starts, stops and the 1 s pause make no jump), turns at most 1.6 degrees a frame (the closing turn towards downtown). Line of sight: `_test_roofdeck` clear. `_test_wall` refused: the first try, on the line y = -840 cm, met a kitchen cabinet panel at x -1323 cm before the wall (a correct refusal, since furniture taller than 0.5 m is solid); moved to y = -1000 cm it is refused at the north exterior wall, "segment 1 (point 1 to 2) passes through Walls_Basic_Wall_B2010_Exterior_Wall_Havord_block_w__1_GYP_12 at x -1386, y -1000, z 1339 cm". A probe of nine parallel lines found the same wall, a single-hung window and a pendant lamp as solid, as they should be. The trace's hit data (actor at index 9 of the hit record) was read back to confirm the tool reads the right fields. |
| J4 | 20:24 | Step 3: render the test path with `wieland_paths.render_requested(include_test=True)` (the same call the owner's requests use): `_test_wall` must be refused and listed in `last_render.json`; `_test_roofdeck` rendered in real time at 1,920 by 1,080, 30 frames a second, one run with 256 warm-up frames, encoded to `delivery\video_paths\_test_roofdeck.mp4`; then the video looked at. | PENDING |
