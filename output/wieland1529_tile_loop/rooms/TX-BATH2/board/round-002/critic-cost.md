# TX-BATH2 — Round 002 — critic-cost (procurement; seat weight 0.20)

**Review basis (2026-11-06).** Blind letters only. Two Triplex rooms, drawn room **38 SF net** and wet tub-wall run **10.41 LF × 7.75 ft**; values are prior handoff/drawing estimates, **not measured in the provisionally authorized 1527-named Revit model** (`geometry.json`). Quantities **92.8 SF wall, 43.7 SF floor and 8.63 SF niche per unit already include 15% waste**; do not add 15% again. Project rates are from ELM's 2026-09-03 quotation carried in Smartsheet; Daltile's price below is public retail only. Actual Chicago product quantities, supplier freight/tax, grout, waterproofing, trim, labor, carton minimums and delivery promises are `null`. The owner has **not allocated a room tile budget** (`state/OWNER_FEEDBACK.md`, line 11), so **no >125% budget hard-gate verdict** is possible.

## Candidate B — Tones Copper/Sandstone, Daltile Portfolio Cream PF07 floor

| Procurement criterion (1–5) | Score | Evidence / one-line reason |
|---|---:|---|
| Historical rate and bid lineage | **3** | ELM **Copper 92.8 SF × $6.95** (Smartsheet `3035984078372740`) and **Sandstone 8.63 SF × $6.95** (`8344502272130948`) are actual project quote references; Daltile **PF07 $6.27/SF, $106.72/carton** is a **public retailer listing**, with project bid **`null`** ([Get Floors Online](https://www.getfloorsonline.com/flooring/tile-stone/daltile/portfolio-12-x-24-cream-11.625in-x-23.375in-17.02sqft-pf07-rct1224mt); `candidates/B.md`, lines 7–9). |
| Material-cost competitiveness | **3** | **$1,025.10/unit** at **three full PF07 cartons** versus quoted Clay reference candidate C **$999.92/unit** (about **+$25.18/unit**); neither includes landed/installed scope (`candidates/B.md`, line 16). |
| Waste, niche reconciliation and box counts | **3** | Prior 38 SF bath floor became **43.7 SF with 15% waste**, yet three **17.02 SF** cartons buy **51.06 SF**; the **8.63 SF niche may already be in the Copper field**, so both quoted gross lines require net reconciliation (`geometry.json`; `candidates/B.md`, lines 8–9). |
| Chicago stock, minimums and lead | **3** | Daltile's PF07 product remains listed and Chicago branches exist, while actual **PF07 lot/stock/lead `null`**; ELM Tones' **US-stocked / 2–4 week** collection claim is not a project delivery commitment ([Daltile PF07](https://www.daltile.com/products/concrete-look/portfolio/cream); [Chicago locator](https://locations.daltile.com/il/chicago/); `research/products/elm-tones-sandstone-2x20.md`). |
| Installation, trim and final landed cost | **2** | Wall terminations, niche returns, bullnose/base/threshold, grout, membrane, mortar, labor and freight/tax have no unit-price or total allowances (`candidates/B.md`, lines 10, 14–16). |

**seat_score: 2.8 / 5.0** — arithmetic mean (3,3,3,3,2). **Confidence: medium** (ELM historical rates and public PF07 carton price sourced; actual project quote and stock not).

**Extended material calculation (two unit copies):** Copper **$644.96/unit**; Sandstone niche **8.63 × $6.95 = $59.98/unit**; PF07 area-only **43.7 × $6.27 = $274.00/unit** but **3 cartons × $106.72 = $320.16/unit**, covering **51.06 SF**. **Illustrative $1,025.10/unit; $2,050.20/two units** using separately rounded carton purchases. The nominal 15% waste is contained in the earlier SF allowances; the additional **7.36 SF/unit** above the 43.7-SF floor schedule is carton rounding, not a second waste factor. If niche gross area replaces field gross area entirely, reduce the duplicated Copper field at its quoted rate, then recalculate exact boxes; do not commit a savings until dimensions and backing/returns are measured. Tax, freight, threshold, waterproofing and labor are excluded.

**top_fix:** Obtain a **supplier-confirmed, product-specific PF07 floor package** for both units that includes the exact measured wet DCOF report, landed Chicago carton pricing/availability and trim, after reconciling niche and floor takeoff.

**gate_flags:**
- **FAIL — FLOOR_DCOF_EXACT_NULL:** Daltile's PF07 page says *Wet & Level Interior Floor: Yes* and *Target DCOF Wet ≥0.42*. This is a **target/application standard**, **not an exact measured ANSI A326.3/AcuTest result for PF07 12×24 Matte**. Published measured exact-SKU value **`null`**, hence strict board gate fails ([Daltile PF07](https://www.daltile.com/products/concrete-look/portfolio/cream), `research/products/daltile-portfolio-cream-pf07-12x24-matte.md`, lines 5–9; `board/BOARD.md`, gate 2).
- **WET WALLS REPORTED PASS:** Copper and Sandstone are reported Wet Areas-rated for wall/niche use only (`research/products/elm-tones-copper-2x20.md`; `elm-tones-sandstone-2x20.md`).
- **HOLD — GEOMETRY/QUOTE/STOCK:** 1529 room dimensions and niche displacement unverified; retailer PF07 code **PF07 RCT1224MT** needs supplier order-code confirmation. Chicago quantities/lead `null`, so **no documented discontinued/no-US-distribution availability fail**.
- **BUDGET NOT GATED:** Owner room budget `null`; the $1,025.10 illustration is **not** a test of the >125% rule. Sink/basin remains unselected (`plumbing.json`, `unselected_fixtures`), with no fixture selection inferred.

## Candidate C — Tones Copper/Sandstone, ELM Cortar Clay Soft floor

| Procurement criterion (1–5) | Score | Evidence / one-line reason |
|---|---:|---|
| Historical rate and bid lineage | **4** | All three surfaces directly match **2026-09-03 ELM same-project quoted rates**: Copper `3035984078372740` **$6.95/SF**, Sandstone `8344502272130948` **$6.95/SF**, Clay Soft `7539583705743236` **$6.75/SF** (`candidates/C.md`, lines 7–9). |
| Material-cost competitiveness | **4** | **$999.92/unit** quoted-rate illustration is approximately **$25.18/unit below B's public-retail three-carton floor scenario**, but still excludes all accessories/installation (`candidates/C.md`, lines 8 and 18). |
| Waste, niche reconciliation and box counts | **3** | **92.8/43.7/8.63 SF** include 15% waste, but niche overlaps Copper field until measured and **ELM carton capacities / attic-stock rounding are `null`** (`candidates/C.md`, lines 7–10, 14–18). |
| Chicago stock, minimums and lead | **2** | Tones historic US-stock/quick-ship note does not reserve project supply; **Cortar Clay Soft Chicago availability and delivery `null`** and Cortar historical overseas import terms need supplier confirmation (`candidates/C.md`, lines 22, 31; `research/products/elm-cortar-bone-soft-12x24.md`, historical Cortar-group terms only). |
| Installation, trim and final landed cost | **2** | No supplier quote for matching edge profiles, base, grout, setting mortar, waterproof niche returns, thresholds, labor, tax or freight (`candidates/C.md`, lines 29–31). |

**seat_score: 3.0 / 5.0** — arithmetic mean (4,4,3,2,2). **Confidence: medium** (direct historical project quote; no current delivery/installed cost).

**Extended material calculation:** Copper **92.8 × $6.95 = $644.96/unit**; Cortar Clay **43.7 × $6.75 = $294.98/unit**; Sandstone niche **8.63 × $6.95 = $59.98/unit**. **$999.92/unit using individually rounded line extensions; $1,999.84/two units**, prior to niche/field netting, final carton procurement and indirect costs. The original 15% schedule waste is already inside all three quantities. The same-price Copper/Sandstone niche may eliminate duplicate field SF, but recess returns and actual geometry govern the adjustment.

**top_fix:** Secure a **manufacturer-certified, wet-DCOF-qualified floor SKU** for the scheduled Clay scope and reprice the reconciled two-unit tile/trim package at current Chicago availability.

**gate_flags:**
- **FAIL — FLOOR_DCOF_EXACT_NULL:** Cortar **Clay 12×24 Soft** has **no published exact wet DCOF ≥0.42** in supplied maker evidence; being called a floor finish or Soft is insufficient (`candidates/C.md`, lines 8, 16, 27; `board/BOARD.md`, gate 2).
- **WET WALLS REPORTED PASS:** Copper/Sandstone wall/niche Wet Areas listings reported in product evidence; no floor DCOF can be transferred from them.
- **HOLD — INVENTORY/GEOMETRY:** Exact Chicago Clay stock, case rounding, measured niche and 1529 room dimensions missing; missing inventory evidence alone is **not a documented discontinued/no-US-distribution hard fail**.
- **BUDGET NOT GATED:** Room-specific budget and owner upgrade note `null`; sink/basin is unselected and remains so.

