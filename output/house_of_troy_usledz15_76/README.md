# House of Troy USLEDZ15-76 picture light

## Deliverable

`House_of_Troy_USLEDZ15-76_Weathered_Brass_R2025.rfa` is a Revit 2025 face-based Lighting Fixtures visualization family. Place it on a vertical wall face above artwork. The metal and LED diffuser finishes are editable family material parameters. The family has a warm diffuser appearance but does not provide a measured IES distribution, MEP connector, or verified photometric room illumination.

## Evidence and geometry

| Feature | Value | Basis |
| --- | ---: | --- |
| Manufacturer and SKU | House of Troy USLEDZ15-76 | Supplied PDF and official listing |
| Overall width, height, depth | 15 × 5.5 × 8 in | [House of Troy product page](https://www.houseoftroy.com/product/ultra-slim-line-led-picture-light-3/) and supplied PDF |
| Shade diameter | 0.75 in | [Perfect Picture Lights listing](https://perfectpicturelights.com/products/USLEDZ15-76_Ultra-SlimLine-15-LED-Weathered-Brass-Picture-Light); not in supplied PDF |
| Support arms | Two swan-neck arms | Supplied perspective product image and reseller listing |
| Finish | Weathered Brass | Supplied PDF and official listing |
| LED specification | 4.5 W, 2700 K, 90 CRI, 360 lm | Supplied PDF and official listing; metadata only, no photometric file |

The arm centerlines, arm spacing/diameter, wall clips, connection ferrules, cap seams, and diffuser size are inferred from a single perspective product image. Their precise dimensions and mounting method are not documented by the supplied source. The family represents the fixture head and wall-facing assembly; the listed eight-foot electrical cord and in-line switch are omitted from the geometry because their route depends on installation. This is a visualization approximation, not an installation or fabrication model.

## Native validation

Revit 2025 reported 12 solid parts with bounds of **15.0 W × 5.5 H × 8.0 D in**. The saved RFA reopened as a family, placed successfully on a disposable wall face, and both `Metal Finish` and `LED Diffuser Finish` accepted replacement materials. Family and project warning counts were zero. The included front, side, and oblique views were exported from Revit and reviewed for silhouette. They are shaded geometry previews, not a photometric or production-render review.

## Contents

- `references/Houseoftroy.pdf`: untouched user-provided source.
- `validation.json`: native Revit build, reopen, wall placement, warning, and editable-material checks.
- `USLEDZ15-76*.png`: native family review views.
- `source/build_house_of_troy_usledz15.py`: Revit family generator.

## Load

In Revit 2025 or newer, use **Insert > Load Family**, select the RFA, then place the `15 in - Weathered Brass` type on a vertical face. Change `Metal Finish` and `LED Diffuser Finish` in the family type if your project uses other materials.
