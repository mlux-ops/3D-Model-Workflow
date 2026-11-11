# Round010 | PH Bath 3 and TX Bath 3 — mutually exclusive tub-versus-shower program control

**Owner-only program decision. No design branch below has been selected, verified in the actual 1529 model, priced as current installed scope, or authorized for construction.** The source is the existing handoff drawing/finish and selected plumbing exports, not a certified live 1529 model. The native Revit session remains titled **25-006 1527 N Wieland**, not confirmed identical to 1529. This document gives the architect, GC and owner two controlled constructability alternatives without changing any selected fixture or historic quote.

## Direct source reconciliation

| Room | Drawing-origin geometry, not certified | Existing selected plumbing schedule | Original 2026-09-03 ELM material-only quote per copy, 15% source waste included | Hard discrepancies |
|---|---|---|---|---|
| **PH Bath 3** | `tub alcove`, source 35 SF room; W1 5.00 ft, W2/W3 2.33 ft, source tiled H 7.75 ft; all openings/niche/drain positions null | **Delta DT062412 4-in tile-in SQUARE shower drain, Chrome**, Hansgrohe Chrome shower controls; **no selected bathtub line in supplied plumbing.json**, sink/basin source row 2580485884149636 explicitly UNSELECTED | wall Tones Opal 2x20 Glossy **86.2 SF / $599.09**; floor Cortar Bone Soft 12x24 **40.2 SF / $271.35**; Sandstone 2x20 niche **8.63 SF / $59.98**; nominal subtotal **$930.42/unit** | Opal individual Wet Areas listing absent for wet use; actual tub drain vs selected square shower drain program conflict, owner sink unselected, exact floor raw wet DCOF null |
| **TX Bath 3** | `tub alcove`, source 37 SF room; W1 5.10 ft, W2/W3 2.60 ft, source tiled H 7.75 ft; openings/niche and drain location null | **Brizo BT062415-BNX 4-in tile-in SQUARE shower drain, Brilliance Black Onyx**, Roccesco shower controls; **no selected bathtub line in supplied plumbing.json** | wall Tones Emerald 2x20 Glossy **91.8 SF / $638.01**; floor Cortar Grey Soft 12x24 **42.5 SF / $286.88**; Sandstone 2x20 niche **4.89 SF / $33.99**; nominal subtotal **$958.88/unit** | Owner tub-versus-walk-in still undecided, no itemized tub selection; individual Emerald wet use and original Soft floor exact numeric wet DCOF require SKU-specific documentation |

These are **per-copy source quantities with the original single 15% waste already embedded**. Each room occurs twice. The niche is quoted separately; existing full wall gross must not be added to new niche back/returns without subtracting the displaced field face from measured net quantities. There is no added primary-bath niche, no WC duplicate floor, and no new flooring price or package implied. Original source gross divided by 1.15 provides only an arithmetic comparison, never an as-built room measurement.

## Branch A — retain the drawing's tub-alcove concept, ONLY upon explicit owner program approval

1. The owner must first select **tub versus shower**. If tub is chosen, an actual bathtub model, dimensional cut sheet, rough-in, waste/overflow and approved drain/valve configuration are **null** until the owner's signed plumbing direction. Existing Delta/Brizo square tile-in SHOWER drains must **not** be silently used as bathtub wastes, reassigned or deleted.
2. Draw a physically verified tub-flange-to-bonded-waterproofing and sealant section, niche sill with positive drainage, valve/shower-head penetration, tub apron and finished tile-to-wood transition; survey the drawing-origin W1–W3 orientation and edge calibration. Original source 40.2/42.5-SF floor becomes **level-floor only** only after accepted tub/area reconciliation; any separate shower-pan quantity is **N/A for an actual standalone tub**.
3. PH Bath 3 wet tub walls cannot retain Tones Opal until the exact product/finish is maker Wet Areas-listed; Tones Sandstone 2x20 maker wet-listed finish is a **conditional comparison**, not an owner substitution. TX Bath 3 Emerald individual finish wet listing must be verified without borrowing another Tones color. Exact floor wet DCOF raw numeric and original tile availability remain **HOLD**. Original source quote cannot be repriced to another SKU.

## Branch B — adopt a tiled walk-in shower around the listed square point drain, ONLY upon explicit owner program approval

1. Owner/architect must authorize a genuine change from the drawing's tub-alcove room program to a walk-in shower with source-compatible selected **DT062412 Chrome** (PH3) or **BT062415-BNX Black Onyx** (TX3). No tub selection may be inferred, and no change to the recorded fixture schedule has been performed.
2. Before specifying a floor quantity, survey the correct 1529 shower footprint, drain center and finished flange elevation, curb/curbless transition, glass/entry dimension, waterproof pan and four-plane positive slopes. **Level bathroom floor SF = null; shower-pan net SF = null; both must reconcile to source gross without adding another 15% waste or buying both full-area products.** Large source 12x24 Soft floor tiles cannot automatically conform to four-plane point-drain slopes.
3. Small-format **Glazzio HNC6715 2x2 hex** is a manufacturer **Shower Floor YES**, reported wet DCOF **>0.50** conditional pan concept, not a released choice. Its manufacturer 4.85 SF/box cannot produce a purchasable carton count until the correct pan net/gross allocation, exact accepted numeric wet DCOF laboratory certificate, membrane/mesh suitability, grout and approved drain detail are established. PH3 wet Opal and TX3 Emerald wet compatibility remain independent product-specific holds.

## Architect/owner and GC decision checkpoint

| Control item | PH Bath 3 | TX Bath 3 | Responsible next source |
|---|---|---|---|
| Owner tub or walk-in program | **null — no selection** | **null — no selection** | Written owner program direction, not this AI comparison |
| Existing point drain item preserved | DT062412 Chrome | BT062415-BNX Black Onyx | Plumbing schedule and exact manufacturer install details |
| Actual selected bathtub, tub waste/overflow | null | null | Owner-approved corrected fixture schedule only for a tub decision |
| Correct 1529 model and field W/niche/drain coordinates | null | null | Revit process/session/title/path confirmed 1529 plus GC survey |
| Wet wall tile maker approval | Opal FAIL for wet use; Sandstone conditional maker Wet Areas | Emerald individual maker wet evidence unresolved | Exact product/finish maker official documents |
| Level-floor SKU raw wet DCOF lab value | null / FAIL | null / FAIL | Numeric source test report for actual finish |
| Walk-in shower pan SKU raw wet DCOF and net SF | null / FAIL until owner program | null / FAIL until owner program | Approved small-format sheet lab report, actual drain slope plan and measured net area |
| Full current Chicago supplier and installed proposal, cartons and trim | null | null | Dated exact-lot quote only after owner branch and physical survey |
| Owner approval / release | **false / false** | **false / false** | Written signature and resolved hard gates |

**Rendering / sample brief (not generated or ordered):** Draw each current source tub alcove as a dashed source condition and a separate explicitly labeled *hypothetical walk-in branch*; do not merge images, assign an unselected basin, invent niches, change fixture finishes, or imply either branch is approved. Each branch requires plan, W1–W3 elevation cuts, drain/threshold section, exact manufacturer tile sample, grout and trim study and signed owner fixture schedule. Design intent should remain appropriate to PH $2.8M / TX $2.7M Old Town price bands (14 listed comp entries / nine independent buildings; Lincoln Park and Gold Coast only secondary); never infer unverified comparable bathroom photographs.
