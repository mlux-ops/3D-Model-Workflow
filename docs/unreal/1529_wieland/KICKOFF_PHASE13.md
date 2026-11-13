Phase 13 (the proposed hotel at 1520-1528 N. Wells, "The Duke of Wells") of the 1529 N. Wieland scene plan, unattended

What this session is for

The owner learned on 2026-11-13 that the neighbouring building and the adjacent empty lot are to be redeveloped as a large hotel, and asked for it to be modelled into the site at once. You are adding it to the Unreal Engine 5.9 project `D:\Unreal_Engine_Projects\Wieland1527 5.9\Wieland1527.uproject`, through the editor's agent server (unreal-mcp), following the plan in `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\PLAN.md` (section "Phase 13"). Phase 11 (packaging) was interrupted for this and resumes after you finish. You have none of the earlier sessions' memory; their records are in the plan folder.

You are running from a terminal, not the editor's panel, and nobody will answer questions. The owner is away and has said the work must not stop. Decide what you can, and put anything that truly needs the owner in the final report. A supervisor checks your progress every 5 minutes and relaunches you if you stop.

If `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\phase13_results.md` already exists, an earlier session started this phase: read its "How to resume" section and its journal from the bottom up, inspect what exists, and continue from the first unfinished line. Do not repeat finished work.

What is known (Chicago YIMBY, 11 February 2024, https://chicagoyimby.com/2024/02/demolition-permit-issued-for-1528-n-wells-hotel-project-in-old-town.html, read 2026-11-13)

- A 12-storey hotel, "The Duke of Wells", at 1528 N. Wells Street, 151 feet tall, 203 rooms. Developer Condor Partners; architect Pappageorge Haymes; interiors Summer Thornton; general contractor McHugh Construction. A foundation permit was issued in 2022. A demolition permit (February 2024) removes the three-storey building at 1520 N. Wells.
- Several terraced setbacks. Red and dark grey brick facades; loft-style windows about eight feet tall. A rooftop lounge and terrace.
- Parking in a three-storey garage at the rear, screened by a pair of three-storey single-family homes.
- 1529 N. Wieland's rear lot line faces the public alley; the west side of Wells (even numbers) backs onto the same alley. The hotel is therefore the project's rear neighbour across the alley, and the "empty lot" the owner names is part of its site. Confirm all of this from the parcel data before building anything.

What to find before modelling (research is approved for this phase)

1. The site: the parcels of 1520 to 1528 N. Wells and any other parcel the project uses (the rear homes and garage), from the county parcel data Phase 2 downloaded (look under `E:\Wieland1529_site_data\` and in `phase2_results.md` for where it is), with their outlines in the project's coordinates. Record which buildings in the present site model stand on them (the earlier detailed neighbour buildings and the Revit neighbour massing).
2. The design: read the article's renderings, the developer's and the architect's project pages, the City of Chicago building-permit records (Chicago Data Portal, "Building Permits") and any zoning or planned-development documents for 1520-1528 N. Wells. Look for drawings or numbers: floor heights, setback depths and the floors where they occur, the footprint of the tower, garage and homes, the facade pattern. Reading web pages is approved. Saving rendering images, drawings and permit records as reference only is approved, at no cost and without accounts: keep them under `E:\Wieland1529_site_data\proposed_hotel\`, list each in `asset_downloads.csv` with its source and the date, 500 MB at most. Never ship a downloaded picture as a texture.
3. Write what you found into `proposed_hotel.md` in the plan folder: every dimension with its source, and every dimension you had to estimate (for example from counting floors and window bays on a rendering), with the method and a stated uncertainty.

What to build

- A new level `/Game/Wieland1529/Site/L_ProposedHotel`, streamed into the top level `/Game/Wieland1529/L_Site_M4`. It holds the hotel tower with its terraced setbacks and roof terrace, the three-storey rear garage, and the two three-storey single-family homes, placed on the confirmed parcels at the confirmed or estimated heights (151 feet to the top, 12 storeys).
- The facade at the level of detail of the earlier detailed neighbour buildings, not a plain box: brick bands in red and dark grey as the renderings show them, recessed window openings of about eight feet with frames and glass, the setbacks, and a parapet. Build the geometry with the editor's own modelling tools or generated meshes; no store or paid assets. Use the project's own parent materials (Phase 5 and Phase 12) for brick, glass and metal. Every material follows the repository rule: seamless and non-repeating, with a colour map, checked under grazing light.
- A Variant Manager list (a set of switchable options) named `Neighbour development`, with the option "Duke of Wells (proposed)", which is the default, and the option "Existing buildings (as surveyed)". The proposed option hides the existing buildings on the hotel's parcels by recorded override, never by editing or deleting them. Test both options both ways.
- Label it on every sheet as "proposed, modelled from published renderings and records, not a survey".

What to check, and how to hand back to Phase 11

- Render a side-by-side sheet of your model against each published rendering, from as close to the same viewpoint as you can, under `review\phase13\`, and measure the height and setbacks on the model against your recorded numbers.
- Render the views from the project that see the hotel: the rear of 1529 and its roof deck, the alley, and every station S1 to S9 and design view D1 to D5 whose picture changes. List in `phase13_results.md` which views change, so Phase 11 re-renders exactly those stills.
- Note the hotel's shadow on 1529 at the plan's review condition (15 August, 15:30) and in the morning, with a picture, since the hotel stands on the east side.
- Re-run the exterior part of the camera path once and record frame time and video memory before and after, so the cost of the new level is known.

Done means

- `phase13_results.md` has the journal (a line marked PENDING before each step, committed before you start it, and a "How to resume" section), the findings, the list of views to re-render, the before-and-after numbers, and a first `Status:` line that says DONE with the time.
- Every error is logged in `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\PROJECT_MEMORY.md` with cause, fix and status, in a new section for Phase 13.
- Everything is committed by explicit path in the plan's working copy on its current branch. Do not push.
- Then stop. Phase 11 resumes in its own session.

Read these first, and only these

1. In `PLAN.md`: "Rules for every phase", "Approvals this plan will ask for", "Phase 4" (surroundings: zones and the detail level of neighbour buildings) and "Phase 13".
2. `phase4_results.md` and `phase7_results.md`: how the neighbour buildings and the surroundings variant list were built and saved, and their tools. Reuse those tools rather than writing new ones.
3. `phase11_results.md`: its status lines, so you know what Phase 11 had done (stills, ground cut) when it was interrupted.
4. The material sections of `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\AGENTS.md` and `WORKFLOW.md`.
5. The last three sections of `PROJECT_MEMORY.md`.

What is still the owner's

- Standing approval: the no-cost rows of the plan's approvals table, inside their caps, and the research and reference downloads named above. Anything with a price, an account or key, any deletion, any change to Revit, Windows, drivers or the graphics card, and any push or merge is not approved: put it in the final report.
- Where the published material does not settle a dimension, estimate it, label it, and list it for the owner. If drawings with dimensions turn up in public records, prefer them over the renderings.

Rules that apply throughout

- Nanite ray tracing is OFF for every render, path-traced included: keep the console variable r.RayTracing.Nanite.Mode at 0 at all times and never set it to 2. In UE 5.9 it hung the graphics card three times (NaniteClusterRayTracing.usf line 539). Path-traced pictures trace the meshes' simplified fallback copies; say so on each sheet. Render one picture at a time and let a freshly opened level settle five minutes first. The agent server does not answer while a picture renders, for up to about 11 minutes.
- Never save `/Game/Wieland/R15_Landscape/L_R15_Production`, never use "Save All", save named assets only, and never edit an asset that Datasmith created; apply changes as overrides, instances, new assets or recorded swaps.
- Memory: the machine has about 79 GB of commit, and other programs hold a large share. Before any heavy step, read free commit; if it is under 30 GB, unload what you can, or close and reopen the editor (nothing unsaved matters once your named assets are saved), and wait rather than start. Log the editor's committed memory every few seconds during heavy steps.
- Build the tower's lowest storeys first and look at them before building the rest.
- Put back any console or quality setting you change for a render, and read it back to confirm.

Finishing the work

Keep going until the done list is met. If you notice yourself offering to stop or handing back a list of remaining steps, do the next step instead. Errors, timeouts and failing tools are ordinary obstacles: diagnose them and work through them. If the editor crashes, the supervisor restarts it; when it is back, check what survived against your journal and continue. If the same step crashes twice, change one thing at a time; after two further crashes of that step, record the best workaround with evidence and move on. If something stalls, say in one line what is stalled, for how long, and the last stage verified, then try another route.

Progress and the final report

Give a one-line update as each step finishes. Finish with a report that stands on its own: what the hotel is and where, every dimension with its source or its estimate, what was saved or changed in the project, how to switch between the proposed hotel and the existing buildings, which views change, the shadow finding, the frame-time cost, the short list of items that need the owner, and the full path of every file you wrote.

The owner knows Revit and construction well and Unreal less well. Use plain words and full sentences, say what an Unreal term means the first time you use it, and use the same word for the same thing throughout.
