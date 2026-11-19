# Belmont / Wieland bed-wall trim verification — 2026-11-19

## Outcome
HOLD full lower bed-wall drawing revision. Existing R02 PDFs preserved. No unsupported lower layout or dimensions added. Owner requires 3/4-inch wood trim framing and the complete bottom portion.

## Verified live source
Thefoundry; Revit 2025 bridge release 3f41f299be45, process 34520. Live document: Autodesk Docs://25 012 - 651 W. Belmont/25-012 651 W. Belmont_Issue for Construction_.rvt. Fresh document session 757b186f-3d69-41f0-8a59-587e86130d17. Final context receipt 946f2f3f-3adb-4eb5-9d00-14c0d140cb57 confirms is_modified=false. No model edits, save, sync, restart, plugin enablement, or outside transmission.

## Current elements
Simplex trim: 13688525 / 143cc7db-40ad-4d7a-acc4-1565c2e66722-00d0decd. Current bounds and standard geometry inspected in simplex_inspect_uid.json (57ee69a2-46e3-43a0-b08f-2daf15590b6b).
Penthouse trim: 13138641 / a90217dd-fa42-44eb-bd0a-2c07a91eab57-00c87ad1. Current inspection penthouse_inspect_current.json (01697618-4715-4821-bf88-f2429798d7c7).
Standard geometry exposes bounds, solid volumes, face areas/normals/references, not ordered boundary coordinates. Exact historical Penthouse loops in output/belmont_selected_window_trim/final_trim_inspection.json differ from current solid volumes/face counts and cannot substitute for current geometry.

## Native visual evidence
current_view_8844668 - Elevation - PRIMARY BED TRIM WALL.png (capture e50d5e7f-c674-4dfe-9795-60d541e8a768): thin current six-bay trim visible against older 1x3 three-row annotations and slat-wall linework. Central lower portion obscured by furniture. Old 5-inch base label conflicts with owner 8-inch base direction. Do not treat annotation dimensions as current trim cut dimensions.
current_view_8844750 - Elevation - MASTER BED TRIM WALL.png (capture cde12f8b-15b1-4afa-8da8-bf443438b8b9): current panel/window region visible but bed-wall field clipped, lower portions obscured. Not a complete full-wall source.
Wieland not open in this connected Revit process; no current Wieland bed-wall geometry verified. No Belmont layout copied to Wieland.

## Access limitation and next required source
Previously installed read-only outline inspector was reviewed but execution rejected: NotSupportedException, Trusted compiled execution disabled; configure CODEX_REVIT_PLUGIN_DIR explicitly. No trust/security configuration changed. Need either an unobstructed current trim-only full elevation of each applicable bedroom, or a supported approved exact-geometry query. Do not enable compiled execution automatically. Keep 3/4-inch wood framing as owner direction; do not invent face width, frame layout, or quantities.

## Quantity / document preservation
Belmont: base 1450 LF, crown 1200 LF, decorative trim 500 LF. Wieland: base 2350 LF, crown 1850 LF, decorative trim 700 LF allowance. No waste. No crown in baths, closets, mechanical. Installer-only PDF wording remains; internal findings stay in this private evidence record.
