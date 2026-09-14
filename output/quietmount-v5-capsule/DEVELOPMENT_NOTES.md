# Development notes

The installed render uses the generated geometry and an illustrative transparent sample, not a photograph or a physical test. Mesh cleanup after the render removed tiny coplanar triangulation remnants without changing the design silhouette.

The final 24 project objects were checked after native export and slicing for six global walls, 100% per-object rectilinear infill and no supports. Bambu serializes the Rectilinear pattern as `zig-zag`, as shown in its [official PrintConfig source](https://github.com/bambulab/BambuStudio/blob/master/src/libslic3r/PrintConfig.cpp). Using the old `rectilinear` string caused substitution with Cubic; the delivered files use the verified `zig-zag` value.

Digital validation checks STL manifold edges, face winding, connected shells, degenerate triangles, positive volume, actual sample solid intersections, the top release sweep in 15-degree steps, and clearance around a 3.5 mm shaft / 7.5 × 2.8 mm head envelope. Cosmetic retaining petals intentionally have small interference with the bore. No mechanical strength or real fit claims follow from these checks.

Only source, output and preview files within this workspace were modified. No print job was sent and no active Bambu project was replaced.

Preset import correction: the initial process JSON lacked `version`, while the exported printer JSON was a system profile for CLI use. Added version 2.7.0.8 to the process generator, moved the system machine file into internal/, excluded it from the consumer ZIP, and regenerated both native 3MF files. Bambu Studio's GUI confirmed "There is 1 config imported" for the repaired process. Selected it in the existing QuietMount_Capsule_H2D_Project window. The printer is Bambu's built-in H2D with 0.4 mm Standard nozzles. The ongoing printer job was not changed.
