# Write-path audit — P01 `candidate-20260918-01`

`ENVIRONMENT.md` records that source builders in this repository contain fixed
destinations, and that `rebuild_adella_precision.py` copies maps back into
production output. The adapted builder removes the source `ROOT` / `OUT` / `RFA` /
`TEMPLATE` constants and routes every write through a single guard, so the hazard
is closed structurally rather than by inspection.

## The guard

`out_path(*parts)` (build_pendant.py:137) joins under `RUN_DIR`, normalises, and
**raises** if the result is not `RUN_DIR` itself or beneath `RUN_DIR + os.sep`.
It creates missing parents. There is no bypass: no other function opens a file
for writing, and no `SaveAs` or `ExportImage` call receives a path built any
other way.

`RUN_DIR` is derived, not hard-coded: `repo_root()` probes `REPO_ROOT_CANDIDATES`
and accepts only a directory containing `AGENTS.md`, then appends
`output/model-transfer-tests/<RUN_ID>/pendant`.

## Every write site

| Line | Call | Destination | Through guard |
|---|---|---|---|
| 152 | `open(..., 'w')` | `validation.json` | yes |
| 156 | `open(..., 'w')` | `logs/validation-<stamp>.json` | yes |
| 380, 386 | `doc.ExportImage` | `evidence/<prefix> - 3D View - *.png` | yes, via `options.FilePath` |
| 478, 479 | `doc.SaveAs` | nested body RFA | yes |
| 565, 566 | `doc.SaveAs` | parent RFA | yes |

Verified by `grep -n "out_path(\|SaveAs\|ExportImage\|open("` over the builder:
every match is either the guard itself, its docstring, a read-only `os.listdir`,
or one of the rows above.

## Reads, which are deliberately unguarded

Family templates under `C:\ProgramData\Autodesk\RVT 2025\Family Templates\English-Imperial`
are read-only inputs. `references/mila/*` and `scripts/build_mila.py` were read as
references. No file outside `RUN_DIR` was opened for writing at any point in
attempts 1–3.

## Residue not produced by the guard

Revit itself wrote `*.000N.rfa` copies inside `RUN_DIR` as each repair cycle
re-saved over the previous attempt. These are inside the run directory and so do
not breach the guard. They are not duplicates of the deliverables — each holds
distinct content — and have been moved to `logs/attempt-rfas/` and renamed by
attempt, so the run root carries only the four families that ship.
