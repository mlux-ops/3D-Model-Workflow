# R039 blind BUILD review — TX-POWDER

Scope: room 102A/102B, one **dry vanity feature wall W1** per copy; existing wood floor retained. Independent BUILD criteria are integer 1–5, equally averaged using decimal HALF_UP to one place. Source geometry is drawing-derived, not field verified. Neither wet floor nor shower assembly is proposed.

## Candidate A — Elm Haze Camel/Wheat Matte 1.6×5 (70/30)

| BUILD criterion | Integer | Specific evidence and constructability judgment |
|---|---:|---|
| Maker dry-wall suitability | **4** | Elm maker Haze collection [manufacturer listing](https://www.elmsurfaces.com/product-collection/haze) indexes Camel/Wheat, matte 1.6×5 and **Applications: Walls**, supporting a dry vanity wall. Item page [Haze Camel](https://www.elmsurfaces.com/product/haze-camel) was not reliably accessible for complete current item details; exact lot and continued US stock remain unconfirmed. |
| Format vs drawing dimensions | **4** | [TX-POWDER geometry.json](../../geometry.json) W1 = **2.99 ft (~35.88 in)** wide, **9.25 ft (111 in)** high. Small 1.6×5 pieces allow workable centered modules and fine adjustments on the narrow wall; precise tile joint and stack orientation require shop layout. |
| Substrate/flatness and installation | **4** | Matte small-format tile is manageable on an appropriately prepared flat, sound interior wall; frequent joints increase setting and alignment labor but avoid large-panel handling. Existing substrate and wall finish layer are **unknown** in [geometry.json](../../geometry.json), so manufacturer-approved adhesive, substrate prep and plane tolerances await field verification. |
| Edge/reveal/mirror/faucet cuts | **3** | [geometry.json](../../geometry.json) has **openings=null**, no verified edge/mirror coordinates. [plumbing.json](../../plumbing.json) lists Hansgrohe two-hole wall rough 32526141 and wall faucet trim 48140991; actual exposed finish and faucet hole positions are unknown. Numerous small cuts around escutcheons and mirror need a centered layout and specified metal/finished-edge transitions. |
| Waste, quantity, schedule risk | **3** | [R039 candidate A](candidates/A.md) carries **31.8 gross SF per copy**, including source **15% waste once**, and two copies; [same-job 2026-09-04 Elm quote](../../../../inputs/TRADE_QUOTES.md) confirms 1.6×5 Haze two-color price and 6.14 SF/box, FOB TX. A 70/30 field mix, cartons, lot, delivery and exact edge cuts still need reconciliation; no new waste multiplier or procurement assumed. |

**BUILD mean:** (4+4+4+3+3)/5 = **3.6** (HALF_UP).

**top_fix:** Produce one full-scale 35.88-in-wide vanity-wall elevation showing 70/30 color distribution, centered module, trim, mirror clearance and wall-mount faucet penetrations; field-measure before final quantity.

**gate_flags:** No proven geometric impossibility, but **GEOMETRY/PENDING** for opening/mirror/escutcheon placement; **AVAILABILITY/PENDING** exact Haze mix/lot and current US distribution (not a finding of discontinuation). Elm maker collection supports dry WALL application; other finish details need confirmation. Budget is FILL IN; no wet DCOF gate applies. No actual owner-veto mapping was disclosed to this blind seat.

**confidence:** **medium** — useful original wall dimensions and trade quote; unknown field substrates and fixture elevations.

## Candidate B — Floor & Decor Pienza Terra Matte 24×48

| BUILD criterion | Integer | Specific evidence and constructability judgment |
|---|---:|---|
| Maker dry-wall suitability | **5** | [Official Floor & Decor SKU 110850387](https://www.flooranddecor.com/porcelain-tile/pienza-terra-matte-porcelain-tile-110850387.html) lists porcelain **Floor/Wall YES** and **Shower Walls YES**, 9 mm, rectified; dry powder wall use is within stated application. Current Chicago lot and availability remain to be confirmed. |
| Format vs drawing dimensions | **2** | [geometry.json](../../geometry.json): wall width **35.88 in** versus **23.59 × 47.30 in actual tile** ([maker page](https://www.flooranddecor.com/porcelain-tile/pienza-terra-matte-porcelain-tile-110850387.html)). A 47.30-in horizontal tile cannot fit whole across this wall; with 23.59-in vertical panels, centered two-panel modules require substantial side cuts. Avoid any forced sub-3-in edge sliver by a measured symmetrical layout; no demonstrated unavoidable sliver, so no present geometry FAIL. |
| Substrate/flatness and installation | **2** | The [maker-listed](https://www.flooranddecor.com/porcelain-tile/pienza-terra-matte-porcelain-tile-110850387.html) large 23.59×47.30 rectified 9-mm panel needs exceptionally controlled wall flatness, appropriate large-format mortar/coverage and careful lifting; [geometry.json](../../geometry.json) does not certify substrate or actual wall plane. Avoid unsupported offset pattern; use a straight stack or field-tested joint layout. |
| Edge/reveal/mirror/faucet cuts | **3** | [plumbing.json](../../plumbing.json) shows two-hole wall-mount rough 32526141 and faucet 48140991; trim finish/positions and mirror size unknown. A 23.59-in-wide face may require difficult precise penetrations close to a cut edge and mirror/trim junction. Field-verified templates and manufacturer-approved drilling are essential. |
| Waste, quantity, schedule risk | **3** | [R039 candidate B](candidates/B.md) carries **31.8 gross SF per copy including 15% once**; retail $2.99/SF is explicitly an **out-of-state** published price, not confirmed Chicago. Narrow-wall cutting of 23.59×47.30 sheets can materially change whole-piece yield; box rounding, breakage, setting labor and Chicago inventory are unverified. Do not charge extra 15% without a measured cutting schedule. |

**BUILD mean:** (5+2+2+3+3)/5 = **3.0** (HALF_UP).

**top_fix:** Prepare a field-dimensioned full-size slab/panel cut diagram proving no edge strips under 3 in, supported cutout positions, flatness preparation and actual whole-tile yield.

**gate_flags:** **GEOMETRY/PENDING** due to 35.88-in wall vs 47.30-in tile and unverified focal-wall cuts, but **no demonstrated unavoidable sliver**; **AVAILABILITY/PENDING** for Chicago stock/lot. Published manufacturer wall permission is affirmative. Wet DCOF does not apply; budget FILL IN; owner-veto status cannot be determined by this blind seat.

**confidence:** **medium** — exact product sheet supports dimensional concerns; field edges, substrate and fixture cutouts remain unknown.
