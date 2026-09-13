# Oyster Wall Sconce - visualization family

Revit 2025 face-based Lighting Fixtures family, reconstructed from the supplied PDF, dimension image, and photographs. Place it on a native wall face. The origin is the center of the frame at its wall-contact plane, with the diffuser at the top.

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

The 0.06-in band thickness is inferred from the thin edge in the close-up photographs; the remaining width difference provides clearance around the 5-in diffuser. The diffuser is a shallow, smoothly domed lens. Its 0.8-in total thickness, exact front/back curves, depth within the frame, and concealed upper mounting/support geometry are inferred. The circular diffuser is centered on the upper semicircular end of the frame.

This is a fixed-size family. Dimension parameters report the modeled size; material parameters are editable. No IES, photometric light source, or MEP connectors are included. The luminous material approximates appearance rather than verified room illumination.

## Review and validation

Shaded front, oblique, side, and top views are supplied for geometry review. They do not verify production-render metal reflections or the intensity of the warm glow. Those depend on the project scene and exposure.

The saved RFA is reopened in Revit 2025 and checked for dimensions, diffuser diameter, an unobstructed lower opening, native wall-face placement, outward orientation, and both material substitutions. The placement check uses a disposable project and does not alter existing user projects.

Source files are preserved under `references/oyster`. Manufacturer documents and earlier fixture outputs are not altered.
