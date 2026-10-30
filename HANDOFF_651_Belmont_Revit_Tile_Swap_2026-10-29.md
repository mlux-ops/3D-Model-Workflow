# HANDOFF - 651 W Belmont (25-012) - Revit tile swap

Written 2026-10-29 by the cloud session. For: Claude Code, running locally on maxspc with a shell.
Language: ASD-STE100 Simplified Technical English.

## 1. Task
Replace the tile in the open Revit model with the current selections. Max's request (2026-10-29 12:52):
"Perform a full Revit tile audit and replacement with the current selections. Align grout lines, add Schluter strips, and select the correct grout colour. Colour and bump maps are in the 3D modelling workflow Google Drive."

## 2. Approvals and limits (from Max)
- APPROVED 2026-10-29 13:00: work in the LIVE model that is open now. Do not make a detached copy.
  - Model: `25-012 651 W. Belmont_Issue for Construction_` (Autodesk Docs, workshared, cloud).
  - The repo rule "never test in the working model" is overridden for this task only. Test each script first in a throwaway project. Then run it on the live model.
- Max is not available for input. When a room or scope cannot be mapped with certainty, do NOT guess. Skip it, and list it in the result report.
- Do NOT synchronize with central. Save locally. Max syncs after review.
- Do NOT delete old tile materials. Leave them unused.
- Do NOT touch the PH primary bath (room 404). No scheme is picked.

## 3. Why the cloud session stopped
- The revitmcp server (pyRevit Routes, API `revit-mcp-v1`, localhost:48884) can read, set parameters and make schedules. It cannot paint faces, create materials, align patterns or load families.
- The cloud session had no shell (device_bash absent).
- You need the in-Revit route: run the scripts INSIDE the open Revit session (pyRevit pushbutton or the pyRevit console). The `pyrevit run --revit=2025` CLI starts its own Revit and cannot reach the open model.

## 4. Read first (repo E:\Claude\3D-Model-Workflow)
1. AGENTS.md, WORKFLOW.md, the October entries in PROJECT_MEMORY.md.
2. `.claude/skills/rfa-family/` SKILL.md and reference.md (run routes, 18 API gotchas, gates).
3. `scripts/PreferredTilesR2Builder.cs`, `scripts/build_preferred_tiles.py`, `scripts/build_belmont_revit.py`: the proven method for AppearanceAssetEditScope + UnifiedBitmap (colour + bump at real-world scale).
4. `references/belmont_tiles/`, `output/belmont_tiles/`.
Rules that still apply: every script writes `validation.json`; a separate verifier checks it; exit code alone is not proof; log every error in PROJECT_MEMORY.md; no Transfer Project Standards; no copying materials between RVTs.

## 5. Current selections (source: project doc `claude/651_belmont_tile_decisions_2026-10-28.md`, rev 2)
| Key | Scope | Product | Item | Proposed grout (NOT picked - mark as proposal) |
|---|---|---|---|---|
| VENDOME | DD + SX primary walls, niches | Porcelanosa Vendome Nature 47x47 | 100348304 | SpectraLOCK PRO 78 Sterling Silver |
| CAPRI | DD + SX primary floor, shower floor, steam-shower ceiling | F&D Capri Oat 32x32 | 101488146 | SpectraLOCK PRO 40 Latte |
| LUXE | Bath 2 wall field + floor (PH, DD) | F&D Luxe Sand 24x48 | 101317865 | Mapei UC+FA 5229 Sea Salt |
| SERENITY | Bath 2 feature wall (PH, DD) | F&D Serenity Sands 14x39 | 101306496 | Mapei 5225 Sandstorm |
| DOMINO | PH Bath 2 niche | MSI Domino Black Matte 1x6 stack | SMOT-PT-RETNERO-1X6STM | Mapei 5010 Black |
| KENTNAVY | Bath 3 wall field (all Bath 3) | Porcelanosa Kent Navy Gloss 3x12 | 100363532 | Mapei 5232 Night Sky |
| KENTDECO | Bath 3 feature wall | Porcelanosa Kent Deco Navy Gloss 3x12 | 100363533 | Mapei 5232 Night Sky |
| NERO | Bath 3 floor | MSI Nero Marquina 12x24 matte | NHDNERMAR1224 | Mapei 5010 Black |
| RIBBED | SX kitchen backsplash | F&D Ribbed Alabaster 3x12 | 101236917 | Mapei 5001 Alabaster |
| COBALT | PH kitchen coffee niche | F&D Pure Cobalt glass 3x12 | 101328086 | Mapei 5231 Deep Ocean |
| ROJO | Powder sink walls (DD + PH), full height assumed | F&D Rojo Umber 2x10 satin | 101075026 | Mapei 5044 Pale Umber |
| ASTORIA | PH foyer floor, room 214 ENTRY only | F&D Astoria Ivory 24x48 | 101236941 | Mapei 5039 Ivory |
| VETTA | PH laundry floor | F&D Vetta Concept Gray 12x24 | 100941533 | Mapei 5009 Gray |
SX Bath 2 = PH/DD Bath 3 spec (decision 2026-10-13). Grout colours are on the "Belmont Grout Picks" page (artifact DmttMvgngdpQc8pM3PYeqp). No pick is saved there yet, so use the proposals above and mark each material "GROUT = PROPOSAL" in its Comments.

## 6. Maps in Google Drive (made 2026-10-29; size in file name = real-world tile repeat)
| Key | Colour file id | Bump file id | Repeat (in) |
|---|---|---|---|
| CAPRI | 1KxG6vVJKS5A7_BX5y27ILCW9POlf4ovD | 15lHBdGLu_wNvt2sGNdW80C2Y_-otOw4C | 96 x 96 |
| LUXE | 1kspMGCFy-xNl_-MxKhWWGI-VdvFdJ4Wk | 1S8yadIvruWqt2ZevrkqtWnVskL-TxJg_ | 144 x 96 |
| SERENITY | 1uBTsC1mRPTpKfnM_M6Gr0o2IL6mTSy90 | 1uMxBYl83NqBXHN9fozk9iVPbS8c_udKz | 117 x 56 |
| DOMINO | 1xpvC8vc9Nn9V1hLBjlVU731arrKQwMig | 1PsDgvPe4U0rXf_2kKbKC-ALStq9PMhtx | 24 x 24 |
| KENTNAVY | 1v7Ro8KuUsrz42quIqDl42nwLjDRX3nKV | 1Z3UO-T-DVkVKF55VEzXQrLePJyJ_VEgV | 71.625 x 65 |
| KENTDECO | 1WO0E8n_pnaeR-4TXPQQQgOU7vU_Dg2t8 | 1g8QXqNtHifh9oH7f2K2gi-R7xgFHmrSu | 71.625 x 65 |
| NERO | 1rmT8KJhfuNRwEbFEoRttJHDxjIidqQdA | 19YPzuCHy7YfGhP-GFO8gv6s10Elx4kCP | 72 x 48 |
| RIBBED | 16dN2M0iCxwzsFrIV0-bmPz1fLEswigtH | 1N3j4Dk3xRl70gz-qnYubizMst3SbN_Xr | 72 x 48 |
| COBALT | 1ruchKF3j0jwPriyG0TIe_SBQ6XuFrB8R | 1apKSNd4tRNuWUK2rfUQbcgSGo0sDRXxI | 72 x 72 |
| ROJO | 1ttTFNF_oaS1GRGLjqxUkXjxMUiPl-WaS | 1zbfBruWyf-uSeZdcKKoa9HWfgQj3mooH | 24 x 60 |
| ASTORIA | 1OjYITxBGz_nTZEBrIlCdjBSOjHgKDjqG | 1ncCDAt3jNdx-DOdl8lC1VdZ6ZNnJV7eQ | 144 x 96 |
| VETTA | 1sL1c8UAnuoiOmuzglEmZ-bi8G9267htk | 1wGeYwXsSB4XRIH9VOoFJRb5x_sYwWlJw | 96 x 96 |
| VENDOME | not found in Drive search | - | Model already has "Porcelanosa - Vendome Nature - 47" x 47" Tile #8/ #8(1)" (id 13111356) and #1-#8 (13111340-13111355). Reuse. |
- Verify every download with `file -b` and check pixel size. Several unrelated Drive files from 2026-10-29 05:51 are 0 bytes; none of the files above was checked for size 0 by the cloud session except by listing (all listed above are > 0 bytes).
- Check if the grout joint is baked into the colour map. If yes, confirm the joint colour is near the proposed grout; if not, record the difference.

## 7. Model state (audit 2026-10-29, full table in project doc `claude/651_belmont_revit_tile_audit_2026-10-29.md`)
- Audit views in the model: `ZZ_CLAUDE_Tile Audit - Walls` (14007890), `- Floors` (14007897), `- Ceilings` (14007904).
- Tile is almost all applied as face PAINT on generic wall/floor types. Some is a layer in a type ("Tile, Porcelain, 24x48" in "C1010_Interior Partition (5 1/2" Stud W/ 1 GYP 1 TILE)"; "Finishes - Tile, Mosaic, Gray" in "Thinset Tile (kitchen)"; Codex Simplex Bath 2 types).
- Levels seen: BASEMENT, 1ST, 2ND, 3RD, 4TH, T/ROOF, GRADE. Unit-to-level mapping is NOT confirmed. Use Rooms (name + number + level) to map faces to scope. Do not map by level alone.
- Defects to report (do not fix without a scope match): Vendome paint on exterior QUICK BRIK walls (62 SF); Arabescato paint on roof deck (1,125 SF); B1-01 Hexagon paint on 4TH ceilings (188 SF); Grounded Alabaster and Soreno paint on exterior walls; dropped tiles still painted (b1-02 Cross Cut Fluted 29 SF, b3-04 bruges 16 SF).

## 8. Method
1. Preflight. In the open Revit: confirm document title, Revit version, workset ownership (tile faces may be on elements owned by others - check `WorksharingUtils.GetCheckoutStatus`). Log in PROJECT_MEMORY.
2. Room map. For each Room: get boundary faces with `SpatialElementGeometryCalculator`. For each face record host element, face reference, current paint material, area. Write `room_face_map.json`. Classify each room into a scope from section 5 by room name. Unclear rooms -> `UNMAPPED`.
3. Materials. Build one material per key in section 5 from the Drive maps (pattern of PreferredTilesR2Builder). Name: `651 Belmont - <KEY> - <Product> <size>`. Fill Manufacturer, Model (item no.), Description, Comments ("GROUT = PROPOSAL <colour>"). Set the surface foreground MODEL pattern to the real tile size so the grout lines show in views. Test in a throwaway RVT first; verify with validation.json.
4. Paint. In ONE transaction per room: `Document.RemovePaint` on the old tile faces, then `Document.Paint` with the new material. Only faces in a mapped scope. Only faces that had tile paint, or faces in section 5 scopes with no tile now (powder sink walls, PH foyer floor) after you confirm the face by room.
5. Grout alignment. Goal: a full tile at the visible start edge of each wall and floor (shower: start at the drain side / niche; walls: centre joints on niches and windows where possible). The API has no public call to align a painted face's model pattern. Options in order: (a) set the UnifiedBitmap offset so the render joints match the pattern origin; (b) if alignment of the model pattern is needed per face, record each face in `alignment_todo.json` for manual Align in the UI. Do not claim alignment you did not verify in a view.
6. Schluter. The model has NO Schluter family. Build a line-based generic model family (see rfa-family skill), one type per profile+finish. Take profile dimensions from Schluter data sheets only - do not invent them. Placement rules (Max 2026-10-29): no strip at bathroom door thresholds (PH foyer + PH laundry thresholds keep theirs); niches: secondary baths only, 2 sides + top, no bottom; a full-length niche gets top only (DD Bath 3 shower niche); PH Bath 2 full-height Domino niche: 2 sides only (interpretation - flag); windows: sides + top, no sill; JOLLY at exposed wall ends and steam-ceiling edges. Finishes (PROPOSAL, not approved): DD + SX primary brushed brass AMGB; Bath 2 matte black MGS; Bath 3 polished chrome ACG; kitchens brushed stainless EB; PH foyer brushed brass; PH laundry brushed chrome; powder rooms none. Place only where the location is certain; list the rest.
7. Verify. Re-run the three ZZ_CLAUDE takeoff schedules. Compare new-material areas with the net SF in section 5 (DD+SX Vendome 307.46, Capri 189.72, Luxe 162.21, Serenity 77.54, Domino 15.34, Kent 135.64, Kent Deco 114.33, Nero 101.06, Ribbed 43.58, Cobalt 16.40, Rojo 58.56, Astoria 20.00, Vetta 21.00). A difference > 10% is a finding, not an error to hide. Export one 3D view per bath to PNG and inspect.
8. Report. Write `output/belmont_tile_swap_20261029/REPORT.md`: what changed (element ids), what was skipped and why, defects, alignment status, Schluter status. Save the model locally. Do not sync.

## 9. Open items you cannot close (list them in the report)
- PH primary: no scheme picked.
- Grout colours: proposals only.
- Trim finishes: proposal only.
- Powder sink wall: full height or wainscot - full height assumed.
- Niche widths not dimensioned: DD primary shower, SX Bath 2.
- Linear drains + one-way slope (DD primary, SX primary, PH Bath 2): not modelled; do not model.
