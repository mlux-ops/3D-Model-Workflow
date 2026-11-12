# Phase 6 results: interiors

Status: IN PROGRESS. Started 2026-11-11 22:09. This file is the journal of the phase. A line
marked PENDING is written and committed before its step starts; the line is replaced by the
outcome when the step ends.

Words used the same way throughout this file:

- "Level" is Unreal's word for one saved scene file. The building, the surroundings and each
  interior group are separate levels that are loaded together.
- "Datasmith" is the Revit-to-Unreal importer. Everything it created is replaced at the next
  reimport, so nothing it created is ever edited here; changes are overrides, new assets or
  recorded swaps.
- "Stand-in" is a labelled grey block of the proposed size, in the place where an item that
  still waits for the owner's approval will go.

## How to resume

1. Read the journal table below from the bottom up. The last line that is not PENDING is the
   last step known to be finished. A PENDING line means the step was started and its result
   is unknown: inspect what exists (assets under `/Game/Wieland1529/Interiors/`, files in
   `review\phase6\`, rows in the CSV files) before repeating anything.
2. Editor: project `D:\Unreal_Engine_Projects\Wieland1527 5.9\Wieland1527.uproject`, level
   `/Game/Wieland1529/L_Site_M2` (loads `L_Surroundings` and `L_Building`). Never save
   `/Game/Wieland/R15_Landscape/L_R15_Production`, never use "Save All", save named assets
   only.
3. In the editor's Python, add the tools folder to `sys.path`:
   `E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools`
   and set `sys.dont_write_bytecode = True`.
4. Before any heavy step read free commit memory; under 30 GB, unload and wait.
5. Commit by explicit path on branch `claude/1529-wieland-scene-plan-e84a03`. Do not push.

## Checks made before any work (2026-11-11, 22:09 to 22:12)

| Check | Result |
|---|---|
| Editor process | 4680, started 19:52, answers the agent server, holds 18 GB of commit |
| Free commit memory | 34.2 GB of 79.1 GB (above the 30 GB floor); free physical 9.8 GB |
| Open level | `/Game/Wieland1529/L_Site_M2` with `L_Surroundings` and `L_Building`; 2,770 objects |
| `r.Material.UseShaderCompilationParameters` | 0, as required |
| Unsaved packages | only `/Game/Wieland1529/Scratch/M_Probe5`, left from before; not touched |
| Phase 5 alternatives | off (0 slots switched); Revit materials are the active default |
| Plan working copy | branch `claude/1529-wieland-scene-plan-e84a03`, head `5e4e5306`, clean |
| Advisor tool | not present in this session; the three advisor checkpoints of the owner's global rules cannot be made and are replaced by my own written checks, as in Phases 4 and 5 |

## Journal

| No. | Time | What is done | Outcome |
|---|---|---|---|
| J1 | 22:13 | Step 6.1: count what the Revit export holds per unit and room, set provisional D1 to D5 cameras, take grey renders, list room by room what the geometry lacks at camera distance | PENDING |

## Acceptance lines

Filled in as the steps finish.

## Files written

Filled in as the steps finish.
