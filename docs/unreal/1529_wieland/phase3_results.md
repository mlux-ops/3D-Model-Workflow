# Phase 3 results: Datasmith import of the owner's Revit export

Companion to [PLAN.md](PLAN.md). This file is written as each step finishes, so a new session can resume from it. Earlier records: [phase1_results.md](phase1_results.md) and [phase2_results.md](phase2_results.md).

**Status at 16:16 Central on 2026-11-11: begun.** The owner wrote "continue" at about 16:10, after lifting the plan's storage limits. The session that finished Phases 1 and 2 went on in the same chat; the editor had not been restarted, so the first step is to free the memory it still holds.

## How to resume, if this chat ends

1. Read the status block above and the journal table below. A journal line that still reads PENDING marks the step that was running.
2. If the editor crashed during that step: record it, read the cause from the editor's log and the engine's source under `D:\Games\UE_5.9\Engine\`, change one thing and try again; after two further crashes of the same step, stop that step and report the options.
3. Otherwise carry on from the first step in "Where each step stands" that is not done. `KICKOFF_PHASE3.md` holds the rules for this phase; `PLAN.md`, "Rules for every phase", holds the rules for all of them.

## Checks made before any work

Made at 16:14 on 2026-11-11.

| Check | Result |
|---|---|
| The editor | Answers. **Not restarted since 11:39** (same process). It holds 23.4 GB, and 1,672 assets of Phase 1's test import are still loaded in it although their level is closed. Free physical memory 6.3 of 31.1 GB; free commit 14.3 of 79.1 GB. |
| `r.Material.UseShaderCompilationParameters` | 0. The import workaround is in force. |
| `r.Lumen.WorldCache.Supported` | Still true in the running editor, because it has not been restarted. The line is out of the settings file. For this phase's profile `r.Lumen.WorldCache.Allowed` is set to 0 for its length. |
| The open level | `L_R15_Production`, 64 objects, nothing unsaved. |
| The plan's working copy | Clean at commit `0246dc7`. |
| Where the editor keeps its folders | Off C:, as the owner's decision on storage limits asks: engine, project, cache and page file on D:; temporary and shader folders on E:; the per-user engine folder is a link to E:. |

## Memory before heavy steps

By the plan's rule: before an import, a reimport, a path-traced render or a lighting trial, free physical memory and free commit are read and written here. Under 12 GB of free commit the step is not started.

| Time | Step about to start | Free physical memory (GB) | Free commit (GB) | Started |
|---|---|---|---|---|
| 16:14 on 2026-11-11 | None yet: the state check (editor at 23.4 GB, Revit closed) | 6.3 of 31.1 | 14.3 of 79.1 | - |
| 16:16 on 2026-11-11 | Import of the first export into the new building level (editor at 23.2 GB after unloading the test import, Revit closed, video memory 8.5 of 16.4 GB in use) | 5.7 of 31.1 | 14.5 of 79.1 | Yes |

## Journal

Each step that can crash the editor or that changes the project is written here before it is made, and committed.

| No. | Time | What is done | Outcome |
|---|---|---|---|
| J1 | 16:16 on 2026-11-11 | Free memory without a restart: unload from the editor's memory the 1,672 assets of Phase 1's test import under `/Game/Wieland1529/Scratch/` (their level is closed and nothing in them is unsaved), then collect garbage. Nothing is deleted, changed or saved; the files on disk are not touched. | **Done at 16:15.** All 1,672 packages unloaded in 4 seconds with no error; none of that folder's assets is loaded now; nothing is unsaved. The editor's own figure hardly moved (23.4 to 23.2 GB) and free commit stayed at 14.5 GB: the engine keeps freed memory for reuse and does not hand it back to Windows. So the gain is room inside the editor for the next import, not a lower reading. |
| J2 | 16:17 on 2026-11-11 | Step 3.1: copy both exports, each with its assets folder and under its own dated folder, into the project's `ImportStaging` folder: `2026-11-10_export_1` (682 MB, 1,366 files) and `2026-11-11_export_2` (922 MB, 1,374 files), from `E:\Claude\3D-Model-Workflow\references\1529 Wieland - Datasmith\`. File names are kept, because each export names its assets folder. A checksum of each `.udatasmith` file and of each folder's file list is recorded. Inside the project folder; 1.6 GB on D:, which has 58.7 GB free. | **Done at 16:16.** Both copies match their source in file count, bytes and the checksum of the `.udatasmith` file. First export: 1,365 asset files, 708,728,030 bytes, file checksum `6B235289...B11AE7`. Second export: 1,373 asset files, 960,362,774 bytes, file checksum `0F4D0B33...1D1A07`. Full figures: `review\phase3\staging_manifest.json`; copy log: `review\phase3\staging_copy.robocopy.log`. D: has 57.1 GB free. |
| J3 | 16:18 on 2026-11-11 | Step 3.2: make a new empty level `/Game/Wieland1529/Building/L_Building` and import the **first** export into it from the staging folder (`ImportStaging\2026-11-10_export_1\`), assets to `/Game/Wieland1529/Building/Datasmith`, lightmap UVs off, with `tools\wieland_datasmith.py`. The level is made in one call, asset preparation is finished in a second, and the import runs in a third. Workaround line in force. Free physical memory 5.7 of 31.1 GB, free commit 14.5 of 79.1 GB, editor at 23.2 GB, Revit closed. The first export goes in first so that the second can come in as a reimport (step 3.10). | PHASE3_J3_PENDING: if this line still reads so, the editor crashed during the import; the level may exist empty and the assets folder may be partly written |
