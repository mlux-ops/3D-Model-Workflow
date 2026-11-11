# TX-BATH3 — Round 002 — critic-cost (procurement; seat weight 0.20)

**Review basis (2026-11-06).** Blind letters only. Two Triplex rooms, **37 SF prior estimated level floor**, wall run **10.30 LF × 7.75 ft tub-based**, originally **91.8 SF gross Emerald**, **42.5 SF gross 12×24 floor**, **4.89 SF gross Sandstone niche**, each **already including 15% waste** (`geometry.json`). **Major scope conflict:** `geometry.json` says *tub alcove*, while `plumbing.json` identifies a **walk-in shower and Brizo BT062415-BNX 4-in tile-in point drain** (row `8488981737635716`). **Shower pan geometry, SF, waste, curb/membrane scope and quote are `null`; original wall-tile height is not validly established for the shower.** Model identity is provisionally 1527-named; no 1529 geometry verified. Owner room tile budget/allocation `null`; **cannot apply >125% budget threshold**.

## Candidate A — Tones Emerald/Sandstone, ELM Cortar Grey Soft floor

| Procurement criterion (1–5) | Score | Evidence / one-line reason |
|---|---:|---|
| Historical rates and bid lineage | **4** | Emerald **91.8 SF × $6.95** (ELM row `6413683798900612`), Sandstone **4.89 SF × $6.95** (`1026152877653892`), Cortar Grey Soft **42.5 SF × $6.75** (`4161883985215364`) trace to 2026-09-03 project quote (`candidates/A.md`, lines 7–9). |
| Extended material cost completeness | **2** | **$958.88/unit** nominal quoted-rate tile allowance omits any **actual walk-in shower pan, remeasured full-height walls or waterproofing allowance** (`candidates/A.md`, lines 10, 18, 29). |
| 15% waste, takeoff and cartons | **1** | All carried areas already have 15% waste, but **pan SF `null`**, the floor/pan split unknown, wall start height based on presumed tub and ELM cartons/attic stock not defined (`geometry.json`; `candidates/A.md`, lines 8–10). |
| Chicago availability and lead | **2** | Tones historically quick ship/US-stocked, while current Emerald/Sandstone lots, Cortar Grey inventory, and Chicago arrival dates **`null`**; Cortar-group import-lead terms are historical only (`research/products/elm-tones-emerald-2x20.md`; `candidates/A.md`, line 31). |
| Trim, waterproofing and labor | **1** | An actual shower requires **pan tile, slope/point-drain membrane, curb/threshold and wet-wall terminations**, none scoped or priced; grout, edge, freight/tax and labor also `null` (`plumbing.json`, Brizo drain; `candidates/A.md`, lines 29–31). |

**seat_score: 2.0 / 5.0** — arithmetic mean (4,2,1,2,1). **Confidence: low** (historic rate arithmetic supported; actual wet-room procurement scope unknown).

**Extended material illustration, only if old tub takeoff is provisionally used:** Emerald **91.8 × $6.95 = $638.01/unit**; niche Sandstone **4.89 × $6.95 = $33.99/unit**; Cortar Grey Soft **42.5 × $6.75 = $286.88/unit**. **Approximately $958.88/unit, $1,917.76 for two units** when rounded line extensions are summed. **Actual shower project total = `null`** because pan, wall height, scope, cartons and trims cannot be established. Niche must replace field area; a stand-alone added 4.89 SF may double-count. No additional 15% factor.

**top_fix:** Reconcile the walk-in shower against verified 1529 geometry and produce **one revised two-unit pan/wall/floor takeoff with a qualifying specified pan SKU and full supplier/installer quote**.

**gate_flags:**
- **FAIL — BATH_FLOOR_DCOF_EXACT_NULL:** Cortar Grey **12×24 Soft** has no documented product-specific measured wet DCOF ≥0.42 (`candidates/A.md`, lines 8, 16, 27; `board/BOARD.md`, gate 2).
- **FAIL/PENDING IF WALK-IN — SHOWER_PAN_UNSPECIFIED:** Plumbing explicitly requires a point-drain shower; this packet specifies **no wet-rated, DCOF-documented pan surface**, and the 12×24 level-floor tile cannot be assumed suitable for four-way fall. Source discrepancy prevents procurement approval; pan SF/price `null` (`plumbing.json`, drain row `8488981737635716`; `candidates/A.md`, lines 10 and 29).
- **WET WALLS REPORTED PASS:** Emerald and Sandstone Wet Areas wall applications are recorded (`research/products/elm-tones-emerald-2x20.md`; `elm-tones-sandstone-2x20.md`); does not fix floor/pan.
- **BUDGET / AVAILABILITY UNTESTABLE:** No room cost cap; current stock/delivery missing is a supply hold, **not** proof of discontinuation or unavailable US distribution.

## Candidate B — Tones Emerald/Sandstone, Daltile PF05 12×24 plus conditional 2×2 pan

| Procurement criterion (1–5) | Score | Evidence / one-line reason |
|---|---:|---|
| Historical rates and bid lineage | **2** | ELM wet walls/niche have direct project quotes; PF05 **$6.27/SF and $106.72/carton** is third-party retail **without a project bid**, and PF05 2×2 mosaic **rate/quote `null`** ([retailer](https://www.getfloorsonline.com/flooring/tile-stone/daltile/portfolio-12-x-24-ash-grey-11.625in-x-23.375in-17.02sqft-pf05-rct1224rmt); `candidates/B.md`, lines 7–10). |
| Extended material cost completeness | **2** | At **three PF05 cartons**, visible allowance is **$992.16/unit + shower-pan cost `null`**, with true total `null` until pan and wall scope are settled (`candidates/B.md`, line 17). |
| 15% waste, takeoff and cartons | **2** | Provisional **42.5 SF gross** main floor maps to **3 cartons / 51.06 SF per unit**; two pooled units theoretically need **5 cartons / 85.10 SF for 85.0 gross**, but pan-vs-level split and four-way slope make this **non-orderable** (`research/products/daltile-portfolio-ash-grey-pf05-12x24-matte.md`; `...pf05-2x2-matte.md`). |
| Chicago availability and lead | **3** | Daltile actively lists PF05 floor and mosaic plus Chicago dealer network, but neither **PF05 size** has verified Chicago stock, date, case minimum or lead; Tones actual project lots also unknown ([Daltile PF05](https://www.daltile.com/products/concrete-look/portfolio/ash-grey); [Chicago locations](https://locations.daltile.com/il/chicago/)). |
| Trim, waterproofing and labor | **2** | Proposes a distinct 2×2 point-drain pan system, but pan tile rate, bonding/waterproofing, pitch, drain frame, curb, thresholds and trade labor are all **unpriced** (`candidates/B.md`, lines 9, 15–17). |

**seat_score: 2.2 / 5.0** — arithmetic mean (2,2,2,3,2). **Confidence: low** (more explicit missing shower scope, but no actual pan quantity/price).

**Extended material illustration:** Emerald **$638.01/unit** + Sandstone **$33.99/unit** + public PF05 **3 × $106.72 = $320.16/unit** = **$992.16/unit for old 42.5-SF gross *main-floor allowance only***. **Two units, purchasing 3 cartons each:** **$1,984.32** preliminary, still excluding the **2×2 pan (`null`)**. Purely conditional shared-lot pooling of the same unchanged 42.5 SF per unit would yield **5 × 17.02 = 85.10 SF for two gross 42.5-SF allowances**, at **$533.60** instead of $640.32 for six cartons; only **0.10 SF** remains beyond scheduled 15% waste, and **the pan/field split is unresolved**, so **do not adopt five cartons as a buying quantity**. Public internet retail is not approved landed Chicago pricing; mosaic rate, case size, import/lead, specialty drain detailing and all other installation costs `null`. **Complete shower total = `null`.**

**top_fix:** Obtain **one dimensioned shower floor/pan split and two-unit Daltile PF05 project quotation** covering certified exact 12×24 and 2×2 wet DCOF values, pan quantities/boxes, stock and complete drain/waterproofing trims.

**gate_flags:**
- **FAIL — PF05_FIELD_DCOF_EXACT_NULL:** Manufacturer labels PF05 as *Wet & Level Interior Floor suitable* with **Target DCOF Wet ≥0.42**. That is a **target, not the tested wet AcuTest value for PF05 12×24 Matte**. Exact measured figure/certificate `null`; fail strict board gate ([Daltile Ash Grey](https://www.daltile.com/products/concrete-look/portfolio/ash-grey); `research/products/daltile-portfolio-ash-grey-pf05-12x24-matte.md`).
- **FAIL — PF05_MOSAIC_DCOF_EXACT_NULL:** Maker lists residential shower floors and **Target DCOF Wet ≥0.42**, with **2×2 Matte** included among formats, but published **exact measured wet DCOF for the proposed 2×2** `null`; strict pan-floor gate also fails (`research/products/daltile-portfolio-ash-grey-pf05-2x2-matte.md`). An aggregate shower-floor checkmark is not an individual mosaic test report.
- **HOLD — SHOWER_AREA_NULL:** Tub/walk-in contradiction remains unresolved; pan area, drain position/slope and revised full-height wet-wall quantity have no verified source (`geometry.json`, `plumbing.json`).
- **WET WALLS REPORTED PASS; BUDGET UNTESTABLE:** Emerald/Sandstone wall ratings reported Wet Areas; no allocated room cap; missing inventory alone is not a proven availability hard-gate failure.

