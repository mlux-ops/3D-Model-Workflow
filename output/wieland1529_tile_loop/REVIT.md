# Revit use for the 1529 Wieland tile loop

Every chat in this loop reads this before any Revit call. The loop only reads Revit; it never
changes, saves or syncs the model.

## The route: `tools/revit_read.py` (verified 2026-11-06 10:35 UTC)

Revit is reached through the native bridge `codex-native-revit-2025` (an add-in inside the open
Revit, HTTP on `127.0.0.1:49327`). Its full guide lives in the other workflow copy at
`H:\Games\3D Modeling Workflows\3D Model Workflow\docs\NATIVE-REVIT.md`, which is outside this
project's CoS roots, so the CoS `read` tool cannot open it. You do not need it: use the
read-only wrapper in this folder through `exec_command`, from this folder:

```powershell
python tools/revit_read.py capabilities
python tools/revit_read.py documents.list
python tools/revit_read.py elements.query --title "25-006 1527 N Wieland" --args-file scratch/req.json
```

- The wrapper refuses every operation that is not a read. Allowed: `documents.list`,
  `context.query`, `categories.query`, `warnings.query`, `elements.query`, `elements.inspect`,
  `parameters.query`, `links.query`, `sheet.inspect`, `view.inspect`, `api.lookup`.
- Write the arguments JSON to a file under `scratch/` and pass `--args-file`; inline JSON quoting
  in PowerShell breaks easily.
- Every completed job is saved in `state/revit_receipts/<operation_id>.json`. Cite receipt ids
  for Revit values in `geometry.json`.
- Do not call the bridge any other way (no `H:\...\tools\revit.py`, no controller, no curl, no
  pyRevit). Do not read or print the token file.
- The RevitMCP / pyRevit Routes plugin is not installed in CoS and is not needed.

## The model

- Open project: `Autodesk Docs://25-006 1527 N Wieland St/25-006 1527 N Wieland.rvt`, title
  `25-006 1527 N Wieland`, workshared, with unsaved changes by the user. Always pass that exact
  title; never query the family documents that may also be open.
- **Owner-confirmed building identity (2026-11-07, `state/OWNER_FEEDBACK.md` line 38):**
  1527 and 1529 Wieland are the SAME building. The open native model `25-006 1527 N Wieland`
  is the correct model for the job 25-006 `1529 Wieland` tile package. The title/address
  difference is not an identity blocker. Continue native READ-ONLY checks using the documented
  title; cite receipt and element IDs for measured values. Identity confirmation does NOT certify
  prior inferred widths, openings, fixture geometry, field measurements, or takeoffs.

## Known results (tested 2026-11-06)

- Works: `elements.query` with `{"category":"OST_PlumbingFixtures","limit":500}` (ids, names,
  location points, bounds, host/level ids), `{"category":"OST_Walls",...}` (bounds),
  `{"category":"OST_Schedules","name_contains":"ROOM"}` -> `ROOM SCHEDULE - IN UNIT` (1084918)
  and `ROOM SCHEDULE` (1084926).
- Fails: `elements.query` with `{"category":"OST_Rooms"}` -> bridge error "The rotation property
  is not supported for the Element related to this LocationPoint." (bridge bug with room
  locations). Do not retry it. Get room names/numbers/areas from `parameters.query` on room ids
  found another way (e.g. a plumbing fixture's room parameter via `parameters.query`), from
  `view.inspect` on the room schedule if it returns rows, or from a room schedule export the
  owner places in `inputs/revit/`. Record which route worked in `state/LEDGER.md`.
- Categories use Revit built-in names (`OST_...`); plain names like "Rooms" fail.
- Units: internal feet; convert and state units in `geometry.json`.

## Order of work (round 0)

1. `documents.list` -> confirm the project above is open; record session time and receipt id.
2. Plumbing fixtures (all pages, `offset`/`next_offset`) -> group by room/unit using
   `parameters.query` on each fixture (room, level, unit parameters). These anchor each bath.
3. Rooms per bath: name, number, level, area, unit (PH/TX) — via the routes above.
4. Walls around each bath: from wall bounds near the room's fixtures, then `parameters.query` /
   `elements.inspect` for length, unconnected height, type and layers. Doors/windows
   (`OST_Doors`, `OST_Windows`): width, height, sill, host wall.
5. Existing tile: wall/floor types with tile layers and painted tile materials, read only.
6. Write `rooms/<ID>/geometry.json` with element ids, receipt ids and a `measured` or `assumed`
   flag on every value.

After round 0, re-read Revit only when the owner says the model changed, or once per 10 rounds
to compare fixture counts and room areas with `geometry.json`. Report differences.

## When Revit is not reachable

- `HTTP 401`: the token file does not match the running Revit. `not reachable`: Revit is closed
  or the add-in is not loaded. A job still `queued`: Revit is busy or showing a dialog; do not
  resubmit, check it later with `python tools/revit_read.py job <operation_id>`.
- One retry after 2 minutes, then put "Revit unreachable since <time>: <error>" in STATUS
  blockers and continue with comps, product research and the board on the data you have.
- Log the error with date, call, message and next step in
  `E:\Claude\3D-Model-Workflow\PROJECT_MEMORY.md` (repo rule) and in `state/LEDGER.md`.
- Never restart Revit, reload add-ins, or install anything to fix access. The owner does that.
