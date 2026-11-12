# Phase 5 results: materials

Companion to [PLAN.md](PLAN.md). Written as each step finishes, so a new session can resume from it. Earlier records: `phase1_results.md` to `phase4_results.md`.

**Status at 20:46 Central on 2026-11-11: begun.** This phase runs unattended from a terminal against the editor started at 19:52 (process 4680). The owner is away; anything that needs the owner is collected under "For the owner to decide or supply".

**What this phase can and cannot be without the site visit.** There are no owner photographs. Steps 5.3 (surface maps from photographs) and 5.9 (renders beside photographs) cannot be done as written, and the colour acceptance line cannot be measured. By the owner's rule of 2026-11-10 the Revit materials stay as exported and stay the active default; this phase audits every one, scores it, and builds a native Unreal candidate for each material scored 3 or lower, assigned through a switchable alternative that is off by default.

## How to resume, if this chat ends

1. Read the journal below. A line that still reads PENDING marks the step that was running.
2. Check the editor: it should answer, `r.Material.UseShaderCompilationParameters` should read 0, and no package should be unsaved. Compare what is on disk under `Content\Wieland1529\Materials\` with the journal.
3. Carry on from the first PENDING or missing step. The scripts of this phase are in `tools\` (names beginning `wieland_materials` and `phase5_`); each skips what already exists.
4. Rules: never save `L_R15_Production`, never "Save All", never edit a Datasmith asset, and leave the switchable alternatives off before any level is saved.

## Checks made before any work

Made at 20:43 on 2026-11-11, read only.

| Check | Result |
|---|---|
| The editor | Answers; process 4680, started 19:52. It holds 16.6 GB of committed memory. |
| Memory | Free commit 35.7 of 79.1 GB; free physical memory 6.7 GB; video memory 7.8 of 16.4 GB in use. |
| `r.Material.UseShaderCompilationParameters` | 0 |
| The open level | `/Game/Wieland1529/L_Site_M2`, showing `L_Building` and `L_Surroundings` by reference. Nothing unsaved. |
| The plan's working copy | Clean at commit `9c982e86`, branch `claude/1529-wieland-scene-plan-e84a03`. |
| Advisor tool | Not available to this session, as in Phase 4; the closing diff is checked by the session itself. |

## Journal

Each step that changes the project or can crash the editor is written here before it is made, and committed.

| No. | Time | What is done | Outcome |
|---|---|---|---|
| L1 | 20:46 on 2026-11-11 | Read-only data gathering for step 5.0: for each of the 286 audited materials, read its parent, colours, numbers, textures (pixel size) and mapping scale from the editor into `review\phase5\material_params.json`; read the old project's parents `M_R15_World_Metric` and `M_R15_UV_Metric`. Nothing is changed or saved. | Done at 20:49. All 286 materials read (none missing): 284 are instances (materials that only set the values of a parent material) of Datasmith's one parent `RevitReference`, 2 belong to the camera marker. `tools\wieland_materials.py` holds the reader. The mapping scale that Revit exports is in repeats per foot (the block wall's 0.255 gives 1.2 m, three 400 mm blocks). The two old parents each take a colour image, a normal image and a combined roughness image with a size in metres per repeat; they have no variation, no weathering and no height. The level viewport measures 2,038 by 782 pixels, the same as for M1. |
| L2 | 20:49 on 2026-11-11 | Repeat of profile M2 before anything in the scene changes, under fixed, recorded conditions: level `L_Site_M2`, placeholder sun of 10 lux with sky, viewport 2,038 by 782, named quality Epic, screen percentage 100, view mode Lit, Game View on, Revit slab and massing hidden in the editor only, the editor brought to the foreground if Windows allows it. Record into `profiles6-11-11_M2\capture_M2_repeat.json`. Every console setting is put back afterwards. Nothing is saved. | PENDING |
