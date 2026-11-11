# PH-BATH3 — Round 001 — critic-cost (procurement, weight 0.20)

**Basis:** Two Penthouse copies (307A and 307B). Rates below are **tile only, per unit**, based on the 2026-09-03 ELM quotation carried in Smartsheet, reviewed 2026-11-06. The quoted 86.2 SF wall, 40.2 SF floor and 8.63 SF niche allowances already contain **15% waste**; do not add 15% again. Rates are not new purchase-order commitments. The wall run (9.67 LF × 7.75 ft) and 35 SF room floor come from `geometry.json`, with live model identity and dimensions unverified. No allocated room tile budget or approved upgrade percentage appears in `state/OWNER_FEEDBACK.md` (line 11), so the **125% budget gate cannot be evaluated or failed**.

## Candidate A — Tones Sandstone tub wall and niche / Cortar Bone floor

| Procurement criterion | 1–5 | Evidence-based reason |
|---|---:|---|
| Rate and quote lineage | 3 | Sandstone **$6.95/SF** is directly carried for the existing niche (Smartsheet **1589102831075204**), but extending it to **86.2 SF of wall** replaces quoted Opal (**4724833938636676**) and requires a revised field quote (`research/products/elm-tones-sandstone-2x20.md`, §§ Project quote). |
| Extended material economics | 4 | **$930.42/unit** on the three separate carried lines; matching wall/niche material avoids a different accent SKU, but the estimate remains provisional (`candidates/A.md`, lines 7–9). |
| Measured quantity / 15% waste | 2 | 9.67 LF × 7.75 ft × 1.15 ≈ **86.2 gross wall SF**; the additional **8.63 SF** niche allowance may overlap this field and must be netted once, with box rounding after field dimensions (`geometry.json`, `candidates/A.md`, lines 7–9). |
| Distribution, stock and lead | 3 | ELM currently lists Sandstone 2×20 glossy for Wet Areas and the Tones collection as **US-stocked/quick ship, 2–4 weeks**; no reserved Chicago lot, exact available boxes or dated delivery confirmation (<https://www.elmsurfaces.com/product/sandstone-tones>, <https://www.elmsurfaces.com/product-collection/tones>, checked 2026-11-06). |
| Trim, setting, labor and freight | 2 | Ceramic terminations, grout, niche returns, labor, taxes and freight have **no priced allowance**; penetrations and actual niche geometry remain unmeasured (`candidates/A.md`, lines 14–20). |

**Extended material check (15% waste already embedded):** Sandstone field **86.2 SF × $6.95 = $599.09**; Cortar Bone Soft floor **40.2 SF × $6.75 = $271.35** (row **2473034124951428**); Sandstone niche **8.63 SF × $6.95 = $59.98**. **Separate-line subtotal $930.42/unit; $1,860.84 for two units.** If all 8.63 SF niche area displaces already-counted wall field at the same rate, the alternative **non-overlapping** illustration is **$870.44/unit**; actual niche returns and quantities must decide which number is correct. Neither amount includes a fresh ELM order quote, trim, setting materials, labor, freight or tax.

**seat_score: 2.8 / 5.0** (unweighted mean of the five criteria above).

**top_fix:** Obtain one revised ELM two-unit Sandstone field/niche quotation from a measured, non-overlapping takeoff, including box rounding, on-hand quantities, trim and freight.

**gate_flags:**
- **FAIL — FLOOR_DCOF_UNKNOWN:** No published wet DCOF ≥ 0.42 for Cortar Bone **12×24 Soft** floor has been supplied; the board treats unknown bath-floor DCOF as a hard failure (`candidates/A.md`, line 20; `board/BOARD.md`, gate 2). Sandstone is wall/niche-only, with an individual manufacturer Wet Areas listing.
- **NOT A FAIL — BUDGET_UNTESTABLE:** No carried room budget; do not compare $930.42 to an invented allowance or trigger the 125% rule.

**confidence: medium** — same-product historical niche price and public manufacturer series information are evidenced; room wall substitution, live stock and niche quantities are not.

## Candidate B — Tones Opal tub wall / Sandstone niche / Cortar Bone floor

| Procurement criterion | 1–5 | Evidence-based reason |
|---|---:|---|
| Rate and quote lineage | 4 | Direct carried room lines: Opal wall **$6.95/SF**, row **4724833938636676**; Cortar floor **$6.75/SF**, row **2473034124951428**; Sandstone niche **$6.95/SF**, row **1589102831075204** (`candidates/B.md`, lines 5–10). |
| Extended material economics | 4 | **$930.42/unit** nominal tile-only subtotal, identical to A at the carried prices, but still subject to niche double-count reconciliation (`candidates/B.md`, line 15). |
| Measured quantity / 15% waste | 2 | Existing 86.2/40.2/8.63 SF contain 15% waste, yet provisional niche backing is said to displace the Opal field; location and cut sizes are absent (`geometry.json`, `candidates/B.md`, lines 9–15). |
| Distribution, stock and lead | 3 | Tones collection advertises **US-stocked/quick ship, 2–4 weeks** but no verified Opal/Sandstone lot count for the project; the dated ELM quote is not a delivery promise (<https://www.elmsurfaces.com/product-collection/tones>, checked 2026-11-06). |
| Trim, setting, labor and freight | 2 | Mock-up, color-matched edges, niche waterproofing/returns, tile-setting and installation have no dollar allowances (`candidates/B.md`, lines 13–19). |

**Extended material check (15% waste included):** Opal field **86.2 × $6.95 = $599.09/unit**; Cortar Bone floor **40.2 × $6.75 = $271.35/unit**; Sandstone niche **8.63 × $6.95 = $59.98/unit**. **Nominal total $930.42/unit, $1,860.84 for two units.** Where the niche is already in the field gross area, deduct the matching 8.63 SF of Opal before adding Sandstone; at identical rates the resulting *illustrative* total is **$870.44/unit**. Provisional backing/returns may change that reconciliation.

**seat_score: 3.0 / 5.0** (unweighted mean of the five criteria above).

**top_fix:** Obtain a measured and netted ELM two-unit order schedule confirming Opal field quantity, Sandstone niche quantity, 15%-waste box counts, current stock and all accessory/installation costs.

**gate_flags:**
- **FAIL — OPAL_WET_WALL_DOCUMENTATION:** The 2026-10-01 product-specific audit records **no Opal-specific Wet Areas listing** (`candidates/B.md`, line 19). ELM's Tones **collection** now lists Wet Areas, but the individual Opal listing could not be verified; the strict product-specific wet-wall gate remains failed pending an individual manufacturer document or written approval (<https://www.elmsurfaces.com/product-collection/tones>).
- **FAIL — FLOOR_DCOF_UNKNOWN:** Cortar Bone 12×24 Soft bath-floor published wet DCOF ≥ 0.42 remains absent (`candidates/B.md`, lines 9 and 19; `board/BOARD.md`, gate 2).
- **NOT A FAIL — BUDGET_UNTESTABLE:** No carried room budget or 125% threshold in dollars exists.

**confidence: medium** — direct carried room rates are clear; manufacturer wet-wall approval for exact Opal color, lot/lead, takeoff and indirect costs are unresolved.
