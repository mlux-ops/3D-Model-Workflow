# Tris light visualization family plan

Goal: Build a Revit 2025 face-based lighting visualization family from the eight supplied images, applying the Purist comparison lessons.

Scope: Chrome housing, thin horizontal rail, three separate acrylic light-guide panels; no connectors, IES data, or engineering systems. Preserve all existing fixture outputs and generators.

## Source interpretation

- Overall width: 25.6 in; projection: 3.4 in.
- Backplate: 5 in wide x 4.5 in high. The supplied inch labels govern; rounded metric labels are not a separate constraint.
- Family axes: X along bar, Y up the wall, Z away from wall. Origin at backplate center on mounting surface.
- Source photos show three horizontal acrylic blades projecting away from the wall, not three vertical shades.
- Estimated panel widths: 6.2 in each; centers at X = -9.7, 0, +9.7 in, giving two 3.5 in clear gaps.
- Estimated panel thickness: 0.18 in; panel depth from Z=1.17 to 3.4 in. Bar height about 0.76 in. Backplate depth about 0.45 in.
- Model continuous rail with two shallow longitudinal channels and simple end caps visible in references. Avoid speculative internal hardware.
- Use restrained rounded plate/panel corners; no invented large bevels or extra seam rings.
- A fine material texture represents the diffuser microdots, avoiding thousands of tiny solids. Its spacing is an appearance approximation, not optical engineering data.
- User selected unlit translucent panels. Both acrylic appearance assets have zero self illumination.

## Implementation and acceptance

- [x] Read workflow lessons and preserve eight source images.
- [x] Write an acceptance check for a saved/reopened RFA and run it before building.
- [x] Create a separate Tris generator using the proven Revit 2025 workflow; retain original Purist generator unchanged.
- [x] Generate chrome and diffuser materials, analytic solid geometry, fixed dimensions, editable finish parameters, and review views.
- [x] Reopen and measure actual geometry; verify three separated panels, plate dimensions, wall face placement, outward orientation, and independent material substitutions.
- [x] Inspect front, side, top, and oblique views; distinguish measured geometry from appearance estimates.
- [x] Prepare RFA, texture asset package, previews, and short accuracy notes for delivery.

Technical lesson: paint assigned through a family parameter is baked into the loaded instance's face material IDs. Verify those geometry IDs rather than relying only on project-level GetMaterialIds(true). The alternate diffuser material appeared on loaded geometry and the original finish was restored.

Visual limitation: the automatic Realistic family view lacks a useful reflective environment, so it does not substantiate a production render match. Package shaded geometry views and explicitly retain project-scene appearance review as a limitation.
