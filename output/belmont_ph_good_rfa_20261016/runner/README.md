# 651 Belmont Penthouse Good — Revit 2025 family batch

This folder contains an **unexecuted** batch runner. It was prepared without opening, launching, closing, or modifying the user's Revit session. The manifest example is illustrative: replace every placeholder with the exact final six-family scope and source identity, and copy it to `manifest.json` before any launch.

## Inputs and builder interface

- `schema_version=1`; **exactly six** family objects.
- Unique `id`; `mode` is `oem` or `custom`.
- For OEM rows, `source_rfa` is an existing **absolute** input .rfa path. It is opened in the isolated process, saved to `target_rfa` (a new absolute .rfa output), closed, then reopened for native validation. OEM input bytes are never overwritten.
- For custom rows, `builder_script` is an existing **absolute** Python 2.7-compatible .py path. The runner executes it using `execfile` inside the isolated Revit process. It receives `__revit__` (UIApplication), `APP` (Autodesk.Revit.ApplicationServices.Application), `DB`, `JOB` (manifest family dictionary), `TARGET_RFA`, `SOURCE_RFA=None`, `progress(stage, detail=None)`, and `result={}`. **The builder is responsible for making and saving a new family directly at `TARGET_RFA`, closing all temporary family documents, and rolling back its own failed transactions.** Do not use a user's open RVT document or save over an OEM RFA. Store any evidence in the task folder.
- `expected_category` defaults to `Lighting Fixtures`; `expected_dimensions_mm` may be `{"width":W,"depth":D,"height":H}`, with `tolerance_mm` defaulting to 1.0. Dimensions are Revit XYZ axis envelope in mm. Provide authoritative axes, not a guessed product body/dropped assembly comparison. An absent dimension target produces an explicit untested dimensional status.

## Offline preflight (does not launch Revit)

```powershell
python "E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\runner\launch_batch.py" --preflight-only
```

The launcher requires the user/prime to prepare `manifest.json` with six existing OEM inputs/builder scripts. All destinations must be new .rfa paths inside the Belmont task. Preflight reads running Revit process information without interacting with those processes.

## Native launch (future, only after explicit prime/user release)

```powershell
python "E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\runner\launch_batch.py" --timeout-seconds 2400
```

The launcher invokes exactly **one** `pyrevit run <absolute batch_runner.py> --revit=2025` CLI process, at below-normal priority, under an exclusive task-local lock. Default CLI: `D:\Games\pyRevit-Master\bin\pyrevit.exe` (override with `--pyrevit`). Runner refuses an active document in its own isolated Revit session and uses only `Application.OpenDocumentFile` to inspect or copy families. It never loads the 651 Belmont project.

Native receipts are under `runner\receipts\`: `progress.jsonl`, per-family `<id>.json`, `batch_final.json`, `batch_error.json`, `launcher_state.json`, and `pyrevit_stdout.log`. A zero pyRevit CLI exit is **not** an acceptance gate. The launcher requires `batch_final.json` and six PASS results. Output files are never overwritten. A replay requires manual evidence reconciliation and a new revision.

The launcher records all pre-existing Revit PIDs but **never kills any Revit.exe**, even on a timeout. On timeout it terminates only its own pyRevit CLI process and reports `TIMEOUT_UNKNOWN_NATIVE_STATE`; an isolated Revit child may remain and must be examined separately using its exact PID and creation time. There is no automated process-tree kill. It does not install/reload pyRevit extensions, edit junctions, registry, cache paths, or global user configuration.

## Validation scope

Each receipt reports source/build SHA256, output SHA256, saved-family reopen, category, measured fine-detail solid envelope (where available), axiswise errors when expected dimensions are supplied, existing family warnings, and distinct capability flags. Native category, no-warnings, reopen and configured dimensional fit are hard gates. Material flex, arbitrary geometry flex, placement and photometry are explicitly **untested** unless separately verified; they are not inferred from opening a family. Physical Revit document and geometry behavior requires a future native run to verify.
