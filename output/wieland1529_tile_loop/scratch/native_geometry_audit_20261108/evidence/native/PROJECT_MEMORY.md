# Native bathroom geometry audit — 2026-11-08

- External native MCP/CLI returned HTTP 401, including a task-local config pointing
  to the live state directory. Installed and in-process assembly is 3f41f299be45,
  PID 45468. Used the existing KitchenTools API dispatcher only to authenticate
  to that same native bridge and run read-only native geometry queries. Fresh
  documents.list 0ad86b1c-e1d2-4e6c-903f-2ab07649b71b completed, transaction not
  started, selecting session 2978497e-b41f-497f-81f3-7be82e0e133d and the exact
  cloud model title/path. No Revit restart, save, synchronization or model mutation.
- Initial room survey used nonexistent OST_Countertops and returned a partial
  read-only receipt. Corrected to actual category IDs from known source elements.
  Completed survey 27622d84-1eef-4d73-b604-1ceaac1f8556: 122 room records,
  29 requested records (including duplicates/unplaced/aliases), 230 context items.
- Initial route printer emitted too much geometry data. Corrected it to print
  operation IDs, paths, counts and bounded error details; full receipts stay local.
- Initial mesh pilot referenced nonexistent Mesh.NumVertices. Consulted Autodesk
  Mesh/Room API documentation and corrected enumeration to Mesh.Vertices. The
  failed pilot and corrected pilot are separate artifacts. Corrected five-element
  pilot has zero extraction errors and includes actual native WC/cabinet/faucet,
  wall and door geometry.
- Initial local pilot analyzer attempted min/max on an empty failed mesh. Added
  empty-array handling and inspected the actual native extraction errors first.
- A 0.00001ft mesh-vs-element-box assertion was too strict for native Revit
  tessellation far from the origin: observed countertop deviation about 0.000017ft.
  Preserve native points; use measured tessellation tolerance in checks rather
  than clamping geometry to category boxes.
- Native findings are distinct from tool errors: 24 mapped native bathroom Room
  boundaries; PH viewer 314A/B corresponds spatially to native 313A/B TOILET;
  TX 203A is unplaced and 203B is a different 7.09SF fragment. Keep the actual TX
  WC enclosures derived from current native wall faces, without claiming Room IDs.
  Current primary areas are PH 122.017 and TX 105.093SF; historical quantities stay
  frozen. Native Room property associations can cross levels or misattribute
  fixtures; validate position and level separately.
- Native batch 2 JSON serialization hit a Python 2 UnicodeDecodeError on a
  non-ASCII source name. Added recursive Unicode normalization (UTF-8, with
  Windows-1252 decoding for legacy byte strings). Retain successful batches
  0/1 by exact requested-ID match; resume only the failed and remaining batches.
- Recursive normalization alone did not resolve the native serialization error.
  A five-material probe proved IronPython marks System strings as both str and
  unicode; Python JSON's ASCII encoder fails on registered/trademark characters.
  ensure_ascii=False passed every sample. Use that proven path with .NET UTF-8
  File.WriteAllText, preserving all original Unicode source names.

- Native source mesh checks found two curved Brizo pieces extending 0.00248/0.00394ft past their category boxes. Independent GetInstanceGeometry verification f7f84d75-d567-4464-8ae9-edf06d4652a5 matched exported bounds within 0.000020ft. Preserve native geometry and record those two source-tessellation exceptions; all other deviations are below 0.0002ft.
- A source-print diagnostic hit Windows cp1252 on a replacement character in legacy source text. Use UTF-8 stdout or ASCII-escaped diagnostic text; no artifact changed.
- A coverage review caught an incorrect use of GRADE/garage datum levels as storey limits. Use occupied Room levels for source clipping. Also query full physical storeys, because native Room heights of 6ft omit real ceilings and high fixtures. These are source-view filtering corrections, never model changes.

- Revit restarted during the audit: PID45468 was replaced by PID72064. Guards stopped supplemental queries. Fresh official documents.list195855a2-1b57-49ac-ba77-59e1be74f481 selected sessionb29598c2-76f2-40ac-b6a0-b8b3f2455a5e. Added explicit native-registry Resolve guards to every current read script; refreshed source rooms and all geometry into separate current-session files. Prior snapshot retained.
- Complete physical-storey survey5c0b334a-990a-4493-afd0-bb4c3a3d9d2c read1641 spatially relevant model records; filtering actual room footprints selected347 elements, all read again from the current process.
- Two source faucet families have four sub-millimeter RevolvedFaces each returning no native mesh, also at explicit triangulation LOD0.5. Native inspection100bc7ba-77d1-43a8-b6e2-559e8f92bec4 measured each face below0.00001SF. Record these native-mesher omissions, do not invent replacement geometry. Other faces exported with no errors.
- An out-of-order patch failed atomically. Reapplied hunks in source order, then syntax/build checked.

- Initial complete browser QA passed all 52 native triangle/position/area comparisons but found section and ceiling controls still guarded to Full mode only. Replaced those shared handlers for both Full and Native room modes; the final suite checks each mode separately.
- Two PH Bath 2 material-study rectangles had no supporting native host-face triangles. Inspected the raw source faces rather than moving or inventing walls; withheld those two unsupported Full-room overlays, retained the frozen samples in Wet-zone detail, and exposed a source note per affected room.
- Reviewing all-room contact sheets caught four upstairs chairs and two upstairs countertop families above bathroom ceilings. Their bounding boxes intersected a broad storey query. Filtered elements wholly above the actual native finish-ceiling underside, with IDs/reasons retained in each room's audit payload. No model elements deleted or moved.
- An audit-print diagnostic again encountered the Windows cp1252 default when printing a Unicode arrow from historical accuracy text. Set UTF-8 stdout for subsequent report diagnostics. No file corruption or model change.

- Native bathroom audit release verified: all 52 Full/Native room checks PASS; final actual E: HTML browser smoke PASS, including native WC picking through clipped walls. Native readback 31ce786a-e66b-4969-8a09-caee0784ffba matched all 347 elements and 26 Room records, no model change. Frozen picks unchanged; original deliverables backed up. Explicit source holds are documented in GEOMETRY_AUDIT.md.
