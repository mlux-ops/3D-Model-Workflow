# R032 independent blind BUILD replacement — PH-POWDER

Seat: tile installer / general contractor. Evaluated A and B independently from R032 neutral cards, own-room geometry/plumbing, manufacturer product pages, and 2026-09-04 same-job trade quotes. Two copies: 405A/405B. **Only a dry decorative vanity wall is tiled; wood flooring remains.** No wet WALL, PAN, LEVEL, NICHE, CEILING, floor DCOF, waterproof assembly, or shower slope gate.

## Candidate A — Elm Vera Forma Earth Lines Glossy relief, 2 × 10 in, $8.20/SF

| BUILD criterion (1–5) | Score | Evidence and constructability reason |
|---|---:|---|
| Substrate and setting | 4 | [Elm Earth Lines](https://www.elmsurfaces.com/product/earth-lines-vera-forma) is a dry-wall-scale relief tile; a flat, plumb vanity-wall substrate and the manufacturer's adhesive/joint requirements must be verified before setting. |
| Setout and cutting | 4 | W1 drawing-derived 4.224 ft (50.688 in) wide × 9.25 ft (111 in) high (geometry.json). The 2-in horizontal module offers flexible width cuts, but vertical 10-in modules require an intentional top/bottom course: eleven nominal full heights would leave only about 1 in total before joints. |
| Plumbing coordination | 3 | Brizo T65722LF-GL Luxe Gold **wall-mounted** faucet and R65700 rough (plumbing.json) put trim/backplate against potentially uneven sculpted tile; establish a flat bearing area/mounting depth with the plumbing installer before approval. |
| Edges, trim and finish | 3 | Raised Earth Lines field needs a confirmed external-edge profile, mirror perimeter, grout width and relief-to-trim junction; exact openings and fixture coordinates have not been field measured. |
| Procurement / sequence risk | 3 | Same-job Elm quote 2026-09-04 establishes $8.20/SF, 6.22 SF/44-piece carton (TRADE_QUOTES.md §b). **Quote states 7 mm but maker Earth Lines listing states 8.6 mm**; confirm actual lot and profile depth. Domestic/local stock and freight unverified. |

**Arithmetic seat mean: (4+4+3+3+3)/5 = 3.4/5.**  
**gate_flags:** None established for this **dry wall**. Verify actual faucet trim seating and wall geometry as implementation holds; neither is a proven impossible condition. No wet DCOF gate. Owner budget missing and no discontinued status established.  
**top_fix:** Detail and mock up a flush wall-faucet escutcheon mounting plane through the relief, with matching edge trim at the verified supplied thickness.  
**confidence:** medium (manufacturer identity, quote and fixture finish known; actual lot, wall dimensions and trim detail unverified).

## Candidate B — Floor & Decor La Belle Purity High Gloss, SKU 100507722, 3 × 12 in, $5.56/SF

| BUILD criterion (1–5) | Score | Evidence and constructability reason |
|---|---:|---|
| Substrate and setting | 4 | [F&D La Belle Purity](https://www.flooranddecor.com/ceramic-tile/la-belle-purity-high-gloss-ceramic-tile-100507722.html) is 8.5-mm pressed ceramic listed as wall tile; verify flat backing and maker's joint/setting instructions for a full-height installation. |
| Setout and cutting | 4 | At W1 50.688 in wide, sixteen 3-in vertical-stack columns leave ~1.34-in symmetrical edge cuts before joints; use fifteen columns and balanced ~2.84-in ends, subject to actual joint dimensions. At 111 in tall, plan the 12-in courses rather than leave tiny terminal strips. |
| Plumbing coordination | 4 | Flat glossy field simplifies mounting the Brizo T65722LF-GL wall faucet/backplate compared with relief; confirm rough R65700 and final tile-to-trim datum before closing the wall (plumbing.json). |
| Edges, trim and finish | 4 | A 3 × 12 pressed rectangular field is straightforward to finish with a suitable profile and consistent stack joints; verify actual 8.5-mm tile/adhesive assembly and mirror offsets. |
| Procurement / sequence risk | 3 | Candidate's $5.56/SF is public Kirkwood, Georgia retail, **not an Illinois delivered quote**. [F&D SKU 100507722](https://www.flooranddecor.com/ceramic-tile/la-belle-purity-high-gloss-ceramic-tile-100507722.html) still needs Chicago stock, matching lot, carton multiple and tax/freight confirmation. |

**Arithmetic seat mean: (4+4+4+4+3)/5 = 3.8/5.**  
**gate_flags:** None established for a dry wall; floor slip/DCOF inapplicable. Confirm store availability and field setout; no verified discontinuation or geometric impossibility.  
**top_fix:** Issue a dimensioned balanced stack layout locating both end cuts, mirror edges and the wall-faucet trim before ordering.  
**confidence:** medium (catalog tile format and finish clear, but pricing locality and native field dimensions open).

**Pricing check:** The candidate A 44.90 SF gross/copy includes 15% waste already: $368.18/copy before rounding; eight 6.22-SF cartons imply 49.76 SF and approximately $408.03/copy. B: 44.90 × $5.56 = $249.64/copy, before piece/carton rounding. Both exclude installation, trims and freight. [Elm Earth Lines](https://www.elmsurfaces.com/product/earth-lines-vera-forma); [F&D La Belle Purity](https://www.flooranddecor.com/ceramic-tile/la-belle-purity-high-gloss-ceramic-tile-100507722.html); inputs/TRADE_QUOTES.md.
