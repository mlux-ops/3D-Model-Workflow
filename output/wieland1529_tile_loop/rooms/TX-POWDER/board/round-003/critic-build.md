# Round 003 — TX-POWDER — critic-build

**Seat:** Tile installer / general contractor, weight **0.25**. Independent blind criteria 1–5; one-decimal seat score. [Geometry](../../geometry.json) records a **dry vanity accent wall** W1 **2.99 ft (35.88 in.) wide × 9.25 ft (111 in.) high**, **27.6575 SF net / 31.8 SF gross incl. ~15% waste**, all drawing-derived and **not live Revit verified**. The floor is **wood**; there is no shower or tiled floor. [Plumbing](../../plumbing.json) lists a **wall-mounted cross-handle faucet 48140991** and **wall rough 32526141**, but its actual trim, spout center, escutcheon dimensions and finish are not measured. The [owner](../../../../state/OWNER_FEEDBACK.md) has supplied **no room tile budget cap**. Both Haze colors are manufacturer **Walls-only** and suitable for a *dry* feature, with **wet-floor DCOF N/A**.

## Candidate B — overall seat score **3.4 / 5.0**

| Installer/GC criterion | Score | Evidence-based reason |
|---|---:|---|
| Dry-wall material and substrate classification | **4 / 5** | [ELM Haze Camel](https://www.elmsurfaces.com/product/haze-camel) and [Haze Wheat](https://www.elmsurfaces.com/product/haze-wheat), matte **1.6×5**, have manufacturer **Walls** applications; for the [dry W1](../../geometry.json), neither shower Wet Areas approval nor wet-floor DCOF is required ([candidate B](candidates/B.md)). |
| Module cuts, alignment and edge quality | **3 / 5** | On [35.88-in. width × 111-in. height](../../geometry.json), slender vertical **1.6×5** courses need a balanced start datum, avoiding tiny edge fractions and short top/bottom cut pieces; actual tile dimensions, grout joints, door returns and exposed edges are unverified ([candidate B](candidates/B.md)). |
| Wall-faucet rough and mirror landing | **3 / 5** | The proposed **centered 30% Wheat** field must be coordinated to [Hansgrohe wall rough 32526141 / cross-handle faucet 48140991](../../plumbing.json), with no grout/uneven tile beneath escutcheon sealing surfaces, mirror anchoring and correct final wall thickness; no measured centerline yet ([candidate B](candidates/B.md)). |
| Two-tone setting, trim and maintenance | **3 / 5** | A **70% Camel / 30% Wheat** vertical stack is organized but introduces color sorting, batch/shade control, mock-up and matched perimeter/wood-floor transitions; grout **1/8 in.** is a proposed target rather than a verified maker or field joint ([candidate B](candidates/B.md)). |
| 15% waste, netting and current procurement | **4 / 5** | [22.26 SF gross Camel + 9.54 SF gross Wheat = the same 31.8 SF total](candidates/B.md), matching [27.6575 SF net × 1.15](../../geometry.json) after rounding; historical **$11.93/SF combined quote** is not two per-color rates, and carton split/Chicago delivery require confirmation ([Camel evidence](../../../../research/products/elm-haze-camel-1p6x5.md); [Wheat evidence](../../../../research/products/elm-haze-wheat-1p6x5.md)). |

**top_fix:** Prepare a **dimensioned 1:1 wall-faucet/mirror elevation** locating the 70:30 Camel/Wheat field against verified **32526141** rough centerlines, then settle safe edge cuts and color-specific box counts.

**gate_flags:**
- **NONE — WET_RATING / FLOOR_DCOF:** Both [Haze colors](https://www.elmsurfaces.com/product-collection/haze) are specified solely for a **dry wall** over a [wood floor](../../geometry.json); a Walls-only listing is sufficient for that scope and the [wet-floor DCOF gate](../../../../board/BOARD.md) is **N/A**.
- **HOLD — SITE_LAYOUT / MOUNTING:** Model identity, W1 actual clear width, mirror mounting, faucet rough elevation, escutcheon area, grout width and wood-floor/paint edge details are unverified ([geometry](../../geometry.json); [plumbing](../../plumbing.json)). No proven unavoidable geometry sliver is established.
- **OPEN — PACKAGING / BUDGET / DELIVERY:** **$379.37/unit** is the dated blended area-rate allowance; the actual **70:30 per-color carton allocation** and local inventory/lead are unknown. Neither a **>125% budget** violation nor a discontinued-product failure may be inferred without a carried cap or manufacturer evidence ([candidate B](candidates/B.md); [owner feedback](../../../../state/OWNER_FEEDBACK.md)).

**confidence:** **medium** — dry-wall use and a defined color split support trade planning, but actual rough centerlines and cut grid are missing.

## Candidate C — overall seat score **2.8 / 5.0**

| Installer/GC criterion | Score | Evidence-based reason |
|---|---:|---|
| Dry-wall material and substrate classification | **4 / 5** | [Haze Camel](../../../../research/products/elm-haze-camel-1p6x5.md) and [Haze Wheat](../../../../research/products/elm-haze-wheat-1p6x5.md) have **Walls-only** manufacturer listings, appropriate for this non-shower vanity feature wall; [wood floor](../../geometry.json) makes wet-floor DCOF inapplicable ([candidate C](candidates/C.md)). |
| Module cuts, alignment and edge quality | **2 / 5** | The [35.88-in. wall width, 111-in. height](../../geometry.json) lack a chosen **1.6×5 orientation, course grid or color band placement**, so narrow edge pieces and visually interrupted upper courses cannot be ruled out ([candidate C](candidates/C.md)). |
| Wall-faucet rough and mirror landing | **2 / 5** | [Wall-mounted rough 32526141 / cross-handle faucet 48140991](../../plumbing.json) requires positive escutcheon landing and coordinated spout/mirror position; [candidate C](candidates/C.md) leaves pattern, grout and landing unspecified. |
| Grout, two-color setting and trim | **3 / 5** | Both Haze matte colors can be installed in a common dry-wall assembly, but [candidate C](candidates/C.md) defers their mix ratio, joint width, grout, edge profile and paint/wood termination to sampling with no defined shop grid. |
| 15% waste, packaging and sequencing | **3 / 5** | The [31.8-SF gross Haze allowance × $11.93/SF](candidates/C.md) is one historical blended rate, already containing ~15% waste above [27.6575 SF net](../../geometry.json); unknown per-color counts and carton rounding can make an undecided split materially short or overordered. |

**top_fix:** Define a **single dimensioned Camel/Wheat orientation, mix ratio and course/rough-in elevation** that protects the selected wall faucet's flat escutcheon seating zone and balances edge cuts.

**gate_flags:**
- **NONE — WET_RATING / FLOOR_DCOF:** The [Haze dry wall](candidates/C.md) is a permitted Walls-only use; the [floor is wood](../../geometry.json), so **wet-floor DCOF N/A**, not FAIL.
- **HOLD — UNSPECIFIED_LAYOUT:** Color proportions, grout, full wall width, faucet/mirror coordinates and cut balances remain undefined; currently **insufficient geometry** to assert [board gate 6](../../../../board/BOARD.md) failure ([candidate C](candidates/C.md); [plumbing](../../plumbing.json)).
- **OPEN — QUOTE / STOCK / BUDGET:** The **$379.37/unit** price derives from the dated TX combined quote, not separately confirmed Camel and Wheat color orders. Local lot/lead are unknown and no approved room budget cap exists for the 125% test ([candidate C](candidates/C.md); [owner feedback](../../../../state/OWNER_FEEDBACK.md)).

**confidence:** **medium-low** — wall application is clear; unresolved module scheme and faucet integration materially weaken constructability confidence.
