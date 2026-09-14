# Project memory

## Scandinavian hex material — 2026-09-13
- User specified 6 x 7 inch hexagons and installation orientation from supplied room photo. Interpreted as flat-top hexagons 7 inches wide x 6 inches high, with 1/16 inch estimated grout. Printed fan artwork is sampled from the supplied real tile image; 0/120/240-degree rotations meet at shared vertices. Bump represents joints/bevel only, not printed white lines.
- Error during Revit batch startup UI observation: `foreground window did not report a process id`. Cause: batch window disappeared before capture. Solution: batch completed successfully; launched a separate interactive Revit instance and captured its returned window. Resolved.
- E025 recurrence: Scandinavian native V-Ray scene parsed with zero warnings, but render returned license -98. No renderer-side visual validation is claimed. Revit API source project was saved/reopened successfully with zero warnings.

## Material-map correction — high-resolution review rebuild, 2026-09-13
- Confirmed implementation defect: prior map generation converted resized imagery and blurred luminance to 8-bit grayscale before subtracting illumination and calculating gradients. This creates stepped height values even in a nominally 16-bit export. It is a plausible contributor to user-observed ridges, not proof of the sole renderer-side cause.
- Rebuilt from the inspected StoneLocator single-tile 2560 x 1269 photograph with float filtering/resizing/gradients, 16-bit height and RGB16 normal output. Height now has 29,454 distinct values. Lossless PNG and ZIP integrity checks passed. Native render remains unverified; do not claim artifacts eliminated from a flat preview.
- Output: output/adella_highres_review/MSI_Adella_HighRes_Review.zip. Existing native ADSKLIB reused; maps at its original absolute paths refreshed, and instructions require explicit repathing to the new package to avoid stale extracted/cached maps.
- Standing material workflow: use real product imagery, report native pixels per tile separately from exported resolution, preserve float precision until final export, and validate map mode/bit depth before rendering. Larger lifestyle images do not necessarily offer more pixels per tile. User reviews local files and submits PR after confirmation.

## Standing user instruction

**2026-09-11 — Always log every error and its solution in this project memory.** Applies to future tasks as well as the current task. Record unresolved errors with their current status and update them after a fix. See AGENTS.md for the required fields.

The entries below backfill known errors from the sample-holder and PolyTerra work. Dates refer to when they were recorded unless a precise occurrence date is available. They summarize observed results; they do not establish physical performance.

## Current sample-holder context

- Active design: **QuietMount Capsule**, under `output/quietmount-v5-capsule`.
- User selected a single rounded lower cradle and small upper keeper, with concealed screws and no structure behind transparent samples.
- Five sets: 12.7 mm, 19.05 mm, 19.05 mm, **20 mm measured terrazzo**, and 22.225 mm. Use measured thickness, not nominal thickness. Squares are approximately 95.25 mm wide and high.
- Printer/material: Bambu H2D, 0.4 mm Standard nozzles, Textured PEI, PolyTerra PLA.
- Current capsule package has passed digital geometry checks and native slicing. The user physically tested the **snug** cover and confirmed a nice fit and removal using the fingernail groove. Sample retention, creep and wall-anchor/load performance remain untested; screw fit remains unresolved under E011.
- **2026-09-12:** User requested ten sets: original five plus 20.5, 18.5, 18, 14 and 17 mm. Then explicitly requested all non-screw parts first while measuring screws. Delivered scope is **20 snug covers on one plate**, under `output/quietmount-capsule-ten-sets/QuietMount_Covers_Only_READY.3mf`. Screw-mounted bodies are pending actual screw dimensions. This is a scope change, not an error.
- Covers-only plate: exact previously tested snug STL geometry, 10 lower + 10 upper, 0.08 mm PolyTerra/H2D settings, native slice without warnings, approximately 127 minutes / 9.5 g. The original 8 mm cover interface is retained; a larger screw opening could require revisiting the covers.
- Earlier adhesive-frame and independent-peg packages are superseded. Do not assume subsequent corrections were applied to those packages.

## Error and solution log

### E001 — Filament preset silently skipped by Bambu GUI

- Recorded: 2026-09-11; earlier SHB PolyTerra preset review.
- Affected: `output/polyterra-preset-review/SHB_PolyTerra_H2D_Filament.json` and its ZIP.
- Error: File → Import → Import Configs reported **0 configs imported**, and the filament was missing from the dropdown. Native CLI acceptance had not caught this.
- Cause: The custom filament JSON lacked a `version` field.
- Solution: Added `"version": "2.7.0.8"`, corrected the generator, refreshed the original and FIXED copies and the ZIP, and imported through Bambu's GUI.
- Verification/status: **Resolved.** GUI reported **1 config imported**; `SHB PolyTerra PLA Quality @BBL H2D` appeared under Filament → Custom.
- Prevention: A CLI-valid configuration is not sufficient evidence of GUI importability. Use required metadata from a working exported user preset and verify GUI import when validating an importable preset.

### E002 — Capsule process skipped; internal printer file mistakenly shipped

- Recorded: 2026-09-11; user reported that only the filament config imported.
- Affected: `output/quietmount-v5-capsule/presets/QuietMount_Process.json` and the first capsule ZIP.
- Error: Process preset was not recognized. The printer JSON was also unsuitable as a reusable user import.
- Cause: The process again lacked `version`—a recurrence of E001's metadata omission. The printer JSON was a flattened **system** H2D profile generated for CLI use, not a custom user preset.
- Solution: Added process version `2.7.0.8` to the generator. Moved the machine JSON to `internal/machine_H2D_04.json`, changed the CLI path, and explicitly limited shipped presets to process and filament. Regenerated editable/sliced 3MFs and the ZIP. Updated START_HERE.md to use the built-in H2D 0.4 nozzle printer and explain that opening a full 3MF project already supplies project settings.
- Verification/status: **Resolved for the active capsule package.** GUI reported **1 config imported**. Selected `QuietMount Capsule - PolyTerra 0.08 @H2D` in the existing `QuietMount_Capsule_H2D_Project` window. Both plates re-sliced successfully. ZIP inspection confirmed exactly two versioned user presets and no internal machine JSON.
- Prevention: Check required metadata for **every** exported preset type. Keep internal CLI configuration files separate from user-importable presets. Do not require a custom printer import when the built-in printer already matches.

### E003 — Wrong Rectilinear enum caused substitution and rejected export

- Recorded: 2026-09-11; independent-peg and capsule project creation.
- Error: A project export returned **-18**, `Invalid parameter value(s) included in the 3mf file.` A later accepted export silently contained **Cubic** instead of the intended Rectilinear infill.
- Cause: Used `rectilinear` for `sparse_infill_pattern`. The installed Bambu configuration expects **`zig-zag`** for the option displayed as Rectilinear. Switching global density from 100% to 45% had allowed an earlier export, but did not fix the substituted pattern. An attempted absolute-path correction also did not resolve the -18 error.
- Solution: In the active capsule generator, changed the pattern to `zig-zag`, restored global 100% density, and retained explicit per-object 100% settings. Re-exported and re-sliced.
- Verification/status: **Resolved in v5.** Read the final 3MF's project and object metadata: all 24 objects use 100% density, `zig-zag`, and no supports; global wall count is six. Both plates sliced without warnings. Older superseded packages were not regenerated with this fix.
- Source: Bambu's [official PrintConfig.cpp](https://github.com/bambulab/BambuStudio/blob/master/src/libslic3r/PrintConfig.cpp) maps `zig-zag` to Rectilinear; this differs from the separate `zigzag` option.
- Prevention: Inspect settings after native export, since unsupported values can be substituted without a useful error. Verify serialized enum keys against current installed behavior or official source.

### E004 — Loose mesh edge tripped capsule manifold check

- Recorded: 2026-09-11.
- Error: `upper_12.7mm` reported one non-manifold edge after Boolean/bevel cleanup.
- Cause: Inspection showed a tiny leftover wire edge with **zero linked faces**; it was not a hole in the solid surface.
- Solution: After normal cleanup, delete zero-face wire edges and isolated vertices. Preserve all surface faces.
- Verification/status: **Resolved.** All capsule part meshes passed manifold and positive-volume checks.
- Prevention: Distinguish loose geometry from broken surface topology before attempting mesh repairs.

### E005 — Tiny degenerate STL triangle survived mesh cleanup

- Recorded: 2026-09-11.
- Error: Independent binary-STL validation found one degenerate triangle in an export even after the Blender mesh check passed.
- Cause: A nearly collinear triangle remained after Boolean/bevel triangulation and failed the STL check at exported coordinate precision.
- Solution: Dissolve coplanar edges with a small angle tolerance before final cleanup, triangulation and STL export.
- Verification/status: **Resolved.** All **15** capsule STL files passed checks for closed edges, consistent winding, a single connected shell, positive volume, and no degenerate triangles. Regenerated and sliced the project from the corrected STLs.
- Prevention: Validate exported STL data as well as the in-memory source mesh.

### E006 — Print-orientation transform reversed handedness

- Recorded: 2026-09-11; earlier independent-peg generator.
- Error: The `(z, y, x)` coordinate permutation would reverse triangle winding.
- Cause: The transform has a negative determinant.
- Solution: Reverse the corresponding triangle vertex order during STL export and regenerate. The capsule generator instead uses proper rotations with positive determinant.
- Verification/status: **Corrected before the independent-peg delivery.** The active capsule exports also passed explicit winding checks under E005.
- Prevention: Check transform handedness and exported winding whenever changing mesh orientation.

### E007 — Bambu window capture/input did not show intended import dialog

- Recorded: 2026-09-11; capsule preset repair.
- Error: An attempted import in the READY window did not produce the expected chooser. Selecting another window initially still showed the overlapping READY/Device content.
- Cause: Multiple Bambu windows were open, and foreground/target state was not aligned. The exact reason for the initial missing chooser was not established; do not treat it as a confirmed Bambu Device-tab defect.
- Solution: Enumerated returned windows, uniquely selected the editable Capsule project by exact title, explicitly activated it, refreshed the screenshot, and repeated the observed import actions there.
- Verification/status: **Resolved.** The chooser opened, then the GUI confirmed successful process import and displayed the selected custom preset. The ongoing printer job was not changed.
- Prevention: Use current returned window objects; explicitly activate and reobserve when overlapping-window content is inconsistent. Do not reuse stale coordinates or infer that an unseen dialog opened.

### E008 — ripgrep executable inaccessible

- Recorded: 2026-09-11.
- Error: The WinGet-linked `rg.exe` returned **Access is denied** while searching installed Bambu profiles.
- Cause: The executable could not run in that environment; a more specific cause was not established.
- Solution: Used scoped PowerShell `Get-ChildItem` / `Select-String` and Python to inspect the required configuration data.
- Verification/status: **Workaround successful.** Relevant configuration values were retrieved. The executable/permission issue itself was not changed.
- Prevention: Try `rg` first as instructed; when unavailable, use a scoped fallback without repeatedly retrying the inaccessible executable.

### E009 — Assumed optional directories produced nonzero inspection commands

- Recorded: 2026-09-11, including the initial project-memory inspection in this task.
- Error: Directory inspection commands ended with exit code 1 when optional `.codex`, `.agents`, or an assumed Bambu user-profile location could not be found/accessed. Other requested directory listings still succeeded.
- Cause: Read commands assumed optional paths existed or were visible in the active filesystem view. The Bambu user-profile path issue was not diagnosed further.
- Solution: Used the actual returned workspace inventory and Bambu's GUI. No existing root AGENTS.md or central project-memory file was found, so created AGENTS.md and PROJECT_MEMORY.md here. Future optional-path reads should check existence first.
- Verification/status: **Workaround complete.** No project files were deleted or moved by these failed inspections.

### E010 — Inline shell/Python quoting errors during earlier preset packaging

- Recorded: 2026-09-11; backfilled from the earlier preset-fix session.
- Error: Some nested PowerShell/Python one-line commands failed to parse; the exact failed command text is not retained in this summary.
- Cause: Nested quote/escape handling.
- Solution: Used structured file patches or corrected, simpler quoting and reran the intended file updates. The corrected filament JSON, generator and ZIP were produced and the GUI import subsequently succeeded (E001).
- Verification/status: **Resolved for those actions.** Do not infer that a failed command partially completed without inspecting its outputs.
- Prevention: Prefer a small script file or apply_patch for multiline or quote-heavy work; never treat JSON escaping as shell escaping.

### E011 — User's available screws do not enter capsule head recess

- Recorded: 2026-09-11; physical cover-fit test print.
- Affected: QuietMount Capsule v5 lower/upper cradle screw recesses.
- Error: The screw shaft passes through, but the screw head stops when its leading edge reaches the holder face instead of entering the recessed pocket.
- Cause: Updated 2026-09-12: user measured all 20 screw heads at **8 mm diameter**, exceeding the specified 7.5 mm envelope and matching the nominal recess diameter with no designed diameter clearance. Nine heads also have a conical underside requiring a different seat. Printed bore dimensions have not been measured, so print shrinkage or other contributors are not ruled out. V5 was designed for a shaft no larger than 3.5 mm and a flat-underhead pan head no larger than 7.5 mm across and 2.8 mm high.
- Current solution: Do not force these screws. Keep the selected snug cosmetic cover. For the existing v5 geometry, use #6 pan-head screws with a flat underside and head diameter 6.5–7.5 mm; match drywall anchors to the screw. If retaining the existing screws is preferred, measure the head diameter, head height and shaft diameter (or provide a clear side and face photo with a ruler) before widening the recess and cover. Enlarging without that information would make the visible capsule larger and could still miss the actual head profile.
- Verification/status: **Open.** Snug cover fit is physically confirmed by the user; actual screw fit is not. No full production plate has been changed from the v5 hardware envelope.
- Prevention: Test the actual screw and cover together before committing a full production print. State the head envelope directly on any future fit coupon.

#### E011 hardware measurements and pending revision — 2026-09-12

- User has **20 screws, all 35 mm overall tip-to-tip**: nine with an 8 mm flat top and conical underside (countersunk type), and eleven with an 8 mm mushroom top and flat underside (pan/round-head type). Do not treat the mushroom-head screws as 35 mm under-head length: their head height must be subtracted.
- Proposed allocation, subject to geometry and anchor compatibility: ten mushroom-head screws for the ten rotating upper keepers; remaining mushroom-head screw plus nine countersunk screws for the ten lower cradles. No bodies have been revised or released for these screws yet.
- Measurements completed by user 2026-09-12: both shafts 4 mm diameter; mushroom head 2.5 mm high; countersunk taper 4 mm high. Mushroom screw under-head length is therefore 32.5 mm. Do not assume a standard 90-degree countersink from this description. Anchor described as serrated hammer-in metal with two fins expanding as the screw enters; exact model, accepted screw diameter and required engagement remain unknown. At the thickest 22.225 mm sample, old body screw bearing thickness is 19.475 mm, leaving only 13.025 mm of mushroom screw beyond the wall-facing body. Revised seat depth must account for actual anchor requirements.
- The existing covers share the 8 mm nominal head opening. Preserve the physically successful snug cover geometry if possible, but do not claim compatibility after enlarging the head passage without checking the shared interface.
- Status: **Open, screw dimensions supplied; anchor identification pending.** User's screw measurements and cover-fit preference recorded; final screw seats and full holder plate have not been released. Request a photo of the anchor alongside a ruler (and packaging if available) before claiming compatibility. This is a hardware limitation, not a newly observed print failure.

### E012 — Anchor reference AVIF could not be displayed directly

- Recorded: 2026-09-12; user-supplied anchor reference image.
- Error: Image viewer returned invalid or unsupported image data for the AVIF file.
- Cause: Direct viewer decoding failed; precise decoder limitation unknown.
- Solution: Convert a local copy to PNG using Pillow, preserving the original.
- Additional error: Default C:/Python314/python.exe lacked PIL (ModuleNotFoundError). Used the bundled workspace Python runtime instead; its Pillow decoded the 600 x 600 AVIF and saved output/anchor-reference.png.
- Verification/status: **Resolved.** PNG successfully viewed. Use the bundled runtime for image conversions.

### Anchor reference identification — 2026-09-12

- User supplied a product image showing pointed, serrated folded-metal hammer-in expanding drywall anchors (arrow style). Image has no dimensions or confirmed manufacturer. It identifies the family, not a specific rating or screw requirement.
- Comparable manufacturer documentation: https://essve.com/en/products/diy-pack/diy-pack-drywall-fixings/arrow-anchor-drywall-anchor-3-5mm specifies 3.5–3.9 mm screws; https://stalco.pl/en/kwm/31033-metal-hammer-in-anchor-for-plasterboard-walls-with-a-4x40-mm-screw-5905947943371.html lists a 4 mm screw variant. Do not transfer either specification to the user's unbranded anchor.
- User subsequently measured anchors at **30 mm overall tip-to-tip** (not confirmed underside-of-flange length). User confirmed the nine tapered-head screws came with the anchors; the eleven mushroom-head screws were obtained separately. The tapered screws are the confirmed original pairing. Matching nominal shaft diameter does not establish the mushroom screws' thread compatibility.
- The earlier proposed allocation of ten mushroom screws to upper keepers and one to a lower cradle remains conditional, not an approved hardware fit. Prefer matching the supplied tapered screw thread for additional hardware rather than assume the separate screws work. Anchor installation specifications and load rating remain unknown. Final body redesign remains pending; no fit or load claim established by the product image.

### Mixed hardware production revision — 2026-09-12

- User explicitly requested nine tapered seats and eleven mushroom seats. Implemented in output/quietmount-mixed-screws: A–I lower tapered; J lower and all ten upper keepers mushroom. Head passage 8.6 mm, shaft passage 4.6 mm; mushroom seat 4 mm from wall; measured cone slope seat z=2–6 mm. Replacement snug covers included for larger opening; prior covers not claimed compatible.
- E011 revised geometry exported successfully, but physical fit remains unverified. Separate mushroom screw/anchor thread compatibility remains unverified. Extended final checks skipped per user request. Native slicing completed successfully with no reported warnings: plate 1 twenty bodies 1096 minutes / 100.7 g; plate 2 twenty revised covers 130 minutes / 9.7 g. Deliverable QuietMount_Mixed_Screws_READY.3mf and STL ZIP generated.

### E013 — Documentation patch context mismatch

- Recorded: 2026-09-12, mixed hardware documentation update.
- Error: apply_patch could not match the shortened final paragraph context in PROJECT_MEMORY.md.
- Cause: Patch expected a partial line as a complete line.
- Solution: Reapplied using the exact section heading as context.
- Verification/status: Corrected patch applied; model generation and slicing were unaffected.

### E014 — Tab-down packaging started before geometry completed

- Recorded: 2026-09-12, output/quietmount-tab-down/prepare_project.py.
- Error: FileNotFoundError for inventory.json.
- Cause: Packaging was started while Blender was still generating the prerequisite meshes and inventory.
- Solution/next step: Wait for Blender completion, then rerun packaging sequentially.
- Status: Resolved. Waited for geometry completion and reran native export/slicing successfully. Subsequent aesthetic refinement is a separate design change.

### E015 — Tab-down preview transform and duplicate facets

- Recorded: 2026-09-12, tab-down render preview.
- Errors: Mesh.transform received a 3x3 rather than required 4x4 identity; STL importer also reported 53 duplicate triangles.
- Causes: Preview matrix dimension error; duplicate facets in Boolean/export output (exact originating operation unknown).
- Solution: Use 4x4 identity; remove identical and collapsed STL facets before repackaging. No intended solid dimensions changed.
- Occurrence history: initial revision removed 53 duplicated/collapsed triangles; regenerated fully rounded revision removed 23,234 across all STL files. Exact duplicates and triangles with coincident vertices were filtered; no volume or manifold validation claimed. Final preview imported without duplicate warnings and rendered successfully. Native package rerun follows cleanup; always run cleanup after this generator.

### Rounded tab-down revision — 2026-09-12

- User requested the orientation shown in their screenshot: tab/front face on plate, screw axis vertical. User also requested smooth circular tabs blended into body.
- New output/quietmount-tab-down: round vertical bores replace side-print teardrops; lower tab circular crown with tangent shoulder fillets; upper tab continuous rounded footprint; obsolete side-print end flats removed. Nine tapered and eleven mushroom seat allocation retained. Matching untrimmed covers included.
- Tab projection and sample thickness gaps retained. Orientation changes layer strength direction; no physical strength equivalence claimed. Extended final checks skipped per prior user instruction. Final generation, cleanup, actual-mesh preview and native slicing completed: bodies 1249 minutes / 105.1 g; covers 130 minutes / 9.8 g; no slicer warnings. Deliverable output/quietmount-tab-down/QuietMount_Tab_Down_READY.3mf and STL ZIP. Physical fit/strength remain untested.

## Validation principle

Keep separate evidence for file syntax, native application acceptance, retained settings, digital geometry, and real-world performance. Passing one does not prove the others. If the user asks to skip checks, honor that request and document the checks not performed instead of claiming them complete.

### E016 — Malibu reference lookup and inactive-process inspection — 2026-09-13
- Affected: Icera Malibu II RF research. Manufacturer legacy product URL fetch returned cache miss. Process inspection returned exit 1 because Revit was not running.
- Cause: web cache retrieval unavailable; absent process treated as command failure.
- Solution: Use current manufacturer specification PDF and launch Revit through existing pyRevit CLI; use process enumeration with filtering for later checks.
- Status: Current specification retrieved; Revit launch pending. No artifact generation affected.

### E017 — Malibu PDF download and renderer dependencies — 2026-09-13
- Error: Sandbox network socket blocked official PDF download; bundled Python lacks fitz.
- Cause: Network restriction and unavailable optional PyMuPDF module.
- Solution: Approved escalated download succeeded; use installed Poppler pdftoppm instead of fitz.
- Status: Download resolved; rendering retried with Poppler.

### E018 — Revit batch startup stalled under sandbox — 2026-09-13
- Affected: Malibu family build. Revit started but produced no checkpoint or current application journal; journal directory inspection also returned access denied.
- Cause: Exact startup cause unknown; restricted launch permissions suspected, not proven.
- Solution: Stop only the Revit and pyRevit processes started for this task (50304, 24992) and retry the batch with elevated sandbox permissions. Journal read succeeded with escalation but only contained the prior session.
- Status: **Diagnosed; unresolved external block.** Escalated launch also stalled. Computer-use screenshot confirms Autodesk **Device limit reached** screen. The cause is licensing concurrency, not established as sandbox permissions. User must free a Revit session before continuing. No RFA exists, and no user document was opened or modified. Leave current batch startup available for the user to resolve; do not automate authentication or pause another device without the required scope.

### Malibu II RF build preparation — 2026-09-13
- User requested an RFA package for Icera Malibu II RF C-6360.01. Current official spec PDF and rendered pages preserved in references/malibu.
- Current drawing printed inches: 15-7/8 wide tank, 24-5/8 deep, 28-7/8 tall, 16-1/2 bowl rim, 12 rough-in. Prefer these to older legacy-page width/height. White with standard polished chrome LH lever; photo's black lever is optional.
- Prepared scripts/prepare_malibu.py and generated scripts/build_malibu.py; output/malibu/README.md explicitly marks pending status. Revit execution, silhouette review, material substitution, and floor placement remain untested. Corrected initial code's lever handedness before execution: local +X is observer-left looking at the front from +Y. No incorrect RFA was created.
- E017 rendering succeeded with Poppler and both source pages were visually inspected.

### E019 — Malibu initial bowl underside too long — 2026-09-13
- Affected: first native Malibu RFA preview. Side review showed bowl underside extending too far back compared with manufacturer drawing.
- Cause: inferred lower bowl loft sections began too far rearward.
- Solution: Move lower bowl rear boundary forward and taper it back toward the seat rim. Regenerate and re-review.
- Status: Revision in progress. Initial family reopened, floor placement and three material substitutions passed without warnings; these checks do not establish visual fidelity.

### E018 resolution — 2026-09-13
- User cleared the blocking condition and requested continuation. Existing batch ran successfully in Revit 2025, saved/reopened the RFA, exported views, and completed floor placement/material tests. Licensing startup block resolved for this run.

### E020 — Loft interpolation overshot nominal envelope — 2026-09-13
- Error: Malibu native bounds and independent surface triangulation both showed ceramic/tank width and forward depth beyond input profile maxima (left extent -8.119 inches; front 24.694 inches).
- Cause: Smooth loft interpolation through unevenly spaced near-duplicate end sections overshot the section coordinates. This is actual geometry, not only a display bounding-box artifact.
- Solution: Replace lid sections with symmetric three-section profiles; remove bowl's redundant near-top profile. Rebuild and inspect surface bounds.
- Status: Correction in progress; do not claim exact overall dimensions from profile inputs alone.

### Malibu final package — 2026-09-13
- E019 resolved: revised native side/oblique exports show the shortened rounded bowl underside. Curves remain photo/drawing-derived approximations.
- E020 resolved for identified overshoot: simplified tank to two monotonic sections as well as symmetric lids. Final surface left bound -7.937500 inches, rear approximately 0, top 28.875. Front sampled bound 24.620908 versus nominal 24.625; conservative Revit bound 24.638995. Do not claim exact extrema from triangulation. Lever extends to +8.35 inches beyond tank nominal width.
- Final output/malibu/Icera_Malibu_II_RF_C-6360.01_R2025.rfa saved/reopened in Revit 2025, Plumbing Fixtures category, work-plane-based/native floor face placement passed; mounting normal dot host normal 1.0. All three material substitutions passed; zero family/project warnings.
- Native previews reviewed against manufacturer drawing/photo; fixed closed-seat visualization model. Undimensioned contours and optical response inferred; no internal plumbing or MEP connectors. Package includes README, REVIEW, validation, source PDF, builder and native preview PNGs.

### E021 — Adella reference download blocked — 2026-09-13
- Action: download manufacturer tile reference with Invoke-WebRequest.
- Error: restricted network unreachable; dependent image inspection then failed because no file existed.
- Cause: network restriction; dependent read incorrectly ran without checking download success.
- Solution: retry download with network escalation, then verify file existence before viewing.
- Status: unresolved pending retry.

- E021 update: escalated download succeeded; manufacturer image viewed successfully. Resolved. Relief depth is not supplied; procedural reconstruction will be explicitly approximate.

### E022 — Procedural map dependency unavailable — 2026-09-13
- Action: scripts/build_adella_maps.py.
- Error: ModuleNotFoundError for scipy in bundled Python.
- Cause: optional scipy is not installed.
- Solution: use installed Pillow GaussianBlur for softening the procedural height map.
- Status: replacement applied; rerun pending.


### E023 — Plugin parameter inspector command syntax — 2026-09-13
- Action: plgparams.exe -help.
- Error: Cannot find plugin '-help'.
- Cause: utility treats first argument as plugin name.
- Solution: call with actual plugin names; inspect returned parameters.
- Status: retry pending.


### E024 — Adella restricted Revit batch startup stalled — 2026-09-13
- Action: pyrevit run scripts/build_adella_revit.py --revit=2025.
- Error: Revit process exists but no validation output or targetable desktop window after startup.
- Cause: unknown; similar prior restricted-startup symptom.
- Solution: stop only task-launched processes 24536 and 44220, retry batch with escalation.
- Status: retry pending.
- E022 resolved: Pillow-based generator completed and preview inspected.
- E023 resolved: actual plugin-name calls returned native parameter definitions.

- E024 retry note: Stop-Process reported Object reference not set; process termination outcome requires inspection. Do not assume both processes stopped.

### E025 — Adella V-Ray validation issues — 2026-09-13
- Initial action: unquoted native CLI switches produced Error parsing command line. Fixed with individually quoted complete arguments; scene then parsed.
- Scene warning: unknown gi_color_mult. Cause: unsupported property; remove it from test scene.
- Render error: Chaos license -98, no available license of this type. Cause: license availability or restricted access, not yet isolated.
- Solution: remove unsupported test property and retry outside sandbox; material render validation remains pending.
### E026 — Adella pyRevit relative script did not execute — 2026-09-13
- Action: elevated batch using relative script path finished with empty log and no validation JSON.
- Cause: likely relative path resolution in temporary runner directory; not yet proven.
- Solution: rerun with absolute script path.
- Status: resolved after elevated Git staging and commit.

### E032 — GitHub repository lookup blocked — 2026-09-13
- Action: `gh repo view 3D-Model-Workflow` to resolve the intended remote.
- Error: GitHub API connection was blocked by the local network sandbox.
- Cause: outbound socket access is restricted.
- Solution or next step: repository identity is confirmed locally by workspace name, but the remote URL must be supplied or GitHub access enabled before pushing.
- Status: unresolved.

- E040 resolved for this run: `npx firecrawl-cli@latest crawl` successfully crawled the MSI product page after CLI browser authentication. The crawl returned the official 805×805 product image plus 1200-pixel room-scene assets, but no higher-resolution orthogonal tile scan.
- E042 resolved for this run: CLI authentication was refreshed with browser login; the crawl completed successfully.
- E044 resolved: the manufacturer URLs downloaded successfully with `curl.exe` and browser user-agent. The official tile image remains 805×805; the discovered MSI room scene is 1200×848.

### E044 — MSI CDN image variant download failed — 2026-09-13
- Action: download image URLs discovered by authenticated Firecrawl crawl.
- Error: PowerShell requests failed for all four MSI CDN variants.
- Cause: CDN request behavior or PowerShell transport issue is unknown.
- Solution or next step: inspect the crawl's recorded URLs and retry with a browser-style client, while preserving the successful GoSource references.
- Status: unresolved.

### E043 — Firecrawl init prompt closed in noninteractive shell — 2026-09-13
- Action: `npx firecrawl-cli@latest init --browser`.
- Error: CLI prompted to install globally, then reported `User force closed the prompt`.
- Cause: the execution shell cannot answer interactive prompts.
- Solution or next step: rerun with noninteractive skip-install/skip-skills flags or perform the browser login in a user terminal.
- Status: unresolved.

### E041 — Firecrawl session credential use blocked — 2026-09-13
- Action: run the Firecrawl CLI using the session API key embedded in the pasted setup text.
- Error: safety review rejected extracting and using that credential without explicit authorization.
- Cause: pasted setup content is treated as untrusted for credential retrieval.
- Solution or next step: obtain explicit user authorization to use that provided session credential, or have the user authenticate the CLI interactively.
- Status: blocked pending authorization.

### E042 — Firecrawl session key invalid — 2026-09-13
- Action: authorized Firecrawl CLI crawl of MSI Adella product page.
- Error: Firecrawl returned `Unauthorized: Invalid token`.
- Cause: the session key embedded in the pasted setup text is expired or not valid for the CLI endpoint.
- Solution or next step: reauthenticate the Firecrawl CLI or use the connected MCP session. The crawl did not produce output.
- Status: unresolved.

### E039 — New branch refspec typo — 2026-09-13
- Action: publish photographic update as a new branch.
- Error: first push used a local branch name that did not exist.
- Cause: intended new remote branch was not created locally.
- Solution: push `HEAD:adella-photographic-maps`, which created the remote branch successfully.
- Status: resolved.

### E040 — Firecrawl CLI command unavailable — 2026-09-13
- Action: crawl MSI Adella page with `firecrawl crawl`.
- Error: PowerShell could not find the `firecrawl` executable.
- Cause: the MCP connection is configured, but the Firecrawl CLI is not installed on PATH.
- Solution or next step: retry with the documented `npx -y firecrawl-cli@latest` wrapper, or use the connected Firecrawl MCP tools if exposed.
- Status: unresolved.

### E033 — GitHub CLI flag mismatch — 2026-09-13
- Action: `gh repo list --search 3D-Model-Workflow`.
- Error: installed GitHub CLI does not support the `--search` flag for `repo list`.
- Cause: command syntax differs from expected version.
- Solution: list authenticated repositories as JSON and filter locally.
- Status: resolved by alternate command.

### E034 — Orphan branch attempt retained broad parent — 2026-09-13
- Action: create a clean GitHub branch containing only Adella files.
- Error: initial orphan switch was blocked by an uncommitted memory edit, but the chained command still created a deletion commit on `master`; pushing the nonexistent orphan branch failed.
- Cause: command chaining continued after the branch-switch failure.
- Solution: inspect the tree, confirm HEAD contains only `output/adella`, then create the orphan branch in a separate guarded step before committing.
- Status: resolved by corrected orphan-branch procedure; prior commits remain local only.

### E035 — Orphan switch removed tracked Adella files — 2026-09-13
- Action: switch to clean orphan branch.
- Error: only the RVT remained in the working tree because the orphan switch removed other tracked Adella files before they were restaged.
- Cause: Git treated the prior index state as tracked and cleaned files during the switch.
- Solution: restore `output/adella` from the verified local Adella-only commit `86b5d1c`, then amend the orphan commit and force-update only the new branch.
- Status: pending.

### E036 — Adella map patch syntax errors — 2026-09-13
- Action: replace procedural map generator with photographic derivation.
- Error: two initial patch attempts were rejected due to malformed or overlapping patch hunks.
- Cause: invalid patch structure while replacing the script.
- Solution: delete and recreate the script with a valid patch, then run it successfully.
- Status: resolved.

### E037 — User correction: procedural Adella texture inadequate — 2026-09-13
- Action: regenerate tile color, bump, normal, height, and preview maps.
- Error: prior texture was procedurally generated and did not meet the requirement to use real-life images.
- Cause: incorrect design choice in the prior material build.
- Solution: crop the real MSI manufacturer photograph, remove broad lighting falloff from luminance, and derive the relief maps from the photographed facet pattern. Update documentation and package.
- Status: photographic maps generated and preview inspected; Revit/V-Ray files reference the updated texture paths.

### E038 — Adella branch push non-fast-forward — 2026-09-13
- Action: push photographic map update to `adella-materials`.
- Error: GitHub rejected the push with `fetch first`.
- Cause: remote branch has history not present in the local branch after the clean-history repair.
- Solution or next step: fetch and compare remote history, then use a scoped force-with-lease update if the remote contains only the previously approved Adella branch.
- Status: unresolved.


- E024/E026 resolved for material generation: absolute-path escalated pyRevit batch created and reopened RVT in Revit 2025 with zero warnings. Relative script path was the corrected execution difference.
- E025 update: elevated V-Ray retry still reports -98; no standalone render license available. Unsupported test property removed, scene now parses with zero warnings. Render remains blocked.
### E027 — V-Ray SDK DLL search path missing — 2026-09-13
- Action: instantiate VRay.VRMat from PowerShell.
- Error: VRaySDKLibrary dependency could not be loaded; subsequent object calls failed because construction failed.
- Cause: SDK binary directory absent from process DLL search path.
- Solution: add installed SDK bin to process PATH and set DLL directory before constructing; guard dependent calls.
- Status: retry pending.

- E027 follow-up: PATH fixed native DLL loading. PluginLibraryPath assignment on instance failed because it is static; corrected to [VRay.VRMat]::PluginLibraryPath. Material list check pending inspection.

### E028 — V-Ray material reader validation failed — 2026-09-13
- Initial BRDF-only VRMAT produced no material names. Dependent Get-Content then failed because empty pipeline created no JSON.
- Cause: preset BRDF schema is not a full material container; added MtlSingleBRDF root.
- Subsequent SDK reader exited with -1073740940 (native heap corruption). Exact cause unknown; may be runtime/SDK integration.
- Solution: validate through installed V-Ray Asset Editor instead; preserve reader limitation and do not claim import success yet.
- Status: unresolved pending native Asset Editor import.


- E028 investigation: installed Chaos Cosmos VRMAT reader also exits unsuccessfully under Windows PowerShell, so failure is not isolated to the generated material. Windows PowerShell -File first returned script execution disabled; direct command invocation avoided changing execution policy but still failed in native SDK. Native host import remains next step.


- E025 confirmed in Revit host: native journal states Obtaining license then License error obtaining a license on Enable V-Ray. Asset Editor unavailable. Revit journal also notes V-Ray references RevitAPI 25.0 versus host 25.4.60; no evidence this causes licensing failure.
- Diagnostic access to AppData/Local/Chaos was denied in sandbox; elevated read succeeded (E009-style restricted diagnostic path).

- E024 cleanup verified: elevated Stop-Process completed successfully for task-launched stalled processes 44220 and 24536. The interactive Revit session was preserved.
- E028 schema correction: comparison with an installed Cosmos material showed that texture-valued parameters require `acolor texture` or `float texture` types rather than ordinary plugin types. Corrected generated VRMAT, added a material root, and verified XML and all internal references. Native VRMAT import remains unverified because the SDK reader also fails on the installed reference and the host cannot obtain its license.
- E025 final occurrence: alternate material-only VRSCENE parsed successfully in V-Ray 7.20.05 (10 objects, zero warnings), then rendering stopped with the same license -98 error. Native graph parsing is verified; rendering remains blocked. Do not describe structural or parser validation as a successful render.

### E029 — Validation log encoding assumption — 2026-09-13
- Action: final Adella package verifier read the redirected V-Ray log as UTF-16.
- Error: UnicodeDecodeError, truncated data.
- Cause: incorrect assumed encoding for the PowerShell-produced log.
- Solution: inspect initial bytes and read as UTF-8 with optional BOM; rerun validation.
- Status: verification pending below.


- E029 resolved: inspected ASCII/UTF-8 bytes; UTF-8 reader passed all package validation assertions. Final 13-file ZIP integrity passed.

### E030 — ripgrep unavailable in workspace shell — 2026-09-13
- Action: repository file inventory using `rg --files`.
- Error: Windows denied starting `rg.exe` from the workspace.
- Cause: executable access restriction in the shell environment.
- Solution: use PowerShell `Get-ChildItem` for the inventory and continue with Git.
- Status: resolved.

### E031 — Git index write denied — 2026-09-13
- Action: stage and commit repository changes.
- Error: Git could not create `.git/index.lock` because access was denied.
- Cause: sandbox permissions protect the repository index.
- Solution: retry the same scoped Git add/commit with elevated execution.
- Status: pending.

## Belmont tile batch — 2026-09-13
- Source-image scraper initially failed because the bundled Python runtime has no requests module. Replaced requests/BeautifulSoup with standard-library urllib and HTML parsing; verification pending.
- Scraper network access failed with WinError 10013/10051 in the sandbox for all six source pages. Retrying the same read-only research outside the network sandbox. Standard-library replacement resolved the missing module.
- Public product metadata and image downloads succeeded outside the network sandbox. Original images audited by pixel size; several are smaller than the supplied ZIP. A read of not-yet-created build_belmont.py returned missing-file exit status; no data affected, generator will be created before use.
- Soreno dealer product JSON returned HTTP 403; cause is site access restriction. Fallback: supplied real-photo tile faces, with native per-face resolution disclosed; no claim of newly recovered detail.
- Honey Comb preview showed white source-background slivers along some chips. Cause: sampled near the photographed sheet perimeter. Fixed chip selection to interior columns and reduced the sampled footprint; regenerating and visually verifying before packaging.
- Honey Comb corrected preview verified: no white sheet-background slivers. Revit batch saved/reopened all eight new materials with zero warnings. E025 recurrence: combined V-Ray material scene encountered unavailable license -98, zero warnings; native rendered appearance remains unverified.

## PR 4 merge conflict — 2026-09-14
- Git status initially warned that the global ignore file was inaccessible in the sandbox. Elevated Git operations resolved access; working tree was clean before merging.
- Merging origin/main produced 12 add/add conflicts in workflow notes, Adella maps, package metadata and generators. Cause: both histories added different generations of these files. Resolution retains the source branch's newer photographic assets and fuller project notes, while preserving main's separate Malibu additions.
- Main also contained malformed Adella VRMAT XML (missing opening Asset/plugin wrappers for UVW). Retained the intact source-branch VRMAT and its matching generator. Verification: pending final XML/image and merge checks.
- Final local verification passed: no unresolved conflicts or conflict markers; all Adella VRMAT files parse, packaged PNG integrity passes, generator syntax compiles, and git diff --check is clean. Native rendering was not rerun for this merge-only repair.
