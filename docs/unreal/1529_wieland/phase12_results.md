# Phase 12 results: material rebuild

Status: DONE 2026-11-13 03:20 Central (started 01:02). Every acceptance line below has a measured number or a workaround with its reason.

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
- J5 (step 12.6) DONE 03:17: all twelve Phase 8 views show the building, so all twelve were rendered again in both ways, 3840 by 2160. Real-time (02:03 to 02:10, 5 to 35 s each) at the project's saved settings, which since Phase 8 include Lumen's hit lighting. Path-traced ground truth (02:11 to 03:16), one view at a time, 1,024 samples: D5 222 s first and alone as a trial, then D1 171 s, D2 499 s, D3 442 s, D4 1,396 s, S1 227 s, S2 128 s, S3 137 s, S4 103 s, S5 92 s, S6 133 s, S9 144 s (`review\phase12\ground_truth\driver.log`, `runs.jsonl`). The level had been open for over an hour before the first picture. `r.RayTracing.Nanite.Mode` was 2 only inside each path-traced render and read 0 after each of the twelve (and 10,000 for `r.RayTracing.Nanite.MaxAppendInstances`); it reads 0 now. No crash and no hang. Memory log `profiles\2026-11-13_phase12\memory_log_phase12.csv`: 807 lines, one every 5 s, from 02:11 to 03:19; lowest free commit 26.3 GB, highest editor commit 30.5 GB; before five of the pictures the driver waited 30 to 90 s because free commit read 27 to 29 GB, under the 30 GB rule, and started once it was back above. The comparison (`review\phase12\compare\compare.csv`, twelve sheets beside it) is in the Acceptance section: 8 of 12 views pass, against 9 of 12 in Phase 8. The temporary camera of each picture left the top level `/Game/Wieland1529/L_Site_M4` marked unsaved; with the camera gone it was saved by name, and the editor reports no unsaved package. The owner's two columns were read again at 03:17: no answer has changed since the materials were handled, so nothing is redone.

## Acceptance

Measured on 2026-11-13 between 01:02 and 03:20 Central. "J" numbers are the journal's lines above.

| Acceptance line of the plan | Result | Number or workaround | Where |
|---|---|---|---|
| Every work-list material has a row in `material_rebuild.csv` with what the finish rests on, its source and licence, its field size and its step 5.8 test results | Met | 220 rows: 122 rebuilt, 90 whose Phase 5 candidate was made active, 8 left as exported with the reason (7 markers that are not finishes, and `EAE_Logo`). Of the 122 rebuilt rows, 122 have what the finish rests on, 122 a source and licence, 122 a field size, 122 a tiling result and 122 a grazing-light result. The 90 candidate rows carry their Phase 5 test result. | J1, J3; `material_rebuild.csv` |
| Every row passes or names why it cannot | Met, with one named failure and one judgement | 121 of 122 rebuilt materials pass. `Larvikite_Stack_192_8_x_145_2_inches__M2MLUQ_` does not: large-scale unevenness 0.061 against 0.05, on a surface 2.3 fields wide; its image is the Revit export's own and is the only evidence of this stone. Eight materials with smooth finishes (sealed veneer, smooth-cut limestone) fall under the grazing-light detail figure of 0.010 because the real finish is smooth; they are counted as passing with that reason in their row, a judgement for the owner to confirm. Of the 90 candidates, 82 passed their Phase 5 test and 8 did not; those 8 are active because the owner chose "candidate", and their rows say so. | J3; `review\phase12\tests.json` |
| Each rebuilt material scores 4 or 5 on the Phase 5 confidence scale with the reason, or says what evidence is missing | Met in part, each gap named | 108 of 122 score 4 with the reason. 14 score 3 and name the missing evidence: `Alminium_White`, `Cedar`, `Plumbing_-_Brizo_-_Pipes`, `Aluminium_Chalk__721`, `G_5051_SCVi_ADA_Panel_Finish`, `Hot_Tub`, `Steel_ASTM_A992`, `Talis_N_Faucet_Finish`, `ViewRail_-_Wood_-_Birch`, `ARCAT_-_Wood_-_Douglas_Fir`, `Aluminium_-_black`, `EPP_White_Plastic`, `Metal_-_Brizo_-_Internal_Pipe`, `white_plastic`. None scores 5: no finish was checked against a physical sample or a measured colour. 22 rows rest partly on an assumption, written in the column `assumption` and on the material's sheet. | `material_rebuild.csv`, columns `confidence`, `confidence_reason`, `assumption` |
| No Datasmith asset changed | Met | 0. Of the 197 files in the project's Content folder changed since 00:59, none lies under a Datasmith folder: 122 rebuilt instances, 65 images, 3 parents, 1 variant list, the 5 building levels (which hold the overrides) and the top level `L_Site_M4`. `L_R15_Production` was not saved; "Save All" was not used. | J4, J5 |
| Every swap can be switched back | Met | 3,176 of 3,176 surfaces on 1,539 objects. The option "Revit as exported" of `LVS_W1529_Phase12_Materials` put the Revit material back on 3,176 surfaces, and "Phase 12 active" put the active material on 3,176; tested both ways. The same list is in `review\phase12\applied_slots.csv`. | J4 |
| Phase 8 real-time tolerance re-measured at every re-rendered view | Measured at 12 of 12 views; 8 pass, 4 do not | See the table below. | J5; `review\phase12\compare\compare.csv` |
| Done means: a new swatch sheet for every rebuilt material, Revit beside rebuilt | Met | 122 sheets in `review\phase12\swatches\sheets\`, and 9 overview pages in `review\phase12\swatches\contact\`. | J3 |

### Real-time against ground truth, after the rebuild

The limits are those of Phase 8: the mean brightness of facade and ground within 10 percent, and no region larger than 2 percent of the frame off by more than one stop (a factor of two). "Phase 8" is the saved state of that phase (`review\phase8\compare\compare_hit1.csv`).

| View | Phase 8 mean difference | Phase 8 largest region | Phase 8 | Now mean difference | Now largest region | Now | Cause where it fails |
|---|---|---|---|---|---|---|---|
| S1 | -1.9 % | 1.14 % | pass | 0.0 % | 0.23 % | pass | |
| S2 | 2.0 % | 0.15 % | pass | 1.9 % | 0.10 % | pass | |
| S3 | -1.0 % | 0.35 % | pass | 0.3 % | 0.27 % | pass | |
| S4 | 2.2 % | 0.06 % | pass | 2.8 % | 0.06 % | pass | |
| S5 | -2.9 % | 1.16 % | pass | -4.2 % | 0.27 % | pass | |
| S6 | -0.1 % | 0.37 % | pass | 0.5 % | 0.27 % | pass | |
| S9 | 31.3 % | 2.06 % | fail | 26.3 % | 2.06 % | fail | As in Phase 8: two regions at the top of the frame, 4.2 and 3.8 stops brighter in real time. Not a material of this phase. |
| D1 | -7.9 % | 0.52 % | pass | -4.9 % | 0.58 % | pass | |
| D2 | 19.9 % | 2.31 % | fail | 2.4 % | 0.35 % | pass | Now passes: the rebuilt floor, cabinet veneer and worktop are close in the two pictures. |
| D3 | 27.7 % | 2.80 % | fail | 29.0 % | 4.32 % | fail | As in Phase 8, the glass shade of the pendant lamp is about 2 stops brighter in real time (3.3 percent of the frame). New: the cabinet fronts at the bottom right are 1.1 stops brighter (4.3 percent). The real-time renderer lights see-through glass more brightly than the path tracer does, and gives the room more bounced light. |
| D4 | 3.2 % | 0.19 % | pass | -30.8 % | 6.08 % | fail | New failure. The bathroom is lit by one wall lamp. Its shade is now `Kohler-Frosted_Glass` on the Diffuser parent, and the walls and bath are now white finishes. The path tracer lets the lamp's light through the shade and bounces it many times between the white surfaces, so its picture became brighter; the real-time picture stayed about as it was. The top left of the frame (6.1 percent) is 1.2 stops darker in real time. The cause is stated from the two pictures; it was not isolated by a trial. |
| D5 | -9.9 % | 0.15 % | pass | -11.4 % | 0.15 % | fail | Fails the mean by 1.4 points; no region is off. The rebuilt pergola wood and deck are darker than the Revit colours, and the real-time picture is darker than the ground truth in the pergola's shade, as it was in Phase 8. |

The lights were not changed in this phase (they are Phase 8's work), so the three failures that involve this phase's materials (D3 in part, D4, D5) are left as measured for the owner and for Phase 9.

### What this phase leaves behind

- `material_rebuild.csv` (220 rows).
- In the Unreal project: 122 rebuilt instances under `/Game/Wieland1529/Materials/Rebuilt/`; 3 new parents under `/Game/Wieland1529/Materials/Parents/` (`M_W1529_Emissive`, `M_W1529_StoneBlend`, `M_W1529_Diffuser`); 65 images under `/Game/Wieland1529/Materials/Textures/` (one of them, `T_W1529_P12_OakVeneer02_C`, is no longer used and was left because this phase deletes nothing); the Variant Manager list `/Game/Wieland1529/Materials/Variants/LVS_W1529_Phase12_Materials`; overrides on 3,176 surfaces saved in the five building levels `L_W1529_Shell`, `L_W1529_NorthTriplex`, `L_W1529_NorthPenthouse`, `L_W1529_SouthTriplex`, `L_W1529_SouthPenthouse`; the top level `L_Site_M4` saved once after the renders.
- New ground truth and real-time pictures of the twelve views in `review\phase12\ground_truth\` and `review\phase12\realtime\` (the 4K pictures stay on disk and are not committed), and the comparison with its twelve sheets in `review\phase12\compare\`.
- Console settings: none is left changed. `r.RayTracing.Nanite.Mode` reads 0 and `r.RayTracing.Nanite.MaxAppendInstances` reads 10,000.

### For the owner

1. Instruction conflict: one place of the kickoff says blank rows scored 3 to 5 stay yours and are left as exported; the plan and another place say every blank row is rebuilt. This phase followed the plan and rebuilt the 75 blank finishes. Each can be switched back.
2. The 22 finishes that rest partly on an assumption, and the 14 that score 3, are listed above and in `material_rebuild.csv`; each sheet carries the label.
3. The eight smooth finishes counted as passing the grazing-light test by judgement, and the one named failure (`Larvikite_Stack...`).
4. D4, D5 and part of D3 now fail the real-time tolerance because of this phase's materials (table above). Bringing the real-time picture closer is a lighting matter.
5. `Kohler-Frosted_Glass` lets 60 percent of the light through; this is a typical figure for frosted glass, not one published by Kohler.
6. kohler.com and hansgrohe.com refused a script (error 403); the Kohler finishes rest on Kohler's specification sheets (techcomm.kohler.com) and the Hansgrohe finishes on Hansgrohe's finish brochure and on dealers' pages, as listed in the column `sources_read`.
7. Surfaces that give off light show white on the swatch stage, whose exposure is fixed for unlit finishes; judge them in the scene pictures. `XAL_DIFFUSE` has no luminance value in the Revit family.
8. `EAE_Logo` is left as exported (99 percent clear); supply the artwork if it is to show.
9. Three parents were added as copies of the Phase 5 Opaque parent. If the Opaque parent is changed later, the three copies do not follow.
10. `r.RayTracing.Nanite.Mode` 2 was used only inside the path-traced renders, as in Phase 8; it is not adopted for real time and remains reported as unstable in 5.9.
11. No advisor tool exists in this session; the closing check of the changes against the scope was done by hand.
