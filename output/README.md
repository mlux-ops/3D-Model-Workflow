# KOHLER Purist visualization pilot

File: `KOHLER_Purist_K-T14489-4_CP_Visualization_R2025.rfa`

- Revit 2025 family, category Plumbing Fixtures.
- Face-based template; work-plane-based family placement.
- Origin: center of the escutcheon's rear mounting face.
- Fixed nominal product size. Geometry uses nine native analytic freeform solids, with smooth revolved profiles rather than an imported polygon mesh.
- Type parameter **Finish** controls every visible part. Default: **KOHLER CP - Polished Chrome**, using Revit's **Chrome - mirror** appearance asset.
- No MEP connectors or operational data.

## Place in Revit

Load the RFA into the project. Use **Place on Face** and select the desired face of the native wall. The plate's back sits on the selected face and the handles project outward. The placement origin is the center of the circular plate. Change the **Finish** type parameter to use another Revit material; duplicate the type first if existing instances should retain chrome.

The three `Visualization` 3D views inside the family are for close-up review. Exported PNGs are shaded geometry previews, not photorealistic renderings. Rendered chrome will reflect the lighting and surroundings in the project.

## Accuracy boundaries

The supplied dimension PDF and the matching product specification PDF in Downloads were used. Printed inch dimensions take precedence over the drawing proportions and rounded metric equivalents:

| Feature | Nominal value |
|---|---:|
| Circular plate diameter | 7.25 in |
| Projection from mounting face | 4.25 in |
| Handle-axis spacing | 3.125 in |
| Each outer lever tip from its axis | 3 in |
| Overall height, derived from those labels | 9.125 in |

Undimensioned barrel and lever diameters, inward lever lengths, plate curvature/thickness, stem transitions, and small edge radii are reconstructed approximations. Chrome uses a standard Revit appearance asset, not measured manufacturer optical data. Small branding and temperature markings are omitted.

The example RFA was not found at the supplied path, so this model has not been compared against that benchmark. It is an independent reconstruction, not an edited or renamed manufacturer family.

`purist-validation.json` records actual Revit save/reopen, measured dimensions, wall-face placement, orientation, material substitution, and warnings checks. The generator and acceptance checks are retained in the workspace for repeatability.
