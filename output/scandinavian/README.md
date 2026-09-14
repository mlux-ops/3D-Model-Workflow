# Scandinavian Decor Grey — 6 x 7 inch hexagon material

Made from your supplied single-tile photograph, with 0/120/240-degree rotations forming the three-tile star/fan arrangement visible in your installation photograph. The tile is interpreted as 7 inches across points (horizontal), 6 inches across flats (vertical). Nominal 1/16 inch light grout is an assumption.

## Files and setup

- Scandinavian_Decor_Grey_R2025.adsklib: open in Revit 2025 under Manage > Materials > Open Existing Library, then add the named Scandinavian material to your project.
- Scandinavian_Material_R2025.rvt: optional source project containing the same material.
- Scandinavian_Decor_Grey.vrmat: import in V-Ray Asset Editor. Alternatively use the material-only .vrscene with material name Scandinavian_Decor_Grey in a host supporting scene material loading.
- textures: required external maps. Keep this folder with the material files. Repath textures after moving the package; Revit's library initially references output/scandinavian/textures in this workspace.
- Pattern_Preview.jpg: flat repeated color-map preview for arrangement review, not a native render.

The rectangular texture repeat is **10.609375 inches wide x 18.1875 inches high** (269.478125 x 461.9625 mm), including joints. Revit appearance scale is set to this. For V-Ray, set mapping channel 1 and the same physical UV repeat. The repeat contains six hexagons; do not scale the entire image to 6 x 7 inches. Rotate the whole material if needed to align it with your floor.

Color: supplied 1535 x 1329 photo sampled and rotated, retaining its grey mottling and white print. Output 2389 x 4096 pixels; this is a multi-tile map, not a claim of 4K detail per hexagon. Source lighting/white balance is retained and not calibrated.

Bump: 16-bit grayscale, only grout and softly beveled tile edges. White printed rays remain flat. Normal: 16-bit RGB tangent-space OpenGL map. Use linear/raw for normal, bump, and roughness; sRGB for color. Do not feed the RGB normal into a grayscale bump slot. Displacement is disabled. Full height range is an estimated 0.25 mm, with actual height difference 0.15 mm. Matte finish assumptions: roughness 0.60, Fresnel IOR 1.5. Revit uses its own bump/glossiness controls.

Revit source was saved and reopened in Revit 2025 with zero warnings. V-Ray scene parsed successfully; rendering is blocked by unavailable Chaos license (-98), and native VRMAT import is unverified. The room photo establishes arrangement, not measured material properties. Review the included pattern locally before publishing.
