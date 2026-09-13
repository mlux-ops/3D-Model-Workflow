# MSI Adella Viso White — Revit 2025 and V-Ray

Created 2026-09-13 for visualization from the linked Villo Home tile and MSI's product reference.

## Files

- **MSI_Adella_Viso_White_R2025.adsklib** — native library created and populated in Revit 2025.4. Material: `MSI Adella Viso White - 12x24 Satin - Stacked`.
- **MSI_Adella_Viso_White.vrmat** — V-Ray material with diffuse, roughness and tangent-space normal textures. **Native import and rendering are not verified:** the installed V-Ray integration and standalone engine could not obtain a license. XML, referenced plugins and texture files passed structural checks. The separate SDK reader also failed on an installed Chaos Cosmos reference material.
- **textures/** — keep with the material files. These are required external 4K assets; ADSKLIB does not embed the full-resolution textures.
- **MSI_Adella_Viso_White.vrscene** — alternate material-only V-Ray scene. Parsed successfully by installed V-Ray 7.20.05 with 10 objects and zero warnings. Rendering remains blocked by license error -98. In hosts supporting material-from-file loading, select material `MSI_Adella_Viso_White`; this file contains no geometry.
- **Adella_Material_R2025.rvt** — optional source project containing the material, saved and reopened in Revit 2025 with zero warnings.
- **Relief_Preview.jpg** — illustrative shading of the photographed relief map, **not a Revit or V-Ray render**.
- **PACKAGE_VALIDATION.json** — validation record and limitations.

## Revit 2025

1. Extract the complete ZIP to a permanent folder.
2. Manage → Materials → library menu at lower left → Open Existing Library. Select the `.adsklib`.
3. Add the Adella material from the library to your project and assign it to the wall finish or paint the desired face.
4. On this computer, the library points to the existing `output/adella/textures` directory in this workspace. If moved or used on another computer, repath both Appearance → Image and Bump → Image to the included `Adella_BaseColor.png` and `Adella_Bump.png`. Alternatively, add the extracted textures directory to Revit's Additional Render Appearance Paths.
5. The color and bump repeats are set to **24.0625 inches wide × 12.0625 inches high** (611.1875 × 306.3875 mm). This represents nominal 24 × 12 inch tile plus a 1/16 inch joint. Use realistic/rendered appearance to see the textures. Rotate the texture if the face mapping places it vertically.

The material library was created through Revit's Material Browser, populated with the named material, and released from its write lock. Its ZIP container integrity was checked. The companion RVT was independently reopened through the Revit 2025 API. Import into a second blank project was not tested.

## V-Ray

1. In a licensed V-Ray Asset Editor, use Import Asset to load the `.vrmat`.
2. Keep `textures/` alongside the `.vrmat`. Repath the three bitmap files if your host does not resolve relative paths.
3. Use mapping channel **1**. Set one UV repeat to **24.0625 × 12.0625 inches** on the target surface. Physical mapping is host-dependent; the VRMAT uses the object's UVs rather than forcing a world projection.
4. In V-Ray for Revit, use Appearance Manager to assign this material as the override for the Revit Adella material, preserving the matching texture scale.

Settings: opaque nonmetallic ceramic; Fresnel IOR 1.5; GGX default; reflection roughness map approximately 0.40 across the tile and 0.78 at grout; normal map in tangent space, amount 1. Color uses sRGB decoding; roughness and normal maps use linear decoding. `Adella_Height16.png` is included for optional host-specific displacement setup but displacement is not enabled in the material.

## Appearance choices and accuracy

- Cool white satin/matte glazed ceramic, horizontal stacked layout, light neutral 1/16 inch grout.
- Color and relief are derived from the exact-product StoneLocator photograph (2560×2560), cropped to a real 24×12 tile panel, denoised at source resolution, enlarged to 4K, and normalized for studio-light falloff. The photograph is not a calibrated scan, so exact mold depth and material response remain approximate.
- Exact relief depth and optical measurements are unavailable. The V-Ray normal map was derived using an inferred 1.5 mm full height range; the actual facet depressions use a fraction of that range. Revit uses its own adjustable bump strength, not calibrated physical displacement.
- White balance and sheen are approximate. Review a physical sample for finish selection. Joint width and stacked layout are visualization choices, not installation specifications.

## References

- [Villo Home supplied product](https://villohome.com/products/adella-viso-white-12x24-glazed-ceramic-wall-tiles-msi-collection)
- [MSI Adella Viso White 12x24 Satin](https://www.msisurfaces.com/3d-large-format-wall-tile/adella-viso-white-12x24-satin/) — cool white ceramic with indented texture; current item NADEVISWHI1224-N.
- [StoneLocator exact-product image](https://www.stonelocator.com/wp-content/uploads/2017/11/NADEVISWHI1224_a2-scaled.jpg) — 2560×2560 retailer image used for the current map derivation.
- [Autodesk material library creation](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Revit-How-to-create-a-Material-Library.html)
- [Chaos V-Ray for Revit Asset Editor](https://docs.chaos.com/display/VREVIT/Asset+Editor)

This is an independently prepared visualization material, not an MSI-issued BIM asset.
