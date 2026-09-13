# Tris 3-light visualization family

Revit 2025 face-based family, Lighting Fixtures category. Origin is at the center of the backplate's mounting surface. Place on the face of a native wall; the bar runs horizontally and the acrylic panels project outward.

## Appearance

- Polished chrome housing and rail.
- Three separate thin horizontal acrylic panels with an approximate fine etched-dot pattern.
- Unlit translucent materials, as requested. No self illumination, IES definition, light source, or MEP connectors is intended.
- Type materials: **Metal Finish**, **Diffuser Finish** (top/bottom panel faces), and **Acrylic Edge Finish**.

The dot pattern is represented by two small texture maps rather than modeled bumps or holes. The textures are stored under `textures` and referenced by the materials. They remain available at their current workspace paths when the RFA is loaded into a project on this computer. When transferring to another computer, extract the complete package and set the two image paths in the Diffuser Finish material to the included PNGs, or add that textures folder to Revit's Additional Render Appearance Paths. The family geometry loads independently of these texture maps.

## Geometry and source confidence

The supplied dimension image governs overall width **25.6 in**, projection **3.4 in**, and backplate **5 x 4.5 in**. Inch values are used; the screenshot's metric labels are rounded.

The photos establish three projecting horizontal blades, a continuous chrome rail, shallow channels, terminal caps, and a central backplate. Estimated details include 6.2-in panel width, 0.18-in thickness, 3.5-in gaps, 0.76-in rail height, channel dimensions, backplate depth, small corner radii, and microdot pitch. These are visualization estimates, not manufacturing or optical specifications.

This is a fixed-size reconstruction from the supplied images. Material settings approximate unlit acrylic and chrome; they are not measured manufacturer optical data. No existing manufacturer RFA was used as the geometry source.

## Review and validation

The packaged PNGs provide front, side, top, and oblique shaded geometry views exported from Revit. These are not production renderings. The automatic Realistic family preview did not provide a useful environment for evaluating mirror chrome and translucent acrylic, so it is excluded from the delivery package. The saved material assets, texture links, and material substitutions were checked; final reflected/transmitted appearance should be reviewed in the intended project scene.

`validation.json` records save/reopen, actual bounds, three-panel separation, face placement, outward orientation, independent material substitution, and Revit warnings checks. The project used for placement testing is disposable and does not modify a user project.
