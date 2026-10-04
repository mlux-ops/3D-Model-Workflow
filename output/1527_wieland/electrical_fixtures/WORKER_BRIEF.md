You run on gpt-6-pro. You own one section of the 1527 Wieland finish database: Electrical Fixtures.
Your items are in output/1527_wieland/electrical_fixtures/ITEMS.json. Work on every line item, one after another.
For this job, your model assignment replaces the model and effort defaults in AGENTS.md;
follow every other rule in AGENTS.md and WORKFLOW.md.

HARD RULE: Do not stop. Do not end your turn. Do not ask questions. Finish the whole task
in a single turn.
- If a decision is ambiguous, pick the most defensible option, record it as an
  ASSUMPTION in the item's notes, and keep going.
- If an item is blocked, record the blocker and the last verified stage, then move on to
  the next item. Don't retry the same failing action unless you have new evidence or a
  different approach. (This replaces "stop and report": a worker reports by logging the
  blocker and continuing.)
- End your turn only after every item has a final status and your SECTION_REPORT.md
  is written.

For each line item:

A. Search for a free, downloadable RFA.
  - Acceptable sources: the manufacturer's official site or BIM library, BIMobject,
    ARCAT, Autodesk-hosted content and other first-party manufacturer listings.
    Don't use random file-sharing sites or files whose origin you can't verify.
  - The RFA must be free, need no login and need no account. If it needs a sign-in, an
    account or a license acceptance, don't create an account, enter credentials or accept
    terms. Record it as AVAILABLE_LOGIN_REQUIRED with the URL, then build your own (step B)
    so the item still gets a family.
  - If you download one, check that it is an RFA (or a ZIP containing one), that it opens
    in Revit 2025 through the repo's headless runner, and that it is the right model number.
    Record the source URL, the license or terms note and the Revit version it was saved in.
    If it is older than 2025, upgrade it and save a 2025 copy.
  - Status: DOWNLOADED.

B. If no acceptable free RFA exists, build one using the repo workflows.
  - Follow WORKFLOW.md and the 3d-model-workflow skill's Revit family workflow: a native
    pyRevit family build, real dimensions taken from the manufacturer's spec sheet or
    cut sheet, the correct family template and category, and material parameters for
    the scheduled finish.
  - Build scripts live in output/1527_wieland/electrical_fixtures/<item>/source/, and the RFA goes
    in output/1527_wieland/electrical_fixtures/<item>/.
  - Run every Revit operation through the serialized headless runner pattern in
    output/effort-trial-2026-09-29-sonnet/sconce/_harness/revit_run.py. It takes the
    revit.lock and runs `pyrevit run ... --revit=2025`. Three workers share one Revit,
    so never launch Revit outside the lock.
    If you wait on the lock for more than 15 minutes, log the stall with its duration
    and work on non-Revit steps (spec research, scripts) for other items in the meantime.
  - Pass the native gates: the family opens, the category is correct, the overall
    dimensions match the spec sheet within 1 mm, the parameters flex without errors,
    and there is a preview image of the 3D view. Record the measured values in
    validation.json. Only measured results count as evidence; a script that ran without
    error doesn't.
  - Status: BUILT, or BUILT_WITH_LIMITATIONS with each limitation listed.

C. For every item, write output/1527_wieland/electrical_fixtures/<item>/NOTES.md with:
  - the Smartsheet row ID and the product identity
  - the status
  - the source URL, or the spec sheet used
  - the dimensions checked
  - any assumptions
  - any blockers

D. Errors: every error (tool, command, Revit import, failed gate) goes into
  PROJECT_MEMORY.md during the task. Use the format in AGENTS.md: date, artifact, error,
  cause (or "unknown"), solution or next step, status. Grep for an existing entry first
  and update it rather than adding a duplicate. Never put credentials in it.

E. Don't upload to Google Drive and don't edit the Smartsheet. The orchestrator decides
  delivery after review.

FINISH: Write output/1527_wieland/electrical_fixtures/SECTION_REPORT.md, with one row per item:
row ID, item, status (DOWNLOADED / AVAILABLE_LOGIN_REQUIRED+BUILT / BUILT /
BUILT_WITH_LIMITATIONS / BLOCKED), the RFA path, the gate results and a one-line note.
Then end your turn.
