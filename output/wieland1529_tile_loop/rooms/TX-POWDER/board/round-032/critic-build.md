# R032 independent blind BUILD review — TX-POWDER

**Seat:** BUILD / tile installer and general contractor (seat weight **0.25**, applied by prime only). Two separately evaluated neutral R032 A/B concepts for **102A/102B**; five 1–5 criteria and an **unweighted arithmetic mean to one decimal** per letter. No prior scoring or role mapping.

**Actual surfaces:** tiled **DRY vanity wall only**, with **wood flooring retained** and **NO tiled LEVEL/PAN/NICHE/CEILING**. Shower-floor DCOF and wet-wall application are inapplicable. Drawing-derived [geometry.json](../../geometry.json): W1 **2.99 ft wide × 9.25 ft tall**, or about 27.66 net SF, with no native aperture or mirror axis; original **31.80 gross SF per physical room includes 15% once**. [plumbing.json](../../plumbing.json) lists two-hole wall-mounted faucet **48140991** and rough **32526141**, but **the actual visible faucet metal finish is UNKNOWN** (structured null); no Chrome/BNX/white assumption.

## Candidate A — Elm Haze Camel + Wheat Matte 1.6×5

| BUILD criterion | Score | Evidence-grounded installer comment |
|---|---:|---|
| **1. Product permission on specified dry wall** | **5/5** | Official [Elm Haze Camel](https://www.elmsurfaces.com/product/haze-camel), [Wheat](https://www.elmsurfaces.com/product/haze-wheat) and [Haze collection](https://www.elmsurfaces.com/product-collection/haze) identify matte ceramic **WALL** applications. This dry decorative wall does **not** require manufacturer wet-wall listing or floor DCOF. Two colors are components of **one** wall quantity. |
| **2. Module, wall substrate and product gauge** | **3/5** | Small **1.6×5-in** pieces can follow a narrow **2.99-ft** W1 field with many joints and tolerances; a straight vertical grid and sample will control alignment, variation and wall flatness. **Candidate A calls 8.5 mm while official Elm Haze collection lists 8 mm**: lot gauge and setting/trim thickness need reconciliation. Color 70/30 is a proposed design split, not confirmed carton composition ([candidate A](candidates/A.md)). |
| **3. Faucet/mirror penetrations and finish-dependent hardware** | **3/5** | A two-hole **wall-mounted** faucet and **32526141** rough require exact spout/handle escutcheon holes, flat support and projection relative to tile face. Finish remains **UNKNOWN**: avoid specifying a metal-matched trim on guesswork. Actual vanity/mirror edges and accessory mounts are not measured ([plumbing.json](../../plumbing.json)). |
| **4. Grout, exposed returns and wood transition** | **3/5** | High joint count and two matte colors need maker grout width/color confirmation, movement/perimeter sealant, edge profile and a clean base termination above wood. Distinct color batches must follow intentional bounded 70% Camel / 30% Wheat layout and not look like an accidental mixed lot. No tile on wood. |
| **5. Cut/waste and two-color ordering readiness** | **3/5** | Gross **31.80 SF** includes the source 15% once. Same-job **2026-09-04 quote $11.93/SF** for Camel/Wheat yields **$379.37/copy** on area; 4 Camel + 2 Wheat cartons is an **illustrative**, unconfirmed mix, not a stock reservation. W1 actual edges, faucet holes and final color allocation are unknown; do not double the area by color ([inputs/TRADE_QUOTES.md](../../../../inputs/TRADE_QUOTES.md)). |

**BUILD A mean:** (5 + 3 + 3 + 3 + 3) / 5 = **3.4/5**.

**top_fix A:** Verify the **wall-mounted faucet's actual two-hole escutcheon footprint and projection**, then set out the Camel/Wheat **70/30 color grid** at confirmed 8-mm Haze thickness, mirror bounds and wood base.

**gate_flags A (hard):** **NONE CONFIRMED.** Exact Haze Wall use is sufficient for dry feature; no selected discontinued item or owner veto evidenced. **OPEN (non-hard):** finish unknown (not an asserted metal clash), 8 vs 8.5-mm discrepancy, faucet rough/mirror geometry, maker grout/profile, color-specific lots, owner budget and landed cost. **Wet DCOF irrelevant.**

**confidence A:** **Medium** on manufacturer dry-wall identity and same-job rate; low on hardware/color-grid details.

## Candidate B — Floor & Decor La Belle Purity High Gloss 3×12

| BUILD criterion | Score | Evidence-grounded installer comment |
|---|---:|---|
| **1. Product permission on specified dry wall** | **5/5** | Exact official [Floor & Decor La Belle Purity **SKU100507722**](https://www.flooranddecor.com/ceramic-tile/la-belle-purity-high-gloss-ceramic-tile-100507722.html) identifies glossy ceramic for wall use. Its other shower-walls rating is not needed for **DRY** W1 and it is not specified on a floor. |
| **2. Module, wall substrate and product gauge** | **4/5** | Single 3×12 vertical ceramic stack over a **2.99-ft** wall is less numerous than A's 1.6×5 blend. Product source identifies **8.5-mm pressed edge** and **manufacturer-suggested 1/16-in joints**; caliber/flatness/lippage, centered column cuts and adhesive setting must still be checked with actual wall width. |
| **3. Faucet/mirror penetrations and finish-dependent hardware** | **4/5** | Flat tile faces give a more predictable seating surface around the two-hole wall faucet **48140991** and rough **32526141** than an irregular tile or multi-color grid. Faucet visible finish **UNKNOWN** and trim projection, mirror edge and actual bores remain to measure; do not invent a finish or wall faucet spec beyond [plumbing.json](../../plumbing.json). |
| **4. Grout, exposed returns and wood transition** | **3/5** | 1/16-in grout is supplier-suggested, but exposed pressed cut edges, metal profile, grout tone, ceiling/side terminations and a movement/sealant separation from the **existing wood floor** have no selected details. No floor tile added. |
| **5. Cut/waste and ordering readiness** | **4/5** | The one-SKU scheme needs no two-color carton allocation; small 3×12 modules are field-adjustable around mirror/faucet, though true cut widths are unknown. Existing **31.80 gross SF (15% already once)** × **$5.56/SF** = **$176.81/copy** using dated **2026-11-07 Kirkwood, Georgia public retail**, with 128 pieces illustrative only; no current Chicago lot or all-in installed price. |

**BUILD B mean:** (5 + 4 + 4 + 3 + 4) / 5 = **4.0/5**.

**top_fix B:** Dimension the **48140991 faucet/rough and mirror clearances** on the 3×12 grout layout, and specify a compatible edge trim and wood-floor isolation detail.

**gate_flags B (hard):** **NONE CONFIRMED.** Dry wall and allowed F&D source are eligible; no proven owner veto, selected discontinuation or finish clash. **OPEN:** visible faucet metal unknown, wall measurements, grout/edge spec, Chicago lot and complete budget/delivery terms. **No tile LEVEL/PAN/NICHE/CEILING and no wet DCOF gate.**

**confidence B:** **Medium** — exact SKU/format known; hardware geometry and local supply unknown.

**Source scope:** own R032 [A](candidates/A.md)/[B](candidates/B.md), geometry.json/plumbing.json, official pages above, research/products/elm-haze-camel-1p6x5.md and elm-haze-wheat-1p6x5.md, inputs/TRADE_QUOTES.md. **$11.93/SF** is **2026-09-04 same-job Elm quote**; **$5.56/SF** is a **Kirkwood, GA public retailer price**. No prior scores or aggregate champion recommendation are part of this BUILD report.
