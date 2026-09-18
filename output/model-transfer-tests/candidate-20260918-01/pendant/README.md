# P01 pendant transfer test — `candidate-20260918-01`

Benchmark test deliverable. **Not a production package**, not a Lightology
product release, and not a replacement for `output/mila/`, which is untouched.

Status: **technical pass, visual review outstanding.** `PENDANT.md` requires
both, so this run is not complete.

## Contents

| File | What it is |
|---|---|
| `Mila_Trial_Dark_Adjustable_R2025.rfa` | A — reproduction. Face-based parent, type `Mila Black`, default Total Drop 60 in |
| `Mila_Trial_Body_Baseline.rfa` | nested body loaded by A |
| `Mila_Trial_SatinBrass_72in_R2025.rfa` | B — controlled variation, type `Mila Satin Brass 72in`, default Total Drop 72 in |
| `Mila_Trial_Body_SatinBrass.rfa` | nested body loaded by B |
| `build_pendant.py` | the builder; builds both configurations from shared construction code in one pyRevit run |
| `verify_run.py` | independent CPython gate verifier; exit code is the result |
| `run_pendant.ps1` | preflight → build → verify, exits on the verifier's code |
| `validation.json` | full measured record of the accepted run |
| `HANDOFF.md` | the preparation session's handoff, written before any native run |
| `INFERENCES.md` | every inferred value, disclosed |
| `PATH_AUDIT.md` | write-path audit against the `ENVIRONMENT.md` hazard |
| `evidence/` | eight native exports: front, side, oblique and hosted, per configuration |
| `logs/` | per-attempt reports, the superseded builders, and `attempt-rfas/` holding each attempt's saved families |
| `references/` | added at packaging time: the Lightology sheet, the dark-finish photograph and the product-sheet render this build was measured against |

## Reproducing

```powershell
powershell -ExecutionPolicy Bypass -File run_pendant.ps1
```

Requires Revit 2025, pyRevit 6.5.5 attached to it, and both English-Imperial
Generic Model templates. A missing prerequisite exits 2 as BLOCKED, never as a
pass or a fail.

**Do not read `pyrevit run`'s exit code as the result.** It returned 0 on both
failing attempts of this run. `verify_run.py` is the gate.

`run_pendant.ps1` parses clean but has not itself been run end to end: the
accepted result came from invoking the builder and the verifier separately, and
executing the script now would start a fourth attempt beyond the assistance
policy. Its two steps are exactly those commands.

## What the run establishes

Technical, for both configurations: fresh RFA saved and reopened as Lighting
Fixtures; placed on a downward-facing overhead face and hanging below it; all
eleven measured dimensions within 0.01 in; default Total Drop preserved through
save, placement and the full flex battery; every flex step matching formula and
measured drop; both nested materials reaching nested geometry; zero family and
project warnings; and all required exports produced. `verify_run.py` re-checks
each of these independently of the builder's own gate map.

## What it does not establish

- **No visual pass.** `visual_verdict` is `PENDING REVIEWER` by design; the
  builder never self-assesses fidelity.
- **No rendered or photometric validation.** The exports are shaded Revit views.
  Glass self-illumination is an appearance setting, not a photometric result.
- **No SKU claim for B.** Satin brass at a 72 in drop is a test variation.
- **Not an unassisted candidate result.** See `logs/` and `PROJECT_MEMORY.md`:
  the preparation session produced the builder but could not run it, and both
  repairs were made by the operator's local session.

## Before packaging

The four RFAs listed above are the deliverable. Revit also wrote `*.000N.rfa`
copies as each repair cycle re-saved over the previous attempt. Those are **not**
duplicates — each has distinct content and is that attempt's saved family — so
they are retained as evidence under `logs/attempt-rfas/`, named by attempt rather
than by Revit's suffix. The suffix is misleading: attempt 1 crashed before the
variant was ever built, so the variant's `.0001` belongs to repair cycle 1.

