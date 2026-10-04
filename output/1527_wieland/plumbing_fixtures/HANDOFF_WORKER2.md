# Plumbing Fixtures handoff from worker 2

Checkpoint created by the orchestrator on 2026-10-02 after worker 2 reached its context limit. The filesystem is authoritative.

## Clean stopping point

- No Plumbing Revit operation is currently in flight.
- The shared runner ledger's last Plumbing entry is:
  - START 2026-10-02 10:54:27, wait 0 s, `run_pending.py`
  - END 2026-10-02 10:55:36, exit code 0, run 69 s
- `_harness/prepare_all.py` and `_harness/prepare_completion_d.py` were updated at 10:56:18, after that last native run. Treat those edits as prepared source for the next batch; they have not yet been validated by a later shared-lock Revit run.
- Do not replay completed native batches. Continue from the current files.

## Inventory state

- `ITEMS.json`: 178 rows.
- Worker 2 reconciled these to 71 unique product groups covering 160 product rows, plus 18 no-SKU rows (15 organizational/header rows and 3 unselected sinks).
- Current artifact counts at checkpoint:
  - 81 RFA files under the Plumbing section tree.
  - 68 `validation.json` files.
  - 65 validations at `stage=complete`, `technical_pass=true`, `native_gates_pass=true`.
  - 3 manufacturer review validations with explicit holds.
  - 0 row-level `NOTES.md` files.
  - no `SECTION_REPORT.md` yet.

## Exact product groups still lacking any validation.json

These are the only three keys from `_harness/resume_inventory.json` with no current validation file:

1. `62820LF-BL` — Brizo European wall pot filler.
2. `63221LF-BLLHP` — Brizo Odin articulating kitchen faucet, less handle.
3. `873111-BNX-2.5` — Brizo Roccesco jointed shower head.

All three are defined in the newly updated `_harness/prepare_completion_d.py`. Run them through the normal publish/build/native-gate path under the shared `revit.lock`; do not launch Revit directly.

## Latest completed native batch

`_harness/batch_current.json` finished at 2026-10-02T15:55:33Z and records native/technical PASS for:

- `K-77685-NA`
- `DT062412`
- `R65700`
- `443306`
- `240328`
- `80019-ISE`
- `700332000000090`
- `BT0734816-BNX`
- `TD954-20LT`
- `TD9028-PCW`
- `TD9028-LS-PCW`
- `THU842_01-A`
- `T84613-BNX_SH84103-BNX_R84100`

This batch supersedes stale states in the earlier `_harness/resume_inventory.json` for those same keys.

## Manufacturer-source review holds

Three downloaded/manufacturer-derived families reopen, place and export in Revit 2025 but intentionally do not pass all technical gates. Preserve them as review holds unless new evidence supports a correction.

### `700337000000090` — Duravit Starck tub

- Manufacturer RFA downloaded publicly and upgraded from 2018 to Revit 2025.
- Category/host/material/view/reopen gates pass; no warnings.
- Width and length measure 1700.000 x 900.000 mm and match the authoritative source.
- Height is 531.042 mm, but the source evidence does not provide an authoritative overall height. Current validator marks the dimension gate false because not all overall dimensions are authoritative.
- Keep this as a documented manufacturer review hold unless the dimensional gate is refined to accept the two authoritative axes without inventing a height.

### `MS642124CEFG_01` — TOTO Nexus

- Official source: TOTO manufacturer RFA, saved to Revit 2025.
- Selected type is `MS642124CEFG`; the source family also contains `MS642234CEFG`.
- Actual measured envelope: 451.348 x 726.017 x 685.800 mm.
- Expected: 444.5 x 725.4875 x 685.8 mm.
- Width deviates +6.848 mm; depth/height pass.
- `Product Material` substitutes correctly; `Flush Lever Finish` is writable but substitution does not reach faces.
- Category/host/views/reopen/warnings pass.
- Keep the width discrepancy and lever-material binding as explicit holds; do not label the native dimension/material gates passed.

### `SS124_01` — TOTO SS124 seat

- Extracted nested manufacturer seat family from the official TOTO source and saved as Revit 2025.
- Actual envelope: 355.658 x 513.772 x 122.104 mm.
- Expected: 355.6 x 473.075 x 46.0375 mm.
- Width passes; depth and height exceed the reference by 40.697 mm and 76.067 mm.
- Material/category/host/views/reopen/warnings pass.
- Keep as a manufacturer dimensional hold unless the source geometry can be defensibly corrected without distorting the product.

## Known identity / finish holds from worker 2

- `BLANCO 443306` and `BLANCO 240328`: source review shows these exact SKUs are white while the schedule text calls for black. Worker 2 retained the scheduled black visual direction as an explicitly unresolved finish variant; do not silently substitute a different SKU.
- `32526141`: source review showed the exact SKU is a wall faucet trim rather than the rough/component implied by the schedule wording. Preserve as an identity/scope hold.
- Earlier source conflicts and descoped/agent-ignore rows remain in `ITEMS.json`; do not drop them from row coverage.

## Native workflow / harness

- All Revit operations must run through:
  `output/effort-trial-2026-09-29-sonnet/sconce/_harness/revit_run.py`
- That runner owns the shared `revit.lock` and invokes `pyrevit run ... --revit=2025`.
- A zero pyRevit exit code is not sufficient evidence; accept only measured `validation.json` results and previews.
- Current Plumbing harness files include:
  - `_harness/prepare_all.py`
  - `_harness/prepare_products.py`
  - `_harness/prepare_hansgrohe.py`
  - `_harness/prepare_brizo.py`
  - `_harness/prepare_completion_a.py`
  - `_harness/prepare_completion_b.py`
  - `_harness/prepare_completion_c.py`
  - `_harness/prepare_completion_d.py`
  - `_harness/queue_prepared.py`
  - `_harness/run_pending.py`
  - `_harness/review_native.py`
  - `_harness/inspect_downloaded_families.py`
- `_harness/prepared_models.json` currently contains 65 prepared models from before the final `prepare_completion_d.py` edit.

## Next actions

1. Re-read `AGENTS.md`, `WORKFLOW.md`, the worker brief, and relevant `PROJECT_MEMORY.md` family/pyRevit/RFA/revit_run/lock entries.
2. Reconcile the handoff against the live filesystem before doing anything else.
3. Publish/build/validate only the three missing groups from `prepare_completion_d.py`, using the shared runner and lock.
4. Reconcile all 71 product groups against the current 68 validation files plus the three new results. Do not trust stale fields in `resume_inventory.json` when a newer validation exists.
5. Preserve the three manufacturer review holds and the BLANCO / 32526141 identity-finish holds unless new primary evidence resolves them.
6. Ensure every one of the 178 `ITEMS.json` rows receives its own `NOTES.md` with row ID, identity, final status, source/spec, dimensions checked, assumptions and blockers.
7. Write `SECTION_REPORT.md` with all 178 rows and one of the required statuses:
   `DOWNLOADED`, `AVAILABLE_LOGIN_REQUIRED+BUILT`, `BUILT`, `BUILT_WITH_LIMITATIONS`, or `BLOCKED`.
8. Log any new error in `PROJECT_MEMORY.md`, updating existing matching entries instead of duplicating them.
9. End with RESULT / CHANGES / VALIDATION / BLOCKERS so the orchestrator can run its independent 30% + all-limited/all-blocked review.

## Protected scope

- Do not edit Smartsheet.
- Do not upload to Drive.
- Do not change product scope or substitute models silently.
- Preserve all existing worker-2 artifacts and use the filesystem as the source of truth.
