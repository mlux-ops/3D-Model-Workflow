# Medina Fes and Medina Ifrane 16 x 16 cm: colour maps and a shared normal map

L'Antic Colonial (Porcelanosa) Medina Fes (green, SKU 100365178) and Medina Ifrane (pink, SKU 100365179): glossy handmade-look ceramic wall tile, shade variation V4. Built 2026-11-13.

## Files (`textures/`, all 5184 x 5184, pixel-registered)

| file | format | use |
|---|---|---|
| `Medina_Fes_Color.png` | 8-bit sRGB | all Fes |
| `Medina_Ifrane_Color.png` | 8-bit sRGB | all Ifrane |
| `Medina_Fes_Ifrane_Mix_Color.png` | 8-bit sRGB | random mix: 125 Fes / 131 Ifrane tiles, independent 50/50 draw per tile |
| `Medina_Normal16_OpenGL.png` | 16-bit RGB | **one normal map for all three** (same tile layout). OpenGL convention (green = +Y up); invert green for a DirectX renderer. |
| `Medina_Bump16.png` | 16-bit grey | same height field as a bump map, if you prefer bump to normal |

## Sample Size

**2592 x 2592 mm = 8'-6 3/64" x 8'-6 3/64"** (102.05 in), i.e. 16 x 16 tiles. Use the same Sample Size on every map; repeat on in both directions.

- Tile 160 mm (tech sheet 6-77/256"; catalog 16 x 16 cm), not 6". The "6x6" on the store is nominal.
- Joint 2 mm, **assumed** (neither source gives one), so the module is 162 mm. The visible dark line on the frontal catalog walls is about 6.5 mm, which matches a 2 mm joint plus the rounded tile edges.
- 2 px per mm (0.5 mm per pixel).

## Colour variation: how it was made accurate

Every tile colour is a real tile measured from the manufacturer's own frontal wall images: 36 Fes tiles and 25 Ifrane tiles (`SOURCE_SELECTION.md`). Each map cell draws one measured tile uniformly at random, with replacement, and never puts the same tile next to itself (wrap included). The placed spread therefore matches the measured spread. All 36 and all 25 measured tiles are used.

| colourway | tile colour range in the map, sRGB (min / median / max of tile centres) | luminance sd |
|---|---|---|
| Fes | (93,118,96) / (164,187,170) / (219,239,231): deep sage to pale mint | 33.3 |
| Ifrane | (144,110,111) / (179,146,147) / (204,168,170): dusty rose to pale pink | 15.1 |

Fes varies much more than Ifrane, as it does on the manufacturer's walls.

Each tile also carries the in-tile glaze clouding of a real low-reflection tile from the same wall (rotated or mirrored, limited to ±12%), and the fine specks and pinholes from that colourway's studio swatch.

Method:
- **White balance** comes from the white basin in each scene.
- **Body colour** is taken from each tile's darker luminance band, because gloss reflections only add light.
- **Exposure** uses one gain per colourway (basin to sRGB 235). Tile-to-tile ratios are untouched: no added tint, no saturation change.
- **Lighting check:** tile position explains R² 0.22 / 0.38 (Fes luminance / chroma) and 0.17 / 0.15 (Ifrane). This is attributed to how the tiles were laid, so the spread was left uncorrected.

**Uncertain:**
- The Ifrane studio swatch on the store page, (203,188,187), is lighter and greyer than every Ifrane tile on the catalog wall. The *spread* is measured; the *absolute* Ifrane brightness and saturation are not confirmed. If Ifrane looks too saturated next to a real sample, lighten it uniformly in Revit (tint or brightness) rather than editing tiles.
- The Fes swatch sits at the 78th percentile of the Fes range, which is consistent.
- The Ifrane wall was identified by inference: it is the only pink colourway, and the catalog page has no caption.

## Relief (one height field, all three maps)

Spec says relief "No", so this is a flat glossy tile; the relief is the handmade-glaze character only:

| term | value |
|---|---|
| glaze face above grout | 2.0 mm (tile 11.5 mm thick) |
| rounded ("pillowed") edge | 0.9 mm drop over 3.5 mm |
| irregular edge outline | ±0.45 mm along each edge, different per tile; 2.5 mm corner radius |
| per-tile bow / tilt | up to about 0.3 mm, different per tile, so neighbouring tiles reflect differently |
| glaze waviness | 0.12 mm RMS, 20-70 mm wavelengths, seamless across the image |
| pinholes | about 6 per tile, 0.12 mm deep |
| lowest face point above grout | clearance 0.36 mm (positive) |

The waviness was tuned with a glancing-reflection preview (`source/_PREVIEW_reflection_3x3_tiles.jpg`) until reflections broke into soft wavy patches like those on the catalog walls and close-ups. A first try at 8-40 mm read as orange peel, and was rejected.

In Revit: on a PBR appearance use the normal map at scale 1.0. On a Generic appearance, use the bump map with an amount of about 0.3-0.5 and a high glossiness, because the relief shows mainly in reflections.

## Checks

- `source/build_report.json`: bit depths, sizes, no equal neighbouring samples, positive clearance, wrap on every map. All pass.
- `source/map_validation.json` (`source/verify_maps.py` decodes the 16-bit PNG bytes itself): sizes are whole modules, unit normals, red and green signs at a tile edge, the three colour maps registered (identical grout positions), wrap on all five maps, and the mix map agrees with the layout. All pass.
- Previews reviewed: `source/_PREVIEW_*_Color.jpg`, `_PREVIEW_*_room_3x3.jpg` (7.8 m square surfaces), `_PREVIEW_reflection_3x3_tiles.jpg`, `_PREVIEW_grazing_corner_120mm.jpg`, `_PREVIEW_normal_corner_120mm.jpg`, `_REVIEW_tile_samples_fes.jpg`, `_REVIEW_tile_samples_ifrane.jpg`.

## Limitations, not done

- Colour sources are manufacturer renders/photos at about 90-125 px per tile, so in-tile clouding is low-frequency only. Fine detail comes from one studio swatch per colourway, rotated or mirrored per tile.
- The atlas repeats every 2.59 m. On the 7.8 m room-scale preview the period can only be found by hunting for the darkest green tiles.
- The relief is procedural (handmade glaze), not measured. No Revit material, ADSKLIB, Revit render or Drive upload (not requested).

Rebuild: `C:/Python314/python.exe source/extract_tiles.py`, then `source/build_maps.py`, then `source/verify_maps.py`.
