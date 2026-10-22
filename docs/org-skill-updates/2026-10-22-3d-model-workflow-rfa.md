# Org skill update: `3d-model-workflow`, RFA sections (Option B)

Prepared 2026-10-22. The synced org skill cannot be published from a local session, so this
file holds the text to paste. Three parts: a full replacement for
`references/revit-pyrevit.md`, line edits to `SKILL.md`, and one edit to
`references/delivery.md`. Evidence for every change is in
`.claude/skills/rfa-family/reference.md` in this repo.

Local synced copy (read-only, overwritten on sync):
`%USERPROFILE%\.claude\skills\synced\<id>\3d-model-workflow\`.

---

## Part 1. Replace `references/revit-pyrevit.md` with the following

```markdown
# Revit family builds and native verification with pyRevit

Worked examples, newest first:
- `output/lightology_20260923/` (12 fixtures, 14 face-based RFAs accepted and delivered
  2026-09-24): `tools/native_fixture_support.py` shared gates and views, builders
  `f03..f06` on the helper (23-64 lines), `tools/final_native_review.py` independent
  pass, `tools/make_release.py` hash-chained release, `release/MANIFEST.json`,
  `PRIME_REVIEW.md`, `FIXTURE_CATALOG.md`, `ORCHESTRATION.md`, `ERRORS_AND_RECOVERY.md`.
- `output/cassia/` (kit, 2026-09-23): `source/cassia_geometry.py` shared spec,
  `run_cassia.ps1` runner, `source/verify_cassia.py` with stale-report guard,
  `source/mock_revit_dryrun.py`, `pyrevit/Cassia.extension/.../BuildCassia.pushbutton`.
  Never run natively; copy its shape, not its result.
- `scripts/HouseOfTroy.extension/...` and `scripts/build_house_of_troy_usledz15.py`
  (2026-09-23): the first build done from a pushbutton in the open Revit session.
- `output/model-transfer-tests/candidate-20260918-01/pendant/` (P01, 2026-09-18):
  `build_pendant.py` measured gates, `verify_run.py`, `HANDOFF.md`, `SCORECARD.md`.
- `scripts/build_kamden.py`, `scripts/build_mila.py`: proven single-file builders
  (rewrite their hard-coded `ROOT`).
- Roccesco Rev4 (2026-10-19, Brizo trim): overlay and photo-comparison sheets as visual
  gates. On Drive under `3D Models/Brizo_Roccesco_Luxe_Gold_R2025_Rev4/source/`, not in git.

## Environment: discover, never assume

Paths differ per machine. Preflight each with `Test-Path`, print what was found, exit 2
BLOCKED if absent (`run_cassia.ps1`, `run_roccesco.ps1` do this).

| Fact | found workstation | E: / MAXSPC workstation |
|---|---|---|
| Checkout | `C:\Users\found\Documents\3\3D-Model-Workflow` | `E:\Claude\3D-Model-Workflow` |
| pyRevit CLI | `C:\Program Files\pyRevit-Master\bin\pyrevit.exe` (6.5.5) | `D:\Games\pyRevit-Master\bin\pyrevit.exe` (6.4.0) |
| pyRevit CPython (stdlib only, no pip) | `...\pyRevit-Master\bin\cengines\CPY3123\python.exe` | same layout |
| System Python (numpy, pillow) | `C:\Python314\python.exe` | same |
| Revit 2025 | `C:\Program Files\Autodesk\Revit 2025\Revit.exe` | same |
| Templates | `C:\ProgramData\Autodesk\RVT 2025\Family Templates\English-Imperial\` | same |
| Drive mount | `F:\My Drive\Folders\3D Model Workflow\3D Models` | `F:\My Drive\3D Model Workflow\3D Models` |

Engine is IronPython 2.7 on .NET Core (`IPY2712PR`). Dead roots that still appear in old
files and must never be copied: `C:\Users\found\OneDrive\Documents\ChatGPT\3D Model Workflow`,
`C:\Users\mlux\Documents\GitHub\3D-Model-Workflow`. V-Ray is not installed. No ADSKLIB
write API exists.

## Two ways to run a builder

1. **CLI.** `pyrevit run "<absolute script>" --revit=2025` spawns its own Revit. Never
   touch the user's open Revit. A relative path returns 0 and runs nothing. The exit code
   is 0 on crashed scripts. Wrap it in a runner that writes `logs/run-start.txt`, ignores
   pyrevit's exit code, runs the CPython verifier, and ends with `RFA written: <path>` or
   `NO RFA was written`.
2. **In-Revit pushbutton.** When the CLI cannot start Revit (native startup exception
   `0xe06d7363`, House of Troy 2026-09-23, nothing written after nine minutes), a pyRevit
   extension button in the already-open session works. The button resolves the builder
   from its own `__file__` and `exec`s it. Register with
   `pyrevit extensions paths add "<checkout>\output\<p>\pyrevit"`, Reload, run, then
   `extensions paths forget`. Writing `C:\ProgramData\pyRevit\pyRevit_config.ini` may need
   an elevated shell.

If no `validation.json` appears within about two minutes of Revit starting, Revit never
ran the script. Check the journal for `0xe06d7363` or a licence dialog (Device limit
reached, Sign in), tell the user at once, and switch route. Do not poll or retry the same
command. Stop only processes this task started. One native run at a time.

For several fixtures, run them as a batch inside one Revit session (`execfile` per
builder with try/except and an incremental JSON ledger, as
`output/lightology_20260923/tools/run_completion_batch_v5.py` does): 18-35 s per fixture.

## Builder structure that has proven itself

1. Locate the repo root at run time: env var set by the runner, then walk up from
   `__file__`, then candidates; require `AGENTS.md`; record `repo_root_source` in the
   report. Never hard-code a user, drive or OneDrive folder in a builder or a handoff.
2. `out_path(*parts)` joins under the run dir and raises if the result escapes it; every
   `SaveAs`, `ExportImage` and `open(...,'w')` goes through it. List the sites in
   `PATH_AUDIT.md`.
3. Keep the geometry spec in a pure-stdlib module shared by the builder, any offline
   preview and the verifier, with provenance per value (PUBLISHED, DRAWING, RENDER,
   INFERRED, USER REVIEW). Preflight profiles: closed, counter-clockwise, no edge under
   0.035 in.
4. Build every configuration from shared code in one run; never copy a finished RFA.
5. Measure, do not restate: `Solid.IntersectWithCurve` rays, native faces for bounds
   (display boxes understate curved parts), formula AND measured value at each flex step,
   body span (drop minus cord) constant, material substitution counted per face.
6. Write `validation.json` at every checkpoint with a per-gate PASS/FAIL map,
   `technical_pass`, `visual_verdict = PENDING REVIEWER`; timestamped copy per attempt in
   `logs/`. Re-raise after writing it.
7. Verify with CPython (`verify_*.py`): re-derive every gate from the JSON and files,
   refuse a report older than `run-start.txt`, exit 0 pass, 1 fail, 2 blocked. That exit
   code is the result.
8. Export views with the face-based template's host hidden and the crop set from fixture
   bounds; include a hosted view. Realistic exports are not visual evidence.

## API gotchas met on these machines

- `Document.GetElement(id).Name` throws `MissingMemberException`; use
  `DB.Element.Name.GetValue(elem)` with a `SYMBOL_NAME_PARAM` fallback.
- `FamilyParameter` has no `.Set`; use `FamilyManager.Set(param, value)`.
- Angle formulas (`'30 deg'`) are rejected; `fm.Set(p, math.radians(30))`. Length
  formulas `'x in'` work.
- `Application.ShortCurveTolerance` is 1/32 in; keep every edge at or above 0.035 in.
- Regenerate the document before reading bounds, and the project before asking a new wall
  or floor for faces; only inside a transaction.
- Loft through uneven or near-duplicate sections overshoots; periodic loft profiles
  self-intersect. Use monotonic, symmetric, or matched arc sections.
- Revolve profiles counter-clockwise; clockwise untested.
- Parent-instance bbox of a nested pendant grows with cord length by design.
- Face-based family on a downward face: local +Z points down in world.
- `ElementId.Value`, not `IntegerValue`, in 2025.
- `SketchEditScope` is project-only. Formulas set from an unordered dict read stale
  dependents: make locked parameters constant formulas. Flex drags unconstrained parts.
- `System.Byte` and numpy scalars are not JSON serialisable.
- Paint inside a family is baked into loaded face material ids.
- `NAME.0001.rfa` backups are distinct per-attempt saves; keep under
  `logs/attempt-rfas/`, ship only current RFAs.
- Appearance assets: clone a `GenericSchema` asset, `AppearanceAssetEditScope`, strip
  connected maps before `SetValueAsColor`; a `UnifiedBitmap` must resolve after reopen;
  appearance values survive `LoadFamily` (verified, Lightology diagnostic).

## Sources and visual review

Resolve the exact linked option (finish, size, CCT, `option_id`); the page default is
often another variant. Printed dimensions beat scaled drawings beat photos; disclose
conflicts in `INFERENCES.md`. Inventory left and right parts before mirroring. When a
photo contradicts an explicit user statement on orientation or form, the user wins
(Roccesco Rev2 regression). The visual verdict is a person's, recorded in `REVIEW.md`,
never written into `validation.json`. Compare proportions, not absolute size, between a
perspective photo and an isometric export; overlay the silhouette on the spec-sheet
vector outline when one exists.

## Handoff from a session without Revit

Status is BLOCKED, never PASS or FAIL. Commit the kit on a branch (RFAs are Git LFS
objects and travel through Drive, not git). Hand over one block:
`git fetch origin; git merge origin/<branch>` (plain merge, not `--ff-only`), then
`Test-Path` of the run script, then the run command. State the branch beside every path.
Check `git branch -r` for an existing kit first; two sessions once built duplicate kits.

## Cost

One builder per product, serial native Revit, no worker fleet. Eight xhigh workers on
the Lightology batch stalled on handoffs and the prime session did every native run
itself. The Sonnet 5.5 effort trial (branch `docs/agents-memory-2026-09-26`) passed every
native gate at high; xhigh and max cost 2.7x and 5x with no gain. Grep
`PROJECT_MEMORY.md` for the product or symptom; do not read the whole file.
```

---

## Part 2. Edits to `SKILL.md`

| Location | Current | Replace with |
|---|---|---|
| Intro, "learned the hard way on 2026-09-18/19" | that phrase | "learned between 2026-09-04 and 2026-10-19; `AGENTS.md` and `WORKFLOW.md` win where they differ" |
| Rule 7 | ends at "Read `validation.json`, not the runner." | append: "If no `validation.json` appears within two minutes of Revit starting, the script never ran (`0xe06d7363` CLI crash or a licence dialog): tell the user and use the in-Revit pushbutton route." |
| Working habits, "Delegate long builds to Sonnet; Haiku for mechanical steps." | that bullet | "Revit family builds: Sonnet 5.5 at high (the effort trial passed every native gate; xhigh 2.7x and max 5x gave nothing). One builder per product, serial Revit, no worker fleet. Haiku for read-only log and journal lookups." |
| Working habits, Python line | `C:\Users\mlux\AppData\Local\Programs\Python\Python312\python.exe` | "`C:\Python314\python.exe` (numpy, pillow) on the found workstation; verifiers use pyRevit's bundled CPython `...\cengines\CPY3123\python.exe` (stdlib only). Check `Get-Command python` and import numpy before relying on any interpreter." |
| Working habits, pyRevit CLI line | `C:\Program Files\pyRevit-Master\bin\pyrevit.exe` | "pyRevit CLI is at `C:\Program Files\pyRevit-Master\bin\pyrevit.exe` on the found workstation and `D:\Games\pyRevit-Master\bin\pyrevit.exe` on the E: workstation; discover at run time, exit 2 BLOCKED if absent." |
| Working habits, Git line | "offer `git merge --ff-only`" | "hand over `git fetch origin; git merge origin/<branch>` (plain merge; `--ff-only` fails once main moved) plus a `Test-Path` of the run script, and name the branch beside every path" |
| Rule 9, Drive path | `F:\My Drive\3D Model Workflow\3D Models` | "the Drive for Desktop mount (`Get-PSDrive -PSProvider FileSystem`); `F:\My Drive\Folders\3D Model Workflow\3D Models` on the found workstation, `F:\My Drive\3D Model Workflow\3D Models` on the E: workstation; pick the one holding existing packages" |
| Worked examples table, "pyRevit family builder with measured gates" row | P01 path only | add rows: "shared gates, views, materials for face-based fixtures: `output/lightology_20260923/tools/native_fixture_support.py`"; "runner with preflight, stale guard and RFA-written line: `output/cassia/run_cassia.ps1`"; "in-Revit pushbutton: `output/cassia/pyrevit/Cassia.extension/.../BuildCassia.pushbutton/script.py`"; "independent native review and hash-chained release: `output/lightology_20260923/tools/final_native_review.py`, `make_release.py`"; "batched native runs: `tools/run_completion_batch_v5.py`" |
| Worked examples table, ADSKLIB generator row | "(byte-exact round-trip, NOT yet Revit load-tested)" | "(byte-exact round-trip; FAILED native load 2026-09-23: Revit showed one blank-named item with a warning icon. Deliver only libraries authored through Revit's Material Browser unless a generated one has opened correctly in a disposable project.)" |
| Working habits | (none) | add: "Before starting a product, `git fetch origin; git branch -r` and check `output/<product>/` on every remote branch." |
| Working habits | (none) | add: "Grep `PROJECT_MEMORY.md` for the product, brand or symptom and read only the hits; the file is over 60k tokens." |

## Part 3. Edit to `references/delivery.md`

| Location | Current | Replace with |
|---|---|---|
| ADSKLIB generator note (lines ~30-32) | "NOT yet Revit load-tested" | same replacement as the SKILL.md table row above |
| Drive mount (lines ~46-54) | `F:\My Drive\3D Model Workflow\3D Models` | same replacement as the SKILL.md Rule 9 row above; add "verify by file id with the v3 `name` field; the connector returns no md5" |
