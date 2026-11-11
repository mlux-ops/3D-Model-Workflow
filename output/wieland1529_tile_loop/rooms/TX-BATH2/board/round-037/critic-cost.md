# R037 Independent Cost Critique — TX-BATH2

## Candidate A

| Criterion | Score | Evidence |
|---|---:|---|
| Material area-rate expense vs. carried budget | 4 | Candidate packet totals $642.91 per copy ($1,285.83 for two) across 145.13 gross SF; the cited rates average about $4.43/SF and the source quantities already include 15% waste once. The [current De Rossi retailer page](https://www.flooranddecor.com/porcelain-tile/de-rossi-ivory-matte-porcelain-tile-100996800.html) shows $6.49/SF at Kirkwood, Atlanta, versus the packet’s $6.99/SF Camelback observation; substituting that Atlanta reading gives $621.06 per copy (~$4.28/SF). Both are below the approximately $10/SF owner target average in inputs/TRADE_QUOTES.md, but the room budget is still FILL IN, so budget compliance is unknown. |
| Unit-size and carton inefficiency | 3 | The [Pienza 24x48 page](https://www.flooranddecor.com/porcelain-tile/pienza-terra-matte-porcelain-tile-110850387.html) lists 15.50 SF/box; 92.8 SF needs 6 boxes (93 SF). The [De Rossi 24x24 page](https://www.flooranddecor.com/porcelain-tile/de-rossi-ivory-matte-porcelain-tile-100996800.html) lists 11.64 SF/box; 43.7 SF needs 4 (46.56 SF). Elm Tones is 6.50 SF/carton; 8.63 SF needs 2 (13 SF). If sold only by full carton, rounding adds about 7.43 SF per copy beyond the already-wasted gross takeoff; the base extension does not include this carton rounding. |
| Price hierarchy and Chicago-price discipline | 3 | The packet uses the 2026-09-04 1529 Elm Tones quote at $6.95/SF and named non-Chicago Floor & Decor observations. The current F&D pages show Kirkwood/Atlanta prices of $2.99/SF for Pienza and $6.49/SF for De Rossi, while the packet records Iowa and Phoenix readings. These are store-context prices, not a Chicago quote; no Chicago amount is inferred. |
| Current sourcing and availability certainty | 3 | As observed 2026-11-07, F&D’s Kirkwood/Atlanta pages show 89 Pienza boxes and 134 De Rossi boxes, with store pickup estimates of Nov 14–21 and delivery estimates of Nov 9–14; the pages say shipping charges may apply. This establishes a live route at that store, not Chicago stock. The Elm quote is project-specific but gives no current lot or ETA. |
| Accessories, freight and reordering exposure | 2 | Trim/edge, niche sill treatment, setting materials, freight, tax and landed cost are unpriced. F&D requires a delivery ZIP for a shipping estimate; Elm’s Tones freight/price validity are unstated. The 300-SF minimum and 10–12-week lead in inputs/TRADE_QUOTES.md apply to Cortar, not Tones, and are not transferred here. |

Seat mean: (4 + 3 + 3 + 3 + 2) / 5 = 3.0

top_fix: Replace the non-Chicago proxy with a Chicago store price and stock check, then carton-round all three surfaces and include freight and trim against the filled room budget.

gate_flags: Budget gate is not evaluable because the carried room budget is FILL IN; no cost-based failure is evidenced. Other technical gates are outside the COST seat.

confidence: medium. On 2026-11-07 the direct Elm Tones Sandstone page returned Internal Error in the browser tool; cause unknown. I used the permitted 2026-09-04 1529 quote in inputs/TRADE_QUOTES.md instead. That quote and $6.95/SF rate are documented, but live maker-page verification remains unresolved; no retry was made.

## Candidate B

| Criterion | Score | Evidence |
|---|---:|---|
| Material area-rate expense vs. carried budget | 3 | Candidate packet totals $845.46 per copy ($1,690.91 for two) across 145.13 gross SF, about $5.83/SF, with the original 15% waste included once. This remains below the approximately $10/SF owner target average in inputs/TRADE_QUOTES.md, but costs about $224.39 more per copy than Candidate A’s current-page Atlanta recalculation. The room budget is FILL IN, so budget compliance cannot be determined. |
| Unit-size and carton inefficiency | 3 | Elm Tones wall tile is 6.50 SF/carton; 92.8 SF rounds to 15 cartons (97.5 SF). The [Luxe Sand 24x24 page](https://www.flooranddecor.com/porcelain-tile/luxe-sand-matte-porcelain-tile-101317949.html) lists 15.52 SF/box; 43.7 SF rounds to 3 boxes (46.56 SF). The [La Belle Purity page](https://www.flooranddecor.com/ceramic-tile/la-belle-purity-high-gloss-ceramic-tile-100507722.html) lists 0.25 SF/piece and 48 pieces/box; 35 pieces cover 8.75 SF, while a full 48-piece carton is 12 SF. The page prices by piece, so full-carton-only purchasing is not confirmed. |
| Price hierarchy and Chicago-price discipline | 4 | The packet applies the exact 2026-09-04 1529 Elm Tones quote ($6.95/SF) and the F&D Atlanta public price for La Belle Purity ($1.39 per 0.25-SF piece, equivalent to $5.56/SF) and Luxe Sand ($3.49/SF). The retailer pages confirm the per-piece and per-box basis. These are trade and non-Chicago public prices; no Chicago price is invented. |
| Current sourcing and availability certainty | 3 | On 2026-11-07, F&D’s Kirkwood/Atlanta page showed 6,751 La Belle Purity pieces and 76 Luxe Sand boxes, with store pickup estimates of Nov 14–21 and delivery estimates of Nov 9–14; shipping charges may apply. The Elm quote covers 773 SF across five Tones colors but does not state current stock or ETA. Atlanta listing data does not establish Chicago availability. |
| Accessories, freight and reordering exposure | 2 | Niche trim/sill treatment, setting materials, freight, tax and landed cost remain outside the area-rate total. F&D requests a ZIP code to estimate delivery; the Tones quote names FOB states but no freight amount or price validity. The Cortar-specific 300-SF minimum and 10–12-week lead do not apply to Tones. |

Seat mean: (3 + 3 + 4 + 3 + 2) / 5 = 3.0

top_fix: Confirm Chicago availability and delivered price, including carton or piece-order rules for both 2x20 and 3x12 tile, then cost the omitted trim and freight against the room budget.

gate_flags: Budget gate is not evaluable because the carried room budget is FILL IN; no cost-based failure is evidenced. Other technical gates are outside the COST seat.

confidence: medium. On 2026-11-07 the direct Elm Tones Sapphire page returned Internal Error in the browser tool; cause unknown. I used the permitted 2026-09-04 1529 quote in inputs/TRADE_QUOTES.md instead. That quote and $6.95/SF rate are documented, but live maker-page verification remains unresolved; no retry was made.
