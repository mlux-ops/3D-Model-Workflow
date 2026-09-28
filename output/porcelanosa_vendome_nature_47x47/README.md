# Porcelanosa Vendome Nature 47x47: Revit colour + bump maps and model pattern

- **Product:** Porcelanosa Vendome Nature 120x120 (47" x 47"), code 100348304, model VENDOME NAT.PV6 120X120(A).
  - 6 mm unglazed matte porcelain ("Nature"), rectified, V3. Product finder: "Relief: NO".
- **Built:** 2026-09-27 for 25-012 651 W. Belmont.
- **Deliverable:** maps and pattern only (no ADSKLIB, RVT or V-Ray).
- **Maps and `.pat`:** `F:/My Drive/Revit Material Maps - 25-012 651 Belmont/`.

## Sizes

| | value |
|---|---|
| actual tile (FTEC sheet) | 1200 x 1200 mm = 47.244 in |
| joint | 1/16 in (1.59 mm). Porcelanosa: "minimum joint of 1,5 mm" |
| drawn tile | 47-3/16 in (47.1875 in), 1.44 mm (0.12 %) under actual, so the module is exactly 47-1/4 in |
| module (tile + joint) | 47.25 in = 3'-11 1/4" |
| resolution | 32 px/in: module 1512 px, face 1510 px, joint 2 px (1 px half joint on every map edge) |
| grout colour | sRGB 200/199/195, light pearl grey. Porcelanosa recommends Butech Colorstuk Rapid **Perla**; this sRGB is my match, not a published value |
| bump | full scale 1.60 mm; joint 1.50 mm deep; eased edge r 1.0 mm; photo micro-relief sd 0.02 mm (bounded ±0.10 mm) |

The drawn tile is 1.4 mm under actual so that every Sample Size is an exact 1/4 in. Revit rounds Sample Size to the
project's 1/4 in, and a non-quarter value drifts against the pattern.

## Revit setup, all three sets

In each material, use the Generic appearance. Set **Image** = colour PNG and **Bump** = bump PNG. Give both the
same Sample Size, keep the scale lock on, and leave Offset 0, Rotation 0.

| set | colour map | bump map | Sample Size (W x H) | Bump amount |
|---|---|---|---|---|
| Designed | `Porcelanosa Vendome Nature 47x47 - Designed - 15'-9.000in x 7'-10.500in.png` | `... - Designed - 15'-9.000in x 7'-10.500in - Bump 60.png` | **15'-9" x 7'-10 1/2"** | **60** |
| Free Mix | `Porcelanosa Vendome Nature 47x47 - Free Mix - 15'-9.000in x 15'-9.000in.png` | `... - Free Mix - 15'-9.000in x 15'-9.000in - Bump 60.png` | **15'-9" x 15'-9"** | **60** |
| Piece 1 … Piece 8 | `Porcelanosa Vendome Nature 47x47 - Piece N - 3'-11.250in x 3'-11.250in.png` | `... - Piece N - 3'-11.250in x 3'-11.250in - Bump 60.png` | **3'-11 1/4" x 3'-11 1/4"** | **60** |

Model pattern: `Porcelanosa Vendome Nature 47x47 - Model Pattern - 3'-11.250in.pat`.

- Pattern name "Porcelanosa Vendome Nature 47x47 - Stack": a 47-1/4 in grid of joint centrelines.
- Use it as the material's Surface Pattern (Model). Import it with Manage > Additional Settings > Fill Patterns > Model > New > Custom > Import.
- One pattern serves all three sets. Its origin is each map's top-left corner, which is a joint crossing; the first tile face starts 1/32 in right of and 1/32 in below the origin.
- No 45 degree pattern is included. Porcelanosa shows no diagonal layout for this product.
- If the rendered joints don't sit on the pattern lines, shift the texture (Texture Editor > Position > Offset, the same values for Image and Bump), not the pattern.

Bump 60 is the editor value (100 x stored). The owner's calibration: 100 is right for a 2.6 mm full-scale map;
60 was used for flat 1.6 mm porcelain (Soreno, Jute). The face itself is flat, as the product is.

## 1. Designed: the manufacturer's continuous strips

The 8 graphics join edge to edge in **two strips of 4 that each loop**, all pieces as supplied (no rotation):

- Row 1, **strip A: 1 - 6 - 7 - 8**, and 8 continues into 1.
- Row 2, **strip B: 2 - 3 - 4 - 5**, and 5 continues into 2.

The veins run unbroken across every vertical joint, including the wrap. Across the horizontal joints there is **no
designed continuity**: none was found in any physically possible orientation, so rows simply alternate A / B.

The map is 4 x 2 tiles and repeats every 15'-9" horizontally and 7'-10 1/2" vertically. That repeat is the real
product: there are only 8 graphics.

Note: Porcelanosa's product finder lists "Continuous design: NO". The strips are what the supplied print files show
(see SOURCE_SELECTION.md). Confirm with the supplier whether they will sequence pieces for installation.

## 2. Free Mix: random installation

This set is 4 x 4 tiles.

- Each of the 8 pieces appears twice, in two different 90-degree rotations.
- The two copies never touch, including diagonally and across the wrap.
- The pieces are rotated, never mirrored: a printed tile can't be flipped.

It reads as a random, non-sequenced installation. The veins break at joints, as they would on site. The map repeats
every 15'-9", so on most walls and floors no repeat is visible.

Layout (piece / clockwise rotation):

| | col 1 | col 2 | col 3 | col 4 |
|---|---|---|---|---|
| row 1 | 2 / 270 | 5 / 180 | 8 / 0 | 6 / 180 |
| row 2 | 1 / 270 | 4 / 270 | 3 / 0 | 7 / 0 |
| row 3 | 5 / 270 | 6 / 0 | 8 / 90 | 2 / 90 |
| row 4 | 7 / 180 | 1 / 180 | 3 / 90 | 4 / 90 |

## 3. Individual pieces: arrange them yourself

1. Make 8 materials, `Porcelanosa Vendome Nature 1` … `8`. Each uses Piece N colour + Piece N bump at 3'-11 1/4" square, bump 60, and the same model pattern. Each piece has its own bump: the micro-relief follows that piece's own face.
2. Divide the surface on the tile grid, by either method:
   - **Split Face:** Modify > Geometry > Split Face. Sketch the lines on the model-pattern lines; snap to them, Tab to pick the pattern line.
   - **Parts:** select the element, Create Parts, then Divide Parts with a sketch or grid on the same lines. Clear "Material By Original" on each part.
3. Paint each tile region with any piece: Modify > Paint, pick the material, click the face or part.

All piece maps, the pattern and the other sets share the same 47-1/4 in grid and origin. So a region cut on the
pattern lines shows exactly one whole piece, with its half joints on the lines.

- **To rotate a piece:** duplicate its material and set Texture Editor > Transforms > Rotation to 90, 180 or 270, the same on Image and Bump. Rotation turns the texture about its origin, a grid point, so the joints stay on the grid.
- **To recreate the designed vein, lay pieces in this order:** row 1 = 1-6-7-8, row 2 = 2-3-4-5, all at rotation 0.
- Piece 8 is noticeably darker along its bottom edge than its top. Used alone over a large area, that shows as a tone step at every horizontal joint. This is product content, not a map seam.

## Grout colour variant

The colour maps can be rebuilt with any grout colour. The bump is byte-identical, and the builder raises an error
if it isn't:

```
C:/Python314/python.exe source/b01_build.py <suffix> R,G,B
```

This writes `Color_<suffix>.png` for each set and `Piece_N_Color_<suffix>.png`. It was tested with 120,118,112;
see `_work/grout_variant_test.json`.

## Verification (`source/b03_verify.py`, results in `<set>/validation.json`)

The verifier re-reads every file and decodes the source faces independently (LittleCMS). Gates:

- **ihdr:** colour 8-bit RGB, bump 16-bit grey, equal sizes.
- **quarter_inch:** fails any non-quarter Sample Size, self-tested.
- **joints:** bump = 0 exactly on the 2 px joints at k x 47.25 in, and nowhere else.
- **wrap:** half joints on all edges; steps across the wrap are no larger than across interior joints.
- **identity:** every cell matches its declared piece and rotation. NCC 0.998 or more; the next best variant is ≤ 0.46; mean |dRGB| ≤ 0.67 levels.
- **continuity:** designed vertical joints. Built NCC 0.52–0.76, equal to the source within 0.03; horizontal joints ≤ 0.07.
- **adjacency:** free mix.
- **clearance:** face ≥ 1.198 mm above the grout floor.
- **colour_bump:** joint pixels are exactly the grout colour; face mean within 0.2 % of the source.
- **cross_set:** each piece's pixels are identical in every set.
- **model_pattern:** analytic; every joint run matched, max offset 0.0 px.

All gates pass for all three sets.

## Limitations

- Not tested in a Revit render; the grazing-light previews are synthetic.
- Grout sRGB is a match to "Perla", not a published value.
- Only 8 graphics exist, so any large area repeats them (true of the product). The free mix shows each graphic twice per 15'-9" square, rotated.
