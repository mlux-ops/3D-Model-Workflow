# ELM Colorado Bruges Antique — Exa mosaic (Revit 2025 review package)

This package contains one native Revit material library and its registered color and 16-bit bump maps. The texture depicts a field of point-up hexagons with dark continuous joints, moderate Antique stone-face variation, and occasional worn or diagonally grooved pieces.

## Load and scale

1. Extract the complete package to a permanent folder.
2. In Revit, open **Manage > Materials > Open Existing Library** and select `ELM_Bruges_Antique_Exa_R2025_Rev4.adsklib`.
3. Add **ELM Colorado Bruges Antique - Exa Mosaic** to the project. If Revit reports missing images after extraction, repath its Color and Bump image fields to the two supplied files in `textures`.
4. Keep both images mapped with identical origin, orientation, and sample size: **185.8268 in wide × 180.7087 in high**. This atlas represents 16 × 18 landscape mosaic sheets, each **11.6142 × 10.0394 in** from the manufacturer's 29.5 × 25.5 cm sheet image. The ELM listing rounds the Mosaic Exa option to 12 × 12 in.

## Construction and limitations

The color map uses 16 distinct face interiors from Kronos's Bruges Antique straight-on finish grid. The point-up Exa shape and mix of plain, worn, and grooved hexagons follow the separate Bruges Exa SKU 8521 image. The public sources do not show a flat photograph of the exact Antique Exa combination; this is a source-grounded composite rather than a measured scan of an installed sheet. See `SOURCE_SELECTION.md` and the preserved manufacturer references.

Atlas size: **7168 × 6984 pixels** or **15.49 × 15.06 ft**. The registered bump image is 16-bit grayscale. Repeated atlas boundaries are pixel-identical. A finite bitmap repeats after one atlas period; visual previews inspect both single-atlas variation and repeated-atlas appearance.

Estimated relief: grout floor **0.50 mm** below the highest stone face; groove depth **0.30 mm**; microrelief at most **0.02 mm**; minimum groove-to-grout clearance **0.18 mm**. These are visualization settings, not manufacturer measurements. Keep the grout and groove depths separate when tuning the material.

The library archive and bitmap paths passed local structural checks. Native Revit import and rendered neutral/grazing-light appearance are **pending** because Revit 2025 was stopped by an Autodesk device-limit prompt on this workstation. Treat this as a review package until those checks pass. No separate RVT is needed to load the ADSKLIB.
