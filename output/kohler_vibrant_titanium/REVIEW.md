# Material review

- Material ID: KOHLER - Vibrant Titanium (TT) - Polished.
- Reference: four user-supplied photographs, plus Kohler's official TT finish description. No photo pixels or photographic lighting are baked into the material.
- Method: native metallic shader with a spatially uniform color map. The bitmap contains no landmarks or directional pattern, so it is intrinsically seamless and visually non-repeating. Source-face count and variation seed are not applicable.
- Technical test target: saved and reopened in Revit 2025; metallic enabled; glossiness 0.94; normal/grazing reflectivity 0.65/0.98; one diffuse bitmap connection; bump disabled.
- Large-surface check: native Realistic export of a 12 x 8 ft panel and cylindrical/flat fixture samples. No texture seams, repeating blocks or directional brush artifacts visible. Realistic mode alone is not proof of ray-traced reflection fidelity.
- Earlier texture-free library export was superseded after the user required an explicit color map. The final package must contain the bitmap-backed library and companion texture.
- Release library: `KOHLER_Vibrant_Titanium_TT_R2025_Bitmap.adsklib`. It was released under a distinct filename because the earlier library was locked by another process; the validated bitmap-backed bytes were preserved unchanged.
- Native polished appearance preview: pending.
- Exact optical match: inferred from images, not measured or certified by Kohler. A physical finish sample remains authoritative for specification.
- V-Ray: not requested.
