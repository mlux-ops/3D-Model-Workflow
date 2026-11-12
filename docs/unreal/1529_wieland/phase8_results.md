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
| J1 | 16:38 | Read-only inventory of what the lighting has to start from: which level holds the placeholder sun and sky, and every light, sky, fog, cloud and exposure object in the loaded levels; the state of the 571 imported lights (on or off, units, photometric file); which photometric files came in with the Revit import; the exposure settings in force. Nothing is changed or saved. | DONE 16:44. Read with `L_Site_M4` open (3,051 objects). **Sun and sky:** three objects, all in the top level `L_Site_M4` itself and tagged `W1529.Placeholder`: `Placeholder_Sun` (10 lux, pitch -45, yaw -135), `Placeholder_SkyAtmosphere` and `Placeholder_SkyLight` (strength 1). There is no fog, no cloud object and no post-process volume (the object that carries exposure settings), so exposure is the project default: automatic, with a +1 stop bias. **Fixture lights:** 571 light objects, all in the four unit levels made in Phase 6 (north triplex 139, north penthouse 165, south triplex 187, south penthouse 80), none in the shell level. Every one is a point light with a unit-less strength, switched off, and of the kind "static", which gives no light at all in this project (static lights only work with baked lighting, which the project does not use); each must be made "movable" when it is switched on. The unit levels are this project's own copies, not Datasmith's, so the lights in them may be set; the settings are still kept in a table and applied by tool, so that a new Revit import can be treated the same way. **Photometric files that came with the import:** 8 (for 59 of the 571 lights); 512 lights have none. **Settings in force (read only):** bounced light and reflections by Lumen with hardware ray tracing; virtual shadow maps on; `r.RayTracing.Shadows` 0; `r.MegaLights.EnableForProject` 0 but `r.MegaLights.Allowed` 1 (MegaLights is the engine's method for drawing many shadow-casting lights at a fixed cost; it can be switched on per post-process volume without touching the project settings). Script: `review\phase8\scripts\j1_inventory.py`. Nothing changed or saved. |
| J2 | 16:45 | Step 8.1, the sun. A new level `/Game/Wieland1529/Lighting/L_Light_SummerAfternoon` is made for the owner's one review condition (15 August 2026, 15:30 Central Daylight Time). It gets a plain sun light (a "directional light") whose direction is set from the Sun Position plugin's own calculation for latitude 41.910215, longitude -87.635389, turned by the street's 1.18 degrees so that it is right in this project's axes (the plugin's ready-made sun object is not used, because its year is fixed at 2019). It also gets a sky atmosphere, a sky light, fog and one post-process volume, all at provisional values that steps 8.2, 8.3 and 8.6 then set. The level is added to `L_Site_M4` as always loaded. The three placeholder objects are not deleted: they are made not visible, and that is recorded. Then the sun's bearing and height are read back from the direction of the placed light and compared with NOAA (241.67 and 46.34 degrees, measured in Phase 1). One check picture from S1. Saved by name: the new level and `L_Site_M4`. Tool: `tools\wieland_lighting.py`. | PENDING |
