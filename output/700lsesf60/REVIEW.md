# Review — 2026-09-15

## Native checks passed

- Saved and reopened the main RFA in Revit 2025.
- Lighting Fixtures category; WorkPlaneBased family with successful native underside-face placement.
- Total Drop tested at 13.2, 36, 48, and 67.2 inches. Actual ceiling-to-bottom distances match within floating-point precision.
- All three type material parameters successfully change corresponding placed geometry.
- No family or project warnings.
- Lower body native bounds confirm 60-inch length and 4.8-inch height. Circular display bounding boxes understate the Y diameter; the revolved analytic profiles use a 1.25-inch outer radius. The display bound is not a dimensional diameter measurement.

## Visual review

Front, side, and oblique shaded exports were inspected against the supplied drawing/photos. They show the narrow straight bar, six evenly spaced cylindrical lamps, overlapping black caps, clear outer cylinders with inset pale diffusers, rectangular canopy, and two slim rods. Their 48-inch total drop is an installation default, not the exact photographed drop. Couplings and hidden attachment details are simplified as stated in README.

## Unresolved Realistic viewport export issue

The native Realistic PNG shows excessively bright/white metal faces and washed-out diffusers. Reducing grazing reflectivity and explicitly disabling metallic mode did not resolve the export. A saved-family appearance audit confirms RGB 25/26/28 for the metal, opacity, zero glow, no connected texture maps, glossiness 0.35, and reflectivity 0.08/0.12. The precise cause of the viewport discrepancy remains unknown. Do not treat the Realistic PNG as an approved material/render match. Use shaded exports for geometry review; evaluate appearance in the intended scene/renderer before production rendering.

Appearance assets are embedded and editable. No claim of a production-rendered or photometrically accurate result is made.
