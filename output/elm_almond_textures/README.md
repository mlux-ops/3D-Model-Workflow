# ELM Almond texture set

Deterministic source-derived PBR atlases for the authorized 2 x 2 inch mosaic, 12 x 24 inch flat, and 12 x 24 inch fluted materials.

## Contents

- Each material has registered diffuse, 16-bit height, 16-bit bump, OpenGL normal, and roughness maps.
- Each atlas is at least 16 x 16 ft physically and uses exact tile-plus-grout dimensions recorded in `manifest.json`.
- `*_preview_3x3.png` and `*_grazing_lambertian_diagnostic.png` are illustrative numerical diagnostics, not native Revit or renderer output.

## Source policy

The default face source is the official `references/elm_almond/almond_main.jpg`. The eight numbered Almond WEBPs were inspected as lifestyle scenes and are excluded from sampling; Palace is a different product scene; Flute is used only as a dimensional/orientation reference. The default build therefore has one genuine official face and many deterministic spatial crops, which is a documented source limitation rather than a claim of multiple product faces.

Pass `--generated-source references/elm_almond/generated_continuous_albedo.png` to add the user-supplied continuous albedo as an explicit secondary color/crop source. It is excluded from the default source-face matching.

## Fluted relief

The fluted map uses twelve irregular horizontal rib bands across the 12 inch short axis of each landscape 24 x 12 inch tile. Pattern relief is 1.2 mm. The encoded grout floor is 1.0 mm below the tile base, making the peak-to-grout step 2.2 mm and leaving 1.0 mm clearance above the grout floor. Relief must still be reviewed under grazing light in the native application.

## Acceptance status

Hash, source registration, unique-interior, and wrapped-boundary statistics are recorded in `manifest.json`. Native Revit binding, native render, seamless visual review, and non-repetition visual review are pending. No ADSKLIB is included or claimed.

Build seed: `20260918`; map axis: `4096 px`; build source mode: `official_face_only`.
