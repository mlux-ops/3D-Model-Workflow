# TX-POWDER — Round 003 — critic-cost (procurement seat; weight 0.20)

**Blind review, 2026-11-06.** Two Triplex dry powder vanity feature walls. Source `geometry.json`: **2.99 ft × 9.25 ft = 27.6575 SF net**, carried **31.8 SF/unit gross including 15% waste**; current 1529 model dimensions remain unverified. Room floor is **wood**, so floor tile quantity is zero and **floor wet DCOF gate N/A**. Plumbing `48140991` is a two-hole **wall-mount cross-handle faucet** and `32526141` its wall rough; final backplate/escutcheon location and trim finish are not independently verified (`plumbing.json`, rows `2050699988500356`, `6554299615870852`). The ELM **2026-09-03 combined Haze Camel/Wheat quote row `4966802551603076`** is **$11.93/SF** (both colors together), not separate confirmed color rates. No allocated room tile budget appears in `state/OWNER_FEEDBACK.md`, so the **>125% budget gate cannot be invoked**.

## Candidate B — specified 70% Camel / 30% Wheat matte dry feature

| Procurement criterion | Score (1–5) | Specific evidence and one-line reason |
|---|---:|---|
| **Quote lineage and $/SF traceability** | **4** | ELM 2026-09-03 TX powder row `4966802551603076` directly carries **31.8 SF combined Haze at $11.93/SF**, but the **70:30 color allocation is not a separately confirmed color-by-color supplier price** (`candidates/B.md`, lines 5–13). |
| **Material cost against carried allowance** | **3** | **31.8 × $11.93 = $379.37/unit** on the carried **blended** tile rate, with no approved premium allowance; a PH Earth Lines **$8.20/SF** reference could illustrate **$260.76/unit** at TX area but is **not an actual TX quote or selected alternative** (`candidates/B.md`, lines 13–15; `research/products/elm-vera-forma-earth-lines-2x10.md`). |
| **Waste, 70:30 split and order cartons** | **4** | Source gross **31.8 SF already includes 15% waste**; explicit **22.26 SF Camel + 9.54 SF Wheat** supports **4 + 2 cartons** if the historical **6.14 SF/carton** applies to both colors, but actual color-by-color purchasing quantities remain unquoted (`candidates/B.md`, lines 9–13; `geometry.json`). |
| **US/Chicago availability and logistics** | **3** | Haze collection shows current US distribution/quick-ship claim; historical ELM price notes **114 pieces/6.14 SF per carton, FOB Texas**, but actual Camel/Wheat batch inventory, Chicago land date, freight, carton minimum are `null` ([ELM Haze Camel](https://www.elmsurfaces.com/product/haze-camel); [Haze Wheat](https://www.elmsurfaces.com/product/haze-wheat); `candidates/B.md`, line 13). |
| **Trim, setting, returns and labor** | **2** | Double-color layout, base trim against wood, full wall 1.6×5 hand-setting, grout and wall-mounted faucet/mirror sealing plane add labor with **no priced installer/trim/freight/tax schedule** (`candidates/B.md`, lines 9–10, 17). |

**seat_score: 3.2 / 5.0** (mean 4,3,4,3,2). **confidence: medium** for historical rate and case arithmetic, low for separate-color delivered quote.

**Tile-only reconciliation:** **31.8 SF/unit × $11.93/SF = $379.374 → $379.37/unit; two-unit raw extension $758.748 → $758.75** (a $0.01 aggregate-vs-per-unit rounding difference, not a new rate). At a *proposed*, unapproved 70:30 ratio, **22.26 SF Camel + 9.54 SF Wheat = 31.80 SF gross**. If colors are separately boxed at **6.14 SF/carton**, the provisional requirement is **4 Camel cartons (24.56 SF)** plus **2 Wheat cartons (12.28 SF)** = **36.84 SF/unit**. Multiplying all cartons by the blended **$11.93/SF** gives **$439.50/unit merely as an unconfirmed carton-priced illustration**; neither separate color carton prices nor whether the same blending discount applies is established. **Do not add another 15% waste** to either full-wall or color subtotals. Grout, cartons/attic stock, installation and freight are outside the quoted tile-rate allowance.

**top_fix:** Obtain a **two-unit ELM quote for the measured 70:30 Camel/Wheat layout** with confirmed color-specific carton counts, current Chicago delivery, landed pricing and priced exposed edges/installer labor.

**gate_flags:**
- **NO HARD WET GATE — DRY WALL:** ELM individual Camel/Wheat products list **Walls**; no wet wall or tile floor in this room. Floor wet DCOF is **N/A**, not a missing/failing floor test (`candidates/B.md`, lines 5–11; `geometry.json`).
- **HOLD — COST/SCOPE:** 70:30 physical mix, actual wall-rough and mirror geometry, joint/trim and separate carton rates unconfirmed. The manufacturer's dry-wall listing is consistent with the surface, and there is **no evidence of a discontinued/no-US-distribution condition**.
- **NO >125% BUDGET FAIL:** Room-specific owner budget and upgrade cap `null`; PH Earth Lines reference is not the carried TX room budget.

## Candidate C — unproportioned Camel/Wheat matte dry feature

| Procurement criterion | Score (1–5) | Specific evidence and one-line reason |
|---|---:|---|
| **Quote lineage and $/SF traceability** | **4** | Exact same **TX Haze combined blend $11.93/SF** from Smartsheet `4966802551603076`; it is a genuine **dated project row**, not a fresh order confirmation (`candidates/C.md`, lines 5–7, 12). |
| **Material cost against carried allowance** | **4** | Historic gross wall **31.8 × $11.93 = $379.37/unit**, without any additional accent material or assumed separate-color upcharge (`candidates/C.md`, lines 7, 13, 17). |
| **Waste, ratio and order cartons** | **2** | **15% waste included** in 31.8 SF, but there is **no Camel/Wheat mix percentage**, so each color's carton quantity, attic stock and cross-color overage are impossible to determine despite historical 6.14-SF cartons (`candidates/C.md`, lines 7, 17; `geometry.json`). |
| **US/Chicago availability and logistics** | **3** | Haze is US-distributed/quick ship at collection level; **current stock in the two colors, local lot/lead and FOB-Texas freight are unconfirmed** ([Haze collection](https://www.elmsurfaces.com/product-collection/haze); `candidates/C.md`, lines 12–13). |
| **Trim, setting, returns and labor** | **2** | Color layout, grout code/width, full-height small-format labor and exact wall-faucet/mirror landing unresolved; no priced trim, mortar, freight, labor or tax (`candidates/C.md`, lines 13, 17; `plumbing.json`). |

**seat_score: 3.0 / 5.0** (mean 4,4,2,3,2). **confidence: medium** for the carried gross allowance; low for order quantity/labor.

**Tile-only reconciliation:** **31.8 SF gross with 15% waste × $11.93/SF = $379.37/unit** by rounded extension, or **$758.75 for 63.6 SF across two units before carton rounding**. A single-color theoretical lower bound is **ceil(31.8 / 6.14) = 6 cartons/unit**, but this is **not a color-by-color purchase list**; with two separately supplied colors the actual box count cannot be calculated without a mix proportion. Product mix does not double the wall SF. Installed cost, Chicago freight and new project quote `null`.

**top_fix:** Fix the **Camel/Wheat proportion in a dimensioned wall-rough elevation**, then obtain two-unit supplier-confirmed color-carton pricing, stock and installation-trim costs.

**gate_flags:**
- **NO WET/FLOOR DCOF GATE:** Decorative **dry wall only**; wood floor remains, both Haze products listed Walls (`geometry.json`; [Camel](https://www.elmsurfaces.com/product/haze-camel); [Wheat](https://www.elmsurfaces.com/product/haze-wheat)).
- **HOLD — QUANTITY/DETAIL:** Color split and wall-mounted faucet/escutcheon backing unverified, but not a proven hard fail for wet use, discontinuation or geometry.
- **NO >125% BUDGET FAIL:** Carried tile quote is a line-item reference, not an approved total room budget.

