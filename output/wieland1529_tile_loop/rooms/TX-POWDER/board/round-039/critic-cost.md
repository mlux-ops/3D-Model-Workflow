# R039 independent COST critique — TX-POWDER (strict blind)

**Scope:** Two physical copies, 102A and 102B; ONE **DRY** W1 vanity wall per copy, drawing-derived 2.99 ft wide x 9.25 ft tall; existing WOOD floors. The original **31.8 gross SF/copy** already includes **15% waste ONCE** (2 x 31.8 = **63.6 gross SF** total). The wall opening, mirror and faucet penetrations are unmeasured. Wall-mounted Hansgrohe finish is unconfirmed. No tiled floor, pan, niche or ceiling; no added waste factor. Sources: [geometry](../../geometry.json), [plumbing](../../plumbing.json), [neutral candidate A](candidates/A.md), [neutral candidate B](candidates/B.md), [2026-09-04 same-job trade quote](../../../../inputs/TRADE_QUOTES.md) sections (a), (b), (c), Elm thread `1a068e80c92c255f`, message `1a06e29c0b2333f4`. All money below is **tile material only**, before tax, freight, trims, setting materials, labor and any budget allowance (FILL IN).

## Candidate A — Elm Haze Camel + Wheat, matte 1.6 x 5, proposed 70/30 mix

| COST criterion | Integer rating / 5 | Independent, source-specific reason |
|---|---:|---|
| C1. Price-source reliability | **5** | **$11.93/SF** is a 2026-09-04 actual **1529 Wieland same-job Elm trade quote**, combining Haze Camel and Wheat on one line, with **6.14 SF/box** and FOB TX, not an out-of-state online retail comparison; see `inputs/TRADE_QUOTES.md` (b), Elm Haze row. Price validity and separate color codes remain unconfirmed. |
| C2. Material-rate and area cost | **2** | **31.8 x $11.93 = $379.37/copy; 63.6 x $11.93 = $758.75/two copies**, before cartons. The $11.93/SF rate is **19.3% above** the owner's approximately $10/SF project average aspiration in `inputs/TRADE_QUOTES.md` (a); that aspiration is not a powder-room budget or a gate. No second 15% is added. |
| C3. Carton/mix efficiency | **2** | The neutral A 70/30 plan on **63.6 gross SF** implies **44.52 SF Camel / 19.08 SF Wheat**. Using the quoted **6.14 SF/box** separately by color requires **8 Camel + 4 Wheat = 12 whole boxes**, **73.68 SF**, approximately **$879.00** at quoted SF rate (**$120.25** over original gross-rate estimate). One-color theoretical 11 boxes would be wrong for the proposed two-color mix; carton rounding is a purchasing constraint, not an extra applied waste percentage. Source: candidate A and Elm Haze quote row. |
| C4. Distribution and lead risk | **3** | [Elm Haze collection](https://www.elmsurfaces.com/product-collection/haze) lists Camel and Wheat 1.6 x 5, wall use, **Quick Ship / US-Stocked** and **2–4 week** collection lead; [Camel](https://www.elmsurfaces.com/product/haze-camel) and [Wheat](https://www.elmsurfaces.com/product/haze-wheat) remain in the active maker catalog. Quote says FOB TX. **No current same-lot quantities, Chicago allocation, date-specific lead or delivered freight price** is confirmed. |
| C5. Installed-scope and change exposure | **2** | Two colors and many 1.6 x 5 joints require an unpriced layout and installation estimate; wood-floor termination, mirror cuts, wall-mounted faucet rough and trim remain unverified ([geometry](../../geometry.json), [plumbing](../../plumbing.json)). Maker [Haze collection](https://www.elmsurfaces.com/product-collection/haze) lists **8 mm** thickness whereas 2026-09-04 Elm quote states **8.5 mm**; reconcile before trim and adhesive pricing. Room allowance, tax, freight, setting and labor costs are unknown, so no budget overrun can be declared. |

**Original integer ratings:** `5, 2, 2, 3, 2` (sum **14**, n=5). **COST mean = 2.8 / 5** (14/5=2.8, one-decimal HALF_UP).

**top_fix:** Obtain one current **itemized, delivered, two-copy Camel/Wheat quote** using the 8+4 carton split, confirmed 70/30 piece layout, batch availability, and reconciled 8/8.5-mm build-up, with trims and labor separately priced.

**gate_flags:** **No confirmed hard-gate failure.** Maker lists DRY `Walls` use and current US distribution, with exact lot/quantities still unverified. `BUDGET_UNTESTABLE` (room budget FILL IN; no 125% comparison); `AVAILABILITY_LOT_UNVERIFIED`; `MIRROR_FAUCET_CUTS_UNVERIFIED`; any owner veto remains for prime to adjudicate from its restricted owner source. Wet-floor DCOF is inapplicable.

**confidence:** **medium** — same-job trade price and maker dry-wall listings are direct; exact color packaging, allocation, installed allowance and live cut geometry are pending.

## Candidate B — Floor & Decor Pienza Terra Beige, matte porcelain 24 x 48, SKU 110850387

| COST criterion | Integer rating / 5 | Independent, source-specific reason |
|---|---:|---|
| C1. Price-source reliability | **3** | The [exact live maker/retailer SKU page](https://www.flooranddecor.com/porcelain-tile/pienza-terra-matte-porcelain-tile-110850387.html) shows **$2.99/SF** and **$46.32/box** under **Kirkwood/Atlanta** store context on 2026-11-07. It is a current **out-of-state public retail listing, not a Chicago or same-job trade quote**. `inputs/TRADE_QUOTES.md` confirms no same-job Floor & Decor quote. |
| C2. Material-rate and area cost | **5** | **31.8 x $2.99 = $95.08/copy; 63.6 x $2.99 = $190.16/two copies** at the posted SF rate, with the source's 15% waste already incorporated. The published rate is materially below the roughly $10/SF project-average aspiration and candidate A's sourced $11.93/SF; **tax, shipping and labor are excluded**. Sources: exact SKU page, candidate B, trade-quote summary. |
| C3. Carton/order efficiency | **3** | The [SKU specifications](https://www.flooranddecor.com/porcelain-tile/pienza-terra-matte-porcelain-tile-110850387.html) report **2 pieces/box, 7.75 SF/piece = 15.50 SF/box**. Combined two-room buy: **ceil(63.6/15.5) = 5 boxes, 77.5 SF = $231.60** at maker's displayed $46.32/box. Separate room batches: **3 boxes/room = 6 boxes, 93 SF = $277.92**. These are buying-unit scenarios, not an added 15% waste or a guaranteed combined-lot order. |
| C4. Stock, shipping and lead | **2** | The [SKU page](https://www.flooranddecor.com/porcelain-tile/pienza-terra-matte-porcelain-tile-110850387.html) is active and shows **89 boxes at Kirkwood, GA**, with that store's collection/delivery options; it does **not** prove Chicago store inventory or jobsite availability. Chicago zip-specific freight, ETA, matched lot and order price remain unverified; avoid transferring a Georgia availability claim to Chicago. |
| C5. Installed-scope and exposure | **2** | The page specifies **actual 23.59 x 47.30 in., rectified, 9 mm**. The 2.99-ft (~35.9-in.) vanity wall is narrower than a 47.30-in. tile length; cuts, access, wall flatness, specialized large-format handling and edge pieces are unpriced, with mirror/faucet locations unknown ([geometry](../../geometry.json), [plumbing](../../plumbing.json)). The cheap material quote does not establish the installed cost. |

**Original integer ratings:** `3, 5, 3, 2, 2` (sum **15**, n=5). **COST mean = 3.0 / 5** (15/5=3.0, one-decimal HALF_UP).

**top_fix:** Obtain a **Chicago-specific exact-SKU inventory/lot and delivered five- or six-carton price**, plus a cut/flatness-based installation allowance for the narrow vanity wall.

**gate_flags:** **No confirmed hard-gate failure.** Retail SKU is actively offered; exact Chicago supply remains `AVAILABILITY_CHICAGO_UNVERIFIED`, not a proven discontinuation. `BUDGET_UNTESTABLE` (room allowance FILL IN); `MIRROR_FAUCET_CUTS_UNVERIFIED`; owner veto held to prime. SKU page permits wall application. Floor slip and shower wet-wall gates do not apply to the DRY feature wall with retained WOOD floor.

**confidence:** **low** — the posted SKU, cartons and regional price are checkable, but local availability, freight, contract price, assembly cost and live wall openings remain unknown.

**Board scope note:** These are independent COST opinions for neutral A/B; no previous candidate status, other reviewer ratings, criterion weights, role mapping or threshold outcome was consulted or applied.
