# Fixture visualization families

Project-wide memory and error logging: see [AGENTS.md](AGENTS.md) and [PROJECT_MEMORY.md](PROJECT_MEMORY.md). Record every error and its solution there, including errors in work outside the fixture-family workflow below.

## Seamless and non-repeating materials

### Required Revit delivery format

Effective 2026-09-17, supply materials as a native `.adsklib` plus companion textures. Never use or recommend Transfer Project Standards or copying swatches from an RVT as the material delivery/import method. An RVT may be an internal test artifact, but is not a substitute for the library. Verify native library opening, material addition, and texture resolution in a disposable project before delivery; do not test transfers in the user's working model. If `.adsklib` export is unavailable, report incomplete delivery instead of handing off an RVT workaround. Older Belmont transfer instructions are withdrawn.

Every delivered appearance asset must include at least one explicit bound color/diffuse bitmap. For a uniform polished, painted, or plated finish, use a spatially uniform bitmap at the intended base color rather than inventing visible texture. This provides a portable Revit appearance input while remaining intrinsically seamless and free of recognizable repetition. Keep the texture beside the library, use package-relative setup notes, and verify that the bound bitmap path resolves before delivery.

Standing user instruction — 2026-09-17: **All materials must be made to appear seamless and non-repeating**, effective immediately for all material types and future work. Existing materials reviewed against this rule must be marked for revision if they do not pass.

Standing user instruction — 2026-09-18: **V-Ray assets are produced on request only.** The default material deliverable is the `.adsklib` plus companion textures and notes. Do not generate VRMAT or VRSCENE files, and do not treat a missing V-Ray asset as an incomplete delivery, unless the user has asked for V-Ray output for that job.

### ADSKLIB build and release discipline

- Invoke pyRevit build/validation scripts with an **absolute script path**. The runner may execute from a temporary working directory, so a relative path can return exit code 0 without actually running the intended repository script.
- Never accept a pyRevit exit code by itself as proof. Require a task-specific output or validation file, confirm its timestamp/content changed during the run, and check the recorded native save/reopen, warning count, material bindings, and texture existence.
- Build or rewrite an ADSKLIB to a temporary/candidate filename first. Before release, verify it is a readable archive, run the repository's independent ADSKLIB codec/readback where applicable, confirm the intended material name and texture paths, and record a SHA-256 digest.
- Do not replace an ADSKLIB in place while it may be open in Revit. If replacement returns a Windows sharing/file-lock error, keep the validated candidate intact and release it under a new revision/descriptive filename. Do not close the user's working Revit session merely to free the old library.
- Package materials from an explicit allow-list: final ADSKLIB, companion textures, concise loading/setup notes, and QA/validation evidence. Exclude temporary RVTs and backups by default when a valid ADSKLIB is supplied.
- Verify the final ZIP independently after writing it, record its size and SHA-256 digest, then upload. A copy into a Drive-mounted folder is only a transfer step; delivery is complete only after Google Drive metadata independently confirms the remote file, destination, and size.

### Construction

- Seamless means no unintended boundary in color, lighting, roughness, normal, bump, or displacement when mapped across a surface. Preserve real grout joints, manufactured edges, flutes, and intentional patterns.
- Non-repeating means no recognizable copied face, mirrored motif, checkerboard, banding, or repeating atlas block at the intended close-up and room viewing distances. A finite bitmap is periodic; do not claim mathematical non-repetition. Record the tested surface extent and viewing conditions.
- Use multiple genuinely different product faces where available. Correct photographic perspective and baked lighting while preserving the product's actual color and character. Rotating one face, adding random tint, blurring detail, or increasing export resolution is not sufficient variation.
- Use a sufficiently large, product-faithful layout or supported per-tile/procedural variation that passes the intended surface test. Avoid adjacent duplicate faces and obvious periodic arrangements. Respect directional grain, rectangular tile orientation, flutes, and designed motifs; do not introduce invalid rotations or mirroring.
- Keep all appearance maps spatially registered with identical physical scale and compatible variation. Transform directional normals correctly. Preserve source resolution disclosure and float precision until export; retain accurate tile and grout dimensions.
- If source images cannot support convincing variation, obtain additional faces or document the limitation and hold final acceptance. Do not invent a different product to conceal insufficient references.
- For a **dimensional / 3D tile**, whose face carries a sculpted geometric pattern, the pattern relief must be pronounced enough to read on its own under grazing light, and clearly stronger than an unmodified photo-derived height estimate yields. Standing user instruction, 2026-09-18. Worked figures from the Adella M01 build, at a 0.6 mm full height range: a pattern amplitude of 0.20 gave 0.203 mm of pattern relief against a 0.210 mm grout step, roughly equal depths, and the reviewer judged the pattern too shallow while the grout was correct. The usable band was 0.30 to 0.40, giving 0.304 to 0.405 mm of relief; 0.50 drove the deepest pattern points 0.057 below the grout floor, which is physically impossible and renders as holes in the tile face. Deepen the pattern alone: the grout floor and the pattern amplitude are independent terms, so do not raise a global bump multiplier, which scales both.

### Required visual acceptance gate

1. Inspect every map wrapped horizontally and vertically, including the four-way corner, in at least a 3 x 3 repetition preview. Check joint width, relief continuity, shading seams, and border bands; intentional grout is not a defect.
2. Inspect a correctly scaled surface covering the largest intended uninterrupted wall/floor or object area. Also inspect multiple atlas repeats so that a large atlas cannot merely hide periodicity in a small swatch. Check both close-up and room views for duplicate landmarks and patterns of repetition.
3. Inspect in the target native application/renderer with neutral and grazing light. Confirm actual map bindings, scale, orientation, highlights, bump/normal response, and absence of visible seams or repeated blocks. File-open success and a flat preview are separate checks, not a rendered appearance pass.
4. Record the material ID, source-face count, variation method/seed, physical atlas size, tested surface size, preview/render evidence, and pass/fail/pending result. Both seamlessness and non-repetition must pass before final delivery. If rendering is unavailable, label that gate pending.
5. For a dimensional tile, review the sculpted pattern's relief specifically, under grazing light, and record the pattern relief, the grout step and the clearance between them in millimetres. A pattern that does not read at a glancing angle fails this gate even when every map statistic passes.

Belmont baseline review: [2026-09-17 tile review](docs/reference-reviews/belmont-tiles-2026-09-17.md). The original six materials are superseded by [corrected R2](output/belmont_preferred_bath2_bath3_r2/REVIEW.md): varied layouts, seamless map boundaries and native bindings verified; full production optical acceptance remains pending. The default preferred-tile build entry point now uses the R2 generator.

## Fixture defaults

- Material delivery (user instruction, 2026-09-18): when an `.adsklib` is provided, a separate Revit project (`.rvt`) is not required. Do not produce individual material projects by default. Include required companion textures and setup notes with the library. Temporary Revit projects may be used as needed for creation or validation; deliver an RVT only when specifically requested or needed because no ADSKLIB is provided.

- Revit 2025 is the oldest supported version.
- Face-based or work-plane-based placement; hosts are in the current native model.
- Purpose: faithful 3D visualization and rendering.
- No MEP connectors, electrical information, IES files, or flow data required.
- Incomplete references are acceptable. Record measured, drawing-derived, and inferred geometry separately.
- Preserve manufacturer source files. Generated families are independent outputs, not copies renamed as new work.
- Finishes use Revit appearance assets and an editable material parameter.
- Prioritize silhouette, component proportions, and smooth profile transitions before adding small seams, rings, or other undimensioned details.
- Treat numerical/Revit validation and visual fidelity as separate acceptance checks. A loadable family with correct overall dimensions can still have visibly wrong component shapes.

## Pilot: KOHLER Purist K-T14489-4

- Finish: polished chrome; Revit materials.
- Sources: supplied K-T14489-4_dimensions.pdf and matching K-T14489-4_spec_US-CA_Kohler_en.pdf found alongside it in Downloads.
- Explicit nominal dimensions, using inch values as authoritative: plate diameter 7.25 in; projection 4.25 in; handle-axis spacing 3.125 in; outer lever tip 3 in from each corresponding handle axis.
- Drawing-derived details: approximately 1.6 in barrel diameter and 0.625 in lever diameter.
- Inferred details: plate radial curvature/thickness, stem transitions, edge rounding, inward lever lengths, and exact optical properties of chrome.
- Printed dimensions override proportions measured from the PDF illustration. These are nominal product dimensions, not manufacturing tolerances.
- The supplied example RFA path was not accessible during creation. A screenshot-based comparison was subsequently recorded; the manufacturer RFA itself has not been opened or measured.

## Lessons from the manufacturer comparison

See [Purist screenshot review](docs/reference-reviews/purist-2026-09-04/REVIEW.md) and its three preserved screenshots. Manufacturer = left/top; generated = right/bottom. The user requested recording lessons only, with no changes to the pilot model.

- Match the fullness and simplicity of necks and shoulders. The pilot's connections were too thin and visually segmented relative to the benchmark.
- Match rounded end caps and supported seams; the pilot's collars read as more separate and mechanically elaborate.
- Check plate profile continuity: the pilot produced a more explicit inner circular break and abrupt reflective transition.
- Compare lever lengths, inner gap, and control spacing relative to plate diameter. The pilot appears taller relative to its plate; an exact correction is not established by the screenshots.
- Do not infer global scale errors or precise color/roughness corrections from side-by-side perspective views. Account for camera, placement, and reflections; use matched-position comparisons when available.
- Flag conflicts between nominal dimensions and visual references for interpretation/variant review. Preserve explicit source dimensions and label uncertainty rather than silently compensating.

## Acceptance

Open the saved family in Revit 2025, inspect solid bounds and material binding, load into a disposable native project, place on a wall face, confirm orientation/projection, test changing the finish parameter, and export review views. Do not describe a preview or generator script as a finished RFA.

Also assess front/side/oblique silhouettes, component ratios, shoulder and cap profiles, plate curvature, and material response. State which details remain inferred. A successful technical check is not a substitute for this visual review.

## Tris lighting fixture

- Reconstructed the supplied 700BCTRS references as a 25.6 in wide x 4.5 in high x 3.4 in projecting face-based Lighting Fixtures family, with a 5 in wide backplate.
- User selected unlit translucent panels for this fixture. Chrome rail and housing; three thin horizontal acrylic blades with material-based microdots and separate edge material.
- Source files are preserved in `references/tris`; output and accuracy/texture-transfer notes are in `output/tris/README.md`.
- Retain companion texture files for detailed diffuser appearance. Technical material verification does not establish an exact optical or production-render match.

## Duo pendant

- Sources preserved in `references/duo`: the supplied Lightology product PDF, two photos, and dimensioned outline.
- Shade diameter and combined shade height are 210 mm; the drawing shows two equal 105 mm rounded sections. Use smooth revolved profiles and retain the photographed upper opening.
- Matte white metal and opal glass are specified by the PDF. User selected soft warm glow for this fixture; do not extend that selection to all future lights.
- Canopy, cord, stem, shell thickness, and opening details are inferred from photographs. Suspension length is an installation choice, not established by these source documents.
- Output notes distinguish fixed geometry, editable materials, and appearance glow from photometric room illumination.

## Courcelette linear pendant

- Sources: supplied DVI/Lightology 873039 PDF, orthographic dimension image, and product photo, preserved in `references/courcelette`.
- Specified fixture body is 46.6 x 21.59 x 12.95 in. User chose 50.5 in total drop and soft warm bulb glow.
- Graphite metal and clear glass follow the PDF. Six hollow globes are arranged on three crossed opposing arm pairs, with staggered heights derived from the drawing.
- Separate material parameters for graphite, clear glass, and visible bulbs. Treat the bulb glow as an appearance setting, not photometric room illumination.
- Record globe diameter, exact centers, rod/hub/canopy sizes, glass thickness, and internal bulb details as inferred where not individually dimensioned.

## Trinity Low pendant

- Sources: supplied Lightology 1009570 PDF and four photos, preserved in `references/trinity`; manufacturer code PD62014-BKSM is shown in the image filenames.
- The PDF contains an embedded dimension drawing. Read embedded diagrams visually as well as extracting PDF text: it supplies the 14.25 in shade diameter, 6.125 in shade height, 9.75 in lower opening, and 4.75 x 0.25 in canopy.
- User selected 48 in total drop and soft warm glow. Black metal, smoke glass, and recessed diffuser are separate editable materials.
- Model the glass as a hollow shade with a real lower opening. Do not turn reflections or the luminous reflection on the rim into additional physical panels.
- Exact optical density, shell thickness, shoulder curves, and hidden housing details remain inferred. The glow is a material setting rather than photometric output.

## Oyster wall sconce

- Supplied references are preserved in `references/oyster`. The PDF and drawing specify 5.24 x 12 x 3 in overall and a 5 in diffuser.
- User selected a stainless-steel-like frame, smooth diffuser, and soft warm glow. This overrides the PDF's brushed brass and patterned acrylic; do not label this visual variant with an unverified manufacturer finish SKU.
- Preserve the open lower frame so the host wall shows through. The apparent pale surface inside the reference is not a full-height backing plate.
- Use a thin continuous capsule band. Additional manufacturer close-up and user correction establish a single cylindrical diffuser spanning the full 3-inch depth, with a nearly flat circular front and a small softened edge. The previous shallow domed lens interpretation was incorrect. Edge radius remains inferred.
- Check exposed undersides and sidewalls before assuming a luminous circular face is a shallow lens. In this fixture the underside reveals its full depth. The white finish in the correction photograph is geometry reference only; retain the selected stainless appearance.

## Vera bathroom vanity light

- User selected the 22.9-inch variant. Supplied PDF specifies exact 22.87 x 4.75 x 3.25 inches, black with white polycarbonate diffusers. Backplate is 4.75 inches square and 0.5 inch deep.
- Include upper and lower diffuser strips: dual-sided diffusion is explicit in the PDF and the opposite sides appear in the close-ups. Warm appearance follows the illuminated references.
- Side profile is gently bowed, with thin end caps and recessed strips. Exact bar height, profile radii, seams, and standoff dimensions remain inferred; document them rather than treating photo-derived geometry as measured.

## AXOR angled-spout faucet

- User ultimately selected the angled-spout image `154__apu90602_tif.png` and matching 13.5-inch drawing, replacing the prior rounded gooseneck request. Do not use the superseded 16.75-inch drawing.
- Use brushed black chrome appearance, 13.5-inch overall height, 8-inch reach, 10.375-inch outlet center height, 2.5-inch base diameter, and 8.875-inch lever height. Dimensions use printed inches; metric equivalents are rounded.
- Place on native horizontal faces, with editable metal and dark outlet materials. Preserve continuous tangent spout bends, a short outlet collar, a real recessed outlet, and the asymmetric lever silhouette.
- Tube sizes, bend radii, body transition, lever thickness and exact finish response remain inferred. Verify matching product geometry before combining photos and dimension drawings.
- Revision using supplied manufacturer 39835USA RFA replaces estimated base/body, joint, and lever with source solids 4108, 4101, and 4105, preserving size and contour. The base is offset behind the neck axis and the body has a substantial rear bulge; do not reduce this assembly to a centered revolved cylinder. Rotate the stored handle 45 degrees upright to match the reference. Source native solids can include overlapping alternative representations; select and inspect individual shapes before reuse.

## Hansgrohe Air Switch

- User linked 04032000 but selected Brushed Black Chrome; official 2026 Hansgrohe catalog page 46 identifies finish SKU 04032340.
- Catalog drawing supplies 1.875-inch trim diameter and 0.9375-inch visible height. Raised button diameter, flange thickness, seam and small edge rounds are estimated from the official photo. Model above-counter assembly only for visualization.
- Native revolved solids may have approximate display bounding boxes that understate one circular axis. Validate exact diameters with solid intersections, not only display bounds.


## Hansgrohe beverage faucet 04117340 - 2026-09-06
Created output/bev_faucet/Hansgrohe_Modern_Beverage_Faucet_04117340_Brushed_Black_Chrome_R2025.rfa from official 2026 catalog page 38. Native countertop face placement, editable materials, exact 9.375 inch crown and 1.75 inch base checked using solid intersections. Reopened and material substitution passed; no warnings. See output README for inferred details.


## Focus X3 adjustable - 2026-09-07
Created output/focus/DCW_Focus_X3_Black_Adjustable_R2025.rfa. Cord Length instance parameter drives nested mobile elevation and suspension extrusion; Total Drop formula includes 1063 mm mobile/canopy. Default 60 inches. Native overhead face placement and material substitution pass, four cord settings 8 to 118 inches verified, no warnings. Official references and inference notes in package.

## Icera Malibu II RF C-6360.01 — 2026-09-13
- Official current C-6360 PDF provides 15-7/8 inch tank width, 24-5/8 depth, 28-7/8 height and 16-1/2 bowl rim. Current drawing overrides conflicting legacy-page dimensions. White ceramic with standard chrome observer-left lever; black photo lever is optional.
- Delivered floor-face visualization family under output/malibu. Closed seat; editable Ceramic Finish, Seat Finish and Lever Finish; no MEP connectors. Revit 2025 reopen, native floor placement and material substitution passed without warnings.
- Smooth multi-section lofts may overshoot intermediate input contours. Inspect actual surfaces, not only profile dimensions; use monotonic sections or symmetric lid profiles. See E019/E020 in project memory and package REVIEW.md.

## Kamden bathroom vanity light — 2026-09-15
- Supplied 1279641 PDF specifies 22.5 x 4.3 x 4.7 inches and 5-inch backplate width. Nightshade Black with three clear rectangular shades and white inner diffusers.
- Revit 2025 wall-face visualization family with editable Frame Finish, Glass Finish and Diffuser Finish. Fixed geometry; no MEP or photometric source. Glass shell thickness, shade sizes, collar/rail and inner diffuser geometry inferred from drawing/photo.
- Native reopen, exact overall bounds, native wall placement and all three material substitutions passed without warnings. References and notes under output/kamden and references/kamden.

## Cassia SF549315AGOP semi-flush -- 2026-09-23
- Sources in `references/cassia`: supplied drawing and two renders, identified as Alora Mood (Kuzco) Cassia; official spec sheet and installation PDF. Printed D17-3/4 x H7-5/8, canopy D4-3/4 x 7/8, globes 6. Aged Gold / Opal Matte Glass (AGOP).
- Three globes at 120 degrees on arms 30 degrees below horizontal whose axes pass through the globe centres; stepped fitter disk with arm collar on each globe's inner shoulder; hub under the canopy; two canopy screws 30 degrees off the arms. Globe centre radius 5.875 follows the printed dimensions; the drawing's own 5.945 is a disclosed ~1 % drawing inconsistency.
- In a two-view drawing of a 3-fold fixture, the elevation shows two of the three globes superimposed: check the offset ratio (here 0.50 = cos 60) before reading a "two-globe" elevation literally. Renders viewed opposite one globe show the far globe lower and partly hidden when the camera is below the fixture.
- Ceiling face-based Lighting Fixtures family with editable Metal, Glass and Lamp finishes; socket sleeves and candle lamps are inferred and hidden by opal, kept so a clear-glass swap reads correctly. Fixed geometry; no light source or MEP data.
- Built by a native kit (`output/cassia/run_cassia.ps1`); constants shared by builder, offline dry-run and verifier in `source/cassia_geometry.py`. Native build, visual review and Drive delivery were pending at the time of writing; see `output/cassia/README.md` and PROJECT_MEMORY.md.
