# 651 Belmont — Kuzco OEM source verification (2026-10-17)

Source directory: `E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017\sources\kuzco`

All ten preserved downloads originate from Kuzco's own product page links, not third-party recreated geometry. Download URLs, byte sizes and SHA-256 hashes are retained in `SOURCE_MANIFEST.json`. ZIP entry listings checked using .NET ZipFile.OpenRead; each REVIT ZIP contains a genuine *.rfa. None was opened in Revit or independently measured in native software.

| Variant | OEM direct page | Body, in | Canopy, in | Minimum hanging height | Maximum supplied wire | Optics and appearance |
| --- | --- | --- | --- | --- | --- | --- |
| Jarvis 41411-BG | https://kuzcolighting.com/products/jarvis-41411-kuzco | D2-3/4 x H12-5/8 | D4-3/4 x H1/4 | 16 in | 120 in clear SSL cable for BG | 1 x GU10 50 W max, bulb *not included*. Clear glass surrounding aluminum socket housing, BG plated finish. 120 V, downlight, dry, ETL. |
| Malabar 402401BG-LED | https://kuzcolighting.com/products/malabar-402401-led-kuzco | D3 x H9-1/2 | D4-3/4 x H3/8 | 14 in | 120 in clear SSL cable | Integrated 6 W, 3000 K, 90 CRI, 248 fixture-delivered lm in BG, ELV 100–10% dimming, omni-directional. Clear exterior/frosted interior acrylic; plated metal trim. 120 V, dry, ETL. |
| Milca 494502M-GD | https://kuzcolighting.com/products/milca-494502m-kuzco | D2-3/8 x H10-7/8 | D4-3/4 x H3/8 | 15 in | 120 in black braided cable | 1 x GU10 50 W max, bulb *not included*. Gold stacked-slice aluminum tubular shade with matching interior. 120 V, downlight, dry, ETL. |

Notes: dimensions above are distinct body and canopy dimensions, and must **not** be modeled as complete fixed assembled drop. Native suspension should have a variable cord/drop and its envelope must avoid falsely extending a rigid solid through the whole 120-inch wire length. Minimum hang height is the OEM overall mounting minimum. For Jarvis and Milca, Kelvin temperature, bulb lumen output, dimming range and photometric distribution depend on the **selected GU10 lamp**, so the source provides no exact fixture IES; do not transplant Malabar's IES. Malabar's integrated module is fixed at **3000 K**, not 2700 K.

## OEM assets preserved

- Jarvis spec and installation PDFs; `REVIT-41411-Jarvis.zip` contains `REVIT-41411-Jarvis/41411 - Jarvis.rfa` (823,296 bytes uncompressed).
- Malabar spec and installation PDFs; `REVIT-402401-LED-Malabar.zip` contains `REVIT-402401LED-Malabar/402401LED-Malabar.rfa` (655,360 bytes uncompressed).
- Malabar `IES-402401-LED-Malabar.zip` has separate BG and CH photometry. Exact entry `IES-402401-LED-Malabar/402401BG-LED - Malabar.IES` (41,684 bytes): IESNA LM-63-2002; manufacturer KUZCO LIGHTING; luminaire catalog `Malabar - 402401BG - LED`; test 3021-25; 2025-01-31; ballast 120 VAC. The CH file is **not** the BG match.
- Milca spec and installation PDFs; `REVIT-494502M-Milca.zip` contains `494502M-Milca.rfa` (1,298,432 bytes uncompressed).

These original OEM RFA filenames are model family level rather than SKU/finish-specific. Native Revit verification should inspect material finish controls and family type names to ensure precise BG and GD output, confirm Lighting Fixtures category and ceiling/workplane placement, solid bounds against the individual dimension diagrams, actual emitting light source and photometric settings. If OEM light source is insufficient, modify a *copy* with a documented correction and validate in a disposable Revit 2025 project.

## Acceptance caveats

1. The official Kuzco Milca M body height is **10-7/8 inches** despite some retailer listings calling it approximately 10-1/4. Use OEM cut sheet.
2. Malabar is clear acrylic externally with a frosted inner optic; do not replace it with opaque milky cylinder.
3. Jarvis has a clear glass outer cylinder and solid central socket housing, requiring distinct material assignments.
4. Jarvis/Milca lamps were not supplied in the manufacturer package; choose an explicit GU10 bulb before making 2700K, glare-control, illumination or IES assertions.
5. OEM RVTs/RFAs are manufacturer-provided inputs; do not mark as tested, production-approved or visually accurate without a native Revit geometry/optics validation.
