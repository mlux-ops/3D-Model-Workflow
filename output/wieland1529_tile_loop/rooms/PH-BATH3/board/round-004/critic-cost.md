# PH-BATH3 — Round 004 independent procurement critique (critic-cost, seat weight 0.20)

**Blind basis — 2026-11-06.** Exactly candidates B and C; no historical role maps. Two PH units, but **actual room program remains contradictory**: geometry.json depicts a **5.00-ft tub back + two 2.33-ft returns** with **7.75-ft tiled height** and **35-SF level bath**, while plumbing.json includes selected **Delta DT062412 4-in square tile-in shower point drain** and Hansgrohe Chrome fixtures. **Do not invent a sloped shower pan SF, silently convert tub to shower or choose a basin:** basin is **owner-unselected** (plumbing row **2580485884149636**). The open 1527-named model has not been identity-verified as 1529. All historical SF already contain **15% waste**. The 2026-09-03 ELM rows are historical tile **material rate references**, no current Chicago stock/installed quote; owner cap **null**.

## Candidate B — Tones Opal wet walls + Sandstone niche + Cortar Bone Soft level floor

| Exactly five procurement criteria | Score (1–5) | Independent, source-grounded reason |
|---|---:|---|
| **1. Historic quoted economics** | **3** | Direct PH ELM rows **4724833938636676** Opal **86.2×$6.95 = $599.09**, **1589102831075204** Sandstone **8.63×$6.95 = $59.98**, **2473034124951428** Bone Soft **40.2×$6.75 = $271.35**, total **$930.42/unit** before netting (candidate B lines 7–13, 25). |
| **2. Source quantities + 15% already included** | **2** | **86.2 SF field plus 8.63 SF niche** may count the same opening twice; niche back/returns unmeasured. The possible **Delta square-drain pan is absent** and source's 35-SF floor may not include a required slope zone if shower governs (candidate B lines 9, 21–25; room geometry/plumbing). |
| **3. True dated quote vs illustrative alternative** | **5** | All three shown rates are **same-room 2026-09-03 ELM quoted lines**, not public retail or cross-room assumed substitute prices. Yet a priceable line does **not** establish wet suitability or actual shower scope (candidate B lines 7–14). |
| **4. Stock/lead/current procurement** | **2** | Historic Tones US quick-ship claim is not a committed Opal/Sandstone Chicago lot; Cortar imported 10–12-week/300-SF terms are old and no current delivery/price is confirmed ([Tones collection](https://www.elmsurfaces.com/product-collection/tones); [Cortar Bone Soft research](../../../../research/products/elm-cortar-bone-soft-12x24.md)). |
| **5. Viable alternative against owner cap UNKNOWN** | **1** | Wet-use proof for **Opal's exact product** is unavailable, level floor exact measured DCOF fails, tub-vs-point-drain scope unresolved and **room budget = null**. $930.42 is not a budget cap (candidate B lines 21–25; board gates 1,2). |

**Overall cost seat_score: 2.6 / 5.0** (3+2+5+2+1 = 13/5). **confidence: medium** for old row economics; **low** for complete buildable and supplier-ready material total.

**Historic quoted-rate extension:** **86.2×$6.95=$599.09** Opal field + **8.63×$6.95=$59.98** Sandstone niche + **40.2×$6.75=$271.35** Bone Soft = **$930.42/unit / $1,860.84/two units**, **before** field/niche overlap correction, any changed pan/wet walls, case rounding, grout, edging, freight, tax, membrane, setting and labor. The combined **94.83 SF gross** wall+niche is a sum of source allowances, **not proof of physically additive tile area**. Existing 15% waste is already included.

**top_fix:** Resolve the **tub-versus-square-drain wet-room scope in a verified 1529 drawing**, then produce an exact floor/pan DCOF-compliant, wet-wall-listed tile schedule with netted niche and current two-unit ELM quote.

**gate_flags:**
- **FAIL — OPAL_WET_WALL:** Exact **Tones Opal 2×20 Glossy** individual manufacturer **Wet Areas approval not established**; quoted product is not automatically wet-listed. The separate [Sandstone](https://www.elmsurfaces.com/product/sandstone-tones) niche approval does not transfer to Opal (candidate B lines 7, 21).
- **FAIL — LEVEL_BATH_FLOOR_DCOF:** Cortar Bone **12×24 Soft** lacks exact published measured wet DCOF ≥0.42 even though [flat Bone](https://www.elmsurfaces.com/product/cortar-bone) has a Wet Areas application tag ([Bone Soft research](../../../../research/products/elm-cortar-bone-soft-12x24.md)).
- **SHOWER PAN CONDITIONALLY FAIL/PENDING:** If the **selected Delta DT062412 point drain** governs as walk-in shower, this candidate has **NO specified, measured, DCOF-proven pan surface**, so shower-floor approval **fails until a priced pan and certification are established**; if actual room is a tub, **no separate shower pan** should be costed (room plumbing.json notes; geometry.json tub alcove).
- **HOLD — geometry, stock, budget:** Basin unselected, niche dimensions/source model identity unverified, current Chicago lead/cases/cost cap **null**. No proven discontinued/no-US-distribution tile finding, no 125% cap test.

## Candidate C — wet-listed Tones Sandstone field/niche + PF07 Cream level floor

| Exactly five procurement criteria | Score (1–5) | Independent, source-grounded reason |
|---|---:|---|
| **1. Historic quoted economics** | **3** | PH Opal wall row **4724833938636676 $6.95/SF** and Sandstone niche row **1589102831075204 $6.95/SF** show a **same-product niche rate**, but **a full PH Sandstone field quote is null**; original Bone floor rate is not PF07's rate (candidate C lines 9–11). |
| **2. Source quantities + 15% already included** | **4** | Candidate explicitly tests **86.2 SF full wet wall inclusive of provisional 8.63-SF niche** by allocating **77.57 +8.63 SF**, preserving 15% once; **40.2 SF gross floor** remains prior room estimate; actual recess back/returns and hypothetical shower pan unknown (candidate C lines 9–12, 16). |
| **3. True dated quote vs illustrative alternative** | **2** | Historic **$659.07 wall+niche two-line allowance** is Opal+Sandstone, while candidate's **$599.09 net all-Sandstone** is a hypothetical overlap deduction, NOT a supplier quote; PF07 **$6.27/SF** is **retailer web price**, not revised PH rate (candidate C lines 9–11, 16; [PF07 evidence](../../../../research/products/daltile-portfolio-cream-pf07-12x24-matte.md)). |
| **4. Stock/lead/current procurement** | **3** | Manufacturer Sandstone/Tones advertises US-stocked quick ship 2–4 weeks and Daltile has Chicago locations, but **Sandstone/PF07 actual site lot, delivery, carton/trim/freight all null** ([Sandstone evidence](../../../../research/products/elm-tones-sandstone-2x20.md); [Daltile](https://locations.daltile.com/il/chicago/)). |
| **5. Viable alternative against owner cap UNKNOWN** | **2** | Sandstone field/niche has exact maker Wet Areas listing, improving wet-wall specification; PF07 bath floor **exact measured DCOF missing**, room program/basin undecided and complete quoted cost/cap **null**, so owner 125% check unavailable (candidate C lines 11–16). |

**Overall cost seat_score: 2.8 / 5.0** (3+4+2+3+2=14/5). **confidence: low** for proposed new price, **medium** for the explicit quantity reconciliation.

**Do not conflate two alternative wall baselines:** *Original dated ELM source lines* **86.2 SF×$6.95 Opal=$599.09** plus **8.63 SF×$6.95 Sandstone=$59.98** = **$659.07/unit** combined source allowances before overlap. *Candidate netted Sandstone-only illustration* **(86.2−8.63)×$6.95 + 8.63×$6.95 = $599.09/unit** assumes niche gross exactly replaces field gross (not measured; new full-wall supplier quote **null**). Historic original Bone Soft floor **40.2×$6.75=$271.35**, cannot be used for PF07. Retail PF07 **40.2×$6.27≈$252.05** by SF or **3 cartons ×$106.72=$320.16/unit** at current referenced public carton cost; combined **$599.09+$320.16=$919.25/unit** is a **non-purchasable, cross-source illustration**, **not** a PH quote or a proven saving. If actual room requires a shower pan, pan SF/$/SKU = **null** and complete candidate cost = **null**. Exclude installed/freight/trim/tax, no extra waste.

**top_fix:** Obtain a **verified tub/shower and niche section plus a PH-specific two-unit Sandstone/PF07 quote**, including measured exact PF07 wet DCOF, case/trim/Chicago delivery and any separately required certified shower-pan SKU.

**gate_flags:**
- **PASS manufacturer wet-wall application:** [Sandstone 2×20 Glossy](https://www.elmsurfaces.com/product/sandstone-tones) expressly lists Wet Areas; both field and niche use the **same product** (candidate C lines 9–10).
- **FAIL — LEVEL_BATH_FLOOR_DCOF:** Daltile [PF07 Cream 12×24 Matte](https://www.daltile.com/products/concrete-look/portfolio/cream) displays **Wet & Level application / Target Wet DCOF ≥0.42**, **not measured exact-SKU value**; actual measured DCOF **null** ([PF07 evidence](../../../../research/products/daltile-portfolio-cream-pf07-12x24-matte.md)).
- **SHOWER PAN CONDITIONALLY FAIL/PENDING:** Delta **DT062412 4-in square** is recorded in PH-BATH3 plumbing but a tub alcove is in geometry; this design has **no priced/certified pan**. If shower governs, pan floor gate **fails pending product-specific wet/DCOF and measured takeoff**; if tub governs, no shower pan should be added.
- **HOLD — source program, cost and owner decisions:** Basin **unselected**, true niche returns/geometry, PH supplier quote, Chicago lot, room cap **null**; no available evidence of discontinued tile/no US distribution or an enforceable >125% limit.

**Market evidence restriction:** PH $2.8M and **14 comps from nine separate buildings** establish bath *program* context only; four 405 W Armitage sales are **one** design precedent. No manufacturer/price assumptions based on uninspected tile photos ([COMPS.md](../../../../research/comps/COMPS.md)).

