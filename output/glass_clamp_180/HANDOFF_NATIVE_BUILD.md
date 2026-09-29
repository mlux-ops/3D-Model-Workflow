# SHB_Glass Clamp 180 Square: handoff for the native build (workstation session)

Written 2026-09-29 by the cloud session. Branch `claude/light-fixture-rfa-yw6npk`, kit commit `6350d2c`.
**Status: kit written and mock-tested. Native Revit run NOT RUN. No RFA exists. Nothing uploaded.**
Read first: `AGENTS.md`, the "SHB Glass Clamp 180 Square" section of `PROJECT_MEMORY.md`, `output/glass_clamp_180/README.md`, `INFERENCES.md`.

## 0. Start

```powershell
Set-Location '<checkout>'          # a checkout of mlux-ops/3D-Model-Workflow; AGENTS.md must be in it
git status                         # clean; teleport offers to stash otherwise
git fetch origin; git checkout claude/light-fixture-rfa-yw6npk; git pull
git lfs install                    # *.rfa, *.png, *.zip are LFS-tracked since PR #8
```

Checkouts seen on this machine: `C:\Users\found\OneDrive\Documents\ChatGPT\3DModelWorkflow` (live on 2026-09-25), `C:\Users\mlux\Documents\GitHub\3D-Model-Workflow`. The builder writes into the checkout it is run from and records `repo_root` in `validation.json`.

## 1. Run

```powershell
powershell -ExecutionPolicy Bypass -File "<checkout>\output\glass_clamp_180\run_glass_clamp.ps1"
```

- pyRevit starts its own Revit 2025. Never touch the user's open Revit session; never open the Belmont model.
- The runner ignores pyRevit's exit code and runs `source\verify_glass_clamp.py`; **its exit code is the result**.
- No `validation.json` after the run: use the button route (register `output\glass_clamp_180\pyrevit`, open Revit, press **Build Glass Clamp**, then run the verifier). Precedent: 2026-09-23 startup exception `0xe06d7363`.
- Revit hangs or shows a modal: say so promptly (AGENTS.md stall rule); do not retry blindly.

## 2. Read the result, in this order

| File | What it tells you |
|---|---|
| verifier output | PASS / WARN (soft) / FAIL per check, re-derived from raw measurements |
| `validation.json` `stage`, `error`, `stage_errors`, `gate_error`, `project_error` | where a crash happened (full traceback) |
| `validation.json` `api_probe` | the Revit overloads and property names that actually exist |
| `validation.json` `family.errors`, `family.dimensions`, `family.alignments`, `family.sketch_plane_modes` | which build steps Revit refused and which strategy was used |
| `logs\validation-<stamp>.json` | one copy per attempt: keep every one as evidence |

## 3. If a gate fails: likely cause, where to fix (all in `source\build_glass_clamp.py` unless noted)

| Symptom | Likely cause | Fix / next step |
|---|---|---|
| G16 fails and `sketch_plane_modes` says FIXED | `SketchPlane.Create(Document, Reference)` unavailable or refused (no precedent in this repo) | read `api_probe['SketchPlane.Create overloads']` and `family.errors`; use the overload that exists, else bind cap position another way; record what Revit did |
| G15 or G16 fails and a `family.dimensions` entry has `eq_set: false` | `Dimension.AreSegmentsEqual` refused | replace the EQ chains in `build_planes_and_dimensions` with labelled half-dimensions driven by formula helper parameters (add them to `clamp_geometry.HELPERS`) |
| `family.alignments` shows `failed` entries | alignment in an elevation view refused (proven only in plan) | read Revit's message; try the plan view or the other elevation for that edge |
| G14 / G25 | `FamilyElementVisibility` property names differ | names are in `api_probe['FamilyElementVisibility properties']`; G14 lists `missing_properties` |
| G08 | built-in `Type Comments` not exposed by `FamilyManager` | note it; do not add a parameter of that name (refused) |
| G19 | `GetUnusedElements` overload or purge cascade | `family.purge`, `api_probe['Document.GetUnusedElements']`; the material and its appearance asset are kept on purpose |
| G20 | file over 500 KB with the compact option set | report `family.rfa_bytes` and `compact_option`; do not hack the file to hit the number; the limit is the task's, ask the user |
| G22 | reopened state differs from saved | compare `state_before_save` with `reopened` in the JSON; constraints lost on save/reopen |
| G02 (soft) | Always vertical needs Work Plane-Based; API refuses with it OFF | not a builder defect if `read_only: true`; tell the user |
| G23-G26 | LoadFamily, type activation, geometry via view detail level | fix the project stage; `project_error` has the traceback |

After any repair: edit the real source, rerun the runner, keep the new `logs\validation-<stamp>.json`. If Revit's real behaviour differed from `mock_revit_dryrun.py`, update the mock so it stops asserting the wrong thing, and say so. Repairs made by a session are assistance: label them as such in the log.

## 4. After a technical PASS

1. **Visual review (human gate).** Open `exports\*.png` (front, plan, side, iso) beside `preview\PREVIEW_geometry_offline.png`: two 1/8 in plates flush to the glass faces, four caps outboard and symmetric, bronze colour, nothing else in frame. `visual_verdict` stays `PENDING REVIEWER` until a person accepts it.
2. Deliverable is the RFA plus the type catalog (no RVT, no V-Ray). Ignore `*.0001.rfa` backups. FBX export is not requested; run it only if asked.
3. **Drive (standing authorisation, AGENTS.md).** Dedup first: search `3D Models` (`1WoLM7G88CPMq-7-w_dloZiqDmk7hjd7W`) for `SHB_Glass_Clamp`. Zip an allow-list (RFA, catalog, README, INFERENCES, `validation.json`, `exports\`, `references\`, `source\`) as `SHB_Glass_Clamp_180_Square_R2025_Package.zip`, verify it reopens (`testzip()`), stage it in temp, copy to `F:\My Drive\3D Model Workflow\3D Models`, then confirm file id and `fileSize` through the Drive connector. A file in the sync folder is not evidence. Report the link.
4. Update the memory entry with new lines only: every error and its fix, the native result, what is and is not claimed.
5. Commit and push to `claude/light-fixture-rfa-yw6npk` only. New binaries (`.rfa`, `.png`, `.zip`) go through LFS.

## 5. Rules

- Never claim ASSUMED values (plate 1/8 in, joint gap 1/8 in, cap D 3/4 in, cap 1/8 in, 2 caps per side) as CRL data. The 3/4 in glass-hole note is an unverified search snippet.
- Belmont placement is manual and only on the user's instruction: never open the working Belmont model.
- No Transfer Project Standards, no third-party RFAs.
- Local results do not reach the cloud session unless pushed.
