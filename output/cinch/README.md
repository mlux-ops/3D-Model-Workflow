# Cinch wall fixture — Revit 2025

Open or load `Cinch_18_625_Brushed_Metal_R2025.rfa` in Revit 2025 or newer. In a project, use Place on Face and select a native wall face. The insertion point is the center of the backplate at the wall surface. Rotate on the face if needed.

Lighting Fixtures category; face-compatible WorkPlaneBased placement. This is a fixed-size visualization family. Metal Finish and Diffuser Finish are editable type material parameters. Dimension parameters document the fixed geometry; they do not resize it.

## Dimensions

The supplied drawing governs all dimensions: bar width 18 5/8 inches, body height 2 3/8 inches, total projection 2 1/2 inches, backplate width 5 3/4 inches, backplate height 2 7/8 inches, backplate depth 7/8 inch. Overall model bounds are 18.625 × 2.875 × 2.5 inches.

The bar depth (1.25 inches), central metal band height (1.30 inches), standoff size, metal thickness and cap seams are estimated from the supplied photographs and drawing. Small edge rounds, mounting screws and hidden electrical components are omitted. Source filenames identify this as Cinch; no manufacturer SKU or certified BIM status is asserted.

## Appearance

Separate continuous upper and lower opal diffusers, central satin metal band with metal end returns, rectangular backplate and concealed standoff. The metal is a texture-free satin approximation of the photographed brushed finish; microscopic directional brushing is not reproduced. Materials are embedded, so there are no external texture dependencies.

The diffuser has a modest warm-white appearance glow based on the illuminated photographs. The 3500 K appearance setting is an artistic assumption, not a verified product rating. No photometric light source, IES file or MEP connector is included. Revit viewport exports are geometry/material review views, not production renders; default viewport lighting makes front-facing surfaces dark in oblique views. Actual rendered appearance depends on scene lighting and renderer.

## Verification

Created, saved and reopened in Revit 2025. Checked exact overall bounds, native wall-face hosting, outward mounting orientation, both material substitutions, and zero family/project warnings. See `validation.txt`. Front, side and oblique native exports reviewed against the supplied images. Undimensioned details remain approximations.

The package includes the native family, review PNGs, source images, setup notes and C# builder source. Google Drive upload is pending: the available browser is not signed in to Drive.
