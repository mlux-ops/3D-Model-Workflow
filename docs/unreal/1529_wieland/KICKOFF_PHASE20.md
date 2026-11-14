Phase 20 (refine the skyline and the surrounding buildings from open street-level and licensed photographs) of the 1529 N. Wieland scene plan, unattended

What this session is for

Phase 17 rebuilt the surroundings and the downtown skyline from the 2022 laser scan, with clean built roofs, and materials chosen by building type where no source said otherwise. The owner wants the buildings refined from images: their cladding, colours, window and mullion patterns, crowns, cornices and other visible details, so the model looks like the real place. You work in the Unreal Engine 5.9 project `D:\Unreal_Engine_Projects\Wieland1527 5.9\Wieland1527.uproject` through the editor's agent server (unreal-mcp). The plan folder is `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\`. You have no memory of earlier sessions; their records are in the plan folder.

You are running from a terminal and nobody will answer questions. Decide what you can and put anything that needs the owner in the final report. A supervisor checks your progress every 5 minutes and relaunches you if you stop.

If `phase20_results.md` already exists in the plan folder, read its "How to resume" section and journal from the bottom up, and continue from the first unfinished line.

Image sources (approved by the owner on 2026-11-14)

1. **The owner's own photographs** in `D:\Wieland1529_owner_photos\` (empty at the start; check it again before finishing). They outrank every other source. Where a photograph shows enough known landmarks, solve its camera and compare the model with an overlay.
2. **KartaView** (formerly OpenStreetCam) street-level imagery, CC BY-SA, through its public interface without an account. Look first at what exists around the site and along the views to downtown.
3. **Wikimedia Commons** photographs under free licences: best for downtown towers and landmarks.
4. **Mapillary** only if a token file `D:\Wieland1529_owner_photos\mapillary_token.txt` exists (the owner creates it; never create an account or key yourself, and never write the token into any file, log or commit).
5. **Never** Google Street View, Google Maps, Google Earth or Google 3D tiles, and no other copyrighted web photographs for matching (a manufacturer's or architect's page may confirm a fact such as "clad in black granite", noted with its address).

All images are reference only: never ship one as a texture, never trace one into geometry beyond confirming what the laser scan already measured. Save the images you use in `E:\Wieland1529_site_data\phase20\` (10 GB at most, no cost, no account), list each in `asset_downloads.csv` with source, author, licence and address, and note CC BY-SA attribution in the licence table. Query the public interfaces politely: small areas, a pause between requests, no contact details in request headers.

What to do

1. **Work list:** from Phase 17's viewshed table, every skyline tower visible from the penthouse roof deck (D1) and every Zone 1 and Zone 2 building visible from the stations and decks, ordered by how much of the views each fills. Do them in that order, skyline from D1 first, committing as you go, so whatever is finished is usable if the weekly usage allowance runs out.
2. **For each building:** gather the images that show it; record what they show (cladding material and colour, glass tint and reflectivity, mullion and window grid, spandrels, crown and roof features, cornices, bays, stoops, signage left out); update its material instance and, where the images show a detail the scan's clean form lacks (a cornice line, a setback lip, a crown frame), add it as a clean built element. Keep Phase 17's measured geometry; images do not override the laser scan on positions and heights.
3. **Materials:** use the project's parent materials and public-domain texture sets, coloured and scaled to match. Every material follows the repository rule: seamless and non-repeating, with a colour map, checked under grazing light. Window grids are scaled to the building's real floor height and bay width.
4. **Confidence:** give each building a confidence from 1 to 5 that it looks like the real building, with the images it rests on; list every building still resting on an assumption.
5. **Check:** the roof-deck skyline panorama again, labelled, beside the two licensed skyline photographs Phase 17 used; re-render stations S1 to S9 (except S7) and design views D1 to D5 in real time and D1 path-traced; side-by-side sheets with the Phase 17 versions; frame time and video memory on the exterior and roof-deck paths against the Phase 9 budget.

Done means

- `phase20_results.md` in the plan folder: a journal (a line marked PENDING before each step, committed before you start it, and a "How to resume" section), the building table (name or address, images used with licences, material set, details added, confidence), the check sheets, the frame-time cost, the items for the owner, and a first `Status:` line that says DONE, with the time.
- Every error is logged in `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\PROJECT_MEMORY.md` with cause, fix and status, in a new section for Phase 20.
- Everything is committed by explicit path on the current branch; downloaded images are not committed. Do not push. Then stop: Phase 19 (the owner's path videos) starts next.

Read these first, and only these

1. `phase17_results.md`: status, the viewshed table, the skyline and Zone 1 tables, the materials table with its assumptions, the levels and tools.
2. In `PLAN.md`: "Rules for every phase", "Budgets" and "Phase 17".
3. The material sections of `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\AGENTS.md` and `WORKFLOW.md`.
4. The last three sections of `PROJECT_MEMORY.md`.

Rules that apply throughout

- Never close, quit, kill or restart the Unreal editor yourself (owner, 2026-11-14). Only the supervisor's watcher restarts the editor, and only after a crash.
- Memory: there is no free-memory floor (owner, 2026-11-14); do not wait or stop because free commit memory is low. Log the editor's committed memory every few seconds during heavy steps.
- Nanite ray tracing stays OFF: keep the console variable r.RayTracing.Nanite.Mode at 0; mode 2 hung the graphics card three times. Render one picture at a time and let a freshly opened level settle five minutes first.
- Never save `/Game/Wieland/R15_Landscape/L_R15_Production`, never use "Save All", save named assets only, never edit a Datasmith asset; changes are overrides, new assets or recorded swaps, and the older surroundings options stay switchable.
- Use the Edit tool, not shell commands, for any text containing backslashes (earlier sessions turned `\t` into tabs).
- Put back any console or quality setting you change, and read it back to confirm.
- Not approved: anything with a price, any account or key, any deletion, any store or Fab asset, Google content of any kind, any change to Revit, Windows, drivers or the graphics card, any push or merge.

Keep going until the done list is met; treat errors and failing tools as ordinary obstacles; if the same step fails twice, change one thing at a time. Write for the owner in plain words: they know Revit and construction well and Unreal less well. Give a one-line update as each building or step finishes, and finish with a report that stands on its own, with the full path of every file you wrote.
