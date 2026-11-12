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

Filled in by J1.

## Journal

| No. | Time | What is done | Outcome |
|---|---|---|---|
| J1 | 09:20 on 2026-11-12 | Checks before any work (editor, free commit memory, open level, unsaved packages, the engine setting `r.Material.UseShaderCompilationParameters`), then a read-only inspection for step 7.0: the 58 parts, the two planting holders and their positions in the earlier production level (read through `L_Site_M1`, which shows that level by reference; the earlier production level itself is not opened for change), what `L_Site_M2` and `L_Surroundings` hold now, and which vegetation assets in the project have a licence line in `asset_licences.csv`. Nothing is changed or saved. | PENDING |

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
