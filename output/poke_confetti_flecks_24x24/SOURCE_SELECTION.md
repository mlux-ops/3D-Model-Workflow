# Source selection — Poke Confetti Flecks 24x24

Product page: https://www.daltile.com/products/terrazzo-look/poke/confetti-flecks-square-24x24-matte

Candidates identified from the page's Scene7 image set (fetched 2026-09-18):

| File / asset | Pixels | View type | Verdict | Reason |
|---|---|---|---|---|
| `poke_confetti_flecks_24x24_3000x3000.jpg` (`DAL_Poke_PK23_24x24_RES_03`) | 3000x3000 | Full bathroom room scene (shower, mirror, vanity, fixtures, floor in perspective) | REJECTED | Not a tile face; contains fixtures, shadows, reflections, and perspective floor/wall convergence. This was mistakenly used as the texture source in the original build — see PROJECT_MEMORY.md. |
| `DAL_Poke_PK24_PK23_24x24_RES_02` | not downloaded | Room scene (comparison) | REJECTED | Same defect class as above (scene, not fetched). |
| `DAL_PK23_24x24_ConfettiFlecks_MT_Angle` | not downloaded | Angled tile detail | REJECTED (not needed) | An accepted straight-on swatch was already found; angled view not required. |
| `DAL_PK23_24x24_ConfettiFlecks_MT_Corner` | not downloaded | Corner/edge detail | REJECTED (not needed) | Detail/edge shot, not a full flat face; not needed once swatch accepted. |
| `DAL_PK23_24x24_ConfettiFlecks_MT_Grid` | not downloaded | Multi-tile grid render | REJECTED (not needed) | Likely a rendered grid, not a raw photographic single-tile face; swatch preferred. |
| **`poke_confetti_flecks_24x24_silo_3000x3000.jpg`** (`DAL_PK23_24x24_ConfettiFlecks_MT_Silo_01`) | 3000x3000 | Flat, straight-on single-tile swatch/chip, no scene, no fixtures, no perspective, uniform lighting | **ACCEPTED** | Matches the WORKFLOW.md requirement for a flat straight-on tile-face image with no baked scene lighting or perspective. Used as the sole colour/pattern source for the final maps. |

## Build note
Built from the accepted Silo swatch only. A 3x3 atlas of the 24 in nominal module (23.81 in
actual tile + 0.19 in joint, matching the page's ~3/16 in grout joint recommendation) was
generated with per-module crop/tone variation for non-repetition, per AGENTS.md's
seamless/non-repeating instruction (2026-09-17) and WORKFLOW.md's visual acceptance gate.
