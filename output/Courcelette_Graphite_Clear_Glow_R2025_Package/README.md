# Courcelette Linear Pendant - visualization family

Revit 2025 face-based Lighting Fixtures family, reconstructed from the supplied Lightology PDF, dimension drawing, and product photograph. Place the canopy on a native ceiling underside or other horizontal overhead face. The origin is the center of the canopy's ceiling face. Local X follows the fixture's long axis.

## Dimensions and source confidence

- Specified overall body: 46.6 in long x 21.59 in wide x 12.95 in high.
- Total ceiling-to-bottom drop: **50.5 in**, selected by the user. The PDF lists an available 30.5-70.5 in range.
- Six 8-in globes and three opposing, crossed arm pairs are reconstructed from the orthographic drawing. Globe diameter, exact arm angles and elevations are drawing-derived estimates, not individually dimensioned manufacturer values.
- Photo-estimated details include a 5-in diameter x 0.9-in canopy, 0.36-in arm/downrod diameter, 1.6-in hub diameter, 0.06-in glass thickness, globe mounting openings, and simplified sockets/bulbs. Small downrod joints and canopy fasteners are included where supported by the references.
- The hollow globes have inward-facing openings. Smooth analytic curved geometry is used, with no external mesh imports.
- This model has fixed geometry. The dimension parameters report that geometry and do not flex it to another suspension length.

## Appearance

The PDF specifies graphite metal and clear glass. Three editable type material parameters control **Graphite Finish**, **Clear Glass Finish**, and **Bulb Finish**. The user selected a soft warm bulb glow, represented by the bulb appearance material. The 2700 K and luminance settings are artistic approximations; no photometric light source, IES, or MEP connectors are supplied.

Native Revit appearance assets are included in the RFA. No external textures are needed. The hollow clear globes let the graphite sockets and warm bulb forms remain visible. Glass reflections, transmission, and perceived brightness still depend on the rendering scene and exposure.

## Review and validation

The package includes shaded Revit views of the full pendant, body, front, side, and plan. These are geometry reviews rather than final production renderings. Canopy and suspension are hidden only in the close-up body views.

Validation checks the saved/reopened Revit family, globe and bulb counts, analytic glass-shell extents, fixture height, downward placement on a native overhead face, material substitutions, and warnings. An isolated disposable project is used; existing user projects are not modified. Analytic sphere intersections are used because display-derived bounding boxes can slightly underestimate curved geometry.

Manufacturer source documents are preserved under `references/courcelette`. No manufacturer RFA was used or altered.
