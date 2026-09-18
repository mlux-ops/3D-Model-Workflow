# Fixture visualization families

Project-wide memory and error logging: see [AGENTS.md](AGENTS.md) and [PROJECT_MEMORY.md](PROJECT_MEMORY.md). Record every error and its solution there, including errors in work outside the fixture-family workflow below.

## Agreed defaults

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
