# Source selection: Indiana Limestone Full Color Blend

Both sources were supplied by the user on 2026-10-03 as colour maps, each stated to be 47 x 94 in.

| file | px | view | decision | reason |
|---|---|---|---|---|
| `references/01_supplied_colormap_A_47x94.webp` | 1000 x 2000 (21.28 px/in) | flat, straight-on face, no perspective, no room lighting | ACCEPTED | Mostly buff (74 %) with gray bands at both edges, brown mottle in the buff and 3 to 4 small iron/rust spots. |
| `references/02_supplied_colormap_B_47x94.webp` | 1000 x 2000 (21.28 px/in) | flat, straight-on face | ACCEPTED | Mostly gray (73 %) with buff bands at both edges. |

Measured from the sources (`source/analysis.json`):
- The buff and gray zones split about 50/50 across the pair, so the output targets 50 %.
- Buff zone mean is sRGB 174/158/140; gray zone mean is 167/155/141.
- Zone boundaries are soft (about 1 to 3 in), wavy, and run mostly vertically.
- Fine grain sigma is about 2.8/255 per channel. The brown mottle is stronger in the buff zones.
- Both maps have a 4 px column block structure: every fourth neighbour step is about 35 % larger. This looks like processing in the supplied files. It carries through into the output grain, and it is invisible at normal scale.
