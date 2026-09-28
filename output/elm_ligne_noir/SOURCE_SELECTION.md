# ELM Vivid Ligne Noir: source selection (2026-09-26)

Product page: https://www.elmsurfaces.com/product/ligne-noir, fetched 2026-09-26. It lists the Vivid collection, 3 x 10, Matte, 7.5 mm and a "Hand Made Ceramics" look. Belmont schedule SKU: 204221E.

The same tile is sold by Nemo Tile + Stone as **Vivant 3x10 Ligne Noir Matte**. The ELM spec sheet and the Nemo brochure share the colour names, finishes and tech data, and the Nemo brochure gives the actual size.

Thumbnails of every candidate are in `references/_thumbs/` and `references/pdf_images/_thumbs/`.

## Size and joint

| Fact | Value | Source |
|---|---|---|
| Actual tile size | **2.75 x 9.66 in** | Nemo Vivant brochure, "Actual Size 2.75x9.66" (`references/nemo_vivant_brochure.pdf`) |
| Thickness | 7.4 mm (ELM page: 7.5 mm) | Nemo brochure |
| Recommended joint | **3/16 in** | ELM Vivid spec sheet (`references/elm_vivid_spec.pdf`) and Nemo brochure |
| Ribs per tile | **10**, running the full length | Measured in all three ELM-derived images: retailer full tile 9.87, ELM installed wall 9.95 per module, ELM swatch 9.47 visible in a cropped width |
| Shade variation | V1 (uniform) | both spec sheets |

**Conflict, disclosed.** ELM's installed wall photo has a module aspect of 3.48, which fits the 2.75 x 9.66 tile with a joint of about 1/16 in, not 3/16. The maps follow the manufacturers' recommended 3/16 in. A 1/16 in version is a one-line change (`JOINT` in `source/b01_build.py`).

The Sep 25 build (`ELM_Ligne_Noir_3x10_Color_Bump_Maps.zip`) used a 3 x 10 in module with a 1/16 in joint. Its tiles (2.94 x 9.94 in) were therefore 7 % too wide and 3 % too long, and its joints were a third of the recommended width.

## Candidates

| File | Pixels | View | Verdict | Reason / use |
|---|---|---|---|---|
| `elm_page_main-image_template.jpg` | 1232 x 338 | flat, straight-on studio swatch of the ribbed face | **ACCEPTED: colour source** | The only straight-on image of the Noir glaze. Rib period is 35.8 px, so 130.3 px/in. The visible area is 9.27 x 2.50 in of the 9.66 x 2.75 in face, cropped inside the edges. |
| `landoftile_vivant_184826.webp` | 1000 x 1000 | same studio photograph, rotated 180°, uncropped, with the whole tile outline | **ACCEPTED: geometry check only** | Its high-pass correlation with the ELM swatch is 0.76 at 180°, so it is the same photo, not a second glaze sample. Its tile outline gives 966 x 272 px (aspect 3.55 against 3.51 actual) and 9.87 rib periods across the width. |
| `elm_ligne-noir_3.jpg` | 1218 x 2461 | frontal installed wall, stack bond, tiles vertical | REJECTED as colour (room light, cast shadow, prop) | **Measurement only.** 9.95 ribs per module and a module aspect of 3.48. Ribs are rounded and convex with narrow channels. Grout measures sRGB 230/225/227 as photographed. |
| `elm_ligne-noir_1.jpg` | 1411 x 2125 | angled backsplash scene with loose samples | REJECTED (scene, perspective) | Cross-check: the leaning Ligne sample's end shows a scalloped, convex rib profile. |
| `elm_ligne-noir_2.jpg` | 1410 x 2126 | smooth Vivid Noir wall and a hand-held Ligne sample | REJECTED (different face, scene) | none |
| `elm_page_prefab_8_portrait.jpg` | 810 x 1220 | mixed Vivid Noir glossy wall and Ligne pieces | REJECTED (scene, and mixes glossy and matte faces) | none |
| `elm_page_prefab_1`–`7`, `_4` | about 1235 x 345 | swatches of other Vivid colours (Blanc, Brut, Marin, smooth Noir, Ligne Blanc, Brut, Marin) | REJECTED | different colour or a smooth face; never mix finishes |
| `pdf_images/nemo_vivant_brochure_*` | 494–1711 px | brochure room scenes | REJECTED (scenes) | none |
| `elm_vivid_spec.pdf` | none | spec sheet | data only | 3/16 in joint, V1, matte pressed |

## What the maps take from each source

- **Colour** is 100 % de-lit pixels from the one ELM swatch.
  - Studio lighting was removed: rib shading of 12.7× peak to trough, a length vignette of 1.29×, and a slight tilt of −0.0027 rows per column.
  - Streaks running along the ribs, left over from shading, were also removed.
  - What remains is quilted into 48 independent faces.
  - The face mean is sRGB **49.5 / 41.7 / 42.6**, the swatch mean, which is a warm near-black.
- **Relief is designed, not photographed**, because no manufacturer section exists.
  - Rib profile: 10 convex rounded ribs, 5.45 mm wide, with 1.54 mm channels at a 6.99 mm pitch.
  - Pattern depth: 1.5 mm.
  - Tile edge: eased with a 1.2 mm radius.
  - The ribs being convex, and the channels being narrow, comes from the installed wall and the leaning sample.
