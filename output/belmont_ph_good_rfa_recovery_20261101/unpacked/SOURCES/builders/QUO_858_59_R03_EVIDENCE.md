# Quorum Veno 858-59 R03 photo-interpreted silhouette

Status: SOURCE CODE ONLY. No native Revit run, approval, or RFA delivery.

Official product: https://quoruminternational.com/products/858-59

Official dimensioned cut sheet: https://images.junipercdn.com/3206/application-assets/juniper-web/product%20cut%20sheets/858-59.pdf

Supplied product image: https://cdn11.bigcommerce.com/s-c1csojjx4j/images/stencil/494x536/products/4597273/5799746/1302095__38680.1750748034.jpg?c=1

Manufacturer-supported geometry: overall fixture D11in x body H19in,
shade H11.25in, canopy D4.75in x H0.75in. One E26 100W maximum;
rods supplied in pairs at 8in, 12in and 16in, plus 12in chain.

R02 used a straight cylindrical glass shell. R03 instead uses a single
native solid of revolution with a closed XZ annular section and an
open bottom and top. The section is photo interpreted. Intermediate
radii and the 0.125in wall thickness are not OEM measured.

| Height above bottom (in) | Interpreted outer radius (in) |
| ---: | ---: |
| 0.00 | 4.65 |
| 0.70 | 4.80 |
| 1.70 | 5.15 |
| 3.20 | 5.50 |
| 4.70 | 5.42 |
| 6.25 | 4.95 |
| 7.75 | 4.12 |
| 9.10 | 3.05 |
| 10.25 | 2.22 |
| 11.25 | 1.72 |

The maximum diameter is bounded to 11 inches. The 24in selected
straight rod comprises two of the manufacturer's 12in rods.
Canopy, socket and visible metal structure remain approximations.
No photometric distribution or precise CAD has been substantiated.

The builder calls DB.GeometryCreationUtilities.CreateRevolvedGeometry,
following the existing native Revit 2025 helper pattern in this project.
It does not call CurveLoop.CreateViaReversed. The R02 CurveLoop.Flip()
fix and both earlier builders are preserved unchanged. On later
execution, inspect native solid creation, warnings, hosting, glass
material substitutions, measured maximum diameter, full vertical
envelope, and front/side/oblique visual match. Polygonal section edges
may require tangency refinement after native visual review.
