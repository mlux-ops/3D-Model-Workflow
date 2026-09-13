# Oyster Wall Sconce - visualization family

Revit 2025 face-based Lighting Fixtures family, reconstructed from the supplied PDF, dimension image, and photographs. Place it on a native wall face. The origin is the center of the frame at its wall-contact plane, with the diffuser at the top.

Use **Hollis_Morris_Oyster_Visualization_R2025_v2.rfa** for the corrected full-depth diffuser. It has a separate family name because the original was open in another Revit instance. Loading it creates a separate family; switch existing Oyster instances to the v2 family/type to use the correction.

## User-selected appearance

- Neutral satin stainless-steel appearance for the metal frame.
- Smooth frosted acrylic diffuser with soft warm glow.

These selections override the supplied PDF's brushed-brass/patterned-acrylic variant. They describe the requested visual model and do not establish an exact manufacturer finish code. The example photo numbered 1353351 is used as an appearance reference, not as verified product metadata.

Editable type material parameters: **Frame Finish** and **Diffuser Finish**. The frame uses a native stainless-steel appearance asset. The diffuser uses a smooth frosted material with 3000 K self-illumination; luminance is an artistic setting.

## Material files when transferring

The stainless appearance references standard Autodesk satin-steel color and bump images. All six installed resolution variants are included in the package's `textures` folder, retaining their relative directory structure. They were checked against the installed originals. The smooth diffuser has no image dependency.

Keep the extracted package together. On a machine where the standard Autodesk textures are unavailable, relink the frame material's missing appearance images to the included files. The highest-resolution alternatives are `textures/3/Mats/Metals.Ornamental Metals.Stainless.Satin.jpg` and `textures/3/Mats/Metals.Ornamental Metals.Stainless.Satin.bump.jpg`. The family itself remains loadable if appearance images need relinking.

## Geometry and confidence

The dimension drawing specifies a **5.24 in width, 12 in height, 3 in projection, and 5 in diffuser diameter**. The capsule frame is a thin continuous metal band with an open lower area through which the native wall remains visible. There is no full-height backing panel.

The 0.06-in band thickness is inferred from the thin edge in the close-up photographs; the remaining width difference provides clearance around the 5-in diffuser. The diffuser is one continuous cylindrical piece, 5 inches in diameter and the full 3-inch fixture depth, as confirmed by the user and the additional manufacturer close-up. It extends from the wall-contact plane to the frame front. Its circular front is nearly flat with a small 0.04-inch edge radius; that radius remains an estimate. The circular diffuser is centered on the upper semicircular end of the frame. Unseen internal construction is omitted.

This revision replaces the earlier shallow 0.8-inch domed diffuser. The additional photograph is used for geometry only; the selected stainless appearance and smooth warm-glowing material remain unchanged. The previous RFA and build notes are preserved locally under `revisions/shallow-diffuser-v1`.

This is a fixed-size family. Dimension parameters report the modeled size; material parameters are editable. No IES, photometric light source, or MEP connectors are included. The luminous material approximates appearance rather than verified room illumination.

## Review and validation

Shaded front, oblique, side, and top views are supplied for geometry review. They do not verify production-render metal reflections or the intensity of the warm glow. Those depend on the project scene and exposure.

The saved RFA is reopened in Revit 2025 and checked for dimensions, diffuser diameter, a single continuous diffuser solid spanning the full 3-inch depth, an unobstructed lower opening, native wall-face placement, outward orientation, and both material substitutions. The placement check uses a disposable project and does not alter existing user projects.

Source files are preserved under `references/oyster`. Manufacturer documents and earlier fixture outputs are not altered.
