# Source selection — Remedy Hydro (Fluted + Handcrafted/flat role)

Product page: https://www.daltile.com/products/wall/remedy/hydro

Candidates identified from the page's Scene7 image set (fetched 2026-09-18):

## Fluted

| File / asset | Pixels | View type | Verdict | Reason |
|---|---|---|---|---|
| `remedy_hydro_fluted_2000x2000.jpg` (`DAL_RD22_2x10_Fluted_Hydro_GL_LivePanel_Angle_01`) | 2000x2000 | Multi-row wall panel (~3 columns x 20 rows of tiles) shot at a camera angle, dark frame baked around the panel | REJECTED | Perspective-skewed; not a single tile; this was mistakenly used as the texture source in the original build (flute pitch "estimated" by autocorrelation on this skewed image, and colour baked its angled highlights) — see PROJECT_MEMORY.md for the recorded error. |
| `DAL_RD22_2x10_Fluted_Hydro_GL_LivePanel_01` (non-angle) | not downloaded | Likely another multi-tile panel scene | REJECTED (not needed) | Same LivePanel family as the rejected angle shot; an accepted single-tile swatch was found instead. |
| **`remedy_hydro_fluted_silo_2000x2000.jpg`** (`DAL_RD22_2x10_Fluted_Hydro_GL_Silo_01`) | 2000x2000 | Flat, straight-on single-tile swatch, installed orientation (10 in wide x 2 in tall), no scene, no perspective | **ACCEPTED** | The only genuinely flat single-tile source found. Clearly shows two rounded flute ridges stacked across the 2 in tall dimension, running the full 10 in length — used to source the flute count directly (see README "Flute geometry"), replacing both the original autocorrelation estimate and an interim single-flute guess made before this swatch was located. |

## Handcrafted (used in the flat role)

| File / asset | Pixels | View type | Verdict | Reason |
|---|---|---|---|---|
| `remedy_hydro_handcrafted_2000x2000.jpg` (`DAL_RD22_2x10_Handcrafted_Hydro_GL_LivePanel_01`) | 2000x2000 | Multi-tile wall of stacked pieces, near-orthogonal grid (not strongly angled) but still a multi-tile installation photo, not a single-tile swatch | REJECTED | Superseded once a genuine flat single-tile Silo swatch was found; kept only as a secondary reference in `references/`, not used for final pixels. |
| **`remedy_hydro_handcrafted_silo_2000x2000.jpg`** (`DAL_RD22_2x10_Handcrafted_Hydro_GL_Silo_01`) | 2000x2000 | Flat, straight-on single-tile swatch, installed orientation (10 in wide x 2 in tall), no scene | **ACCEPTED** | Matches WORKFLOW.md's flat straight-on tile-face requirement. Used as the sole colour source for the flat-role maps. |

## Build note

Both final map pairs are built only from their ACCEPTED flat single-tile Silo swatches. The
Remedy 2x10 module installs horizontally (10 in wide x 2 in tall); atlases are 3 tiles wide x
12 rows tall (30 x 24 in total) in a simple grid/stack bond, with per-module tone variation for
non-repetition per AGENTS.md (2026-09-17). Flute relief is built as a pure function of the
across-height coordinate (2 half-round flutes per module, sourced from the accepted swatch),
independent of any photo perspective, per AGENTS.md's 2026-09-18 dimensional-relief
instruction and WORKFLOW.md line 30 ("Correct photographic perspective and baked lighting
while preserving the product's actual color and character").
