# R030 independent blind critique — TX-PRIMARY — COST

Seat: procurement, weight 0.20 for prime to apply after independent critiques. Two physical copies 202A/202B; date 2026-11-07. Five equal COST criteria, each 1–5, arithmetic mean to one decimal. Selected 48-in **BNX LINEAR solid metal grate + distinct BR73480 rough** and inherited TX-WC FLOOR are kept; **no niche**. Tiled shower ceiling remains an independent **overhead HOLD**.

**Cost source priority:** Elm 2026-09-04 **same-job** quote (inputs/TRADE_QUOTES.md, thread 1a068e80c92c255f): Cortar Clay FLAT Soft 24×48 **$8.14/SF**, 15.39 SF/carton; Tones Copper Glossy 2×20 **$6.95/SF**, 6.50 SF/carton. F&D Kirkwood, Atlanta GA public 2026-11-07 retail: [Riviera Oat 101487775](https://www.flooranddecor.com/porcelain-tile/riviera-oat-matte-porcelain-tile-101487775.html) **$3.99/SF, $63.84/16.00-SF carton**; [Perimeter Gray 101239218](https://www.flooranddecor.com/porcelain-tile/perimeter-gray-matte-porcelain-tile-101239218.html) **$3.99/SF, $61.84/15.50-SF carton**. Neither public rate is a Chicago job quote, confirmed lot or delivered price. Source: research/products/R030_FIVE_SKU_LIVE_STORE_CONTEXT_VERIFICATION_20261107.md.

## Candidate A — Elm Clay walls / Riviera Oat LEVEL + LINEAR PAN

| Independently judged COST criterion | Score / 5 | Evidence and reason |
|---|---:|---|
| Historical material-rate value | **4** | Illustrative source gross: **134.4 SF WALL+CEILING × $8.14 + 116.1 SF LEVEL/PAN/WC × $3.99 = $1,557.26/copy** versus original **$1,999.60/copy**, saving **$442.34 (22.1%)** before cartons. The 134.4-SF source **includes a held ceiling** and is not a certified selected wall-only quantity. |
| Rate provenance | **4** | Exact selected Clay has current-year **1529 trade quote**, whereas exact Riviera is **Georgia retail**; commercial certainty remains mixed. |
| Packing and duplicate-count control | **3** | Quotes disclose Clay **15.39-SF** and Riviera **16.00-SF** cartons. Historic **15% waste was counted once**; inherited WC is already within 116.1 SF. Ceiling/wall and LEVEL/PAN net split are unknown, so **final carton counts are not supported**. |
| Chicago continuity / schedule | **2** | Elm Cortar quote gives **10–12-week imported**, 300-SF combined minimum, 50% deposit; current batch/lead unconfirmed. F&D Riviera has only a nonlocal selected-store price/pickup route, no matching Chicago lot. |
| Unpriced physical and commercial scope | **2** | Separate 48-in LINEAR PAN net/cut area, ceiling attachment and quantity, trim, grout, setting materials, freight, tax, labor and owner allowance remain open. Drawings W1 5.1875 ft/W2 4.7708 ft are not live Revit receipts. |

**Overall COST seat score: 3.0 / 5 = (4 + 4 + 3 + 2 + 2) / 5 = 3.0.**

**top_fix:** Separate the 134.4-SF historic pool into supported wet-wall SF and the held ceiling, then assemble a two-copy landed Clay/Riviera carton budget from verified Chicago quantities.

**gate_flags:** Selected [Elm Cortar Clay FLAT](https://www.elmsurfaces.com/product/cortar-clay) has individual maker **Walls + Wet Areas**; exact Riviera 101487775 has **Bathroom Floor YES + Shower Floor YES + wet DCOF ≥0.42**. **No proved selected-product wet-use, discontinued or owner-veto failure.** Overhead ceiling is **HOLD**, not validated by wall permission; field LINEAR cut/rough and Chicago same-lot supply are OPEN. Owner bath budget **FILL IN**, so original $1,999.60 is **not** a signed budget or basis for an automatic 125% gate.

**confidence: medium** on comparative rate; **low** on actual procure-to-install total.

## Candidate B — Elm Clay walls with bounded Tones Copper substitution / Perimeter Gray LEVEL + LINEAR PAN

| Independently judged COST criterion | Score / 5 | Evidence and reason |
|---|---:|---|
| Historical material-rate value | **4** | At **f = 0** feature SF, the provisional source-rate baseline is **$1,557.26/copy** as above. Each independently measured **gross f SF** replaced Clay by $6.95/SF Copper reduces that baseline by **$1.19 × f**. **f = null** now; no exact B total or full-site saving can be claimed. |
| Rate provenance | **4** | Both **Clay $8.14** and **Copper $6.95** have precise 2026-09-04 1529 trade price; Perimeter Gray **$3.99** is Kirkwood public retail with no project price. |
| Packing and duplicate-count control | **2** | Adding 6.50-SF/carton Copper creates a **third SKU/lot and possible open-carton exposure**. Feature is a same-area **substitution**, not an added wet-wall purchase; f, wall return cuts and ceiling share are unmeasured, preventing a defensible carton calculation. Original 15% already included and WC not added. |
| Chicago continuity / schedule | **2** | Clay carries the Elm **10–12-week/300-SF/50%-deposit** historical terms; Copper present lot unverified. Perimeter Gray lacks Chicago quantity/lead despite **no Kirkwood local discontinued notice**. |
| Unpriced physical and commercial scope | **2** | Copper insert width/location, exact gross f, held shower ceiling, separated LEVEL/PAN SF, trim/setting/freight/labor/tax and owner budget all open. F&D Perimeter nominal 48×24 versus 7.75-SF/tile needs factory face confirmation. |

**Overall COST seat score: 2.8 / 5 = (4 + 4 + 2 + 2 + 2) / 5 = 2.8.**

**top_fix:** Fix a measured gross **f** for one bounded copper panel and show actual Clay-to-Copper carton substitutions for **both** showers, with a separate unapproved ceiling line.

**gate_flags:** [Elm Clay FLAT](https://www.elmsurfaces.com/product/cortar-clay) and individually documented [Tones Copper](https://www.elmsurfaces.com/product/copper-tones) have maker **Wet Areas WALL** listing; selected Perimeter 101239218 has exact **Shower Floor YES + Bathroom Floor YES + wet DCOF ≥0.42**. **No evidenced selected-product hard-gate failure**, and the feature is **not** a niche. Independent overhead ceiling approval remains **HOLD**. The former **Concept Gray 101055101** is **excluded** from B; its store-level clearance/discontinuation warnings must not be transferred to Perimeter Gray. Chicago same-lot supply, native cuts and owner budget are OPEN rather than fabricated gate outcomes; $1,999.60 historical cost is **not** owner-approved 125% cap.

**confidence: medium** for source rates and $1.19/f sensitivity; **low** for unmeasured panel/cartons and delivered pricing.

Evidence: inputs/TRADE_QUOTES.md; own geometry.json and plumbing.json; research/products/elm-cortar-clay-flat-24x48-soft.md, elm-tones-copper-2x20.md, R030_FIVE_SKU_LIVE_STORE_CONTEXT_VERIFICATION_20261107.md; linked exact manufacturer/retailer pages. No emails, requisitions, procurement or outside writes.
