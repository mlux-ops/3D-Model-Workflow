---
name: rfa-family
description: Use when asked to build, fix, rerun, verify, package or hand over a Revit 2025 family (RFA, fixture family, face-based family, pyRevit builder) in this repo, including when a pyrevit run produces no RFA, a session has no Revit, a builder is being adapted from an earlier product, or several fixtures are requested at once.
---

# Building Revit RFA families in this repo

An RFA is finished when three separate things are true: a reopened native family passes
measured gates written to `validation.json`, an independent CPython verifier exits 0, and a
human has visually accepted the exported views. A pyRevit exit code, a mock dry run, a
preview script, or a technical pass alone is none of those. Everything below was learned
between 2026-09-04 and 2026-10-19 across about 50 families; `AGENTS.md` and `WORKFLOW.md`
win where they differ. Full catalogue, API gotchas and worked examples: `reference.md`.

## Before touching geometry

1. `grep -n -i "<product>\|<brand>\|<symptom>" PROJECT_MEMORY.md` and read the matching
   entries. That satisfies the `AGENTS.md` instruction to apply its lessons without loading
   the whole file (60k+ tokens).
2. `git fetch origin; git branch -r` and check `output/<product>/` on every remote branch.
   Two sessions once built duplicate Glass Clamp kits on two branches.
3. Resolve the exact product option the user linked (finish, size, CCT, `option_id`). The
   page default is often a different variant. Record the resolved SKU in the README.
4. Separate every dimension by provenance: PUBLISHED (spec sheet), DRAWING (scaled from a
   drawing), RENDER/PHOTO, INFERRED, USER REVIEW. Printed values beat scaled values beat
   photos. Write conflicts into `INFERENCES.md`; do not silently normalise them.
5. For paired or mirrored geometry, inventory left and right parts from every view
   (mount, plate, clip, ferrule, cord exit) before mirroring. House of Troy shipped a
   junction box on both arms because the loop mirrored the right side.
6. When a photo and an explicit user statement disagree on orientation or form, the user
   wins or you ask. Photo analysis fills unstated dimensions only (Roccesco Rev2 lesson).

## Kit layout

Copy the file shape from `output/cassia/`, the ray measurements from
`output/model-transfer-tests/candidate-20260918-01/pendant/build_pendant.py`, and the gate
set from `output/lightology_20260923/tools/native_fixture_support.py`. `reference.md`
sections 4 and 5 list every gate set and geometry technique with its file.

```
output/<product>/
  source/build_<p>.py        IronPython 2.7 builder, runs inside Revit via pyRevit
  source/<p>_geometry.py     pure-stdlib spec: constants with provenance, profiles, rays
  source/verify_<p>.py       CPython, stdlib only, re-derives every gate, exit 0/1/2
  source/package_<p>.py      allow-list ZIP, SHA-256, refuses without visual ACCEPTED
  run_<p>.ps1                preflight, pyrevit run, verifier; exit code = verifier's
  pyrevit/<P>.extension/<P>.tab/Build.panel/Build<P>.pushbutton/script.py
  README.md  INFERENCES.md  PATH_AUDIT.md  logs/  evidence/
```

Builder rules that every failure in the catalogue traces back to:

- **Repo root at run time.** Env var set by the runner, then walk up from `__file__`, then
  candidates. Require `AGENTS.md` in the root. Record `repo_root_source` in the report.
  Never hard-code a user, drive or OneDrive folder; six different roots exist in history.
- **`out_path()` write guard.** Every `SaveAs`, `ExportImage`, `open(...,'w')` goes through
  one function that raises if the path escapes the run dir. List the call sites in
  `PATH_AUDIT.md`.
- **Template and category.** `C:\ProgramData\Autodesk\RVT 2025\Family Templates\English-Imperial\Generic Model face based.rft`
  (verify it exists), then set `OST_LightingFixtures` or `OST_PlumbingFixtures`,
  `FAMILY_ALWAYS_VERTICAL = 0`. Local +Z follows the host face normal: on a ceiling it
  points down in world; on a wall it is the projection axis leaving the wall, and family +Y
  must be world up (the Roccesco gates check both).
- **Solids.** `GeometryCreationUtilities` extrusion, revolve, sweep, loft wrapped in
  `FreeFormElement.Create`; one subcategory per part; `MATERIAL_ID_PARAM` associated to a
  type material parameter. Revolve profiles counter-clockwise, no edge under 0.035 in
  (`ShortCurveTolerance` is 1/32 in), lofts through monotonic or symmetric sections only.
- **Regenerate** the document before reading any bounds and the project before asking a
  new wall or floor for its faces. Only inside an open transaction.
- **Measure, do not restate.** `Solid.IntersectWithCurve` rays for diameters and
  thicknesses, native faces for bounds (display boxes understate curved parts), formula
  value AND measured value at every flex step, body span (drop minus cord) constant.
- **Checkpoint JSON** at every stage, then `raise` after writing it. Keep a timestamped copy
  per attempt under `logs/`. `visual_verdict` is hard-coded `PENDING REVIEWER`.
- **Materials.** Clone the first `GenericSchema` appearance asset, edit in
  `AppearanceAssetEditScope`, strip connected maps before setting colour. Glow is
  `generic_self_illum_luminance` plus colour temperature on diffusers only, and is an
  appearance setting, not photometry. Any bound bitmap must resolve on reopen.

## Running Revit

Two routes exist. Both only ever create, save and close new documents.

**Route A, CLI:** `& '<pyrevit.exe>' run '<absolute builder path>' --revit=2025` through
`run_<p>.ps1`. Known CLI locations: `C:\Program Files\pyRevit-Master\bin\pyrevit.exe` on
this PC, `D:\Games\pyRevit-Master\bin\pyrevit.exe` and `%APPDATA%\pyRevit-Master\bin` on
the E: workstation; test each, never assume (`reference.md` section 2 has the full
environment table). The runner preflights every path with `Test-Path` and exits 2 BLOCKED if one
is missing, prints the checkout and the expected RFA path first, writes `logs/run-start.txt`,
ignores pyrevit's exit code, runs the verifier, and ends with `RFA written: <path>` or
`NO RFA was written`. pyRevit has returned 0 on two crashed scripts and on a relative path
that was never found.

**Route B, in-Revit button:** the pushbutton script resolves the builder from its own
location and `exec`s it in the already-open Revit. Register with
`pyrevit extensions paths add "<checkout>\output\<p>\pyrevit"`, then pyRevit tab, Reload.
Registration writes `C:\ProgramData\pyRevit\pyRevit_config.ini` and may need an elevated
shell. Forget the path afterwards. This is the route that worked when A crashed.

| What you see | What it means | Do |
|---|---|---|
| No `validation.json` 2 min after `Get-Process Revit` lists the new process | Revit never ran the script | Check the Revit journal for `0xe06d7363` (CLI startup crash) or a Device limit / Sign in dialog. Tell the user now. Switch to Route B. |
| `validation.json` with `stage` not `complete` | Builder reached that stage and died | Read `error` in the JSON, fix, rerun. |
| `stage: complete`, `technical_pass: false` | Gates failed | Read `gates` map; never edit the JSON by hand. |
| Verifier exit 2 | Prerequisite or report missing | BLOCKED, not FAIL. |
| `*.0001.rfa` beside the RFA | Revit re-saved over an earlier attempt | Distinct content. Move to `logs/attempt-rfas/`; never ship. |
| Realistic export looks washed out or dark | Viewport limitation | Judge geometry in shaded views; it is not a visual verdict. |

Never kill a Revit you did not start. Stop only the PIDs the task launched, and inspect
the result of `Stop-Process`. One native Revit run at a time, serial.

## Acceptance

Technical gates, all measured in a reopened RFA loaded into a fresh project: category;
`WorkPlaneBased`; placed on a real wall or floor face with `Host` set and normal dot 1;
dimensions within 0.025 in of the published values; every material parameter substituted
and counted on faces; saved defaults and flex rows; CCT parameter; zero family and project
warnings; at least five exported views with the template host hidden and the crop set from
fixture bounds. The verifier re-derives all of it from the JSON and the files on disk.

Visual gate, done by the user or the reviewer they name: front, side and oblique against
the source, proportions not absolute size, each side counted separately for asymmetric
fixtures, grazing light for relief. Give them side-by-side comparison sheets (source photo
beside the export, cropped to content, same height) and record their words in `REVIEW.md`,
never in `validation.json`. Until they answer, the family is `PENDING REVIEWER`, and the
packager must refuse. A technically passing family was rejected visually three times in
the catalogue (Purist, Oyster, Covet).

## Delivery and handoff

- Allow-list ZIP, `testzip()`, SHA-256 in a manifest, no `.000N.rfa`, companion textures
  included with a note on Additional Render Appearance Paths.
- Copy to the Drive for Desktop mount (`Get-PSDrive -PSProvider FileSystem`; the folder is
  `F:\My Drive\Folders\3D Model Workflow\3D Models` on this PC and
  `F:\My Drive\3D Model Workflow\3D Models` on the E: workstation), then confirm with the
  Drive connector's get-file-metadata call by file ID: parent is the 3D Models folder
  (`1WoLM7G88CPMq-7-w_dloZiqDmk7hjd7W`), name and byte size match. Search can lag behind
  Desktop uploads and no md5 is returned. A sync-folder copy is not delivery. A session
  without the mount reports the upload as pending.
- Superseded revisions: rename to `Historical__<name>`; keep RFA filenames unchanged so
  Load Family can overwrite.
- RFAs are Git LFS objects. A cloud session commits the kit, never a real RFA; the RFA
  travels through Drive. Hand over `git fetch origin; git merge origin/<branch>` (plain
  merge; `--ff-only` fails once main moved) followed by `Test-Path` of the run script, and
  name the branch beside every path.
- Log every error in `PROJECT_MEMORY.md` during the task: date, artifact, error, cause or
  "unknown", fix or next step, status.

## Cost

One builder per product, serial Revit, no worker fleet. The Lightology batch dispatched
eight xhigh workers; their handoffs timed out repeatedly and the prime session ended up
doing every native run itself in batched `execfile` sessions under an hour. The effort
trial on the `docs/agents-memory-2026-09-26` branch found Sonnet 5.5 at high passed every
native gate and xhigh or max cost 2.7x and 5x for no gain. Use a cheap read-only agent for
journal and log lookups.

## Common mistakes

- Copying a builder's `ROOT` constant from an earlier product.
- Reading success from the pyrevit exit code, the runner's last line, or a mock pass.
- Shipping a mock dry run or preview as if native (Cassia SF549315AGOP has never run natively).
- Editing `validation.json` to carry a human verdict.
- Deepening relief or fixing proportions after a photo contradicts the user's explicit note.
- Giving the user a path from the prompt text instead of locating the checkout first.
- Starting a second kit for a product that already has one on another branch.
