# R039 blind BUILD review — TX-POWDER2

Scope: rooms 009A/009B, **one dry vanity feature wall W1** per physical copy, existing wood floors. Each of five BUILD ratings is independent integer 1–5; unweighted arithmetic mean rounded one decimal HALF_UP. Mirror, basin, substrate and live wall dimensions unverified.

## Candidate A — Elm Vera Forma Indigo Edge Glossy Relief 6×6

| BUILD criterion | Integer | Specific evidence and constructability judgment |
|---|---:|---|
| Maker dry-wall suitability | **4** | [Official named maker item](https://www.elmsurfaces.com/product/indigo-edge-vera-forma) is the candidate's Elm Vera Forma glossy relief wall tile; [R039 candidate A](candidates/A.md) cites dry-wall use and **8.6 mm** from the actual Elm same-job quotation ([TRADE_QUOTES](../../../../inputs/TRADE_QUOTES.md)). Direct exact manufacturer page could not be reliably retrieved to independently verify all current applications or distribution. Dry-wall suitability therefore provisionally supported, exact item status pending. |
| Format vs drawing dimensions | **4** | [geometry.json](../../geometry.json) W1 **3.806 ft (~45.67 in)** by **9.25 ft (111 in)**. Nominal 6×6 lends itself to a centered module: about 7.6 tiles across before grout, permitting balanced perimeter cuts instead of unavoidable narrow slivers. Verify actual manufactured dimensions and grout before release. |
| Substrate/flatness and installation | **3** | Small relief 6×6 pieces are physically manageable but visible glossy joints and surface relief require precise plane and grout alignment, profile-aware setting/cleaning. [geometry.json](../../geometry.json) has no wall-finish type or certified substrate. Relief plane must coordinate with trim and mirror. |
| Edge/reveal/mirror/basin cuts | **3** | [plumbing.json](../../plumbing.json) specifies **deck-mounted** Hansgrohe Tecturis E **73072341 Brushed Black Chrome**, while **basin remains UNSELECTED**; do not add wall faucet holes. Mirror position, vanity/basin backsplash boundary and side termination absent from [geometry.json](../../geometry.json). Relief tiles demand a flat termination/trim strategy before mirror clearance can be accepted. |
| Waste, quantity, schedule risk | **3** | [candidate A](candidates/A.md) uses **40.5 gross SF/copy** already including 15% waste; two copies. [2026-09-04 Elm quote](../../../../inputs/TRADE_QUOTES.md) shows 6×6 Vera Forma Indigo Edge at $8.20/SF, 30 pcs/7.34 SF per box, FOB TN; carton-rounded final order, current lot and any relief-edge cutting losses remain unresolved. |

**BUILD mean:** (4+4+3+3+3)/5 = **3.4** (HALF_UP).

**top_fix:** Confirm basin, mirror profile, tile relief depth and matching edge trim, then center the 6×6 grid on an actual measured 45.67-in wall elevation.

**gate_flags:** **GEOMETRY/PENDING** for actual mirror and basin interface, no demonstrated impossible cut; **MAKER APPLICATION/AVAILABILITY/PENDING** precise current item sheet and US supply, not a confirmed rejection. Wood floor unchanged, no floor/wet DCOF requirement. Budget FILL IN; blind seat cannot establish historical owner-veto match.

**confidence:** **medium-low** — drawing geometry and historical quote available; item live maker detail and selected basin absent.

## Candidate B — Elm Tones Sandstone Glossy Ceramic 2×20

| BUILD criterion | Integer | Specific evidence and constructability judgment |
|---|---:|---|
| Maker dry-wall suitability | **5** | [Elm official product URL](https://www.elmsurfaces.com/product/sandstone-tones) identified in [candidate B](candidates/B.md) as **Walls / Wet Areas YES**; 2×20 glossy ceramic 8.5 mm. Current maker page fetch was unreliable, so direct contemporary stock/finish order code needs confirmation; a dry vanity wall is consistent with the reported manufacturer wall application. |
| Format vs drawing dimensions | **4** | [geometry.json](../../geometry.json) W1 ~**45.67 in** wide and 111 in high. A horizontal **20-in nominal** field can center two full lengths with ~2.8-in perimeter cuts each before grout if uniform, which approaches the 3-in focal-cut caution. Prefer a deliberate centered 20/5.7/20 layout or vertical stack with tested full-height repeats; actual nominal/working tile dimension and joint must be verified to avoid slivers. |
| Substrate/flatness and installation | **4** | Slim 2×20 ceramic can install readily on a dry vertical wall with properly prepared plumb, flat substrate; length requires control of warpage/lippage and any offset (if running bond, limit to **1/3** length unless maker permits otherwise). Source [geometry.json](../../geometry.json) has unknown existing wall build-up. |
| Edge/reveal/mirror/basin cuts | **3** | [plumbing.json](../../plumbing.json) identifies deck-mounted Hansgrohe **73072341**, Brushed Black Chrome, with **no selected basin**. Slim tile permits relatively local mirror and backsplash cuts, but long thin pieces may fracture at notches; no wall penetrations for the deck faucet should be assumed. Exact finish edge/reveal strategy remains a field drawing hold. |
| Waste, quantity, schedule risk | **3** | [candidate B](candidates/B.md) original **40.5 gross SF per copy** already includes 15% waste, two copies; [2026-09-04 same-job Elm quote](../../../../inputs/TRADE_QUOTES.md) identifies Tones Sandstone among five 2×20 colors, $6.95/SF, 24 pcs/6.50 SF per carton. Exact individual color/order code, batch and carton-rounded yield unverified; avoid an extra waste charge. |

**BUILD mean:** (5+4+4+3+3)/5 = **3.8** (HALF_UP).

**top_fix:** Produce a measured centered layout proving perimeter cut width at the selected 2×20 orientation, including mirror/vanity edge and basin clearance; confirm exact Sandstone SKU and current batch.

**gate_flags:** **GEOMETRY/PENDING** centered horizontal option could produce ~2.8-in edges depending on grout: must redesign if real measured strips would be under 3 in; vertical/alternative layout appears feasible, therefore no demonstrated unavoidable sliver or hard failure. **AVAILABILITY/PENDING** current color lot, precise order code and US distribution, no confirmed discontinuation. No wet/floor DCOF gate; budget FILL IN; owner veto not exposed to the blind evaluator.

**confidence:** **medium** — historical quote and drawing sizes support assessment, but not installed dimensions or final basin.
