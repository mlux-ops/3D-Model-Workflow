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

- J1 (step 12.1) DONE 01:30: `material_rebuild.csv` has 220 rows: 122 to rebuild (22 brand names, 24 `rebuild`, 1 `keep` with a note, 75 blank), 90 `candidate` rows whose Phase 5 candidate becomes active, 8 left as exported (7 markers and `EAE_Logo`). The recipes are in `tools\phase12_recipes.py`; 55 images were made by `tools\phase12_make_textures.py` into `review\phase12\generated_textures\` (43 MB); three Poly Haven CC0 wood sets were downloaded (42 MB). Nothing in the Unreal project has changed yet.
- J2 (step 12.2) DONE 01:36: `Cabinet_Wood_Veneer` was rebuilt first and its sheet looked at (`review\phase12\swatches\sheets\Cabinet_Wood_Veneer.jpg`). Two faults were found and fixed on this one material before any batch: the oak image's grain was too faint to read on a wall (a copy with the grain 2.5 times stronger is now used), and the recipe file gave the editor paths relative to this folder, which the editor could not find (paths are now absolute). The sheet now shows a pale oak with fine straight grain and no visible repeat. Saved in the project by name: three images `T_W1529_P12_OakVeneer02_Strong_C`, `_N`, `_R`, one image no longer used (`T_W1529_P12_OakVeneer02_C`, left in place because this phase deletes nothing), and the instance `MI_W1529_R_Cabinet_Wood_Veneer`. No level has changed.
- J3 (steps 12.2, 12.3 and 12.5) DONE 01:56: batch. Three parents were added under the Parents folder, each a copy of the Phase 5 Opaque parent with one more block: `M_W1529_Emissive` (a surface that gives off light), `M_W1529_StoneBlend` (large zones of colour over a stone) and `M_W1529_Diffuser` (a thin sheet that scatters the light it lets through). 61 images were imported (0 failed; 64 with the 3 of J2). All 122 instances exist under `/Game/Wieland1529/Materials/Rebuilt/`; the check of each saved instance against its recipe found 0 differences. 122 swatch pictures and 122 sheets were made (`review\phase12\swatches\rebuilt\`, `review\phase12\swatches\sheets\`), and all were looked at on 9 overview pages (`review\phase12\swatches\contact\`). One material read wrong and was changed: `Kohler-Frosted_Glass` on the Glass parent looked like dark clear glass, so it now uses the Diffuser parent and reads as a white frosted shade. Brushed brass, nickel and stainless show their scratches and a highlight stretched across them under grazing light; polished chrome and gold read as mirrors. The step 5.8 tests (`review\phase12\tests.json`, merged into `material_rebuild.csv`): 121 of 122 pass. The one that does not is `Larvikite_Stack_192_8_x_145_2_inches__M2MLUQ_`: its image is the Revit export's own sheet of tiles, 4.88 m wide, with a large-scale unevenness of 0.061 against a limit of 0.05, and the largest surface is 2.3 fields wide, so a repeat can in principle be recognised; the image is kept because it is the only evidence of this stone. Eight materials with smooth finishes (sealed veneer and smooth-cut limestone, four relief images) fall below the grazing-light detail figure of 0.010 because the real finish is smooth; they are counted as passing with that reason written in their row, and this is a judgement of this phase for the owner to confirm. Measured relief of sculpted tile: Kit Kat 1.8 mm, Larvikite stack 3.4 mm (`review\phase12\relief.json`). The swatch job left the instances marked unsaved; 120 were saved again by name, and the editor now reports no unsaved package. Nothing is applied to the building yet.
- J4 (step 12.4) DONE 02:00: the owner's two columns were read again first (candidate 94, blank 90, rebuild 29, keep 7; no row changed its group). In `/Game/Wieland1529/L_Site_M4` an override (a material set on a placed object, which leaves the asset itself untouched) now shows the active material on 3,176 surfaces of 1,539 objects: Shell 535, NorthTriplex 920, NorthPenthouse 521, SouthTriplex 870, SouthPenthouse 330. All 212 materials (122 rebuilt, 90 Phase 5 candidates) are on at least one surface. 2,771 surfaces whose material is not on the work list were not touched, and no surface carried an override from another source. Every override is listed in `review\phase12\applied_slots.csv` (3,176 rows). The five building levels were saved by name; the editor reports no unsaved package; 0 Datasmith assets were changed. The Variant Manager list (a saved list of switchable states) `/Game/Wieland1529/Materials/Variants/LVS_W1529_Phase12_Materials` holds the two options "Revit as exported" and "Phase 12 active" for all 3,176 surfaces. The switch was tested both ways: "Revit as exported" put the Revit material on 3,176 of 3,176 surfaces, "Phase 12 active" put the active material back on 3,176 of 3,176. One fault was found and fixed: the first build of the list missed 9 surfaces (7 of `Metal_-_Acristalia_-_Inox`, 2 of `Wood`) on railing objects, because the engine lists the main part of an object without its name; `tools\wieland_rebuild.py` now finds that part by its place in the list. The project is left in the "Phase 12 active" state. A rule for later work: after switching to "Revit as exported", switch back to "Phase 12 active" before running `wr.sync` again. `r.RayTracing.Nanite.Mode` reads 0.
- J5 (step 12.6) PENDING: render again the Phase 8 pictures of every view that shows a changed material (all twelve views S1 to S6, S9, D1 to D5 show the building, so all twelve). First the real-time pictures (`review\phase12\scripts\realtime_one.py`, job in `review\phase12\realtime\job.json`), then the path-traced ground truth one view at a time (`review\phase12\scripts\truth_one.py`, job in `review\phase12\ground_truth\job.json`, 1,024 samples as in Phase 8) with the memory log running (`tools\memory_log.ps1`), reading `r.RayTracing.Nanite.Mode` back as 0 after each picture. Then `tools\compare_tiers.py review/phase12/ground_truth review/phase12/realtime review/phase12/compare` and the numbers set beside Phase 8's `review\phase8\compare\compare_hit1.csv`. If this step stopped half-way: the pictures already in the two folders are finished pictures (each is written at the end of its render); continue with the views that have none.

## Acceptance

(filled at the end)
