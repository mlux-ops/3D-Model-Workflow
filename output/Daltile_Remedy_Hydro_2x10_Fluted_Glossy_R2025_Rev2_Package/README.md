# Daltile Remedy Hydro — 2x10 Fluted Glossy

Revit 2025 material library for Daltile Remedy Hydro, Fluted, Glossy, SKU `RD22RCT210FLUGL`.

Manufacturer facts used: nominal 2 x 10 in, nominal 1/2 in thickness, glossy finish, V4 Random shade variation. The color atlas is derived from official Daltile Hydro imagery. The flute height is recreated as geometry in the bump/normal maps rather than copied from photographed lighting.

## Load in Revit

1. Keep the `.adsklib` and `textures` folder together.
2. Revit > Manage > Materials > Material Browser > Open Existing Library and select `Daltile_Remedy_Hydro_2x10_Fluted_Glossy_R2025_Rev2.adsklib`.
3. Add the material to the project. If Revit reports missing texture paths after moving the package, repath the Base Color and Bump maps to the supplied `textures` folder.

The ADSKLIB binds the BaseColor and 16-bit Bump maps. A registered tangent-space OpenGL Normal map and Roughness map are included as companion assets for renderers that support them.

Physical atlas: 201.2500 x 20.6250 in (20 x 10 tile modules) with assumed 1/16 in grout. The finite bitmap repeats mathematically, but the atlas deliberately uses broad V4 per-tile variation and avoids immediate duplicate palette assignments.

Relief estimate: pattern 1.20 mm; grout step 2.20 mm; remaining clearance 1.00 mm. Daltile does not publish flute depth, so these are visual/rendering estimates, not measured product geometry.
