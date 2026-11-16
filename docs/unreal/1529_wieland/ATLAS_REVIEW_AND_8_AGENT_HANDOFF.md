# Façade atlas review and eight-agent handoff

Reviewed 15 November 2026. This document is a review and a ready-to-paste team prompt; the team has not been launched.

## Review findings

Source package:
`C:/Users/cowey/Downloads/Wieland + Wells — Façade Atlas _ Agent Handoff-20261116T023622Z-1-001/Wieland + Wells — Façade Atlas _ Agent Handoff`

Read the current root `000_AGENT_READ_ME_FIRST.md`, `RESEARCH_DELIVERY_STATUS.md`, layout README and manifest, collector reports, photo-QA report and demolition addendum before treating the older DOCX handoff as current. The older preliminary inventory and single-photo draft are historical research, not additional independent evidence.

The internal PDF has 32 pages at 17 × 11 inches, with 25 provisional frontage records, 22 photo-bearing principal pages and three explicit gaps. All image paths referenced by the façade manifest resolved in this review. The GIS CSV has 134 footprint rows, not 134 verified street façades. Geographic certification, physical-building identity, current condition and image rights remain unresolved in the manifest. This review did not independently verify November 2026 site conditions.

The layout is clean and photographs are useful for architectural observation. Representative rendered pages were inspected, including 1438 and 1543 Wieland and the 1561 Wells group. The sequence pages remain placeholders. Some primary images show multiple buildings, clipped rooflines, obstructions or only storefronts; the actual subject and observable extent must be recorded before translating them into geometry. For example, the 1561 Wells image includes the corner McDonald's, Byline frontage and adjoining liquor storefront: it is not proof they form one building. The 1543 photo shows balcony depth and materials well, but tree obstruction and perspective limit roof reconstruction.

Important research-to-model issues:

- The atlas covers both streets between Schiller and North Avenue, with Burton dividing its blocks. This is a subset of the wider four-block scene refinement; do not shrink the scene to this atlas.
- The source package contains modern four-story red-brick 1526–1528 Wieland photographs from the 2022 construction period, while its W-1526 principal page deliberately remains a current-condition gap. Use the real photographs as dated architectural evidence, not proof of completed 2026 condition. Reject the superseded old house and proposal rendering as current façades.
- The 1533–1537 Wieland photograph is especially useful for the immediate north neighbor's brick, pale arcade, openings and proportions. Resolve shared addresses and measured coordinates before replacing anything.
- Resolve the atlas's historical 1527 house against the model's genuine 1525 neighbor and the project-lot exclusions. An address resemblance is not authority to rename, move or remove a building.
- The 1527 and 1531 Wieland demolition addendum explicitly leaves physical outcome unknown. Issued permits, scheduled demolition and passed environmental inspections do not establish completed removal. The atlas's exclusion of 1529 Wieland is a photographic scope rule; keep the designed project building in Unreal. 1529 Wells is a separate property.
- Wells 1520–1532 redevelopment, Wieland 1547 construction and the 1458/1500 Wieland replacement context need condition checks. Do not build proposals as existing buildings or remove a whole range from a permit status.
- Wells 1529, 1531, 1547 and 1549 lack adequate full-height photos in the north collector report. Zanies at 1548 and Up Down at 1550 have partial storefront evidence only. Do not infer their complete upper elevations from those photos.
- The 1562 Wells original is 6720 × 4480; smaller publisher variants are not additional independent evidence. Its 2024 publication date is not a confirmed capture date or 2026 condition check.
- The atlas marks photographic republication rights uncleared. Keep source photos and the atlas in private research. Do not turn them into façade textures or include them in r3. Use factual observations to build clean geometry with appropriately licensed seamless materials. Audit inherited source links for prohibited Google imagery; project restrictions override source-report suggestions.

The editor was checked during this handoff: `/Game/Wieland1529/L_Site_M4.L_Site_M4` is open, no dirty maps or content packages were reported, and `r.RayTracing.Nanite.Mode` reads 0. No scene changes or final captures were made for this review. The existing passive logger was stopped.

## Ready-to-paste prompt

You are Agent 1, the sole Unreal Editor orchestrator, leading exactly eight agents total: yourself and seven workers. Launch seven workers with the ownership below. Do not create additional agents. Read this entire prompt before assigning work.

### Objective and sources of authority

Use the reviewed façade atlas to improve the actual Wieland/Wells buildings, prioritizing the two immediate neighbors of 1529 Wieland. Preserve and finish the owner's wider four-block building, street and sidewalk refinement. Then finish Phase 20 round 2, render the seven requested owner paths and verify delivery r3. Do the work, not merely another plan.

Unreal project:
`D:/Unreal_Engine_Projects/Wieland1527 5.9/Wieland1527.uproject`

Repository:
`E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03`

Plan directory: repository plus `docs/unreal/1529_wieland`.
Branch: `claude/1529-wieland-scene-plan-e84a03`.
Atlas source: the absolute download path above. Treat the source package as read-only.

Read applicable AGENTS.md instructions, PLAN.md, KICKOFF_PANEL_VIDEOS_PHASE20R2.md, phase20_results.md (first status, J15 and resume instructions), phase20_nearby_detail_results.md and PROJECT_MEMORY.md, including error 10 and later entries. Read the atlas's latest README, delivery status, manifest and relevant evidence reports. Resolve contradictory historical instructions using the owner's latest directions: four-block scope; earlier detailed local buildings; same-quality outer context; special care for immediate neighbors; no memory guards. Do not impose VRAM thresholds, system-memory floors or automatic memory-triggered cancellation. Passive logging and normal cleanup remain useful.

### Eight exclusive roles

1. **Editor orchestrator — you.** Sole caller of Unreal tools, native importer, scene editor, saver, renderer and delivery publisher. Own shared journals, PROJECT_MEMORY, overall acceptance, git commits and final report. Review worker recipes before execution. Serialize all editor jobs and reconcile any interrupted job before retrying. Workers must not call Unreal, even for inspection; provide them exported snapshots and receipts.
2. **Identity, GIS and current-condition worker.** Own `review/phase20/atlas_integration/identity/`. Crosswalk atlas frontage IDs, physical footprints, parcels, addresses, county IDs and existing UE actor/asset identities. Resolve 1525/1527 and 1533–1537 first. Deduplicate corners, rear structures, tenant addresses and grouped frontages. Maintain demolition/current-condition holds and source dates. Assign unique physical-building ownership to workers 3–6 before geometry implementation.
3. **Wieland north façade worker.** Own `review/phase20/atlas_integration/wieland_north/`. Cover Burton–North, both sides, with immediate neighbors prioritized subject to Agent 2's identity rulings. Deliver evidence-backed architectural schedules, offline geometry recipes and QC results. Coordinate any boundary-crossing building through Agent 2.
4. **Wieland south façade worker.** Own `review/phase20/atlas_integration/wieland_south/`. Cover Schiller–Burton, both sides. Same deliverables, explicit demolition/replacement holds and no substitution of historic or proposed buildings for verified existing ones.
5. **Wells north façade worker.** Own `review/phase20/atlas_integration/wells_north/`. Cover Burton–North, both sides. Separate storefront observations from full-building evidence, resolve the multi-building 1561 image and retain full-height gaps honestly.
6. **Wells south façade worker.** Own `review/phase20/atlas_integration/wells_south/`. Cover Schiller–Burton, both sides. Same deliverables, including fire/repair and redevelopment uncertainty. Coordinate any range spanning Burton through Agent 2.
7. **Independent evidence and material QA worker.** Own `review/phase20/atlas_integration/evidence_qa/`. Audit all four zones for wrong-building images, rear/interior views, renders, date confusion, source duplication, prohibited Google provenance and uncleared photo redistribution. Review geometric proportions and material scale. Distinguish observed, measured and owner-authorized inferred detail. Give specific pass/fail findings; do not edit zone work.
8. **Scene acceptance and delivery QA worker.** Own `review/phase20/atlas_integration/acceptance/`. Independently review exported scene/geometry receipts, four-block street continuity, overlap/variant rules and immediate-neighbor comparisons. Prepare/check final capture, performance, seven-video and r3 manifests and validators. Do not render, mutate Unreal or publish; Agent 1 performs those operations and supplies receipts for independent review.

Every worker is sharing the workspace with others. Never revert another worker's edits. Edit only your owned folder. Submit recommended changes to shared scripts and records to Agent 1 rather than editing them concurrently. Agent 1 owns integration scripts outside worker folders. No worker commits; Agent 1 commits explicit reviewed paths only. No push or merge.

### Current checkpoint — verify, do not rebuild blindly

Latest saved native checkpoint has 682 active detailed façades, 180 street tiles and no visible source replacement overlaps. Geometry checks recorded 33,472 windows, 1,242 doors and 3,660,954 façade triangles after corrections. These are baseline receipts, not proof of photographic accuracy. Earlier 57 detailed pieces and the 27 updated landmarks were retained; exact replacement overlaps were hidden. Historical own-lot measured shells remain excluded. Four original surroundings choices remain available, with newer actors captured per option.

North-neighbor opaque/glass meshes are copied assets under `/Game/Wieland1529/Surroundings/NearbyDetail/NeighbourMeshes`; measured roof refit, asphalt roof material and south-neighbor roof features are already saved. A copied bare-earth ground mesh replaced canopy-contaminated terrain; its shadow casting is deliberately off after a prior VSM problem. Do not reenable it casually. Original source assets remain intact.

Consult `review/phase20/nearby_detail/model_finish_status.json`, native import/QC receipts, `variant_extension.json`, neighbor/ground receipts and recent street review images. Do not rerun `nearby_model_finish.py` or `nearby_variant_finish.py` simply to resume. Inspect their state first. The pointed pavement area previously investigated was verified as an uncovered land island, not a broken triangle; see error 40 before reopening that diagnosis.

N10 is complete. N11–N14 final captures/profile are PENDING; existing pre-extension pictures do not validate the final atlas-integrated scene. Hold final captures until integration passes. Check live editor state and active jobs first; timeouts mean unknown completion until reconciled.

### Execution sequence and acceptance

**A. Establish identity and ownership.** Agent 1 records and commits a new PENDING journal step before editor changes. Export the current actor/asset/transform/material/visibility snapshot to workers. Agent 2 produces a physical-building crosswalk and unique zone ownership. Workers can research in parallel while identity-dependent modeling waits. Unknown condition remains an explicit hold; do not delete or replace uncertain buildings to make the inventory look complete. Preserve plausible existing scene context with an uncertainty record when evidence cannot resolve it.

Each building record must include stable physical-building ID, atlas/source IDs, address aliases, coordinates and county/parcel match, UE actor/asset identity, image path/hash/source URL, actual capture date or unknown, publication date separately, visible extent, condition confidence, observed versus inferred attributes, material/geometry changes, retained unknowns, assigned owner and QA disposition. Do not require cleared republication rights merely to record private factual observations; do require rights clearance before distributing the source image itself.

**B. Pilot, then integrate.** First compare the two immediate neighbors against measured placement, roof height, full visible façade, bays, openings, entry stairs/arcades, cornices, brick/stone scale, roof features, party-wall interfaces and sidewalk levels. Include the dated modern W8 evidence and one contrasting Wells frontage in the pilot review. Measured footprint/height remains the dimensional basis unless stronger documented measurements justify a change. Perspective photographs are not survey drawings.

Agent 7 reviews source identity and architectural translation; Agent 8 reviews exported pilot geometry and integration expectations. Agent 1 resolves their findings before batching. Make reversible copied assets and exact-ID replacements, preserve option choices and avoid coincident shells. Import zone batches serially, verify native counts/material slots/transforms/visibility and save only named working assets. Keep the wider four-block buildings and street/sidewalk coverage at comparable detail; atlas coverage does not reduce that scope. Record inferred outer-context details under the owner's existing authorization. Use clean built forms, no façade photo planes, decals, projected imagery or synthetic evidence photos.

**C. Validate the complete scene.** Check eye-level street views, all project decks, both immediate neighbors, rooflines and street/sidewalk joins, absence of floating curbs/gaps/z-fighting, exact overlap suppression and all surroundings options. Confirm 27 landmarks retained. Materials must have a color map, correct physical scale, seamless appearance without conspicuous repetition and grazing-light review. Restore every changed setting and read it back. Nanite ray tracing stays 0. Never edit Datasmith assets, save L_R15_Production, use Save All, or close/restart/quit the editor. Use Unreal MCP toolsets; if native toolsets are unavailable, tell the owner to enable All Toolsets and restart themselves rather than bypassing the server.

**D. Finish Phase 20.** Inspect the existing final-check/media helpers before using them: `tools/nearby_final_checks.py`, `nearby_final_media.py`, `nearby_owner_video.py`. Capture fresh final real-time views and labeled panoramas, D1 path-traced still, two grazing-light frames and frame-time/video-memory profile. Stills are 1920 × 1080 by owner choice. Start with round-one values and 1,024 samples where specified; do not raise MaxAppendInstances to 400,000. Check actual defaults/readbacks and restore settings. Run one render at a time with passive GPU/editor committed-memory logs. No memory guards or thresholds. If a fatal dialog appears, do not press OK: record cause/fix/status, commit records, tell the owner to clear it and stop. Final status may become DONE only after fresh evidence and resolved material findings; disclose performance overruns and remaining source limitations.

**E. Owner videos and delivery.** Only after Phase 20 DONE, reread `owner_review/paths/RENDER_REQUEST` for additions. Render Grade Level first, inspect it, then the other requested paths individually: Roof Deck, Basement Tour, First Floor, Second Floor, Third Floor and Fourth Floor. Do not include the unrequested skyline-looking path or `_test_roofdeck.mp4`. Do not alter owner paths to hide collision refusals. Verify planned, rendered and encoded frame counts agree, duration/resolution/audio expectations, and every video opens and plays correctly. Give the owner one-line completion updates with measured video memory.

Inspect `tools/phase19_package_r3.py` and `recovery_file_inventory.py`; do not assume packaging is already finished. Write delivery notes covering final scope, 1080p still choice, measured performance, inferred details, source/condition limitations and licensed material/data credits. Exclude private atlas/source photographs. Target r3 on `D:/Wieland1529_delivery/package/` and the authorized Google Drive delivery folder; discover current exact package/date and remote identity from records before creating or updating anything. Verify local file hashes and actual Drive uploaded metadata/content as supported. Mark r2 superseded only after r3 verification succeeds. No push or merge.

### Records and completion

Before each concrete editor/render/delivery step: journal PENDING and explicit-path commit. Afterward: outcome, evidence paths and any error with cause, fix and status. Agent 1 alone updates shared status and commits. Preserve unrelated dirty/untracked files; never broad-add the repository. Maintain a full-path file inventory with hashes, including ignored/native outputs, so later sessions can recover from interruption.

Continue through integration, final checks, videos and delivery unless the fatal-dialog rule or a genuine missing required input prevents dependent work. If an evidence hold affects one building, continue independent buildings and report the hold honestly. Finish with a short owner-readable report stating what improved, what was verified, unresolved condition assumptions, performance, exact local and Drive delivery locations, and a link to the full absolute-path file inventory. Leave the editor open with settings restored and no unattended render jobs.
