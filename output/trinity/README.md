# Trinity Low Pendant - visualization family

Revit 2025 face-based Lighting Fixtures family, reconstructed from the supplied Lightology product PDF and four photographs. Place the canopy on the underside of a native ceiling or other horizontal overhead face. The origin is the center of the canopy's ceiling-contact surface.

## Dimensions

- Shade diameter: **14.25 in**.
- Shade height: **6.125 in**.
- Bottom opening diameter: **9.75 in**.
- Canopy diameter: **4.75 in**, thickness **0.25 in**.
- Ceiling-to-bottom drop: **48 in**, selected by the user.

The shade and canopy dimensions come from the dimension drawing embedded in the supplied PDF. Its 4.875-in internal vertical dimension is interpreted as the distance from the recessed light plane to the lower opening, positioning the diffuser approximately 1.25 in below the shade top.

The shade is a hollow smooth revolved shell with a real open underside. Rounded shoulders and the larger lower opening are reconstructed from the photographs. Estimated details include the exact shoulder curves, 0.08-in glass thickness, 6.2-in upper opening, 6.6-in internal lamp housing, 5.29-in diffuser, 0.375-in downrod, and small fittings. These are visualization estimates, not manufacturing dimensions.

This version has fixed geometry. Its dimension parameters report the modeled dimensions; they do not change suspension length. The selected total drop is an installation modeling choice and does not assert an exact assembly of the supplied stock rod segments.

## Materials

Separate editable type parameters control **Black Metal Finish**, **Smoke Glass Finish**, and **Diffuser Finish**. The smoke material uses a native Revit Solid Glass appearance asset with custom gray transmission. No external texture files are needed.

The user selected soft warm glow. The recessed diffuser has a self-illuminated material with a 3000 K appearance temperature matching the product specification; luminance is an artistic setting. No IES, MEP connectors, or photometric light source is provided. Material glow is not verified room illumination.

Reflections, smoke density, transmitted light, and perceived brightness depend on the rendering scene and exposure. They remain visual approximations rather than measured manufacturer optical data.

## Review and validation

Shaded full, front, oblique, and underside previews show geometry. Suspension is hidden in close-up views. Preview shading is not a production rendering of the requested smoke and glow appearance.

The automatic Realistic viewport did not provide a reliable view of the diffuser glow, so its image is excluded from the package. The saved glow settings and smoke-transmission color are checked separately; final appearance remains to be reviewed in a project rendering.

The saved family is reopened in Revit 2025 and checked for dimensions, open underside, material bindings, and downward placement on a native overhead face in a disposable project. Curved diameters are measured by intersection with the analytic solids; the report also retains the display-derived bounds. Existing user projects are not modified.

Source documents are preserved under `references/trinity`. No manufacturer family was copied or altered.
