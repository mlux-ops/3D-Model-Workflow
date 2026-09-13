# AXOR angled faucet — manufacturer-based revision

Load `AXOR_Angled_Faucet_Brushed_Black_Chrome_R2025_v2.rfa`, then switch existing instances to the v2 family/type. This is a separate Revit 2025 face-based Plumbing Fixtures family, preserving the previous version.

The supplied manufacturer 39835USA family was opened and measured without saving changes. Its shared body/base, control joint, and curved lever solids replace the earlier estimated assembly. The rear projection, offset base, flowing body-to-control transition, and handle surface contours are retained directly from the manufacturer geometry. Selected source element IDs are 4108, 4101, and 4105; alternative overlapping representations were excluded.

Shared parts are transferred at original size using rigid transformations only. The handle is rotated 45 degrees from the manufacturer's stored operating position into the upright reference position. Source and transferred solid volumes are compared in the validation report. No scale change is applied to these parts. The resulting upright handle height is about 8.79 inches; this source-based geometry differs slightly from the drawing's rounded 8.875-inch handle annotation. The reporting parameter reflects the transferred geometry.

The smaller angled spout remains reconstructed from the supplied drawing: 13.5-inch overall height, 8-inch reach, 10.375-inch outlet center height, and 20-degree outlet inclination. The manufacturer base follows its nominal 64 mm size (approximately 2.52 inches), rather than forcing the rounded 2.5-inch annotation. The family origin is at the spout axis on the countertop plane; the base extends farther behind that axis, as in the source model.

Place on a native horizontal face. Local X points toward the outlet, local +Y toward the control, and local Z upward. `Metal Finish` retains the brushed black chrome approximation; `Outlet Finish` controls the dark aerator and spout seam. Both materials are editable. No internal plumbing or MEP connectors are included.

The manufacturer body and handle contours are now source-based. Spout bend radii, outlet details, and exact material optical properties remain approximations. The finish is not a measured manufacturer appearance asset. Shaded previews review geometry; production reflections depend on the project environment.

Validation reopens the saved RFA, checks height, transferred solid volumes, rear extension, material substitutions, and native horizontal-face placement. Manufacturer and earlier generated families remain unchanged.
