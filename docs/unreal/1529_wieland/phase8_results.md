# Phase 8 results: lighting and atmosphere

Status: STARTED at 16:38 on 2026-11-12. Unattended run; the owner is away. Nothing is pushed.

This file is the journal of the phase. A line marked PENDING is written and committed before
its step starts; the line is replaced by the outcome when the step ends.

Words used the same way throughout this file:

- "Level" is Unreal's word for one saved scene file. The building, the surroundings, each
  interior group and (new in this phase) each lighting condition are separate levels that are
  loaded together by a "top level".
- "Datasmith" is the Revit-to-Unreal importer. Everything it created is replaced at the next
  reimport, so nothing it created is ever edited here; changes are overrides, new assets or
  recorded swaps.
- "Photometric file" is the file a lighting manufacturer publishes for a fixture (file
  ending `.ies`). It records how much light the fixture sends in each direction.
- "Lumen" written in lower case (lm) is the unit of light output of a lamp. "Lumen" with a
  capital L is the name of Unreal's real-time method for bounced light. The two are not
  related.
- "Path-traced" names the slow, physically exact way of rendering, used here as the ground
  truth. "Real-time" names the fast way the walk-through uses.
- "Exposure" is the camera setting that decides how bright the picture is for a given amount
  of light, written as an EV number (exposure value); one EV step up halves the brightness
  ("one stop").

## How to resume

1. Read the journal table below from the bottom up. The last line that is not PENDING is the
   last step known to be finished. A PENDING line means the step was started and its result
   is unknown: inspect what exists (assets under `/Game/Wieland1529/Lighting/`, files in
   `review\phase8\`, rows in `fixture_table.csv` and `asset_downloads.csv`) before repeating
   anything.
2. Editor: project `D:\Unreal_Engine_Projects\Wieland1527 5.9\Wieland1527.uproject`, top level
   `/Game/Wieland1529/L_Site_M4` (11 levels before this phase). Never save
   `/Game/Wieland/R15_Landscape/L_R15_Production`, never use "Save All", save named assets
   only.
3. Calls go through `tools\ue_call.py` (`python -B ue_call.py py <script file>`). A script
   returns the value of its last expression; `print` goes to the editor's log, not to the
   caller. In the editor's Python, add the tools folder to `sys.path`:
   `E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools`
   and set `sys.dont_write_bytecode = True`.
4. Before any heavy step read free commit memory; under 30 GB, unload and wait.
5. Commit by explicit path on branch `claude/1529-wieland-scene-plan-e84a03`. Do not push.

## Checks made before any work (2026-11-12, 16:35 to 16:38)

| Check | Result |
|---|---|
| Editor process | 8960, started 14:26, answers the agent server, holds 20.2 GB of commit |
| Free commit memory | 30.3 GB of 79.1 GB (just above the 30 GB floor); free physical 12.4 GB |
| Open level | `/Game/Wieland1529/L_Site_M4` with 11 levels, engine 5.9.0 |
| `r.Material.UseShaderCompilationParameters` | 0, as required |
| `r.RayTracing.Nanite.Mode` | 0 (project setting; not changed) |
| `r.Lumen.WorldCache.Supported` | false |
| Unsaved packages | none |
| Plan working copy | branch `claude/1529-wieland-scene-plan-e84a03`, head `0d127a18`; only review pictures untracked |
| `phase8_results.md` | did not exist: this is a fresh start, not a resume |
| Advisor tool | not present in this session; the advisor checkpoints of the owner's global rules cannot be made and are replaced by my own written checks, as in earlier phases |

## Journal

| No. | Time | What is done | Outcome |
|---|---|---|---|
| J1 | 16:38 | Read-only inventory of what the lighting has to start from: which level holds the placeholder sun and sky, and every light, sky, fog, cloud and exposure object in the loaded levels; the state of the 571 imported lights (on or off, units, photometric file); which photometric files came in with the Revit import; the exposure settings in force. Nothing is changed or saved. | PENDING |
