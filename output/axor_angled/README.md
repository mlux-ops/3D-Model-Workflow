# AXOR angled-spout faucet

Revit 2025 face-based Plumbing Fixtures family. Place on a native horizontal countertop face. The base center is the family origin; local Z points upward, the spout extends along local X, and the control is on the local +Y side. Rotate in the host plane to orient it toward the sink.

The latest angled-spout photograph `154__apu90602_tif.png` and drawing `Screenshot 2026-09-06 003554.png` govern this model. The previous gooseneck proposal and 16.75-inch drawing are superseded. Exact AXOR product SKU is not verified.

Drawing dimensions: 13.5-inch overall height, 8-inch horizontal spout reach to outlet center, 10.375-inch outlet center height, 2.5-inch base diameter, and 8.875-inch handle height. The drawing also shows the control extending to 5.25 inches from the opposite base edge. Inch values govern because the paired metric labels are rounded. The outlet is inclined 20 degrees from vertical.

The spout is a continuous swept round profile with tangent bends. A separate short outlet collar and dark recessed aerator follow the photo. The body, side control, and sculpted lever are native Revit solids with editable `Metal Finish` and `Outlet Finish` type material parameters. Dimensions are fixed reporting parameters, not adjustable geometry controls. No MEP connectors or internal plumbing are modeled.

Tube diameter (1.1 inches), bend radii, base thickness, body contour, hub sizes, and lever thickness/curvature are inferred from the drawing and photographs. Concealed details and branding are omitted. The brushed black chrome appearance approximates the warm dark metallic tone and softened reflections in the supplied photograph; fine directional brushing and exact manufacturer optical properties are not calibrated.

Validation checks saved-family reopening, size, native horizontal-face placement, outward orientation, material substitution, and Revit warnings in a disposable project. Geometry previews do not establish a production-render material match; reflections depend on the scene.

The two governing source images are preserved in `references/axor_angled` in the workspace.
