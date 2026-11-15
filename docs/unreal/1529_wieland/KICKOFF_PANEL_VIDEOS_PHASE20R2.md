# Kickoff prompt: the owner's path videos, then Phase 20 round 2, editor panel

Written by the supervising session on 2026-11-15 for the owner to paste into the Unreal editor's agent panel. Everything below the line is the prompt.

---

Make the owner's seven walking-path videos and a new delivery revision, then refine the surroundings again from the new photograph set and the owner's skyline sightline sheet (Phase 20, round 2), for the 1529 N. Wieland scene plan

What this session is for

Earlier in this panel session (2026-11-15, from 10:57), you or a previous chat refined the John Hancock Center (875 N Michigan) at the owner's request: tapered, angled sides and visible exterior cross-bracing, in place of the rectangular box. Keep that work. If its journal lines or commit are missing, record it now in `phase20_results.md` (a round-2 journal line with what changed and the asset names) and commit it, then go on. In Part 2, check Hancock in the panorama with the others rather than rebuilding it.

You are working in the Unreal Engine 5.9 project `D:\Unreal_Engine_Projects\Wieland1527 5.9\Wieland1527.uproject`, for the plan in `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\PLAN.md`. You have none of the earlier sessions' memory; their records are in that plan folder. Phases 17, 20 and 19 are DONE (2026-11-14). The owner is away and wants the work to keep going: decide what you can, and put anything that truly needs the owner in the final report.

Part 1: the owner's path videos (do this first)

- The owner drew and saved seven paths on the path page (http://127.0.0.1:8766/) and pressed "Request videos" at 01:17 on 2026-11-15. `owner_review\paths\RENDER_REQUEST` lists them: Roof Deck, Basement Tour, First Floor, Fourth Floor, Grade Level, Second Floor, Third Floor. A pending request is kept until you rename it.
- A path named "Roof deck looking towards skyline" is saved but was not requested. Do not render it; mention it in the report.
- Follow `owner_review\paths\RENDER_HOW.md` and the "How to resume" section of `phase19_results.md`. In the editor's Python, run `wieland_paths.render_requested()` from `tools\wieland_paths.py`. It renders each requested path into `delivery\video_paths\<name>.mp4`, refuses a path that passes through a wall and gives the place, and writes `owner_review\paths\last_render.json`. Render one video at a time.
- These paths are long (35 to 204 points). Before the full set, render the shortest (Grade Level) and watch it: check it is the right floor, it does not walk through walls or furniture, the eye height is right, and the motion is smooth. Fix the tool, not the owner's path, if something is wrong; if a path itself is impossible, refuse it with the reason and place, as the tool does.
- Then rename `RENDER_REQUEST` to `RENDER_REQUEST.done_<yyyyMMdd_HHmm>`.
- Make delivery revision r3 as Phase 19's brief, step 6, describes (`KICKOFF_PHASE19.md`): the videos and updated notes in a new dated package `D:\Wieland1529_delivery\package\1529_Wieland_UE5.9_Delivery_<date>_r3\` and in Google Drive `F:\My Drive\Folders\3D Model Workflow\3D Models\1529_Wieland_UE5.9_Delivery_<date>_r3\`, each file checked by size and SHA-256. Mark r2 as superseded in both places with a SUPERSEDED.md note, and delete nothing.
- Record this in `phase19_results.md`: add journal lines (each one PENDING and committed before its step), and a short "Owner videos" section with each video's length, render time and any refusal. Phase 19's first Status line stays DONE; add the new time to it.

Part 2: Phase 20, round 2

Read `phase20_results.md` first: the journal, the building table and the report. Round 2 continues that file. Change its first Status line to "IN PROGRESS (round 2)" and add journal lines from J9 on. Then do the following.

1. **The owner's skyline sightline sheet.**
   - Sources: `reference\1529_The_Wieland_Skyline_Sightline_Sheet.pdf`, with its 27-landmark schedule as `reference\skyline_landmarks_owner_sheet.csv`. The sheet gives each landmark's true bearing, distance, roof and tip height, and elevation angle from a 52 ft penthouse deck eye.
   - The model's D1 eye is at Z = 1,684 cm, about 55 ft above the level's origin. Say what that origin is, and work in the same terms.
   - For each of the 27, find its building in the model (county id) and measure from the model the bearing and the angle up to its roof and its tip from the D1 eye. Put the sheet's and the model's numbers side by side in a table in the results file.
   - The sheet computed its numbers from the street-address grid, so a difference of 1 to 3 degrees in bearing is expected. The laser-scan geometry from Phase 17 stays the authority on positions and heights.
   - What the sheet settles is the list. All 27 must be present and labelled in the roof-deck panoramas.
     - Any landmark missing from the model, hidden when it should not be, or off by more than 3 degrees in bearing or 1 degree in elevation is a fault. Find the cause and fix it, or explain it.
     - A tree in the way is a valid explanation. Say whether the view is leaf-on or leaf-off.
   - The supervisor's quick match found these 27 landmarks by name in the Phase 17 targets: 900 N Michigan, Waldorf Astoria, One Chicago, Aon, Two Prudential, Trump, 330 N Wabash, Chase, 300 N LaSalle, Franklin Center, 311 S Wacker, Willis, 110 N Wacker. The others could not be matched by name and need finding by footprint.
   - Several of those matched show zero visible cells from D1 in leaf-on conditions: Waldorf Astoria, One Chicago, Aon, Two Prudential, 900 N Michigan. Check them against the panorama frames.
2. **The landmarks as buildings.**
   - Every one of the 27 not already settled in round 1 gets the round-1 treatment, from photographs: cladding, colour, glass, mullion grid, crown. This includes Hancock, Lake Point Tower, Palmolive, Water Tower Place, One Magnificent Mile, Olympia Centre, Park Tower, St. Regis, Aqua, Blue Cross Blue Shield, NEMA, Salesforce, 150 N Riverside, 110 N Wacker and 311 S Wacker.
   - Where a photograph shows a crown or rooftop feature that reads at the distance it is seen from (1.4 to 5.6 km), build it as a clean element, for example:
     - Hancock's two antennas and its exterior X-bracing as a material pattern;
     - Willis's antennas;
     - Trump's spire;
     - the Palmolive beacon mast;
     - Aqua's wavy balconies as a material, not geometry.
   - Measured geometry stays.
3. **The new photograph set** (gathered by the supervisor on 2026-11-14 and 15; reference only, never shipped, never traced).
   - **Location:** `E:\Wieland1529_site_data\phase20\round2\`.
     - `commons\zone12\`: about 1,300 Wikimedia Commons files from the Old Town categories, Old Town street and business searches, and every geotagged file within 700 m of the lot.
     - `commons\towers\`: files for the 22 skyline towers still resting on an assumption and for the 27 landmarks.
   - **Index:** `round2_index.csv` lists each file with its licence, author, page address, coordinates, what it was gathered for and how it was found. Refused files are in `round2_refused.csv`. `tower_identity.json` gives each unsettled tower's position, the names tried and its OpenStreetMap identity.
   - **A second download pass may still be running** when you start. It appends to the index and the `towers` folder when it ends. Begin with `zone12`, and re-read the index before the towers.
   - **Many files are irrelevant** (zoo animals, food, interiors, the beach). Narrow the list first:
     - files geotagged within about 250 m of the lot, or with Wells, Wieland, North Avenue, North Park, Schiller, Burton, Old Town, Zanies, Up Down Cigar or Ale House in the title or description;
     - then contact sheets, kept outside the repository like round 1's.
   - **Skip zero-byte files.** About 16 failed downloads left empty files.
   - List the files you actually use in `asset_downloads.csv` (rows "Phase 20 round 2"), with author, licence and address, and note CC BY-SA attribution in the licence table.
   - **Other sources checked, with nothing near the lot:**
     - KartaView: no image within 540 m.
     - Panoramax: none within 600 m.
     - Library of Congress survey photographs: none near the lot.
     - OpenStreetMap: no colour or material tags, but storey counts on 319 nearby buildings. Use those to check floor heights and window grids.
     - Openverse: did not answer. You may try it once more through its public interface, without a key.
   - **Never use Google imagery of any kind.** Owner photographs in `D:\Wieland1529_owner_photos\` still outrank everything; check the folder again before you finish.
4. **Zones 1 and 2** (the 48 work-list neighbours on Wieland, Wells, North Avenue and North Park). From any photograph that shows a facade, set its material instance `MI_P17_Z_<id>`:
   - brick colour and bond;
   - stone or painted trim;
   - cornice and bay;
   - window grid scaled to real floor height and bay width;
   - storefronts.

   Add cornices, bays and parapets that the photographs show as clean built elements. Raise each building's confidence only as far as its photographs justify, and keep every assumption listed.
5. **The 22 unsettled skyline towers**, from the round-2 tower photographs, in the same way.
6. **Checks.**
   - The D1 and D1S panoramas again, with all 27 landmarks labelled, beside the Phase 20 round-1 versions and the two licensed skyline photographs.
   - The stills as in round 1, J6.
   - Frame time and video memory on the exterior and roof-deck paths against the Phase 9 budget.
   - Under grazing light: the changed materials, and any repetition visible in them.
7. **Report and status.**
   - Write the round-2 report in `phase20_results.md`: the landmark table, the building table updates, the confidence counts, and the items for the owner. The owner items include a photo list: name the facades and corners whose photographs would settle the most remaining assumptions, with the best standpoint for each.
   - Set the first Status line to DONE, with the time.
   - If anything visible to the owner changed after the r3 package, add the new stills and panoramas to the r3 package on D: and Drive. Update its notes and checksums in both places.

Keeping records

- **The journal:** write each line as PENDING and commit it before its step, then replace it with the outcome.
- **Errors:** log every error in `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\PROJECT_MEMORY.md`, with cause, fix and status, under a "Phase 20 round 2" or "Owner videos" heading.
- **Commits:** commit by explicit path on the current branch, `claude/1529-wieland-scene-plan-e84a03`. Videos and downloaded photographs are not committed. Do not push or merge.

What is still the owner's

- **Covered:**
  - the photograph folder above and the 10 GB cap in `E:\Wieland1529_site_data\phase20\`;
  - the delivery locations on D: and the Google Drive folder named above;
  - at no cost.
- **Not covered; put these in the final report instead:**
  - anything with a price;
  - any account or key;
  - any deletion;
  - any store or Fab asset;
  - Google content of any kind;
  - any change to Revit, Windows, drivers or the graphics card;
  - any push or merge.

Rules that apply throughout

- **Do not restart the editor.** This session runs inside the editor's panel, so closing it ends the session. Never close, quit or restart it.
- **Memory:** there is no free-memory floor. Free memory inside the editor when you need to by opening an empty level and then the working level, or by running garbage collection. Log the editor's committed memory every few seconds during heavy steps.
- **Roofs and details:** every addition is a clean built form, never a draped scan surface. Measured positions and heights stay.
- **Nanite ray tracing stays OFF.** Keep the console variable `r.RayTracing.Nanite.Mode` at 0; mode 2 hung the graphics card three times. Render one picture or video at a time, and let a freshly opened level settle for five minutes first.
- **Saving:** never save `/Game/Wieland/R15_Landscape/L_R15_Production` and never use "Save All". Save named assets only.
- **Datasmith assets:** never edit one; apply changes as overrides, new assets or recorded swaps.
- **Materials:** follow the repository rule. Every material is seamless and non-repeating, has a colour map, and is checked under grazing light.
- **Backslashes:** use the Edit or Write tool, not shell commands, for any text containing backslashes.
- **Settings:** put back any console or quality setting you change, and read it back to confirm.

Finishing the work

Keep going through both parts. If you notice yourself offering to stop or handing back a list of remaining steps, do the next step instead. Errors, timeouts and failing tools are ordinary obstacles: diagnose them and work through them. If the same step fails twice, change one thing at a time. If something stalls, say in one line what is stalled, for how long, and the last stage you verified, then try another route.

Progress and the final report

Give a one-line update as each video or step finishes. Finish with a short report that stands on its own:

- the seven videos (each one's file, length, and any refusal with its reason and place);
- the r3 package on D: and on Google Drive, checked;
- the landmark table's outcome;
- what round 2 changed, with the confidence counts before and after;
- the frame-time numbers;
- the owner's photo list and other owner items;
- the full path of every file you wrote.

The owner knows Revit and construction well and Unreal less well. Use plain words and full sentences, say what an Unreal term means the first time you use it, and use the same word for the same thing throughout.
