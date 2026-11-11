# Round 003 — TX-POWDER2 — critic-build

**Seat:** Tile installer / general contractor, weight **0.25**. Blind independent review; five 1–5 rubric scores per candidate and one-decimal overall seat score. The [room geometry](../../geometry.json) describes an **assumed 3.806-ft (45.672-in.) × 9.25-ft (111-in.) dry vanity feature wall**, **35.2055 SF net / 40.5 SF gross with 15% waste** and an **existing wood floor**; dimensions and exact model identity have **not been verified live**. The [plumbing schedule](../../plumbing.json) lists Hansgrohe **Tecturis E 73072341, Brushed Black Chrome, single-hole DECK-mounted faucet** and a **sink/basin still UNSELECTED** (row **5006187243962244**). There is no wall-mounted faucet or wet shower floor in this room; any flat landing concerns the **mirror, countertop/backsplash interface and supports**, not an invented wall faucet escutcheon.

## Candidate A — overall seat score **3.4 / 5.0**

| Installer/GC criterion | Score | Evidence-based reason |
|---|---:|---|
| Dry-wall material classification and substrate | **4 / 5** | [ELM Vera Forma Indigo Edge 6×6 Glossy Relief](https://www.elmsurfaces.com/product/indigo-edge-vera-forma) is manufacturer **Walls-only**, appropriate on the [dry W1](../../geometry.json); actual flatness, substrate stiffness and secure mirror anchors remain unverified ([candidate A](candidates/A.md)). |
| 6×6 relief course balance, cut quality and lippage | **4 / 5** | On [45.672-in. provisional W1](../../geometry.json), seven nominal 6-in. full tiles would leave ~**1.84-in. side cuts**, while six full modules give balanced **~4.84-in. end cuts before joints**; [candidate A](candidates/A.md) explicitly proposes the more workable six-module-centered grid, subject to actual face measurements and relief alignment. |
| Flat landing, selected faucet and basin coordination | **3 / 5** | A **provisional flush mirror/backsplash mounting zone** helps avoid relief under support brackets and splash-critical countertop joints, but its material, dimensions and interface remain `null` pending the **unselected sink**; [73072341](../../plumbing.json) is **deck-mounted** and requires no wall spout penetrations ([candidate A](candidates/A.md)). |
| Edge profiles, setting and maintenance | **3 / 5** | The [glossy three-dimensional tile](../../../../research/products/elm-vera-forma-indigo-edge-6x6.md) needs a 3×3 grazing-light mock-up, precise grout depth, compatible dark trim, smooth relief-to-panel transition and wipeable backsplash sealant; final profile, grout and flush-panel fastening are unspecified ([candidate A](candidates/A.md)). |
| 15% waste, displacement and schedule | **3 / 5** | The [40.5-SF carried tile amount](candidates/A.md) already incorporates ~15% over [35.2055 SF net](../../geometry.json); the **flush panel's `null` area must be deducted before carton count**, with a hypothetical six **7.34-SF cartons = 44.04 SF** and **$361.13** area-rate illustration versus **$332.10 carried tile rate**, not a panel/installation quote ([Indigo evidence](../../../../research/products/elm-vera-forma-indigo-edge-6x6.md)). |

**top_fix:** Detail one **measured mirror/backsplash flat-zone assembly** including backing, material, splashproof countertop joint, tile transition and exact tile quantity deduction **after the owner selects the basin**.

**gate_flags:**
- **NONE — WET_WALL / FLOOR_DCOF:** [Indigo Edge is Walls-only](https://www.elmsurfaces.com/product/indigo-edge-vera-forma) and is proposed only on a **dry accent wall** above [wood flooring](../../geometry.json); **wet-floor DCOF is N/A**.
- **HOLD — BASIN / FLAT_PANEL:** [Sink/basin selection `null`](../../plumbing.json) prevents locating a flush backsplash/anchor zone or confirming finished panel material, durability, finished thickness and drainage/splash interface. **Deck-mounted 73072341** remains unchanged; do not specify wall-mount rough-ins ([candidate A](candidates/A.md)).
- **HOLD — MEASURED_GRID / MATERIAL_NETTING:** The six-module cut option is conceptual because the [45.672-in. wall](../../geometry.json) has no live verification; **panel SF and displaced tile** remain `null`, so no approved takeoff or trim order exists ([candidate A](candidates/A.md)).
- **OPEN — QUOTATION / AVAILABILITY / BUDGET:** The **$332.10/unit** Indigo area-rate is historical and **not** an all-in hybrid quote; the flat panel has no selected material or price, exact local tile stock and delivery are unknown, and no room budget cap exists for the 125% test ([Indigo evidence](../../../../research/products/elm-vera-forma-indigo-edge-6x6.md); [owner feedback](../../../../state/OWNER_FEEDBACK.md)).

**confidence:** **medium** — practical module correction and an appropriate deck-faucet interpretation, subject to basin/panel design and measured geometry.

## Candidate B — overall seat score **2.8 / 5.0**

| Installer/GC criterion | Score | Evidence-based reason |
|---|---:|---|
| Dry-wall material classification and substrate | **4 / 5** | [Vera Forma Indigo Edge 6×6 Relief](../../../../research/products/elm-vera-forma-indigo-edge-6x6.md) is acceptable for a **dry** powder feature wall, with no tile floor, but its irregular face requires stable setting and adequately backed wall-mounted mirror supports ([candidate B](candidates/B.md)). |
| 6×6 relief module, perimeter cuts and lippage | **2 / 5** | [45.672-in. provisional wall width](../../geometry.json) risks **~1.84-in. side slivers** with seven centered full 6-in. modules; [candidate B](candidates/B.md) lacks a specified balanced cut grid, tile size verification and relief-profile transition detail. |
| Mirror/backsplash landing and deck faucet | **2 / 5** | [Candidate B](candidates/B.md) leaves a flat landing around the **faucet or mirror** unresolved, although [Hansgrohe 73072341](../../plumbing.json) is a **DECK-mounted** faucet; the critical installation decision is support/cleanability at the mirror and unselected sink's countertop splash zone, not a wall faucet aperture. |
| Grout, edges and splash maintenance | **3 / 5** | [Full-height relief ceramic](candidates/B.md) needs exposed trim depth, flexible edge sealant, grout control, flat mirror support and a cleanable backsplash-to-counter connection; exact panel or protective termination is absent. |
| Waste, takeoff and installation sequence | **3 / 5** | The [40.5-SF gross / 15%-waste tile line at $8.20/SF](candidates/B.md) follows the provisional [35.2055-SF net wall](../../geometry.json), but the final cuts, mirror landing and basin opening are unmeasured; the [supplier carton coverage 7.34 SF](../../../../research/products/elm-vera-forma-indigo-edge-6x6.md) requires separately rounded boxes. |

**top_fix:** Draw a **dimensioned mirror and basin splash-zone setting elevation** with centered six-module Indigo cuts and a confirmed flat/cleanable support interface, recognizing **73072341 as deck-mounted**.

**gate_flags:**
- **NONE — WET_WALL / FLOOR_DCOF:** The [Indigo product](https://www.elmsurfaces.com/product/indigo-edge-vera-forma) is confined to a dry wall above a [wood floor](../../geometry.json); shower Wet Areas and bath-floor DCOF gates are **N/A** ([board](../../../../board/BOARD.md)).
- **HOLD — MIRROR / BASIN / DECK FAUCET:** The [sink remains unselected](../../plumbing.json), and the [candidate's](candidates/B.md) generic “flat landing at faucet” wording needs correction for a **deck-mounted** unit. Mirror anchorage, splash zone and counter clearance remain unknown; **no wall-mount faucet rough is implied**.
- **HOLD — CUTS / BASE / TRIM:** A centered six-tile panel grid is feasible conceptually from assumed dimensions but not shown; actual wall width, relief depth, edge returns, ceiling and wood-floor terminations are unverified ([geometry](../../geometry.json); [candidate B](candidates/B.md)).
- **OPEN — STOCK / PRICE / BUDGET:** **$332.10/unit** is the 2026-09-03 carried tile-rate illustration before box rounding, labor and trim. Chicago batch/ETA are `null`; no room budget cap is supplied, so a >125% budget FAIL is unsupported ([Indigo evidence](../../../../research/products/elm-vera-forma-indigo-edge-6x6.md); [owner feedback](../../../../state/OWNER_FEEDBACK.md)).

**confidence:** **medium-low** — acceptable dry material but unresolved basin/mirror and uneven relief-face assembly.
