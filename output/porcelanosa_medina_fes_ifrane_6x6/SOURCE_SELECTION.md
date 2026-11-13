# Source selection: L'Antic Colonial (Porcelanosa) Medina Fes and Medina Ifrane, 16 x 16 cm

Product pages (saved HTML in `references/`, fetched 2026-11-13):
https://store.porcelanosa.com/us/medina-fes-6x6 (SKU 100365178) and https://store.porcelanosa.com/us/medina-ifrane-6x6 (SKU 100365179).

Facts from the pages and tech sheets (`references/tech_100365178.pdf`, `tech_100365179.pdf`):
- ceramic wall tile, gloss, relief "No", shade variation V4, not rectified;
- format 6-77/256" x 6-77/256" x 29/64" (tech sheet); the catalog gives 16 x 16 x 1.15 cm;
- recommended grout Colorstuk Rapid Gris N (grey). No joint width is stated.

The Medina catalog (`references/MEDINA_catalog_plitka.pdf`, retailer copy found by web search; images extracted to `references/catalog_imgs/`) describes the collection as having "strong color variation", irregular edges and a glossy finish.

| file | px | view | decision | reason |
|---|---|---|---|---|
| `100365178_T.jpg` (Fes store swatch) | 1920 x 1440 | one tile, flat, studio, neutral grey background | **ACCEPTED: fine detail only** | about 750 px across the tile, colour-calibrated studio shot. But it is one piece of a V4 range, so it cannot give the variation. Used for the high-pass glaze detail (specks, pinholes) on Fes tiles, and as a cross-check of absolute colour. |
| `100365179_T.jpg` (Ifrane store swatch) | 1920 x 1440 | as above | **ACCEPTED: fine detail only** | same role for Ifrane. |
| `100365178_500X500.jpg`, `100365179_500X500.jpg` | 500 x 500 | smaller copies of the swatches | REJECTED | duplicates at lower resolution. |
| `100365179_01.jpg` (Ifrane store room render) | 1920 x 1440 | kitchen island, near-frontal | REJECTED for colour | strong warm cast: the steel hob reads (112,92,85) and the wine glass (163,132,121). Nothing in the scene is a usable neutral, so the measured colours could not be corrected. It does confirm the V4 spread visually. |
| `P.AMB.002317.webp` | 4000 x 3000 | unrelated marble room scene served by the page | REJECTED | not this product. |
| placeholder `_01`/`_02` images | - | identical 33,822-byte placeholder | deleted | not product images. |
| `catalog_imgs/p11_0.png` (catalog; same scene as page 2, captioned "Wall Covering: Medina Fes") | 1303 x 1706 | frontal bathroom wall, daylight, white basin | **ACCEPTED: Fes per-tile colour and clouding** | about 124 px per tile, frontal. 41 whole tiles right of and above the mirror; 5 rejected after review (bottom row reflects the bench; c7r7 carries a sky reflection), leaving 36. |
| `catalog_imgs/p8_0.png` (catalog) | 1306 x 1708 | frontal pink vanity wall, neutral light, white basin | **ACCEPTED: Ifrane per-tile colour and clouding** | identified as Ifrane by **inference**: it is the only pink colourway in the collection and the page has no extractable caption. About 88 px per tile; 20 wall tiles under the counter and 5 apron tiles, 25 in all. |
| `catalog_imgs/p6_2.png`, `p7_0.png` | 1304 x 981, 1304 x 729 | oblique close-ups, glossy | REJECTED for colour, **used as relief reference** | angled; their broken, wavy reflections set the scale of the glaze waviness in the normal map. |
| other catalog images | - | other colourways, rooms | REJECTED | not Fes or Ifrane, or not frontal. |

How colour was measured, and its limits:
- White balance comes from the white basin in each scene. Grout was tried first and rejected: in these renders it carries tile colour and shadow, and it turned Ifrane grey.
- Gloss reflections only add light, so each tile's body colour is the mean of its 15-45th luminance percentile.
- One exposure gain per colourway maps the basin to sRGB 235. Tile-to-tile ratios are kept exactly as measured.
- Lighting check: tile position explains R² = 0.22 of Fes luminance and 0.38 of its chroma, and 0.17 / 0.15 for Ifrane. Chroma clusters more than luminance, and white light does not change chroma, so the spatial pattern comes from how the tiles were laid. The spread was left uncorrected.
- Cross-check against the studio swatches: the Fes swatch sits at the 78th luminance percentile of the corrected Fes range, consistent with it being a pale piece. **The Ifrane swatch (203,188,187) is lighter and greyer than every corrected Ifrane tile** (max (202,167,167)). The absolute Ifrane level and saturation are therefore uncertain; the relative spread is not affected.
