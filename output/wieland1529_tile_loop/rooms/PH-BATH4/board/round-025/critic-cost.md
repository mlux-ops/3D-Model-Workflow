# PH-BATH4 — round 025 independent COST/SELECTION critique (seat weight 0.20)

Blind **A**/**B** evaluated independently **2026-11-06 America/Chicago**, five equally averaged 1–5 procurement criteria each. This bath is an owner-selected **WALK-IN** with fixed **Brizo BT062415-BNX Black Onyx 4-inch square POINT drain**, so the same proposed tile must qualify separately for **LEVEL** and the installer-cut **four-plane POINT PAN**. Historical source covers **two** PH-BATH4 instances; figures here are **per one**. No weighted board total.

**Supplier verification:** [2026-09-04 1529 Elm same-job quote](../../../../inputs/TRADE_QUOTES.md), thread **1a068e80c92c255f**: **Cortar Bone flat 24x48 Soft $8.14/SF**, 15.39 SF/box, imported 10–12 week original estimate (50% deposit, 300-SF combined import minimum); **Tones Sandstone/Copper Glossy 2x20 $6.95/SF**, 6.50 SF/box, not a price for unlisted Ribbed. Maker lists exact [Bone flat Wet Areas WALL](https://www.elmsurfaces.com/product/cortar-bone), [Sandstone Wet Areas NICHE/WALL](https://www.elmsurfaces.com/product/sandstone-tones), [Copper Wet Areas NICHE/WALL](https://www.elmsurfaces.com/product/copper-tones). Current non-Chicago F&D storefront: [Luxe 101317949 $3.49/SF/$54.08 per 15.52-SF box](https://www.flooranddecor.com/porcelain-tile/luxe-sand-matte-porcelain-tile-101317949.html); [Riviera 101487775 $3.99/SF/$63.84 per 16-SF box](https://www.flooranddecor.com/porcelain-tile/riviera-oat-matte-porcelain-tile-101487775.html), with documented other-store **$4.39/SF/$70.24** ([prior direct observation](../../../../research/products/R022_FD_LUXE_SAND_RIVIERA_OAT_24PLUS_LEVEL_AND_SHOWER_PAN.md)). Current selected site defaults to **Kirkwood, Atlanta GA**, not Chicago.

## Option A — Bone flat wet WALL / Sandstone wet NICHE / Luxe 24x24 LEVEL and POINT PAN

| Independent cost criterion | Score | Cited evidence and reason |
|---|---:|---|
| 1. Exact Elm quoted wet materials | **5/5** | Bone **flat Soft 24x48 $8.14/SF**, **107.20 gross WALL SF**; Sandstone **$6.95/SF**, **8.63 gross NICHE SF**. Separate exact Elm wet-area listings; original Ribbed $7.37/SF is not a compliant flat-wall replacement rate. [Same-job quote](../../../../inputs/TRADE_QUOTES.md); [Bone flat](https://www.elmsurfaces.com/product/cortar-bone); [Sandstone](https://www.elmsurfaces.com/product/sandstone-tones) |
| 2. Exact LEVEL + POINT PAN retail | **5/5** | Luxe **SKU101317949 24x24 $3.49/SF**, maker/seller exact **Bathroom Floor, Shower Floor, wet DCOF >=0.42**; lower published floor price than B. F&D Atlanta price cannot be treated as Chicago transaction. [Official Luxe page](https://www.flooranddecor.com/porcelain-tile/luxe-sand-matte-porcelain-tile-101317949.html); [selected BNX point drain](../../plumbing.json) |
| 3. Original SF/price and 15%-once basis | **4/5** | Source **107.20 gross WALL +40.20 combined LEVEL/PAN +8.63 NICHE SF**, 15% waste already in source. Unrounded-line aggregate **$1,072.88** product-only (round once: $872.608 +$140.298 +$59.9785); original carried **$1,352.24**, provisional **125% original $1,690.30**, **not an owner-allocated budget**. [A source IDs and figure](candidates/A.md); [quote and source-gross discipline](../../../../research/products/R025_PH_THREE_ROOM_QUOTED_ELM_FD_LFT_WET_GATE_EVIDENCE.md) |
| 4. LEVEL/PAN split and POINT yield | **3/5** | Real ordered SF must replace 40.20 combined gross with **LEVEL net×1.15 + POINT PAN net×1.25**, never add waste again to historical gross. Owner carries **35 SF floor**, but prior Revit showed **27 SF**, so actual LEVEL net and POINT footprint need native reconciliation; 24x24 four-plane cutting by selected installer is acceptable in principle. [Room geometry owner override](../../geometry.json); [owner LFT slope rule](../../../../state/OWNER_FEEDBACK.md); [A source](candidates/A.md) |
| 5. Full boxes, delivery and Chicago lot | **2/5** | Old-source-only minimum boxes: **ceil(107.20/15.39)=7 Bone**, **ceil(8.63/6.50)=2 Sandstone**, **ceil(40.20/15.52)=3 Luxe**. Approximate **$1,129.51 boxed product only** using quoted Elm $/SF and F&D posted **$54.08/box**; freight, tax, grout, cuts, trim, matching shade/lot, Chicago on-hand and ETA still unknown. [Elm quote terms](../../../../inputs/TRADE_QUOTES.md); [F&D exact product](https://www.flooranddecor.com/porcelain-tile/luxe-sand-matte-porcelain-tile-101317949.html) |

**Arithmetic mean A:** (5 + 5 + 4 + 3 + 2)/5 = **3.8/5**.  
**top_fix A:** Resolve the owner's 35-SF versus older 27-SF room-floor discrepancy with verified net LEVEL/PAN areas before applying the separate 15%/25% waste and full-carton rounding.  
**confidence A:** medium for quoted products; low for delivered quantity and lot.

## Option B — Bone flat wet WALL / Copper wet NICHE / Riviera 24x48 LEVEL and POINT PAN

| Independent cost criterion | Score | Cited evidence and reason |
|---|---:|---|
| 1. Exact Elm quoted wet materials | **5/5** | Bone flat **$8.14/SF on 107.20 gross WALL**; Copper glossy **$6.95/SF on 8.63 gross NICHE** from same Sept 4 Tones multi-color line. Both individually wet WALL listed; no use of unverified Ribbed relief wet approval. [Owner same-job quote](../../../../inputs/TRADE_QUOTES.md); [Bone flat](https://www.elmsurfaces.com/product/cortar-bone); [Copper](https://www.elmsurfaces.com/product/copper-tones) |
| 2. Exact LEVEL + POINT PAN retail | **4/5** | Riviera **SKU101487775 nominal 24x48**, public **$3.99–$4.39/SF** across sourced store snapshots, **Bathroom Floor and Shower Floor**, wet **DCOF >=0.42**. Higher than A by **$0.50–$0.90/SF**; no verified Chicago delivered quote. [Current Riviera maker/seller page](https://www.flooranddecor.com/porcelain-tile/riviera-oat-matte-porcelain-tile-101487775.html); [store variance](../../../../research/products/R022_FD_LUXE_SAND_RIVIERA_OAT_24PLUS_LEVEL_AND_SHOWER_PAN.md) |
| 3. Original SF/price and 15%-once basis | **4/5** | **107.20+40.20+8.63 original gross SF** with waste once gives **$1,092.98–$1,109.06** unrounded-line, once-rounded product screen, vs original **$1,352.24** and only provisional **$1,690.30** 125%-of-original comparison. Increment above A: **$20.10–$36.18** SF extension. Owner has not allocated a binding room budget. [B sources/arithmetic](candidates/B.md); [owner budget line](../../../../state/OWNER_FEEDBACK.md) |
| 4. LEVEL/PAN split and POINT yield | **2/5** | The owner confirms WALK-IN and Brizo **BT062415-BNX square POINT**, requiring a separate four-plane PAN. 24x48 actual **23.58x47.28** needs field cut-yield validation and **LEVEL net×1.15 + POINT PAN net×1.25**, not a second percentage on original **40.20 SF**. The owner's **35 SF** versus prior **27 SF** floor conflict remains open. [Plumbing](../../plumbing.json); [geometry](../../geometry.json); [F&D format](https://www.flooranddecor.com/porcelain-tile/riviera-oat-matte-porcelain-tile-101487775.html) |
| 5. Full boxes, delivery and Chicago lot | **2/5** | Old-gross-only illustration: **7 flat Bone boxes +2 Copper niche boxes +ceil(40.20/16)=3 Riviera boxes** implies **$1,158.79–$1,177.99 boxed products**. Actual four-plane cut waste, same-lot shade, Chicago stock, Elm lead, freight, tax and accessory costs remain unknown; site default is Atlanta. [Elm cartons/terms](../../../../inputs/TRADE_QUOTES.md); [F&D per-box price](https://www.flooranddecor.com/porcelain-tile/riviera-oat-matte-porcelain-tile-101487775.html) |

**Arithmetic mean B:** (5 + 4 + 4 + 2 + 2)/5 = **3.4/5**.  
**top_fix B:** Validate a measured 24x48 four-plane POINT PAN cut layout/yield against the actual 35-vs-27-SF room and Brizo drain position before quantifying Riviera cartons.  
**confidence B:** medium on price/product use; low on final cut and shipped quantities.

## gate_flags

| Gate | A | B |
|---|---|---|
| WALL | **PASS** — exact Bone flat Soft maker Wet Areas WALL | **PASS** — same Bone flat Soft maker Wet Areas WALL |
| NICHE | **PASS** — Sandstone individually listed wet NICHE/WALL | **PASS** — Copper individually listed wet NICHE/WALL |
| LEVEL | **PASS** — Luxe published Bathroom Floor + wet DCOF >=0.42 | **PASS** — Riviera published Bathroom Floor + wet DCOF >=0.42 |
| Conditional PAN (owner confirms WALK-IN) | **PASS (tile item only)** — Luxe Shower Floor + wet DCOF; installer four-plane geometry still unknown | **PASS (tile item only)** — Riviera Shower Floor + wet DCOF; installer four-plane geometry still unknown |
| BUDGET | **UNKNOWN** — $1,690.30 is only 125% historic original, no owner allocation or full delivery cost | **UNKNOWN** — same |
| GEOMETRY | **UNKNOWN** — owner 35 SF vs old 27 SF; W1 5.00 ft and two 2.54-ft returns provisional; no native drain offset or proven <3-in cut | **UNKNOWN** — same, with larger 24x48 yield sensitivity |
| CHICAGO STOCK | **UNKNOWN** — F&D Chicago lot/cartons/ETA and Elm warehouse unconfirmed | **UNKNOWN** — same |

No evidenced hard-gate **FAIL** from cost sources; product-level PAN PASS does not certify four-plane slope/cut feasibility. Total is rounded **once from unrounded SF extensions**: A **$1,072.8845 → $1,072.88**, B **$1,092.9845–$1,109.0645 → $1,092.98–$1,109.06**; adding displayed, separately rounded component cents may differ by $0.01. F&D Luxe **$54.08/box** differs from **15.52×rounded $3.49=$54.16**; boxed illustration uses the posted box price. No weighted total, owner signoff, supplier contact or purchase.
