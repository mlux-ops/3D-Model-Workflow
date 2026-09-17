# Rounded Linear24 wall light — Revit 2025

Load `Linear24_Black_Patterned_Diffuser_R2025.rfa` in Revit 2025 or newer. Choose Place on Face and select a native wall face. The insertion point is the backplate center at the wall. The default orientation is horizontal; rotate 90 degrees on the wall for the vertical arrangement in the supplied photograph.

Lighting Fixtures category, face-compatible WorkPlaneBased placement. Fixed-size visualization geometry with editable type parameters for Metal Finish and Diffuser Finish. Dimension parameters document the geometry; they do not resize it. No manufacturer or SKU is asserted from these unlabeled references.

## Geometry and assumptions

The supplied drawing specifies 24 inches overall width, 5 inches overall height, 3.1 inches total projection and 4.3 inches backplate width. Printed inches are authoritative; metric labels are rounded equivalents.

Photo-derived estimates: 0.5-inch backplate depth, 0.9-inch frame height, 0.30-inch corner radius in the projecting frame, 0.13-inch perimeter wall, and 0.08-inch light-guide thickness. The light guide is recessed inside a continuous rounded frame, in a plane perpendicular to the wall. It is not a solid luminous strip on the narrow outer metal edge. Small fasteners, seams and microscopic edge rounds are omitted.

The included texture maps approximate the regular staggered microdot pattern visible in the close-up. The nominal row spacing is 0.04 inch, unmeasured. Texture geometry and optical response are inferred rather than manufacturer data. The panel has partial transmission and a warm appearance glow (3000 K, artistic setting); no IES or photometric light source, electrical connector or MEP data is included.

## Keep companion textures

Extract the entire ZIP to a permanent location. The two PNG files under `textures` are required for detailed rendered appearance. The RFA initially references their original creation location. If moved, open the Diffuser Finish appearance asset and repath its color and transparency images to the extracted `textures` folder, or add that folder to Revit's additional render appearance paths. Shaded views show material colors without the detailed texture.

Native review PNGs show geometry and viewport materials, not production-rendered photometry. Brightness, reflections and transmission depend on the renderer and scene lighting.

## Verification and delivery

See `validation.txt` for the native Revit save/reopen, bounds, material, wall-face placement and vertical-rotation checks. The package preserves all five supplied references and builder source.

Google Drive delivery is pending: the available browser redirects to Google sign-in. No cloud upload has been verified.
