# F09 - Il Fanale Madame A.288.10.ON - Brass

This folder prepares the exact linked Lightology selection as a native Revit 2025 face-based Lighting Fixtures family.

The exact option is A.288.10.ON / IFA1254270 in Brass. Lightology publishes 2.36 in W x 16.33 in H x 14.17 in D. Its product Q&A separately gives a 3.94 in diameter backplate. The dimension diagram and product photo show that the 2.36 in value belongs to the cylindrical head. The builder therefore preserves 2.36 in as the head outside diameter and validates a 3.94 in installed envelope width because the U.S. junction canopy is wider.

Geometry modeled from the source silhouette:
- convex 3.94 in circular U.S. canopy against the host face;
- small lower spherical arm joint;
- thin U-shaped bent brass arm;
- spherical shoulder above the shade;
- 2.36 in OD open-bottom cylindrical shade with a rounded upper shoulder;
- recessed warm lamp/interior cue inside the open shade.

Exact/drawing-derived values:
- head diameter: 2.36 in;
- overall height: 16.33 in;
- projection: 14.17 in;
- U.S. backplate diameter: 3.94 in.

Image-derived/inferred values:
- 0.30 in arm tube diameter;
- 0.96 in lower joint sphere diameter;
- 0.90 in upper shoulder sphere diameter;
- 1.68 in canopy projection/profile depth;
- 0.16 in nominal shade wall thickness;
- exact arm bend radius and vertical break points.

Native execution is serialized by prime. The builder uses output/lightology_20260923/tools/native_fixture_support.py, the Revit 2025 English-Imperial Generic Model face based.rft template, Lighting Fixtures category, editable Brass and Lamp/Interior material parameters, saved-RFA reopen validation, true wall-face hosting, placement-normal verification, material substitution reaching geometry, warning checks, and front/side/oblique/material/hosted PNG exports.

Prime-only native command:
D:\Games\pyRevit-Master\bin\pyrevit.exe run "E:\Claude\3D-Model-Workflow\output\lightology_20260923\f09_1254269\build_madame.py" --revit=2025

Preparation status: builder/source package ready after syntax/static checks. Native RFA, validation JSON, and review PNGs remain pending prime's serialized Revit run.
