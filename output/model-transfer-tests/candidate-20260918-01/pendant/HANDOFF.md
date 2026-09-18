# P01 pendant transfer test — handoff

Run ID: `candidate-20260918-01`
Run directory: `output/model-transfer-tests/candidate-20260918-01/pendant`
Specification: `docs/model-transfer-tests/PENDANT.md`
Prompt: `docs/model-transfer-tests/PROMPT_PENDANT.md`
Handoff written: 2026-09-18. Status: **preparation complete, native run NOT RUN (blocked).**

## 1. Why the run stopped

The session executing the prompt was a remote Linux container, not the Windows
workstation the kit requires.

| Requirement (ENVIRONMENT.md) | Observed in that session |
|---|---|
| Windows host | `Linux 6.18.44-fc-v33 x86_64` |
| `C:\Program Files\Autodesk\Revit 2025\Revit.exe` | absent; no Windows volume mounted (`/mnt/c`, `/c` absent) |
| `C:\Program Files\pyRevit-Master\bin\pyrevit.exe` | absent |
| Family templates under `C:\ProgramData\Autodesk\RVT 2025\...` | absent |
| CPython with `numpy` + `PIL` | Python 3.11.15; `numpy` and `PIL` absent at session start (`PIL` installed ad hoc for reference measurement only) |
| .NET / Revit API | no `dotnet`, no `mono` |
| Native Material Browser / renderer UI | not available |
| Google Drive tooling | Drive MCP tools present, but no final package exists to deliver |

Every native gate in PENDANT.md is therefore **BLOCKED**, not failed. Nothing in
this directory claims a native result.

## 2. Repository root discrepancy — resolve before running

Three different repository roots are in play:

| Source | Path |
|---|---|
| `PROMPT_PENDANT.md`, `ENVIRONMENT.md`, `scripts/build_mila.py` | `C:\Users\found\OneDrive\Documents\ChatGPT\3D Model Workflow` |
| Operator's message during this session | `C:\Users\mlux\Documents\GitHub\3D-Model-Workflow` |
| `.gitattributes` LFS entry (committed) | `C:/Users/mlux/Documents/GitHub/3D-Model-Workflow/...` |

`build_pendant.py` probes both Windows candidates at startup (`REPO_ROOT_CANDIDATES`)
and aborts if neither contains `AGENTS.md`. Confirm which checkout is authoritative;
if it is the GitHub one, `ENVIRONMENT.md` and `PROMPT_PENDANT.md` still name the
OneDrive path and should be corrected.

## 3. Source-drift check — executed, real result

Verified all 20 entries of `docs/model-transfer-tests/SOURCE_MANIFEST.csv` against
the working tree at `98087e3`.

| Group | Result |
|---|---|
| 8 binary entries (PDF, JPG, PNG) | byte-identical, SHA-256 matches |
| 10 text entries | content identical; SHA-256 matches only after CRLF normalisation |
| `AGENTS.md` | **drifted.** Manifest hash = the file as of kit commit `0a34a61` (2848 B, LF). Current file is 4310 B, changed by later merge `98087e3`. |
| `WORKFLOW.md` | **unverifiable.** Manifest hash (13538 B) matches **no committed revision** — `0a34a61` holds 13424 B LF / 13545 B CRLF. The hash was taken from an uncommitted working-tree state. |

Two defects in the manifest itself, worth fixing in the kit:

- Hashes were computed over a mixed line-ending tree (`AGENTS.md` hashed as LF,
  `scripts/build_mila.py` as CRLF), so a clean checkout can never match all 20
  byte-for-byte. Normalise line endings before hashing, or record the git blob OID.
- The manifest was frozen before the same commit finished editing `AGENTS.md` and
  `WORKFLOW.md`, so it was already stale when committed.

Neither drift affects the pendant geometry targets.

## 4. Reference review — executed, real measurements

Read `references/mila/PRODUCT 661292 - Mila Pendant.pdf` / `product-sheet.png`
(Lightology, SPEC MMK661292) and the dark-finish photo `references/mila/661293.jpg`.
Photo measurements are pixel extents scaled on the 8.2 in outer loop width.

| Feature | Photo-derived | Drawing / spec | PENDANT.md target |
|---|---|---|---|
| Loop outer width | 8.2 (scale datum) | 8.2 | 8.2 |
| Loop outer height | 29.27 | 29.1 | 29.1 |
| Loop aspect h/w | 3.569 | 3.549 | 3.549 |
| Frame (strap) thickness | 0.528 | 0.5 | 0.5 |
| Globe diameter | 6.64 | not dimensioned | 6.7 (inferred) |
| Globe centre above loop bottom | 4.2 | not dimensioned | 3.9 (29.1 − 25.20) |

Findings that matter for a candidate run:

- **The drawing's `6.8"` and `21.7"` are a second product size, not the globe.**
  Both elevations carry stacked pairs — `21.7"` over `29.1"`, and `6.8"` over
  `8.2"`. The Specifications block pins MMK661292 to `8.2"W x 29.1"H`, and the
  photo's measured aspect (3.569) matches 29.1/8.2 (3.549), not 21.7/6.8 (3.191).
  A candidate that reads `6.8"` as the globe diameter or the inner loop width will
  be wrong. PENDANT.md does not warn about this; consider adding it.
- The 6.7 in globe inference is well supported: measured 6.64 in, and the inner
  loop width is 8.2 − 2(0.5) = 7.2 in, so the globe nearly fills the loop as the
  photo shows.
- Globe centre sits 0.3 in lower in the photo (4.2 in) than in the source model
  (3.9 in). Within "lower end of loop", recorded as an observation, not a defect.
- The two drawing elevations show the globe at opposite ends of the loop; the
  photo and PENDANT.md both put it at the **lower** end. Follow the photo.
- Satin brass for variation B, sampled from the manufacturer render's brass pixels:
  median RGB `(194, 175, 122)`, mean `(196, 179, 131)`, p10 `(178, 158, 106)`,
  p90 `(226, 208, 147)`. `build_pendant.py` uses diffuse `(186, 166, 112)` —
  deliberately below the median, because sampled pixels already carry specular lift.

## 5. Orientation logic — read this before judging the exports

The parent is face-based. Placed on a **downward-facing** floor/ceiling face, its
local +Z follows the face normal and therefore points **down** in world space. So
in body-local coordinates:

- local `z = 0` is the **top** of the loop, where the `Upper cable socket`
  (`z = -0.35 … 0.1`) meets the cord;
- local `z = 29.1` is the **bottom** of the loop;
- the globe at local `z = 25.20` is 3.9 in above the bottom;
- body bounds are `z = -0.35 … 29.1`, i.e. 29.45 in overall.

The 29.45 in figure is the body including the socket. The loop itself is 29.1 in.
Do not shrink the loop to make the bounds read 29.1.

Drop chain: canopy `0 … 1.1`, cord `1.1 … (Cord Length + 1.45)`, nested body top at
`Cord Length + 1.45`, loop bottom at `Cord Length + 1.45 + 29.1` = `Cord Length + 30.55`
= `Total Drop`. Defaults: baseline Cord 29.45 → 60 in; variant Cord 41.45 → 72 in.

## 6. What is already built

`build_pendant.py` (789 lines, syntax-checked under CPython 3.11 — `ast.parse` only;
it cannot be *executed* outside Revit because it needs `__revit__` and the .NET API).

It builds **both** configurations in one pyRevit run from the same construction
code — no completed RFA is copied:

| | Baseline (A) | Variant (B) |
|---|---|---|
| Parent RFA | `Mila_Trial_Dark_Adjustable_R2025.rfa` | `Mila_Trial_SatinBrass_72in_R2025.rfa` |
| Nested body | `Mila_Trial_Body_Baseline.rfa` | `Mila_Trial_Body_SatinBrass.rfa` |
| Type name | `Mila Black` | `Mila Satin Brass 72in` |
| Default Total Drop | 60 in (Cord 29.45) | 72 in (Cord 41.45) |
| Metal diffuse | `(53, 50, 44)`, gloss .42 | `(186, 166, 112)`, gloss .50 |
| Flex inputs | 8, 18.1496062992, 48, 118 | 12, 60 |

Adaptations made against the hazards in ENVIRONMENT.md:

- source `ROOT` / `OUT` / `RFA` / `TEMPLATE` constants removed; every write goes
  through `out_path()`, which normalises the path and **raises** if it resolves
  outside the run directory. This is the guard the `rebuild_adella_precision.py`
  write-back hazard calls for, applied structurally rather than by inspection.
- nested family names and material **element** names are run-specific, so baseline
  and variant can coexist in one project. Parameter names stay exactly
  `Metal Finish`, `Glass Finish`, `Cord Length`, `Total Drop` as the spec requires.
- `OverwriteExistingFile=True` is retained but can now only ever target the run
  directory; each run also writes a timestamped `logs/validation-<stamp>.json`
  alongside `validation.json`, so repair-cycle evidence is retained.
- the script **re-raises** after writing its JSON. The source swallowed exceptions
  and exited clean; ENVIRONMENT.md warns that a zero exit code is not evidence.

Measurement work added beyond the source builder:

- `Solid.IntersectWithCurve` ray probes for real geometric measurement rather than
  restated constants: frame thickness (each strap), loop inner width, globe
  diameter at its centre plane, canopy diameter at mid height.
- per-element bounding boxes for loop width/height, band depth, canopy height.
- `Total Drop` formula value **and** measured host-to-bottom drop recorded at every
  flex step, each with its own tolerance and pass flag (0.01 in for the formula,
  0.1 in for the measured drop).
- body height captured at each flex state and compared, to prove the body does not
  change size while the cord flexes.
- default Total Drop verified three times: in the reopened RFA type, on the placed
  instance before flexing, and in the RFA reopened after the whole flex battery.
- material substitution records faces inspected, faces carrying the substitute,
  distinct material IDs and the restored ID — not just a boolean.
- a hosted 3D view is exported from the test project in addition to the three
  family views, as PENDANT.md requires.
- `gate_summary()` writes an explicit per-gate PASS/FAIL map; `visual_verdict` is
  left as `PENDING REVIEWER` by design — the script never self-certifies fidelity.

## 7. What still has to be produced

Not yet written in this directory:

1. `SCORECARD.md` — run-local copy of `docs/model-transfer-tests/SCORECARD.md`.
   Leave the model-identity, token and cost rows for the operator's client to fill;
   do not invent them.
2. `verify_run.py` — CPython gate verifier that reads `validation.json` and exits
   nonzero on any missing or failed gate. Needed because pyRevit's exit code is
   unreliable.
3. `run_pendant.ps1` — the absolute-path runner (draft in §8).
4. `README.md` and `INFERENCES.md` — package notes and the inference disclosure
   (globe diameter 6.7 in, band depth 0.5 in, socket/seat/cable details, satin
   brass appearance values).
5. `PATH_AUDIT.md` — the write-path audit table; `build_pendant.py`'s header
   currently references it.
6. Root `PROJECT_MEMORY.md` entry. **Required by `AGENTS.md` and not yet written.**
   It should record, dated 2026-09-18: the environment block (no Windows/Revit in
   the executing session), the `AGENTS.md` / `WORKFLOW.md` manifest drift, the
   manifest's mixed-line-ending defect, the repository-root discrepancy, and the
   `6.8"`/`21.7"` second-size reading of the drawing. Add new entries only; do not
   alter historical ones.

## 8. Resuming on the Windows workstation

```powershell
Set-Location 'C:\Users\mlux\Documents\GitHub\3D-Model-Workflow'   # confirm the root first
$run     = 'candidate-20260918-01'
$builder = Join-Path (Get-Location) "output\model-transfer-tests\$run\pendant\build_pendant.py"
if (-not (Test-Path -LiteralPath $builder)) { throw 'Adapted trial builder is missing' }

# Preflight, per ENVIRONMENT.md
Test-Path 'C:\Program Files\Autodesk\Revit 2025\Revit.exe'
Test-Path 'C:\ProgramData\Autodesk\RVT 2025\Family Templates\English-Imperial\Generic Model face based.rft'
Test-Path 'C:\ProgramData\Autodesk\RVT 2025\Family Templates\English-Imperial\Generic Model.rft'

& 'C:\Program Files\pyRevit-Master\bin\pyrevit.exe' run $builder --revit=2025
```

Then, regardless of exit code, open
`output\model-transfer-tests\candidate-20260918-01\pendant\validation.json` and check
`stage` is `complete`, `technical_pass` is `true`, `failed_gates` is empty, the two
`rfa_mtime_utc` values are fresh, and both RFAs open in Revit 2025. Close no Revit
session that this run did not launch, and do not open an active user project.

Assistance policy for the run: one initial attempt, then at most two repair cycles;
keep each attempt's `logs/validation-<stamp>.json`. Record further attempts
separately rather than resetting.

## 9. Standing rules that apply to the finish

- Log every error and its solution in root `PROJECT_MEMORY.md` in the same task
  (`AGENTS.md`, user instruction 2026-09-11).
- Final model packages go to Google Drive `3D Model Workflow`
  (`1Xsd3Y96SOi00cWNaxqYeqlp4tNe3Z8CD`) → `3D Models`, labelled as a benchmark test
  delivery, deduplicated, with the remote link verified. Standing authorisation
  exists; local placement is not evidence of upload.
- Report technical pass, visual pass and unverified items separately. Missing native
  access is BLOCKED, never PASS.
- Existing `output/mila/*` and `scripts/*` are read-only references and were not
  modified by this session.
