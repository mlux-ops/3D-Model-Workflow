# Indiana Limestone Full Color Blend: seamless colour and bump

## Deliverables

| file | format | size |
|---|---|---|
| `Indiana Limestone Full Color Blend - 16'-0in x 16'-0in.png` | colour, 8-bit sRGB | 4096 x 4096 |
| `Indiana Limestone Full Color Blend - 16'-0in x 16'-0in - Bump 15.png` | bump, 16-bit grey | 4096 x 4096 |

Copies are in `F:\My Drive\Revit Material Maps - 25-012 651 Belmont`. Local copies are in `textures/`.

## Revit setup

- **Sample Size: 16'-0" x 16'-0" (192 x 192 in)** for both maps, with repeat on in both directions. Both values are whole inches, so Revit's quarter-inch rounding has no effect.
- **Bump amount: 15** on the Texture Editor scale (stored value 0.15). This is a starting value for a honed or smooth face. Raise it to about 25 to 30 for a sawn or rubbed finish. It has not been checked in a Revit render.
- No grout or joint lines are drawn: the texture is continuous stone. If the stone is laid as panels, model the joints in geometry or a fill pattern.

## How it was built (`source/build_maps.py`, seed 20261003)

The texture is 21.33 px/in. The sources are 21.28 px/in, a 0.26 % scale difference that was ignored.

1. **Zone field.** A periodic random field, longer vertically (about 12 in across by 72 in tall), is thresholded to a 50 % buff share. Spurs and islands narrower than 2.5 in are removed, and the edges are softened by 1.5 in. It is coloured with the buff and gray means measured from the sources.
2. **Detail (grain and mottle).** This is the real source texture: each source minus its 40 px low-pass. It is rebuilt by toroidal image quilting: 1,024 patches, each 7.5 in, joined along minimum-error cuts. Buff-zone patches are placed where the output is buff and gray-zone patches where it is gray. Each source position and flip is used once. Patches containing the source's iron spots are excluded, so no spot appears twice.
3. **Iron spots.** 14 unique small spots are drawn at the colour offset measured from the source spots.
4. **Bump.** Built from the detail luminance: darker pores sit lower. It uses the full 16-bit range.

## Checks (`source/verify_maps.py` → `source/validation.json`: PASS)

- PNG headers: colour is 8-bit RGB and bump is 16-bit grey, both 4096².
- **Seamless wrap.** The step across the wrap divided by the interior step at the same 4 px phase is 1.00 (x) and 1.06 (y) for colour, and 1.03 / 1.04 for bump. 1.0 means indistinguishable.
- **No copied blocks.** The largest off-centre autocorrelation of the detail beyond 2 in is 0.003, against a gate of < 0.2.
- Mean colour: the output is 170.4/156.8/140.3 and the sources average 170.4/156.8/140.3.
- The previews below were reviewed by eye. The 47 x 94 in window matches the sources' character. The 1:1 wrap corner and the grazing-light bump show no seam.

## Previews (`previews/`)

`_REVIEW_source_A_B_vs_output_47x94*.jpg` puts the two sources and a 47 x 94 in output window side by side. `_PREVIEW_wall_40x12ft*.jpg` is a large wall. `_PREVIEW_tiling_3x3_48ft*.jpg` shows the tile repeated 3 x 3. `_PREVIEW_wrap_corner_1to1*.png` shows the wrap corner at 1:1. `_PREVIEW_grazing_light_bump_corner.png` shows the bump under grazing light. Files named `_stretch` have 6x contrast to expose seams and repeats.

## Limitations

- A finite bitmap is periodic. The grain does not visibly repeat. The broad buff and gray bands do repeat every 16 ft, which shows faintly on surfaces wider than 16 ft.
- The texture has no detail finer than the supplied 21 px/in maps. The 4 px block structure in the sources is carried through.
- The bump is derived from colour. It is not a measured surface scan.
- The Revit render check under neutral and grazing light is pending: it was not run.
