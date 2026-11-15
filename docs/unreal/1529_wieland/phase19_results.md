# Phase 19 results: the owner's walking paths, from drawn path to video

Companion to [PLAN.md](PLAN.md), section "Phases 18 and 19", and to `KICKOFF_PHASE19.md`. Written as each step finishes, so a new session can resume from it.

Status: IN PROGRESS (started 20:21 Central on 2026-11-14, editor panel session, Opus).

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
| J1 | 20:21 | Checks before work, read-only: saved paths in `owner_review\paths\`, the page, the editor's state, ffmpeg. | PENDING |
