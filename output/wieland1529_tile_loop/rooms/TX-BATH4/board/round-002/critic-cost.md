# TX-BATH4 — Round 002 — critic-cost (procurement; seat weight 0.20)

**Review basis (2026-11-06).** Blind letters only; two Triplex units. Owner-confirmed **tub alcove** appears in the candidate packets and `plumbing.json` includes a Duravit built-in tub. Prior 1529 handoff geometry (not live verified) shows **5.00-ft back + two 2.54-ft returns = 10.08 LF**, tiled **7.75 ft** over tub deck, plus a **38.5 SF net main floor**. Carried **89.8 SF Charcoal wall, 44.3 SF Bone Soft floor, and 8.63 SF niche** per unit **already include 15% waste**; niche and any accent must displace matching wall area, not duplicate it. ELM prices below are historical **2026-09-03 project quote rates**. No room budget is allocated in `state/OWNER_FEEDBACK.md`, so **the >125% budget gate is untestable**. Chicago live stock/lead/landed cost and installed finish labor are `null`.

## Candidate A — Cortar Charcoal flat, Soho Black niche, Cortar Bone Soft floor

| Procurement criterion (1–5) | Score | Evidence / one-line reason |
|---|---:|---|
| Historical rates and bid lineage | **3** | Charcoal 24×48 Soft **89.8 × $8.14** (Smartsheet `502709287976836`) and Bone floor **44.3 × $6.75** (`5006308915347332`) are project references; **Soho Black has no priced TX-BATH4 quote, rate `null`** (`candidates/A.md`, lines 7–10; `research/products/elm-soho-black-2x10.md`). |
| Material economics / quote completeness | **2** | **$1,030.00/unit** for quoted-rate wall+floor **before Soho**, with niche price and full room cost `null`; Clara's **$33.70/SF** cannot be transferred to Soho (`candidates/A.md`, lines 8, 17). |
| Waste, wall/niche netting and box quantities | **3** | **10.08 LF × 7.75 ft × 1.15 ≈89.83 SF** supports the provisional **89.8 gross wall SF**, but **8.63 SF niche** may overlap, and Soho/Charcoal carton rounding plus attic stock are unmeasured (`geometry.json`; `candidates/A.md`, lines 8 and 15). |
| Chicago supply, historical lead and minimum | **2** | Cortar note carries **10–12 weeks, overseas, 50% deposit, 300 SF import minimum**, not a current quote; **two-unit Charcoal 179.6 SF** is **120.4 SF short** of that historical threshold if separately enforced. Soho listing active, exact stock/lead `null` (`research/products/elm-cortar-charcoal-24x48-soft.md`; [Soho Black](https://www.elmsurfaces.com/product/soho-black)). |
| Installed work, trim and freight | **2** | 24×48 wall setting, colored edge, wet niche waterproofed returns/sill, bullnose, floor threshold, grout, labor, freight and tax have no priced allowances (`candidates/A.md`, lines 7–11, 15–17). |

**seat_score: 2.4 / 5.0** — arithmetic mean (3,2,3,2,2). **Confidence: low** (two historical rates grounded; Soho price and supplier confirmation entirely missing).

**Extended material illustration (15% waste already included):** Flat Charcoal **89.8 × $8.14 = $730.97/unit**; Bone Soft **44.3 × $6.75 = $299.03/unit**; **partial subtotal $1,030.00/unit or $2,060.00/two units, plus Soho 8.63 SF × `null` price**. **Actual completed material total = `null`**. The historical **Clara Caviar 8.63 × $33.70 = $290.83/unit** is **a rejected price proxy** for Soho, **not** a substitute estimate. Actual niche field displacement could also change the Charcoal amount; box minima and attic stock are unpriced. The **300 SF import minimum is an historical term only**, and it is **not verified as per-SKU** or applicable after pooling Cortar purchases across the project; do **not** apply an invented import surcharge.

**top_fix:** Obtain a **revised, two-unit current ELM package quote** for flat Charcoal + exact Soho Black niche + Bone Soft floor, with measured field/niche netting, 300-SF-minimum resolution, cartons, stock dates and priced trim/freight.

**gate_flags:**
- **FAIL — BONE_SOFT_FLOOR_DCOF_EXACT_NULL:** Cortar Bone **12×24 Soft** has a manufacturer *Wet Areas* application listing but **no published exact wet DCOF ≥0.42** for this format/finish (`research/products/elm-cortar-bone-soft-12x24.md`; [ELM flat Bone](https://www.elmsurfaces.com/product/cortar-bone); `board/BOARD.md`, gate 2).
- **WET WALLS PASS IN SPECIFIED SCOPE:** Flat Cortar Charcoal and Soho Black **individual products list Wet Areas** ([Charcoal](https://www.elmsurfaces.com/product/cortar-charcoal); [Soho Black](https://www.elmsurfaces.com/product/soho-black)). **Bone Ribbed is explicitly conditional for a verified dry location**, area `null`, excluded from the costed wet design; if installed on tub walls, it would fail for missing Wet Areas (`research/products/elm-cortar-bone-ribbed-24x48-relief.md`).
- **HOLD — QUOTE/DELIVERY:** Soho rate, lot, cartons, Chicago ETA, and final wet-wall/niche net quantities `null`; there is no substantiated *discontinued / no US distribution* availability failure.
- **BUDGET UNTESTABLE:** No allocated room cap, so neither this partial $1,030.00 nor any hypothetical Soho premium establishes a >125% failure.

## Candidate B — Cortar Charcoal, conditional Bone Ribbed panel, Clara Caviar niche, Bone Soft floor

| Procurement criterion (1–5) | Score | Evidence / one-line reason |
|---|---:|---|
| Historical rates and bid lineage | **4** | Quote rows carry Charcoal **$8.14/SF** (`502709287976836`), Clara Caviar **$33.70/SF** (`5529752505024388`) and Bone Soft floor **$6.75/SF** (`5006308915347332`), but **TX-specific Bone Ribbed panel quantity and rate `null`** (`candidates/B.md`, lines 7–10). |
| Material economics / quote completeness | **3** | **$1,320.83/unit** at historical rates includes **$290.83 niche** (≈22.0% of nominal total), with Bone Ribbed priced area missing and wet-niche release unsupported (`candidates/B.md`, lines 8–11). |
| Waste, wall/niche netting and box quantities | **2** | 89.8/44.3/8.63 SF already contain 15% waste, but **Ribbed must replace some Charcoal field** and niche displaces another portion; the net split, 24×48 cartons and 2×8 zellige order minimum are **`null`** (`candidates/B.md`, lines 15, 17, 21). |
| Chicago supply, historical lead and minimum | **2** | Same historic **Cortar 10–12 weeks, 300 SF import threshold** and uncertain pooling apply; **exact Clara lot/Chicago lead `null`**, and the 179.6-SF two-unit Charcoal base is below 300 SF if separate SKU minimum is enforced (`candidates/B.md`, line 34; `research/products/elm-cortar-charcoal-24x48-soft.md`). |
| Installed work, trim and freight | **1** | Relief/flat transitions, an unapproved wet niche, waterproofing, alignment/trim, floor transition and specialty labor remain unpriced, making the $1,320.83 estimate unsuitable for release (`candidates/B.md`, lines 8–10, 21, 30–34). |

**seat_score: 2.4 / 5.0** — arithmetic mean (4,3,2,2,1). **Confidence: low** (three direct historical rates, unknown wet-panel split, no current ETA/installed price).

**Extended material illustration:** Charcoal **89.8 × $8.14 = $730.97/unit**; Bone Soft **44.3 × $6.75 = $299.03/unit**; Clara Caviar **8.63 × $33.70 = $290.83/unit**. **Illustrative $1,320.83/unit; $2,641.66/two units**, **before deduction for niche/replaced field SF and addition/substitution for an unmeasured Bone Ribbed panel**, plus crates/carton rounding, trim, labor, freight/tax. The candidate packet quotes **$1,320.82**; arithmetic on its displayed per-line rounded rates gives **$1,320.83**, a **$0.01 rounding discrepancy**, not a confirmed price change. Neither full quantity split nor order total is complete. The 300 SF import term must be reconfirmed and cannot be presumed per SKU.

**top_fix:** Replace the **unapproved wet niche/relief scope with documented wet-rated, measurable products**, then obtain an itemized ELM re-quote splitting Charcoal, any permitted dry Bone Ribbed and niche SF with freight/box/installation costs.

**gate_flags:**
- **FAIL — CLARA_WET_NICHE:** Clara Caviar lacks manufacturer **Wet Areas** authorization yet is placed in a tub alcove niche (`candidates/B.md`, lines 9, 17, 25; `board/BOARD.md`, gate 1).
- **FAIL/PENDING — BONE_RIBBED_LOCATION:** Individual Bone Ribbed page lacks Wet Areas; proposed relief area/location `null`. **Any** placement on tub wet walls fails. Until designer locates it wholly dry with a measurable deduction, wet-wall approval cannot be cleared (`research/products/elm-cortar-bone-ribbed-24x48-relief.md`).
- **FAIL — BONE_SOFT_FLOOR_DCOF_EXACT_NULL:** Exact measured wet DCOF ≥0.42 for Cortar Bone **12×24 Soft** is **`null`** (manufacturer wet listing alone insufficient; `research/products/elm-cortar-bone-soft-12x24.md`).
- **BUDGET / INVENTORY UNTESTABLE:** No room budget; no verified SKU stock or dated delivery, but no demonstrated discontinued/no-US-distribution event. Historical minimum remains a purchasing hold.

