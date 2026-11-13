# Phase 12 results: material rebuild

Status: STARTED 2026-11-13 01:02 Central. Not finished. Read "How to resume" first.

Project: `D:\Unreal_Engine_Projects\Wieland1527 5.9\Wieland1527.uproject` (Unreal Engine 5.9).
Plan: `PLAN.md`, Phase 12 (runs after Phase 8, before Phase 9).
The owner's answers are read from `material_audit.csv` (columns `decision` and `owner_note`). This phase never writes to that file.

## How to resume

1. Read the journal below from the bottom up. A line marked PENDING was committed before its step began; if it is still PENDING the step did not finish, so check what survived (files on disk, assets in the project) before repeating it.
2. Work done on each material is recorded in `material_rebuild.csv` (one row per work-list material). A material whose row has an empty `state` has not been handled.
3. The editor is reached through the agent server with `python -B tools\ue_call.py py <script> [timeout]`. Scripts of this phase are kept in `review\phase12\scripts\`.
4. Before any heavy step read the free commit memory (`Get-CimInstance Win32_OperatingSystem`); under 30 GB free, unload and wait.
5. `r.RayTracing.Nanite.Mode` stays 0 except during one path-traced render; read it back after every render.
6. Never save `/Game/Wieland/R15_Landscape/L_R15_Production`, never use "Save All", never edit an asset Datasmith created.
7. Read `decision` and `owner_note` again before each material and before the last step.

## Checks made before work (2026-11-13 00:59 Central)

| Check | Reading |
|---|---|
| Editor | process 25884, started 00:24:26, agent server answers |
| Open world | `/Game/Wieland1529/L_Site_M4` with its 12 levels |
| Unsaved packages | none |
| `r.RayTracing.Nanite.Mode` | 0 |
| Free commit memory | 37.9 of 79.1 GB; the editor holds 19.4 GB |
| Working copy | branch `claude/1529-wieland-scene-plan-e84a03`, last commit 6765a46e (Phase 8 done) |
| Advisor tool | none in this session; closing checks are done by hand and noted for the owner |

## The work list as read at 00:55 Central

| Group | Count | What happens |
|---|---|---|
| Name contains Brizo, Hansgrohe or Kohler | 22 | researched from the manufacturer and rebuilt, whatever the decision |
| `rebuild` | 24 | rebuilt, owner's note first |
| blank | 83 | rebuilt (76 finishes); 7 are markers, not finishes, and are left as exported with the reason in their row |
| `keep` with a note asking for another finish | 1 | `Door_-_Frame`, rebuilt |
| `candidate` | 90 | the Phase 5 candidate is made active |
| `keep` | 66 | left alone (this includes `RNT_Material`, decision keep, no note) |

One instruction conflict, decided and to be reported: the kickoff says in one place that blank rows scored 3 to 5 stay the owner's and are left as exported; in another place, and in `PLAN.md` (owner, 2026-11-13), it says every blank row is rebuilt whatever its score. This phase follows `PLAN.md`: blank rows are rebuilt. Every swap can be switched back to the Revit material.

## Journal

- J1 (step 12.1) DONE 01:40: `material_rebuild.csv` has 220 rows: 122 to rebuild (22 brand names, 24 `rebuild`, 1 `keep` with a note, 75 blank), 90 `candidate` rows whose Phase 5 candidate becomes active, 8 left as exported (7 markers and `EAE_Logo`). The recipes are in `tools\phase12_recipes.py`; 55 images were made by `tools\phase12_make_textures.py` into `review\phase12\generated_textures\` (43 MB); three Poly Haven CC0 wood sets were downloaded (42 MB). Nothing in the Unreal project has changed yet.
- J2 (step 12.2) PENDING: rebuild `Cabinet_Wood_Veneer` first (import its three images, make the instance under `/Game/Wieland1529/Materials/Rebuilt/`, take its swatch picture, make its sheet and look at it) before any batch.

## Acceptance

(filled at the end)
