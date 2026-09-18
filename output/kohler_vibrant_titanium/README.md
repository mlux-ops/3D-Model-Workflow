# KOHLER Vibrant Titanium (TT) — Revit 2025

Material: **KOHLER - Vibrant Titanium (TT) - Polished**.

Independent visual approximation from the four supplied product images and [Kohler's finish sheet](https://resources.kohler.com/webassets/kpna/brochures/Titanium_SellSheet_FIN_.pdf). Dark, slightly warm gray polished metal with strong reflections. Optical settings are inferred; this is not a manufacturer-certified material or measured finish sample.

## Load the material

1. Extract the package to a permanent folder.
2. In Revit, open **Manage > Materials**. Show the library panel, then use its library menu > **Open Existing Library**.
3. Open `KOHLER_Vibrant_Titanium_TT_R2025_Bitmap.adsklib` and add **KOHLER - Vibrant Titanium (TT) - Polished** to your project.
4. Assign it to the fixture's material parameter or geometry. Use its **Appearance** asset for rendering.

Keep the `Textures` folder with the library. The Appearance asset uses `Textures/KOHLER_Vibrant_Titanium_TT_Color.png` as an explicit color map. The map is spatially uniform, so it is inherently seamless and has no visible repeat, baked highlight, logo, scratch, or directional grain. Reflections depend on your scene: bright walls/windows create bright bands; dark surroundings produce the charcoal look in the references. Shaded mode uses a uniform gray and does not reproduce polished reflections.

Native Generic appearance: Metallic enabled; color RGB 108/104/101; glossiness 0.94; normal reflectivity 0.65; grazing reflectivity 0.98; opacity 100%; one diffuse color-map connection; bump and self-illumination disabled. This clean polished finish deliberately has no invented brushed grain.

Validation is recorded in `REVIEW.md`. Temporary Revit test projects are excluded from delivery. V-Ray assets: not requested.

The earlier texture-free library remains untouched because Revit had it locked during this revision. Use the `_Bitmap.adsklib` file above; it is the superseding library for this package.
