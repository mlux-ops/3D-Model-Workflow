# R039 independent COST critique — TX-POWDER2 (strict blind)

**Scope:** Two physical copies, 009A and 009B; ONE **DRY** W1 vanity wall per copy, drawing-derived 3.806 ft wide x 9.25 ft tall; existing WOOD floors. The original **40.5 gross SF/copy** already includes **15% waste ONCE** (2 x 40.5 = **81.0 gross SF** total). Hansgrohe Tecturis E **73072341** is a **DECK-mounted** faucet in **Brushed Black Chrome**, and the basin remains **UNSELECTED**. Mirror, basin interfaces and field wall openings are unverified. No floor/pan/niche/ceiling tile. Sources: [geometry](../../geometry.json), [plumbing](../../plumbing.json), [neutral candidate A](candidates/A.md), [neutral candidate B](candidates/B.md), [2026-09-04 same-job trade quote](../../../../inputs/TRADE_QUOTES.md) sections (a), (b), (c), thread `1a068e80c92c255f`, message `1a06e29c0b2333f4`. All costs are **tile material only**, before sales tax, freight, trims, setting materials, labor, and the unknown room budget (FILL IN).

## Candidate A — Elm Vera Forma Indigo Edge glossy relief 6 x 6

| COST criterion | Integer rating / 5 | Independent, source-specific reason |
|---|---:|---|
| C1. Price-source reliability | **5** | **$8.20/SF** is a 2026-09-04 actual **1529 Wieland same-job Elm trade quotation** for Vera Forma **Indigo Edge 6 x 6** (Elm thread above), not a generic internet price. Quote states **7.34 SF/box**, FOB TN, and **8.6 mm**. Current price validity is unconfirmed. See `inputs/TRADE_QUOTES.md` §(b) Elm row. |
| C2. Material-rate and area cost | **4** | **40.5 x $8.20 = $332.10/copy; 81.0 x $8.20 = $664.20/two copies**, already including the source's single 15% gross-area waste. Rate is below the owner's approximately $10/SF project average aspiration (`inputs/TRADE_QUOTES.md` §(a)), but the budget specifically carried for this powder room is unknown. |
| C3. Carton efficiency | **4** | Maker/quote pack **7.34 SF/box** on **81.0 gross SF** yields **ceil(81/7.34)=12 boxes = 88.08 SF**, approximately **$722.26** at quoted $8.20/SF; separate ordering requires **6 boxes per copy**, also **12 total**. Carton excess is **7.08 SF**, approximately **$58.06** over the original area-rate comparison; no second waste percentage is applied. Source: Elm quote and neutral candidate A. |
| C4. Distribution and schedule | **3** | Active [Elm Vera Forma collection](https://www.elmsurfaces.com/product-collection/vera-forma) identifies Indigo Edge in **6 x 6** format, `Walls`, glossy, 8.6 mm, **Quick Ship / US-Stocked**, with a **2–4-week** collection lead; [exact Indigo Edge maker page](https://www.elmsurfaces.com/product/indigo-edge-vera-forma) corroborates the format and wall permission. **No exact Chicago matching lot, current stock depth, committed shipping date or delivered cost** confirmed; quote FOB TN. |
| C5. Total installed-cost exposure | **2** | Indigo Edge has a **3D/relief face** per exact maker page; mirror reveal, tile edge build-up, small-unit grout layout and deck-mounted faucet/basin interface could require extra trim/detail labor beyond material SF. The **basin is unselected** (`plumbing.json`), openings and wall layers unmeasured (`geometry.json`), and installed labor, thinset, trim, tax, freight and room allowance are unstated. No justified installed-cost estimate is available. |

**Original integer ratings:** `5, 4, 4, 3, 2` (sum **18**, n=5). **COST mean = 3.6 / 5** (18/5=3.6, one-decimal HALF_UP).

**top_fix:** Secure one **delivered 12-box Indigo Edge quote** with batch availability and a priced mirror/edge and relief-tile installation detail after basin selection.

**gate_flags:** **No confirmed hard-gate failure** for the selected DRY wall; maker lists `Walls` and US distribution. `BUDGET_UNTESTABLE` (room allowance FILL IN), `MATCHED_LOT_UNVERIFIED`, `BASIN_MIRROR_EDGE_UNVERIFIED`. Any restricted owner veto is for the prime's gate audit. Shower-floor wet DCOF and pan/ceiling ratings are inapplicable.

**confidence:** **medium** — direct same-job unit rate and maker wall application, with outstanding lot, installed labor, budget and basin information.

## Candidate B — Elm Tones Sandstone glossy ceramic 2 x 20

| COST criterion | Integer rating / 5 | Independent, source-specific reason |
|---|---:|---|
| C1. Price-source reliability | **5** | **$6.95/SF** is the **2026-09-04 1529 Wieland Elm trade quote** for Tones 2 x 20 glossy, listing **Sandstone among the five colors** at one combined rate and **6.50 SF/box** (Elm thread above; `inputs/TRADE_QUOTES.md` §(b)). Individual Sandstone order code and a specific batch were not quoted. |
| C2. Material-rate and area cost | **5** | **40.5 x $6.95 = $281.48/copy; 81.0 x $6.95 = $562.95/two copies**, with the 15% gross source allowance included once. This is **$101.25 less over two copies** than candidate A's same-job **$664.20** area basis and below the owner's approximate $10/SF project-wide aspiration; neither fact supplies a room-specific budget. |
| C3. Carton and attic-stock flexibility | **3** | The Elm quote says **6.50 SF/box**. **Joint order for 81.0 gross SF:** **ceil(81/6.5)=13 boxes = 84.5 SF**, material **$587.28** (half-up cents). **If purchased as independent 40.5-SF batches:** **7 boxes/copy = 14 boxes / 91 SF**, **$632.45**. The additional carton count, matching lot and attic-stock requirement need a confirmed ordering strategy; no second waste factor is added. |
| C4. Distribution and lead | **4** | [Elm Tones collection](https://www.elmsurfaces.com/product-collection/tones) and [exact Sandstone maker page](https://www.elmsurfaces.com/product/sandstone-tones) show current **2 x 20, glossy, wall / wet area** catalog listings, **Quick Ship / US-Stocked** and a **2–4-week** collection lead; the same-job quote specifies FOB options **FL, IL, NJ or TX**. Presence of an Illinois FOB option is useful distribution evidence, **not confirmed stock or lead for this Sandstone lot**. |
| C5. Installed-scope predictability | **3** | The standard **8.5-mm** glossy wall tile on one dry vanity feature wall avoids candidate A's specifically modeled 3D relief, but 2 x 20 tile orientation, mitred/trimmed terminations, mirror cuts and grout layout are not fully priced. The **Brushed Black Chrome deck-mounted faucet** is specified; the **basin remains UNSELECTED**, so edge and countertop installation costs cannot be finalized. Sources: [exact maker page](https://www.elmsurfaces.com/product/sandstone-tones), `plumbing.json`, `geometry.json`. |

**Original integer ratings:** `5, 5, 3, 4, 3` (sum **20**, n=5). **COST mean = 4.0 / 5** (20/5=4.0, one-decimal HALF_UP).

**top_fix:** Confirm the **exact Sandstone ordering code and matching lot**, then price one delivered **13-box pooled two-copy order** (or explain the necessary 14-box separated order), including finish trims after the basin decision.

**gate_flags:** **No confirmed hard-gate failure**; maker lists current US distribution and DRY wall permission. `BUDGET_UNTESTABLE` (room allowance FILL IN), `SANDSTONE_CODE_LOT_UNVERIFIED`, `BASIN_MIRROR_EDGE_UNVERIFIED`; any owner veto belongs to the prime's restricted-source gate audit. Wet-floor DCOF is inapplicable to retained WOOD flooring.

**confidence:** **medium** — precise same-job rate and packing with active maker listing; Chicago batch, landed total, exact order code, installed costs and basin are unresolved.

**Board scope note:** These are independent COST evaluations of neutral A/B. No previous roles/scores, outcome mapping, other seat critiques or weighted aggregate were inspected or calculated.
