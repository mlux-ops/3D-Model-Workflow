# Riad Tile Turron 24x24 Venezia Terrazzo, honed: bump and normal maps

Product: https://riadtile.com/products/turron-honed-24x24 (SKU RD-TRZ-C10-24). Built 2026-11-13.

## Files (`textures/`)

| file | format | use |
|---|---|---|
| `Riad_Turron_Honed_24x24_Bump16.png` | 6144 x 3072, 16-bit grey | Revit bump / height map. White = tile face, black = grout. |
| `Riad_Turron_Honed_24x24_Normal16_OpenGL.png` | 6144 x 3072, 16-bit RGB | tangent-space normal map, OpenGL convention (green = +Y up). For a DirectX-convention renderer, invert green. |
| `Riad_Turron_Honed_24x24_Color.png` | 6144 x 3072, 8-bit sRGB | matching colour map. Included because the relief follows the actual chips and only lines up with this colour image. |

All three are pixel-registered. Use the same Sample Size and offset on each.

## Sample Size

**8'-0" x 4'-0"** (96 x 48 in), i.e. 4 x 2 tiles. Repeat on in both directions; no offset needed. Pixel aspect is 2:1, matching the Sample Size.

- Module 24" = 23-15/16" tile + 1/16" joint (half a joint on each outer edge so it wraps). The joint width is **assumed**; Riad does not state one. The installed-floor vignette shows hairline joints.
- 64 px per inch.

## Non-repetition

Riad publishes only one flat straight-on face. A square tile has 8 symmetries (4 rotations, each mirrored or not), and terrazzo has no direction, so each of the 8 cells uses a different one: no cell is a copy of another. The layout was chosen by exhaustive search so that, at every joint and every four-way corner, including across the wrap, the two (or four) cells present different source edges and corners. Without that, a strip of chips meets its own mirror image across the joint and reads as a kaleidoscope; the first build did exactly that and was rejected. Each cell also has a ±1.5% tone shift.

**What that does and does not give you.** No cell is a duplicate of another, but every tile is the same photo rotated or mirrored. Large distinctive chips (for example the big tan and black triangular chips) therefore appear 8 times in each 8'-0" x 4'-0" atlas, once per cell in a different orientation, and the atlas itself repeats on bigger surfaces. Every pixel of tile content is the real product photo; no chips were synthesised. Riad publishes no second complete 24" face; the slab photo is too coarse and the 12x12 and close-up faces are too small (see `SOURCE_SELECTION.md`).

**Non-repetition gate: held for the owner's judgement, not passed.** WORKFLOW.md does not accept rotations of one face as sufficient variation. Room-scale check (`source/_PREVIEW_room_scale_3x3_24ft_x_12ft.jpg`, a 3 x 3 repeat covering 24'-0" x 12'-0"): the field reads as even terrazzo, with no kaleidoscope, no block repeat I could pick out and no visible seam. Individual large chips are not recognisable at that distance. They are recognisable up close, when more than one tile is in view.

## Relief (honed: flat face, flush chips)

| term | value |
|---|---|
| tile face above grout floor (joint step) | 1.00 mm |
| eased edge | 0.35 mm drop over 2 mm |
| matrix porosity, from the photo's own fine speckle | ±0.06 mm (chips keep 15% of it, as honed stone is smoother) |
| hairline seam at chip boundaries | 0.03 mm |
| lowest point on the flat face | 0.89 mm above grout floor |
| clearance above grout floor | 0.77 mm (positive) |

This is not a dimensional tile, so the relief is kept low. Starting point in Revit: Generic bump amount about 0.2, or a normal-map scale of 1.0 in a PBR appearance. Raise it if the porosity does not read in renders.

## Checks

- `source/build_report.json`: bit depths, 2:1 aspect, 8 distinct transforms, no self-mirrored joint or corner, positive clearance, wrap step no larger than the typical neighbour step. All pass.
- `source/map_validation.json` (`source/verify_maps.py` decodes the PNG bytes itself because Pillow reduces RGB16 to 8-bit): 16-bit headers, 19,821 distinct bump levels, unit-length normals, red and green signs at a joint, wrap on bump and normal. All pass.
- Previews reviewed: `source/_PREVIEW_room_scale_3x3_24ft_x_12ft.jpg` (from `source/preview_room_scale.py`), `source/_PREVIEW_tiling_color_2x2.jpg`, `_PREVIEW_closeup_corner_grazing.jpg`, `_PREVIEW_grazing_native_24in.jpg`, `_PREVIEW_normal_native_corner.jpg`, `_PREVIEW_wrap_corner.jpg`, `_REVIEW_source_crop.jpg`, `_REVIEW_chip_mask.jpg`.

## Not done

- No Revit material, ADSKLIB or Drive upload (not requested). No render in Revit; viewport and render response is unverified.
- Source is a marketing photo (about 95 px/in over the face), not a scan. Resampled down to 64 px/in, with a 1.96% stretch from the 22 px edge trim.
- The chip mask controls both where porosity is softened and where the chip seam dip goes, so its errors show in the relief. Rev 1 computed it before removing the studio light and flagged matrix speckle as chip where the light was dimmer; that left uneven, blotchy relief under grazing light. Rev 2 recomputes it on the de-lit colour and drops components under 150 source px (about 10 mm²). Porosity contrast is also normalised locally, since real porosity is even across the face. Chips smaller than about 10 mm² are treated as matrix.

Rebuild: `C:/Python314/python.exe source/build_maps.py`, then `source/verify_maps.py` and `source/preview_room_scale.py`.
