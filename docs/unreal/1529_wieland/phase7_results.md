# Phase 7 results: site, surroundings and vegetation

Status: STARTED at 09:15 on 2026-11-12, unattended, in a headless session against the editor
started at 09:13. Scope by the owner's instruction of 2026-11-12: the site model and its
surroundings only (neighbouring buildings, the site's ground and street, vegetation). The
interiors, the house's own materials, lighting proper (Phase 8), optimisation and delivery are
not touched.

This file is the journal of the phase. A line marked PENDING is written and committed before
its step starts; the line is replaced by the outcome when the step ends.

Words used the same way throughout this file:

- "Level" is Unreal's word for one saved scene file. The building, the surroundings and the
  vegetation are separate levels that are loaded together by a top level (`L_Site_M2`).
- "Object" is one placed thing in a level (Unreal calls it an actor). "Mesh" is the stored
  shape an object shows. "Material" is the surface finish on a mesh; a mesh has one "slot" for
  each material it carries.
- "Earlier production level" is `/Game/Wieland/R15_Landscape/L_R15_Production`, the site model
  of October 2026. It is only read here and is never saved.
- "Earlier detailed buildings" are the 58 merged parts of that level. "Phase 4 survey massing"
  is the set of plain blocks that Phase 4 built from the 2022 laser scan and county outlines.
- "Variant Manager" is the engine's tool that holds lists of named options; choosing one option
  changes a set of objects in one action.
- "Datasmith" is the Revit-to-Unreal importer. Nothing it created is edited here.
- "Stand-in" is a labelled placeholder (tag `W1529.Placeholder`) where evidence or the owner's
  approval is still missing.

## How to resume

1. Read the journal table below from the bottom up. The last line that is not PENDING is the
   last step known to be finished. A PENDING line means the step was started and its result is
   unknown: inspect what exists (levels and assets under `/Game/Wieland1529/Surroundings/` and
   `/Game/Wieland1529/Vegetation/`, files in `review\phase7\`, the CSV files named in the line)
   before repeating anything.
2. Editor: project `D:\Unreal_Engine_Projects\Wieland1527 5.9\Wieland1527.uproject`, top level
   `/Game/Wieland1529/L_Site_M2`. Never save
   `/Game/Wieland/R15_Landscape/L_R15_Production`, never use "Save All", save named assets
   only, never edit a Datasmith asset.
3. This session had no direct connection to the editor's agent server (the terminal's own
   connection failed at start because the editor was still loading). It talks to the server
   with `tools\ue_call.py` (`python -B ue_call.py py <script file>`), which sends a Python
   script to the editor. The Phase 7 editor code is `tools\wieland_site.py`; in the editor's
   Python the tools folder is put on `sys.path` and `sys.dont_write_bytecode = True` is set.
4. Before any heavy step read free commit memory; under 30 GB, unload and wait. The editor's
   memory is logged to `review\phase7\memory_log.csv` during heavy steps.
5. Commit by explicit path on branch `claude/1529-wieland-scene-plan-e84a03`. Do not push.

## Checks made before any work

Read at 09:23 to 09:25 on 2026-11-12:

- Editor: Unreal 5.9.0, process started 09:13, ready for calls at 09:22 (it spent the first nine
  minutes building the earlier level's meshes). It had opened the earlier production level on its
  own, as the project's start level. No package was marked as changed, before or after the reading.
- Free commit memory: 27.0 GB of 79.1 GB, with the editor holding 18.9 GB while the earlier
  production level and its eleven trees are loaded. That is under the 30 GB line, so the first
  act of step 7.0 is to leave that level (a new, empty level is opened), which gives its memory back.
- The engine setting `r.Material.UseShaderCompilationParameters` reads 0, as the plan requires.
- The terminal's own connection to the editor's agent server failed at 09:14 because the editor
  was still loading. The work goes through `tools\ue_call.py` instead, which speaks to the same
  server; the toolset for Python is `editor_toolset.toolsets.python_scripting.PythonScriptingTools`,
  tool `execute_python`.

## Journal

| No. | Time | What is done | Outcome |
|---|---|---|---|
| J1 | 09:20 on 2026-11-12 | Checks before any work (editor, free commit memory, open level, unsaved packages, the engine setting `r.Material.UseShaderCompilationParameters`), then a read-only inspection for step 7.0: the 58 parts, the two planting holders and their positions in the earlier production level (read through `L_Site_M1`, which shows that level by reference; the earlier production level itself is not opened for change), what `L_Site_M2` and `L_Surroundings` hold now, and which vegetation assets in the project have a licence line in `asset_licences.csv`. Nothing is changed or saved. | DONE at 09:25. Read in the earlier production level itself (the editor had it open; it was not changed and not saved), not through `L_Site_M1`. Records: `review\phase7\old_level_readback.json` (all 64 objects) and `review\phase7\old_level_trees.json`. Found: 58 parts (31 opaque, all with Nanite, which is the engine's system for very detailed meshes; 27 glass, without), every part placed at 0, 0, 0 without turn or scale, 645 material slots showing 123 materials, 13 of the slots through an override on the placed object. Shifted into the new frame the parts reach from 98 m north to 106 m south of the lot's south-west corner and from 46 m west to 137 m east. Every opaque part also carries ground (asphalt, concrete paving, turf, wood chips), merged with its buildings. The eleven trees are instanced skinned meshes of the Megaplant library (no licence record), 6 to 18 m tall; the 2,557 ground plants are Poly Haven models (grass, moss, weed, shrub) whose licence line reads NO RECORD because the grass texture's source is recorded three ways. So no vegetation asset in the project has a recorded licence: every plant placed in this phase is a stand-in and is listed for the owner. |
| J2 | 09:26 | Step 7.0, first part: a new, empty level `/Game/Wieland1529/Surroundings/L_Surroundings_R15` is made and opened (this also unloads the earlier production level, without saving it). One part is placed first (`R15_PART_opaque_xm02_yp00_part01`): same mesh, at the shift x + 15,482.32 cm, y + 5,053.7 cm, with the same materials, the object-level overrides included; it is compared with the record of J1. Then the other 57. Each copy is tagged `W1529.R15Copy`. The level is saved by name. Nothing else is saved. | DONE at 09:26. The trial part matched its record (same mesh, bounds within 0.0004 cm, 9 of 9 slots). Then all 58: 58 copies, 645 of 645 material slots show the same material as in the earlier production level, largest difference of any bounding box 0.0005 cm, shadow settings the same, no problem reported. `L_Surroundings_R15` saved by name (154,590 bytes); no package left marked as changed. The earlier production level's file still carries its date of 10 November 19:00: it was not saved. Tool: `tools\wieland_site.py` (`new_level`, `place_parts`, `verify_parts`, `save_current`). |
| J3 | 09:29 | Step 7.0, measuring before anything is hidden (read-only): for each of the 31 opaque parts and each Phase 4 object (144 buildings, 37 ground objects) the height of the top surface is read on one shared grid of 0.5 m cells, by rays cast straight down on the mesh itself. From the two height maps: which Phase 4 buildings the earlier buildings cover, footprint and roof height of each against Phase 4 and the 2022 laser scan, and how the earlier parts' own ground lies against the Phase 4 ground. Files go to `review\phase7\heights\`. Nothing is changed or saved. | PENDING |

## Acceptance lines

Filled in as the steps finish. The lines are the plan's five for Phase 7 and the owner's steps
7.0 to 7.3 and the review of the instruction of 2026-11-12.

| # | Line | Measured | Verdict |
|---|---|---|---|
| 7.0-a | New level `L_Surroundings_R15` holds placed copies of the 58 parts, same meshes, materials and positions; the earlier production level is not saved | | |
| 7.0-b | It is the default view in `L_Site_M2`; the Phase 4 buildings it overlaps are hidden; Phase 4 ground and far buildings are kept | | |
| 7.0-c | One action switches between "Earlier detailed buildings" and "Phase 4 survey massing" (Variant Manager list `Surroundings`) | | |
| 7.0-d | Footprint and height of each overlapping building, earlier against Phase 4 and the laser scan, are recorded | | |
| 7.1-a | Every Phase 4 building that the earlier level does not cover carries materials, not bare grey | | |
| 7.1-b | Audit findings fixed without a photograph: A5 (siding gaps, step texture), ML2 (brick bands on 1533), A10 (world ending; distant-city stand-in) | | |
| 7.2-a | Ground, street, kerbs, sidewalks, parkway and paving carry materials at physical scale, seamless and non-repeating under the repository's gate | | |
| 7.2-b | The Revit site slab and Revit neighbour massing are hidden in the site view by a recorded per-object override; Datasmith assets and Revit untouched | | |
| 7.3-a | Plan line 1: every surveyed tree present, trunk within 0.3 m, diameter within 2 cm, height and crown spread within 1.0 m | | |
| 7.3-b | Plan line 2: each tree's species matches the survey table; low-confidence species listed | | |
| 7.3-c | Plan line 3: leaf-off side-by-side sheets S2 to S5, trunk bases within 1.5 percent of image width | | |
| 7.3-d | Plan line 4: no plant stands where the photographs show paving | | |
| 7.3-e | Plan line 5: vegetation's cost on the exterior path is 3.0 ms or less of graphics-card time | | |
| 7.3-f | The earlier level's trees and planting are brought across where they match the 2022 aerial photograph and laser scan; each tree's position is recorded against those data | | |
| 7.3-g | `vegetation_proposal.csv` proposes species, size, source, licence, size on disk and cost; nothing acquired | | |
| R | Review sheets S1 to S9 with the earlier buildings and with the Phase 4 massing, beside the earlier production level's renders where they exist, with the "PLACEHOLDER: no photograph" panel | | |
| P | Profile M5 on the fixed camera path, with its conditions stated | | |

## What was saved or changed in the Unreal project

Filled in as the steps finish.

## For the owner

Filled in as the steps finish.

## Files written

Filled in as the steps finish.
