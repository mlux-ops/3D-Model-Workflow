# Icera Malibu II RF — C-6360.01

Independent Revit 2025 visualization family. White ceramic, white closed seat and lid, polished chrome tank lever. Category: Plumbing Fixtures. Native horizontal face placement; no MEP connectors or internal flushing mechanism.

Revit 2025 native family, with independent visualization geometry. Validation details are in `validation.json` and `REVIEW.md`.

## Load and place

Load `Icera_Malibu_II_RF_C-6360.01_R2025.rfa` into Revit 2025 or newer. Choose Place on Face and select the top face of a native floor. The origin is the rear center at finished floor; the fixture extends along local +Y. Position the rear face 1/2 inch from the finished wall. The nominal outlet center is 11-1/2 inches forward of the family origin, giving 12 inches from the wall. The outlet and plumbing are not modeled.

Edit the type's Ceramic Finish, Seat Finish, and Lever Finish material parameters to change appearance. Geometry dimensions are fixed reference values; this is not a resizable product family. Seat is modeled closed.

## Reference and accuracy

Source: [Icera official specification, C-6360](https://icerabath.com/wp-content/uploads/2024/11/Icera_spec_C-6360.pdf), preserved unchanged in the package. Page 1 supplies photographs; page 2 supplies the dimension drawing. The photo shows an optional black lever; this family uses the specified standard polished chrome finish.

Printed inches govern: tank width 15-7/8 inches; overall ceramic height 28-7/8 inches; depth 24-5/8 inches; ceramic bowl rim 16-1/2 inches; tank depth 6-3/4 inches; base width 10-7/8 inches; rough-in 12 inches. The side lever projects beyond the nominal tank width. The current drawing takes precedence over older legacy-page nominal width/height values.

Drawing/photo-derived or inferred: curved skirt and bowl sections, tank corner radii, lid profiles, closed-seat height and seams, cover-tile position, lever size and appearance response. The bowl interior is concealed and omitted. External forms are visualization solids, not a manufacturing or installation model. Separate components overlap where concealed; internal ceramic wall thickness is not modeled.

## Package contents

- Native RFA and exported front, side, top, oblique, and material review images.
- Manufacturer specification PDF.
- Reproducible Revit Python builder and validation report.

The supplied builder runs through pyRevit CLI in Revit 2025. Its ROOT and TEMPLATE paths must be updated when rebuilding on another computer. Loading the finished RFA does not require pyRevit or the builder.
