# Purist pilot: manufacturer comparison

Recorded 2026-09-04 from three user-supplied screenshots.

**Purpose:** Capture differences to improve future fixture outputs. The user explicitly requested no rebuild or revision of this model. This review changes documentation only and preserves unedited copies of the screenshots.

**Identification:** Manufacturer family is left in images 1 and 2, and top in image 3. The generated family is right in images 1 and 2, and bottom in image 3. The manufacturer family is the user's visual quality benchmark; its screenshot does not establish exact physical dimensions or material settings.

## Observations and future modeling lessons

| Feature | Visible comparison | Confidence / limits | Lesson for future outputs |
|---|---|---|---|
| Body-to-lever neck | The manufacturer model has a thicker, simpler connection with a fuller shoulder. The generated model has a visibly narrow exposed pin and several small transitions near the lever. The side view makes this particularly clear. | High for the silhouette difference. Exact neck dimensions cannot be obtained from these screenshots. | Match neck diameter, shoulder fullness, and connection silhouette before adding small detail. Do not invent a thin stem or stacked transitions from ambiguous imagery. |
| Circular body end / collar | The manufacturer end reads as a rounded, integrated cap. The generated end reads as a more distinct ring or washer, with additional concentric edges and a sharper division from the barrel. | High for different visible edge structure; view edge lines can exaggerate physical seams. | Use restrained, reference-supported seams. Match the cap's roundness and its transition into the neck; additional geometric detail can reduce fidelity. |
| Plate curvature | The manufacturer plate reads as a more continuous surface with a gentler transition toward its center. The generated plate shows a strongly defined inner circular boundary separating a flatter center and broad outer band. | High for different surface/edge appearance; exact curvature and depth remain uncertain. | Check tangent continuity across radial profiles. Use broad, smooth transitions where references support them; do not let a reconstructed profile create an unsupported hard circular break. |
| Lever proportions | The generated assembly appears taller relative to its plate, with levers extending farther beyond the plate, especially below it in image 2. Image 3 also suggests a different relationship among lever lengths, plate height, and control spacing. | Moderate. Perspective, offsets, and possible family/type differences prevent an exact size correction. | Compare normalized ratios: total height/plate diameter, lever length/diameter, axis spacing/plate diameter, and inner gap. Verify dimension-arrow endpoints and document conflicts between the dimension sheet and visual benchmark rather than declaring dimensional checks sufficient. |
| Chrome appearance | The manufacturer plate has softer, more distributed tonal transitions in these views. The generated plate shows stronger dark-to-bright separation and a concentrated reflective band. Both pick up warm tones from the scene. | The appearance difference is visible, but attribution is uncertain: geometry, surface normals, material roughness, location, and reflected surroundings can all contribute. No specific color or roughness adjustment is justified yet. | Evaluate chrome in a representative scene. Inspect geometry and reflection flow before changing material settings. A standard chrome asset is a starting point, not evidence of a visual match. |
| Overall size / placement | The larger apparent manufacturer fixture in image 1 is not evidence of a global scale error. Plate sizes appear much closer in image 2; both fixtures appear mounted against the wall in image 3. | Qualitative only. These are not calibrated, identical-position orthographic comparisons. | Avoid correcting overall scale from a perspective screenshot. Keep nominal dimensional validation and visual proportion assessment as separate checks. |

## What this pilot established

The broad product identity is captured: circular plate, two projecting cylindrical bodies, and two vertical lever handles. Successful Revit loading, placement, material binding, and nominal-dimension checks did not establish fidelity of the smaller shapes or reflective appearance.

The highest-priority improvements for future models are the neck/shoulder silhouette, end-cap construction, plate curvature, and lever-to-plate proportions. Tiny ornamental details are lower priority and should not be added without evidence.

## Comparison method for future fixtures

1. Separate specified dimensions, reference-derived proportions, and inferred details before modeling.
2. Review the silhouette in front, side, and oblique views, then inspect component ratios and profile transitions.
3. When references disagree, flag the disagreement and check dimension interpretation and product variant/revision. Do not silently stretch geometry to match a perspective image or assume the manufacturer family is fabrication-accurate.
4. When a benchmark is available, prefer comparing at the same position and camera, alternating visibility, with the same view settings. This reduces perspective and reflected-environment differences.
5. Assess reflective materials after the shape is credible. Compare both surface continuity and material response.
6. Report visual fidelity separately from Revit compatibility and numerical checks. Preserve uncertainty rather than calling a successful file export an accurate visual match.

## Preserved evidence

- [Image 1: oblique side-by-side](01-oblique.png)
- [Image 2: near-front comparison](02-front-oblique.png)
- [Image 3: side comparison](03-side.png)

Original screenshot pixels are preserved without modification. The manufacturer RFA itself was not opened for this review. No changes to the generated RFA or generator are authorized by this feedback request.
