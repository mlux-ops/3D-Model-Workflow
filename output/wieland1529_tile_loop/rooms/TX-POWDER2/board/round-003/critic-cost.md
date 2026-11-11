# TX-POWDER2 — Round 003 — critic-cost (procurement seat; weight 0.20)

**Blind review, 2026-11-06.** Two Triplex powder rooms (009A/B). Drawn dry vanity feature wall **3.806 × 9.25 = 35.2055 SF net** and original **40.5 SF gross/unit already including 15% waste** (`geometry.json`). Existing floor is **WOOD**, with no tile floor/wet enclosure; therefore shower wet-wall and bath-floor DCOF gates are **N/A**. The exact ELM dated **2026-09-03** Indigo Edge 6×6 Relief line is Smartsheet **`7258108729032580`**, **$8.20/SF**, historical **30 pieces / 7.34 SF per carton**, FOB TN, with no current Chicago lot confirmation (`research/products/elm-vera-forma-indigo-edge-6x6.md`). `plumbing.json` lists Hansgrohe Tecturis E **73072341 Brushed Black Chrome** as **DECK-MOUNTED, SINGLE-HOLE** and sink/basin **UNSELECTED** (row `5006187243962244`). No fabricated wall-mount rough or sink selection is costed. No allocated room budget or owner-approved upgrade percent appears in `state/OWNER_FEEDBACK.md`.

## Candidate A — Indigo Edge relief with a provisional smooth mirror/backsplash zone

| Procurement criterion | Score (1–5) | Specific evidence and one-line reason |
|---|---:|---|
| **Historical quote and component price traceability** | **4** | Full 40.5-SF Indigo Edge source at **$8.20/SF** is a directly quoted TX powder row `7258108729032580`; proposed **smooth sealed non-tile panel** has **no selected product/area/rate or installed quote (`null`)** (`candidates/A.md`, lines 9–13). |
| **Final material subtotal completeness** | **1** | **$332.10/unit** is only a **whole-relief wall reference**; proposed partial relief replacement could offset that tile and add unknown panel/profile/finish cost, so **final hybrid material total `null`** (`candidates/A.md`, lines 9–10). |
| **Net area, waste and case count** | **2** | Prior **40.5 SF already includes 15% waste**, 6 × 7.34-SF Indigo cartons would cover **44.04 SF** if entire field remained, but smooth landing SF, relief deduction, trim lengths and potential carton savings are unknown (`geometry.json`, `candidates/A.md`, lines 9–15). |
| **Current US supply, Chicago lead and minimums** | **3** | Individual Indigo Edge remains manufacturer-listed for **Walls** and Vera Forma collection advertises **US-stocked/quick ship/2–4 weeks** generally, while exact Chicago Indigo lot and panel supplier/lead/FOB-TN freight are **`null`** ([ELM Indigo Edge](https://www.elmsurfaces.com/product/indigo-edge-vera-forma); [Vera Forma](https://www.elmsurfaces.com/product-collection/vera-forma)). |
| **Installed specialty detail and trade cost** | **2** | An engineered smooth backsplash/mirror mounting substrate within relief needs panel/finish, backing/anchors, multiple transition profiles, grout and installer rates, with basin still unselected; **no costed assembly** exists (`candidates/A.md`, lines 10, 15; `plumbing.json`). |

**seat_score: 2.4 / 5.0** (mean 4,1,2,3,2). **confidence: low** on hybrid total, medium on existing Indigo quote.

**Material quantity check:** Existing complete Indigo wall **40.5 × $8.20 = $332.10/unit** (**$664.20/two units**) at the historical *area rate*. Full-wall case example **ceil(40.5 / 7.34) = 6 cartons/unit**, **44.04 SF/unit** and **$361.13/unit** if the same $8.20 rate could be applied to full-carton purchase; actual carton billing/stock are unconfirmed. The proposed **smooth zone area = `null`**, so **net Indigo gross area after subtraction = `null`**, **Indigo carton count for this hybrid = `null`** and **smooth panel/backing installed price = `null`**. **No defensible final Candidate A total** or proven savings exist. Keep original 15% waste intact; never add a second full 40.5-SF panel area on top of tile.

**top_fix:** Dimension the **flush backsplash/mirror landing after the owner selects the basin**, then obtain a single installed hybrid quote showing Indigo deduction, smooth backing/edge assembly, case rounding and Chicago availability.

**gate_flags:**
- **NO WET-WALL/FLOOR DCOF HARD FAIL:** [Indigo Edge](https://www.elmsurfaces.com/product/indigo-edge-vera-forma) is listed for Walls and is proposed **only in dry powder**; **wood floor** remains, so wet-floor DCOF N/A (`geometry.json`; `candidates/A.md`, lines 5–11).
- **HOLD — UNSELECTED BASIN/INSERT:** Sink selection `null`; mirror/backsplash panel dimensions and product `null`. Tecturis E **73072341 is deck-mounted**, so no wall-faucet bores or materials may be assumed (`plumbing.json`, row `6413562127515524` and unselected row `5006187243962244`).
- **STOCK/ROOM BUDGET UNKNOWN, NOT HARD-FAILED:** No established 125% denominator; public live collection listing and general US stocking do not equal Chicago on-hand proof but do not prove discontinuation.

## Candidate B — full-height Indigo Edge relief dry feature

| Procurement criterion | Score (1–5) | Specific evidence and one-line reason |
|---|---:|---|
| **Historical quote and component price traceability** | **4** | `candidates/B.md` line 7 matches **ELM TX room row `7258108729032580`**, quoted **40.5 SF gross × $8.20/SF** for Indigo 6×6 relief on 2026-09-03. |
| **Material subtotal completeness** | **4** | Entire intended wall has a priceable historical material-rate allowance **$332.10/unit**; setting and trim remain excluded but there is no additional unpriced smooth-panel SKU (`candidates/B.md`, lines 5–8). |
| **Net area, waste and case count** | **3** | **35.2055 SF net × 1.15 = 40.4863 ≈ 40.5 SF gross**, needing **6 × 7.34-SF cartons** if purchased by full case per unit; wall openings and attic-stock policy remain unverified (`geometry.json`; `research/products/elm-vera-forma-indigo-edge-6x6.md`). |
| **Current US supply, Chicago lead and minimums** | **3** | Vera Forma current collection advertises **2–4 weeks / US-stocked/quick ship** and Indigo Edge remains listed; actual lot, Chicago distribution quantity, ETA and FOB Tennessee freight **`null`** ([Vera Forma](https://www.elmsurfaces.com/product-collection/vera-forma); `candidates/B.md`, line 12). |
| **Installed specialty detail and trade cost** | **2** | Full-height 6×6 textured relief needs grout, edge, base above wood floor and mirror anchors; basin remains unselected and **no installer, trim, freight or sales tax allowance** has been bid (`candidates/B.md`, lines 7, 13, 17; `plumbing.json`). |

**seat_score: 3.2 / 5.0** (mean 4,4,3,3,2). **confidence: medium** for tile-rate economics and historic case data; low for installed price/site stock.

**Tile-only check:** **40.5 SF × $8.20 = $332.10/unit** historical gross including 15% waste; **$664.20/two units** at area rate. **ceil(40.5 / 7.34) = 6 cartons/unit**, **44.04 SF/unit**; at the *same unconfirmed per-SF rate*, carton-rounded material would be **$361.13/unit** or **$722.26/two units**. Exact Indigo case billing, shared-lot pooling, trim quantities and unit-installed rate are `null`. Do not treat the whole-wall quote as an approved contract amount.

**top_fix:** Finalize a **dimensioned full-height Indigo tile grid around the selected basin/mirror**, then obtain a vendor-supported case-rounded and trim/installer quote with confirmed Chicago lead and the deck-mounted Tecturis E landing.

**gate_flags:**
- **NO WET-WALL/FLOOR DCOF HARD FAIL:** Dry decorative wall product, wood floor; shower wet listing and 0.42 floor DCOF requirements do not apply. Manufacturer [Indigo Edge](https://www.elmsurfaces.com/product/indigo-edge-vera-forma) lists Walls, which matches proposed use.
- **HOLD — OWNER BASIN/DETAILS:** Basin remains **UNSELECTED**; Brushed Black Chrome **Hansgrohe 73072341** is **DECK-MOUNTED single-hole**, so a wall-faucet cut/rough should not appear on the tile ordering list (`plumbing.json`; `candidates/B.md`, line 17).
- **NO EVIDENCED AVAILABILITY OR >125% BUDGET FAIL:** Present collection listing with uncertain site lot is not proof of discontinuation; room-level carried budget `null`.

