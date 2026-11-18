# Source selection: Riad Tile Turron 24x24 Venezia Terrazzo, honed (RD-TRZ-C10-24)

Product page: https://riadtile.com/products/turron-honed-24x24 (product JSON saved as `references/product.json`, fetched 2026-11-13).
Stated facts: 24" x 24", 0.7" (18 mm) thick, 4 sq ft per tile, sold per tile. Joint width is not stated.

| file | px | view | decision | reason |
|---|---|---|---|---|
| `TerrazzoTurron24x24.jpg` | 3000 x 3000 | single tile, flat, straight-on, white background | **ACCEPTED** | the only full straight-on face. Silhouette edges fit to within about 0.01 px per px of slope (left/right/top/bottom), so no perspective correction needed. Face measured at x 378-2662, y 372-2660 (about 95 px/in). Trimmed 22 px each side to drop the eased edge and the thin side band visible along the bottom and right. Soft studio light gradient (0.94-1.05 of mean on the matrix) removed. |
| `TerrazzoTurronDetail_...jpg` | 3000 x 3000 | angled close-up of a tile corner and edge | REJECTED | oblique view; shows the 18 mm edge. Used only to confirm the face is flat honed with flush chips and a fine-pored cement matrix. |
| `Turron_Floor_Vignette_HP.jpg` | 2800 x 2800 | installed floor, raking sunlight, angled | REJECTED | room scene, perspective, baked shadows. Shows hairline joints, which supports the 1/16" joint assumption. |
| `TerrazzoMoodBoard_02.jpg` | 2800 x 2800 | mood board, tiles overlapping other products | REJECTED | partial, overlapped and shadowed tiles. |
| `TurronTerrazzo24x24TileInstallation-AMFConstruction-Large.jpg` | 2001 x 3000 | room photo | REJECTED | room scene, floor at a steep angle. |
| `Turron24x24TileInstallation-AMFConstruction-Large.jpg` | 2001 x 3000 | room photo | REJECTED | room scene, floor at a steep angle. |
| `TurronTerrazzo24x24TileInstallation-AMFConstruction-Large_1.jpg` | 2400 x 3000 | mudroom photo | REJECTED | room scene; floor is a small angled strip. |

Second-face search (store search for "turron": 24x24, 12x12, 6x6, 4x4, 106x70 slab), checked 2026-11-13:

| file | px | view | decision | reason |
|---|---|---|---|---|
| `TurronTerrazzoSlab-1_...jpg` (slab page; -2, -3 and the Olivia Katz shot not used) | 3000 x 1996 | whole 106" x 70" slab, flat | REJECTED | about 19 px/in over the face, so a 24" cell would be about 450 px: too coarse for chip edges or porosity. |
| `TerrazzoTurron12x12.jpg` (12x12 page) | 3000 x 3000 | single 12" tile, flat | REJECTED for this build | a genuine different face, but only 12": it cannot fill a 24" cell without a seam through the tile. |
| `turroncloseup_...jpg` (slab page) | 1916 x 1917 | flat close-up of one tile corner | REJECTED for this build | a partial face of unknown size; same reason. |

No second complete 24" face exists from the manufacturer, so non-repetition comes from the 8 square symmetries of the one face (see README).
