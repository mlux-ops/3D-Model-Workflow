# R032 independent blind BUILD replacement — TX-POWDER2

Seat: tile installer / general contractor. Scored A and B independently using only neutral R032 cards, own geometry and plumbing, exact maker listings and same-job quotes. Two copies: 009A/009B. **Only the dry vanity feature wall is tile; wood floor remains.** No wet floor, wall, niche or pan is proposed. Hansgrohe Tecturis E **73072341 = Brushed Black Chrome (341)** per faucet SKU and plumbing notes, despite structured finish=null; **basin not selected by owner**.

## Candidate A — Elm Vera Forma Indigo Edge Glossy relief, 6 × 6 in, $8.20/SF

| BUILD criterion (1–5) | Score | Evidence and constructability reason |
|---|---:|---|
| Substrate and setting | 4 | [Elm Indigo Edge](https://www.elmsurfaces.com/product/indigo-edge-vera-forma) 6 × 6-in glossy relief is wall-scaled; establish flat substrate, specified joint and adhesive for the relief. |
| Setout and cutting | 4 | W1 3.806 ft = 45.672 in × 111 in high, drawing-derived and not live checked (geometry.json). Seven nominal 6-in columns would leave ~1.84-in balanced edge slivers; six centered columns plus ~4.84-in ends are preferable before joint allowance. |
| Plumbing coordination | 3 | 73072341 is a **deck-mounted** Hansgrohe Tecturis E faucet, Brushed Black Chrome, so no wall-faucet rough cutout; however the unselected basin, spout projection and mirror-to-backsplash relation remain undefined (plumbing.json). |
| Edges, trim and finish | 3 | Relief and saturated glaze require deliberate termination and mirror offsets; edge profile and actual factory depth must be coordinated to avoid projecting unfinished relief edges. |
| Procurement / sequence risk | 3 | 2026-09-04 same-job Elm Indigo Edge quote confirms $8.20/SF, 7.34 SF/30-piece carton, 8.6-mm stated thickness (TRADE_QUOTES.md §b), consistent with maker Vera Forma thickness; local matching batch and freight remain unverified. |

**Arithmetic seat mean: (4+4+3+3+3)/5 = 3.4/5.**  
**gate_flags:** No evidenced hard failure for this dry wall. Basin selection is unresolved and must remain provisional. No wet-floor/DCOF test, no plumbing-finish inference from structured null.  
**top_fix:** Complete the chosen basin/backsplash-mirror height interface, then issue a six-column balanced grid with relief-edge detail.  
**confidence:** medium (faucet suffix and same-job quote documented; basin and native geometry open).

## Candidate B — Floor & Decor La Belle Antique Blue High Gloss, SKU 100507706, 3 × 12 in, $5.56/SF

| BUILD criterion (1–5) | Score | Evidence and constructability reason |
|---|---:|---|
| Substrate and setting | 4 | [F&D La Belle Antique Blue](https://www.flooranddecor.com/ceramic-tile/la-belle-antique-blue-high-gloss-ceramic-tile-100507706.html) is a pressed ceramic wall tile; provide flat backing and maker-approved bedding/joint details. |
| Setout and cutting | 4 | At 45.672-in width, fourteen 3-in vertical columns leave ~1.84-in ends; thirteen columns yield ~3.34-in end cuts before actual grout joints. At 111-in height, avoid narrow termination pieces with a full vertical course schedule. |
| Plumbing coordination | 4 | Flat tile keeps basin/mirror and backsplash junction more adaptable with deck-mounted Hansgrohe 73072341 Brushed Black Chrome; final detail awaits owner basin choice (plumbing.json). |
| Edges, trim and finish | 4 | Regular 3 × 12 pressed ceramic simplifies a clean vertical stack and perimeter edge profile; physical thickness and final trim profile must be matched at procurement. |
| Procurement / sequence risk | 3 | [SKU 100507706](https://www.flooranddecor.com/ceramic-tile/la-belle-antique-blue-high-gloss-ceramic-tile-100507706.html) public Kirkwood, GA price $5.56/SF; verify local Chicago availability, lot, actual thickness, carton multiples and delivered cost. Candidate correctly leaves exact thickness unverified. |

**Arithmetic seat mean: (4+4+4+4+3)/5 = 3.8/5.**  
**gate_flags:** No evidenced hard failure for a dry wall; unselected basin is an owner/open detail, not permission to choose one. Wood floor and DCOF outside scope.  
**top_fix:** Confirm basin and vanity/mirror dimensions, then issue a centered thirteen-column stack with coordinated perimeter and tile-to-countertop trim.  
**confidence:** medium (product and faucet identity known; exact thickness, local availability, basin unknown).

**Material check:** A 40.50 SF gross/copy includes 15% waste already, yielding $332.10/copy before carton rounding; six 7.34-SF cartons are 44.04 SF and approximately $361.13/copy. B: 40.50 × $5.56 = $225.18/copy at public GA price before packaging; 162 pieces cover 40.5 SF if 0.25 SF/piece. Excludes trim, setting, tax, freight and labor. Sources: [Elm Indigo Edge](https://www.elmsurfaces.com/product/indigo-edge-vera-forma); [F&D Antique Blue](https://www.flooranddecor.com/ceramic-tile/la-belle-antique-blue-high-gloss-ceramic-tile-100507706.html); inputs/TRADE_QUOTES.md.
