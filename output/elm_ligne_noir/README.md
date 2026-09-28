# ELM Surfaces Vivid Ligne Noir: colour + 16-bit bump (2026-09-26)

A Revit texture pair for ELM Vivid **Ligne Noir** (3x10 matte relief, SKU 204221E), which is Belmont B3-02. It supersedes the Sep 25 `ELM_Ligne_Noir_3x10_Color_Bump_Maps.zip` and the B3-02 R2 maps; see `ERRORS.md` items 1–3.

## Delivered

| File | Where | What it is |
|---|---|---|
| `ELM Vivid Ligne Noir - 2'-11.250in x 3'-3.500in.png` | `F:\My Drive\Revit Material Maps - 25-012 651 Belmont` | Colour, 3525 × 3950, 8-bit sRGB |
| `ELM Vivid Ligne Noir - 2'-11.250in x 3'-3.500in - Bump 100.png` | same folder | Bump, 3525 × 3950, 16-bit grey. White is high; 0 is the grout floor. |
| `ELM Vivid Ligne Noir - Charcoal Grout - 2'-11.250in x 3'-3.500in.png` | same folder | Colour variant with **dark charcoal grey grout**, sRGB 68 / 68 / 70. Tile faces are pixel-identical to the standard map. Use it with the same Bump 100 map, Sample Size and pattern. |
| `ELM Vivid Ligne Noir - Model Pattern - 2'-11.250in x 3'-3.500in.pat` | same folder | Revit model (surface) fill patterns at real scale: *ELM Vivid Ligne Noir R2 - Vertical stack* (matches the maps) and *R2 - Horizontal stack* |

**R2, 2026-09-26: the Sample Size is now exact on a quarter inch.** Revit's Texture Editor rounds lengths to the project units (1/4 in in the Belmont project), so R1's 39.39 in height became 3'-3 1/2" and the texture no longer matched the model pattern.
- R2 draws the tile 9 11/16 in long instead of the actual 9.66 in. That is 0.7 mm longer, inside pressed-tile tolerance, with the joint kept at 3/16 in.
- Both numbers are now exact: 2'-11 1/4" × 3'-3 1/2".
- The R1 files (`… 3'-3.390in …` and `… - Model Pattern.pat`) are superseded and still in the folder.
| `ELM_Vivid_Ligne_Noir_Package.zip` (this README, source selection, errors, report, validation, previews, scripts, references) | `3D Model Workflow/Material Packages` | everything except the two maps |

## Revit set-up

- **Sample Size: 2′-11 1/4″ × 3′-3 1/2″ (35.25 × 39.50 in), exact at Revit's 1/4 in rounding.** Turn Repeat on in both directions, and keep the scale lock on: the pixel aspect equals the physical aspect.
- Put the colour map in *Image* and the bump map in *Bump*, with **Amount 100** (editor value).
  - This is the starting value calibrated on the Formed Hexagon Sand map, whose full scale is 2.6 mm. This map's full scale is 2.9 mm.
  - The ribs here are steeper than the hex relief, so if they read too strong, drop to 60–80.
- **Layout:** 12 columns × 4 rows (48 tiles) of 2.75 × 9 11/16 in tiles (actual 9.66) with a 3/16 in joint, so the module is 2.9375 × 9.875 in.
  - Tiles are vertical, ribs vertical, in straight stack, as in ELM's installed photo.
  - There is half a joint on every image edge, so both maps wrap.
  - For horizontal tiles, rotate both maps 90° in the texture settings (Rotation 90) and swap the two Sample Size numbers.
- **Model pattern:** Manage > Additional Settings > Fill Patterns > Model > New > Custom > Import `ELM Vivid Ligne Noir - Model Pattern - 2'-11.250in x 3'-3.500in.pat`. Pick *R2 - Vertical stack* and set Import scale 1.
  - Lines are the joint centrelines: 2.9375 in apart horizontally and 9.875 in apart vertically.
  - The pattern origin is a joint intersection, like every corner of the maps. Use Align on the pattern lines to put a joint where the tiling should start.
  - `source/e01_model_pattern.py` re-reads the file and checks it against the colour map: all 330 joint runs have a line within 0.25 px (0.0025 in) of their centre. Preview: `textures/_PREVIEW_model_pattern.jpg`.
- Matte glaze: use low glossiness in the Generic appearance (about 0.2–0.3). No roughness map is supplied.

## What is measured, what is designed

| Item | Value | Basis |
|---|---|---|
| Tile | **2.75 × 9.66 in actual**, 7.4 mm thick | Nemo Vivant brochure (same product) |
| Joint | **3/16 in** | ELM Vivid spec sheet and Nemo brochure. ELM's own photo looks nearer 1/16 in (disclosed). |
| Ribs | **10 per tile**, full length, convex and rounded, pitch 6.99 mm | counted in 3 images (9.87 / 9.95 / 9.47 visible) |
| Rib / channel | 5.45 mm / 1.54 mm | installed photo; designed proportion |
| Relief | ribs **1.50 mm** above the channel floor. Field **1.20 mm** above the grout floor. Eased edge 1.2 mm radius. Face waviness ±0.12 mm. | designed (no section published) |
| Clearance | lowest face point **1.04 mm** above the grout floor. Measured pattern 1.67 mm (p99.5 crest − p2 channel), full scale 2.92 mm. | `textures/validation.json` |
| Colour | face mean sRGB **49.5 / 41.7 / 42.6** (warm near-black), per-tile tone σ 5 % (V1), channels 4 % darker (glaze pooling) | de-lit ELM studio swatch, 100 % real pixels |
| Grout | sRGB 230 / 225 / 227 | ELM installed photo, as photographed |

**De-lighting.** Removed from the swatch:
- rib shading, 12.7× peak to trough;
- the length vignette, 1.29×;
- rib-aligned streaks.

The residual glaze grain is quilted into 48 independent faces from real swatch pixels, in 0.48 in Hann-blended patches with random flips.

## Checks

`python source/b03_verify.py` re-reads the PNGs and exits 0 only if every gate passes. **All 8 pass.**

| Gate | Measured |
|---|---|
| Format (IHDR bytes) | colour 8-bit RGB, bump 16-bit grey, both 3525 × 3939 |
| Aspect | 3525 × 3950 px = 35.25 × 39.50 in at 100 px/in, both exact quarter inches |
| Joints | 220 vertical and 60 horizontal interior runs, median 19 px (design 18.75); edge half joints 10 + 10 px |
| Ribs | 10 in every one of the 48 tiles |
| Clearance | lowest face point 1.04 mm (> 0.5 mm gate) |
| Distinct faces | max \|NCC\| between tiles **0.010** |
| Wrap | colour edge step 0.73 / 0.70 against 1.4–1.8 interior; bump edge step 0.000 mm |
| Colour stripe at the rib period | 1.020 peak to trough (only the designed channel darkening) |

**Review.** I opened each of these myself, at 800 px or less:
- the swatch / built tile / lit tile comparison;
- the 1:1 colour crop, stretched ×3;
- the 1:1 grazing crop over a joint crossing;
- the whole-map grazing render;
- the 2 × 2 wrap seam under grazing light.

No seams, repeated faces or streaks remain. Ribs read as raised rods with narrow shadowed channels, as in ELM's wall photo.

## Limitations

See `ERRORS.md`:
- There is one glaze photo, so there is no large-scale clouding.
- Relief depths are designed.
- The joint follows the 3/16 in spec, not the tighter photo.
- The grout colour is baked in; a 1/16 in joint or a different grout needs a rebuild of about 2 minutes.
- No ADSKLIB, RVT or V-Ray (not requested).

## Rebuild

`python source/build_all.py` (seed 2026092601). Every write goes through `source/guard.py`.
