# Round 001 — PH-BATH4 — critic-build

**Seat:** Tile installer / GC (**weight 0.25**). Scores are 1–5; **seat scores use one decimal**. [Room geometry](../../geometry.json) is drawing-derived and live-Revit-unverified: 5.00-ft shower back wall, two 2.54-ft returns, 9.25-ft height, 10.08-LF tiled perimeter, nominal 5.00 x 2.54-ft walk-in shower. The recorded bath-floor area is an **owner 35-SF override of prior 27-SF data**. No confirmed niche position, wall buildup, openings, 4-in. drain location or pan elevations are available. [Plumbing](../../plumbing.json) specifies Brizo **BT062415-BNX 4-in. tile-in square point drain** and Black Onyx shower fittings.

## Candidate A — seat score **2.2 / 5.0**

| Installation criterion | Score | One-line evidence-based reason |
|---|---:|---|
| Wet-wall substrate, flatness and finish | **3 / 5** | The [24 x 48, 9-mm Cortar Bone Ribbed](https://www.elmsurfaces.com/product/bone-ribbed-cortar) demands a very flat, fully waterproofed substrate and controlled relief-bearing surfaces at fixture plates, yet its manufacturer page lists only **Walls / Back Splashes**, not Wet Areas. |
| Cut layout, lippage and offset | **2 / 5** | On the assumed [60-in. back, 30.48-in. returns and 111-in. height](../../geometry.json), 24 x 48 cuts and relief continuity must be worked around corners/niches; if staggered, the 48-in. long edge should be offset no more than one-third (16 in.), and no verified cut elevation exists. |
| Shower pan, slope and floor format | **1 / 5** | [Cortar Charcoal 12 x 24 Anti-Slip](candidates/A.md) lacks a published wet DCOF >=0.42 and a demonstrated four-way slope/tile-cut solution to the [4-in. square point drain](../../plumbing.json); the current row even quotes **Soft**, not Anti-Slip. |
| Niche, edge profiles and penetrations | **2 / 5** | [Clara Tierra Madre Caviar 2 x 8 zellige](candidates/A.md) has no documented Wet Areas listing; relief-to-niche trim, glass/valve sealing lands and sill drainage are unmeasured ([geometry](../../geometry.json)). |
| Waste, boxes, lead time and sequence | **3 / 5** | [107.2-SF wall and 8.63-SF niche quantities](candidates/A.md) are provisional, 15% waste may not reflect pattern-sensitive 24 x 48 cuts, and the existing quote did **not** include the two-room 214.4-SF ribbed wall quantity ([flat-Bone comparison evidence](../../../../research/products/elm-cortar-bone-flat-24x48.md)). |

**top_fix:** Replace the proposed **12 x 24 point-drain shower pan layout** with a dimensioned, positively sloped **smaller-format tile plan carrying a published wet DCOF >=0.42** and obtain the required revised selection approval.

**gate_flags:**
- **FAIL — BONE_RIBBED_WET_WALL:** [Manufacturer's Bone Ribbed page](https://www.elmsurfaces.com/product/bone-ribbed-cortar) lists Walls / Back Splashes, omitting Wet Areas; a collection-wide listing for flat Bone does not approve relief Bone Ribbed ([board gate 1](../../../../board/BOARD.md)).
- **FAIL — CLARA_NICHE_WET_WALL:** The supplied [candidate audit](candidates/A.md) has no manufacturer Wet Areas approval for Clara Caviar in the shower niche ([board gate 1](../../../../board/BOARD.md)).
- **FAIL — FLOOR_DCOF_UNPROVEN:** Charcoal Anti-Slip's actual SKU/rate and published DCOF >=0.42 have not been established; the active quote is for Soft ([candidate](candidates/A.md); [manufacturer Charcoal application](https://www.elmsurfaces.com/product/cortar-charcoal)).
- **HOLD — POINT_DRAIN_GEOMETRY:** A 12 x 24 rigid floor cannot be presumed to follow the point-drain fall without a cut/slope drawing; as submitted no corrective floor layout is stated ([geometry](../../geometry.json); [plumbing](../../plumbing.json); [board gate 6](../../../../board/BOARD.md)).

**confidence:** **medium** — the wet-wall manufacturer exclusion is explicit; drain geometry and floor material remain unverified.

## Candidate B — seat score **3.0 / 5.0**

| Installation criterion | Score | One-line evidence-based reason |
|---|---:|---|
| Wet-wall substrate, flatness and finish | **4 / 5** | [Flat Cortar Bone 24 x 48 Soft](https://www.elmsurfaces.com/product/cortar-bone) expressly lists **Wet Areas** and provides a more tractable flat bearing face at valve trims than Ribbed; a flat, waterproofed LFT substrate is still required ([product evidence](../../../../research/products/elm-cortar-bone-flat-24x48.md)). |
| Cut layout, lippage and offset | **3 / 5** | [60-in. back / 30.48-in. returns / 111-in. height](../../geometry.json) allow plausible centered 24-in.-wide panels (e.g. 18-in. back-wall sides before joints), but corners, 48-in. course breaks, niche openings and a <=16-in. offset if staggered require actual elevations. |
| Shower pan, slope and floor format | **2 / 5** | [12 x 24 Charcoal Anti-Slip](candidates/B.md) still has no published DCOF >=0.42 and is unproved on the [4-in. point-drain pan](../../plumbing.json); the candidate acknowledges a smaller approved tile may be needed but supplies no selected layout. |
| Niche, edge profiles and penetrations | **3 / 5** | [Soho Black 2 x 10 Glossy](https://www.elmsurfaces.com/product/soho-black) lists **Wet Areas**; its approximately **9.5-mm** body must be reconciled with quoted **9-mm** flat Bone, edge trim, positively sloped sill and Brizo fixture penetrations ([product evidence](../../../../research/products/elm-soho-black-2x10.md)). |
| Waste, boxes, lead time and sequence | **3 / 5** | [Flat Bone quote precedent](../../../../research/products/elm-cortar-bone-flat-24x48.md) cites 10–12-week overseas lead and a historical 300-SF minimum against two rooms' 214.4-SF allowance; the [Soho](../../../../research/products/elm-soho-black-2x10.md) price/stock and actual niche field deductions remain unknown. |

**top_fix:** Issue an **approved DCOF-tested, small-format shower-floor and four-plane point-drain slope detail**, keeping the 12 x 24 tile only where the setting plane is flat and otherwise appropriate.

**gate_flags:**
- **FAIL — FLOOR_DCOF_UNPROVEN:** Cortar Charcoal Anti-Slip is marked Wet Areas by [ELM](https://www.elmsurfaces.com/product/cortar-charcoal), but the exact shower/bath floor finish still has **no published numeric wet DCOF >=0.42** ([candidate](candidates/B.md); [board gate 2](../../../../board/BOARD.md)).
- **HOLD — POINT_DRAIN_GEOMETRY:** The candidate includes a smaller-tile remedy **in principle**, but without an actual approved tile, slope drawing and drain position a 12 x 24 shower-pan layout cannot be released ([geometry](../../geometry.json); [plumbing](../../plumbing.json)).
- **OPEN — SIZE/PRICE/AVAILABILITY:** Anti-Slip selection differs from the quoted Soft finish; flat-wall order terms and Soho niche price/lot are unconfirmed ([candidate](candidates/B.md); [product evidence](../../../../research/products/elm-soho-black-2x10.md)). No discontinuation or unavailable-US-distribution failure is established.

**confidence:** **medium** — flat Bone and Soho Wet Areas evidence is specific; point-drain construction and the live room remain unmeasured.
