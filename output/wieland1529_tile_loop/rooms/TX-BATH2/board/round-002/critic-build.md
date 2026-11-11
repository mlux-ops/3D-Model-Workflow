# Round 002 | TX-BATH2 | critic-build

**Seat:** Installer / general contractor; **weight 0.25**. All scores are independently assessed on a 1–5 scale. Seat scores are one decimal. **Evidence condition:** [geometry](../../geometry.json) is earlier drawing-derived, live Revit unverified, and the open 1527-named model is provisionally relevant only. Per room, 5.207-ft (62.484-in.) tub back wall, two 2.60-ft (31.20-in.) returns, 7.75-ft (93-in.) assumed tiled height above tub deck, 10.41 LF total wet-wall run, and 38 SF bath floor. [Plumbing](../../plumbing.json) records a Duravit 59-in. built-in bathtub, chrome Hansgrohe shower fittings, and **unselected basin**. No separate shower pan is established. The [board](../../../../board/BOARD.md) requires manufacturer-listed wet-wall use and a **published measured wet DCOF ≥0.42 for the exact bath-floor product**.

## Candidate B — seat score: **3.2 / 5.0**

| Build criterion | Score | One-line evidence-based reason |
|---|---:|---|
| Wet-wall approval / waterproof substrate | **4 / 5** | [Tones Copper 2×20](https://www.elmsurfaces.com/product/copper-tones) and [Tones Sandstone](https://www.elmsurfaces.com/product/sandstone-tones) carry Wet Areas listings in [manufacturer audit evidence](../../../../research/products/elm-tones-copper-2x20.md), but tub-flange waterproofing, backing and change-of-plane sealant still need actual details ([candidate B](candidates/B.md)). |
| Wall cuts, joint pattern and lippage | **3 / 5** | On a provisional [62.484-in. back wall](../../geometry.json), three 20-in. nominal modules leave only 2.484 in. before joints, so start with **two centered full tiles plus balanced ~11-in. ends**; the two 31.2-in. returns also require controlled edges and fixture penetrations ([candidate B](candidates/B.md)). |
| Bathroom floor performance, 12×24 setting and slope | **3 / 5** | [PF07 Cream 12×24 Matte](https://www.daltile.com/products/concrete-look/portfolio/cream) is listed for wet **level** interior floors with **Target DCOF ≥0.42** and 1/8-in. grout, and zero offset reduces lippage; no actual **PF07 12×24 measured wet DCOF** is published in the reviewed evidence ([product file](../../../../research/products/daltile-portfolio-cream-pf07-12x24-matte.md)). |
| Tub, niche, exposed trims and penetrations | **3 / 5** | [Sandstone niche 8.63 SF gross](candidates/B.md) is a provisional displaced wall area; its waterproof recess, sloped sill, jamb returns, trim and Hansgrohe control elevations are missing from [geometry](../../geometry.json), and the sink remains unselected ([plumbing](../../plumbing.json)). |
| Takeoff, waste, carton and trade sequence | **3 / 5** | [43.7 SF floor gross](candidates/B.md) versus three PF07 cartons at 51.06 SF shows carton rounding beyond the carried waste basis; September ELM wall rates and public Daltile pricing are not final contractor pricing, with niche/field SF overlap to audit ([PF07 product file](../../../../research/products/daltile-portfolio-cream-pf07-12x24-matte.md)). |

**top_fix:** Secure a **manufacturer test report stating the measured wet DCOF for exact Portfolio Cream PF07 12×24 Matte** (minimum 0.42); if unavailable, specify and quote a verified compliant bath-floor tile.

**gate_flags:**
- **FAIL — FLOOR_EXACT_DCOF:** Daltile's manufacturer page uses the column **“Target DCOF Wet ≥0.42”**, an application target, **not a measured PF07 12×24 SKU value**; exact numerical test evidence is `null`. The strict [floor gate](../../../../board/BOARD.md) remains failed ([manufacturer page](https://www.daltile.com/products/concrete-look/portfolio/cream); [evidence record](../../../../research/products/daltile-portfolio-cream-pf07-12x24-matte.md)).
- **HOLD — SOURCE_GEOMETRY:** The 62.484-in. wall and 38-SF floor are provisional; verify tub flange, wall/outlet/niche positions, substrates and 12×24 perimeter cut sheet before final quantity or installation ([geometry](../../geometry.json)).
- **OPEN — COST / AVAILABILITY:** Exact project PF07 quote, Chicago lot and ETA are `null`, and the owner's room budget is unspecified; neither an availability nor a >125%-budget hard-gate failure is demonstrated ([candidate B](candidates/B.md); [owner feedback](../../../../state/OWNER_FEEDBACK.md)). No basin selection is authorized.

**confidence:** **medium** — clear DCOF documentation gap and constructible nominal layout; unverified model/room survey limits precision.

## Candidate C — seat score: **3.0 / 5.0**

| Build criterion | Score | One-line evidence-based reason |
|---|---:|---|
| Wet-wall approval / waterproof substrate | **4 / 5** | [Tones Copper](../../../../research/products/elm-tones-copper-2x20.md) and [Sandstone](https://www.elmsurfaces.com/product/sandstone-tones) are recorded Wet Areas-capable for the tub surround/niche, while exact cementitious backing, waterproofing continuity and tub lip remain unverified ([candidate C](candidates/C.md)). |
| Wall cuts, joint pattern and lippage | **3 / 5** | The same [62.484-in. W1 and 31.2-in. W2/W3](../../geometry.json) require centered 2×20 courses rather than narrow 1–2-in. terminal strips; field adjustments depend on actual grout, openings, niche and trim ([candidate C](candidates/C.md)). |
| Bathroom floor performance, 12×24 setting and slope | **2 / 5** | The quoted [Cortar Clay 12×24 Soft](candidates/C.md) is a plausible level-floor format but **no published exact product wet DCOF ≥0.42** was established, and no flatness/threshold elevation or verified floor cut layout exists ([candidate C](candidates/C.md)). |
| Tub, niche, exposed trims and penetrations | **3 / 5** | The [8.63-SF gross Sandstone recess](candidates/C.md) has no recorded physical opening, sill elevation, returns or waterproofing detail; [Duravit tub / Hansgrohe chrome fittings](../../plumbing.json) require accurate rough-in and termination setting. |
| Takeoff, waste, carton and trade sequence | **3 / 5** | Existing [92.8-SF Copper, 8.63-SF niche, and 43.7-SF Clay](candidates/C.md) quantities use 15% allowances but cannot be released until niche displaced-field deduction, box rounding and ELM current lot/lead are reconciled. |

**top_fix:** Replace the **Cortar Clay Soft 12×24 floor** with a manufacturer-verified, published **measured wet DCOF ≥0.42** selection, preserving the wet-listed Copper/Sandstone wall layout.

**gate_flags:**
- **FAIL — FLOOR_EXACT_DCOF:** Current Cortar Clay 12×24 Soft quote provides no actual published wet DCOF test value; product finish and floor application alone cannot pass [gate 2](../../../../board/BOARD.md) ([candidate C](candidates/C.md)).
- **HOLD — SOURCE_GEOMETRY:** No measured wall/niche/opening dimensions or floor/threshold elevations from a confirmed 1529 Revit model; geometric buildability remains **unverified rather than proven impossible** ([geometry](../../geometry.json)).
- **OPEN — SUPPLY / BUDGET:** Historical ELM price and quick-ship statement do not establish current Chicago stock or a room-specific spend cap; no hard availability/budget breach evidenced ([candidate C](candidates/C.md); [owner feedback](../../../../state/OWNER_FEEDBACK.md)).

**confidence:** **medium** — primary construction bottleneck is the missing floor test; project wall dimensions remain unverified.
