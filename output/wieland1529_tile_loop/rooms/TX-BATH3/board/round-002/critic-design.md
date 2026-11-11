# TX-BATH3 — Round 002 blind design critique

**Seat:** Interior design, **weight 0.25**. Five criteria scored 1–5; overall score is their arithmetic mean to one decimal. **Unresolved program conflict applies to both candidates:** [geometry](../../geometry.json) assumes a **tub alcove**, 5.10-ft rear wall, 2.60-ft returns and 7.75-ft tile height above a tub rim, while current [plumbing](../../plumbing.json) expressly calls for a **walk-in shower with no tub** and **Brizo Black Onyx 4-in square tile-in drain BT062415-BNX**. The actual pan area, slope, perimeter, waste and cost are all **null**. The 1527-named Revit project is only provisionally permitted for this 1529 scope; room geometry has **not** been confirmed ([owner feedback](../../../../state/OWNER_FEEDBACK.md)). The shared [Old Town comps](../../../../research/comps/COMPS.md) corroborate bath quality/program, not Emerald tile colors or grout patterns.

## Candidate A — Emerald / Sandstone / Cortar Grey

| Criterion | Score | One-line evidence-based assessment |
|---|---:|---|
| **Plumbing finish and forms** | **4/5** | **Emerald 2 × 20 Glossy** creates deliberate saturation against specified **Brizo Brilliance Black Onyx** rain head **81392-BNX-2.5** and valve trim **T755110-BNXLHP**, a visually compatible contrast pending a real sample ([A packet](candidates/A.md), [plumbing](../../plumbing.json)). |
| **Color / unit cohesion** | **4/5** | Emerald plus Grey floor provides a cooler Triplex register among the shared [Copper](../../../../research/products/elm-tones-copper-2x20.md) and [Charcoal](../../../../research/products/elm-cortar-charcoal-24x48-soft.md) product families; the Sandstone niche returns to a warm Tones accent without claiming any other room's final selection ([A packet](candidates/A.md)). |
| **Light / scale** | **3/5** | Deep glossy Emerald above **Cortar Grey Soft 12 × 24** can be visually rich but may read dense in a prior **37-SF** room; no verified light levels or tile samples establish actual contrast ([geometry](../../geometry.json), [A packet](candidates/A.md)). |
| **Layout / grout / cuts** | **3/5** | Straight-stacked **20-in** Emerald courses create an orderly back wall, yet the assumed **61.2-in rear wall / 31.2-in returns**, niche alignment, grout color and the tub-versus-shower tile start height are unresolved ([A packet](candidates/A.md), [geometry](../../geometry.json)). |
| **Niche / drain / transitions** | **2/5** | The **4.89-SF** Sandstone niche is provisional; the **12 × 24 Grey** floor is only identified as the level-floor field, with no selected/verified small-format pan for the specified 4-in point drain if the walk-in shower governs ([A packet](candidates/A.md), [plumbing](../../plumbing.json)). |

**overall_score: 3.2/5.0** (16/25).

**top_fix:** Resolve the tub/walk-in discrepancy and produce a measured wall-and-floor design separating the level Grey floor from an explicitly selected, wet-tested, point-drain-compatible shower pan, with its niche/grout/threshold layout.

**gate_flags:**
- **FAIL — bathroom-floor numerical wet DCOF.** **Cortar Grey 12 × 24 Soft** lacks a product-specific published exact **wet DCOF >=0.42**; measured result = **null**. Floor-use wording is not sufficient for [board gate 2](../../../../board/BOARD.md) ([A packet](candidates/A.md)).
- **HOLD — pan/geometry cannot be approved.** Plumbing documents **walk-in shower / BT062415-BNX** but geometry documents **tub alcove**. **Pan area, thickness, slope, installed format, drain location, cut plan and price = null**, so no floor design can be verified against the selected drain. This is an unresolved program/geometry conflict, not a claimed measured impossible sliver ([plumbing](../../plumbing.json), [geometry](../../geometry.json), [A packet](candidates/A.md)).
- **Wet-wall listing supported.** [Tones Emerald](../../../../research/products/elm-tones-emerald-2x20.md) and [Tones Sandstone](../../../../research/products/elm-tones-sandstone-2x20.md) carry product-specific **Wet Areas** approval for wall/niche use.
- **No HIGH plumbing finish/form clash demonstrated.** Saturated Emerald and Black Onyx are intentional contrasts; the tub-versus-shower conflict concerns the fixture **program**, not incompatible metallic finishes ([plumbing](../../plumbing.json)).
- **Current stock and room-level budget unknown.** No current Chicago lot/lead or approved room budget, and no pan quantity, is established; do not invent a procurement gate ([A packet](candidates/A.md), [owner feedback](../../../../state/OWNER_FEEDBACK.md)).

**confidence: low.** Wall color and Brizo finish are identifiable, but wet-floor design and the governing bath configuration are unresolved.

## Candidate B — Emerald / Sandstone / PF05 Ash Grey with conditional mosaic pan

| Criterion | Score | One-line evidence-based assessment |
|---|---:|---|
| **Plumbing finish and forms** | **5/5** | Glossy Emerald, Ash Grey matte and **Brizo Black Onyx** form a controlled contrast with rain head **81392-BNX-2.5** and Roccesco **T755110-BNXLHP**; Sandstone remains a bounded warm niche accent ([B packet](candidates/B.md), [plumbing](../../plumbing.json)). |
| **Color / unit cohesion** | **4/5** | A cool Ash Grey/green bath is distinct from the documented **Tones Copper** and **Cortar Charcoal** color families while the Sandstone accent links the mineral vocabulary, pending physical sample comparisons ([Copper](../../../../research/products/elm-tones-copper-2x20.md), [Charcoal](../../../../research/products/elm-cortar-charcoal-24x48-soft.md), [B packet](candidates/B.md)). |
| **Light / scale** | **4/5** | A matte neutral **PF05 Ash Grey 12 × 24** provides visual rest beneath vivid Emerald glossy walls; **2 × 2** in the same color could continue the floor into a shower without creating a new dominant accent ([B packet](candidates/B.md), [PF05 field](../../../../research/products/daltile-portfolio-ash-grey-pf05-12x24-matte.md), [PF05 mosaic](../../../../research/products/daltile-portfolio-ash-grey-pf05-2x2-matte.md)). |
| **Layout / grout / cuts** | **4/5** | Zero-offset **12 × 24** field with Daltile's proposed **1/8-in** joints and straight-joint **2 × 2** pan offers a credible grid hierarchy; 20-in Emerald wall courses and all drain, curb and niche cuts still need verified elevations ([B packet](candidates/B.md), [geometry](../../geometry.json)). |
| **Niche / drain / transitions** | **3/5** | The same-color field/mosaic boundary and Sandstone niche are coherent in concept, but exact pan-to-floor break, 4-in drain border, threshold, negative space and niche corners are undefined because **pan dimensions are null** ([B packet](candidates/B.md), [plumbing](../../plumbing.json), [PF05 mosaic](../../../../research/products/daltile-portfolio-ash-grey-pf05-2x2-matte.md)). |

**overall_score: 4.0/5.0** (20/25).

**top_fix:** Establish the actual walk-in shower perimeter and issue one dimensioned wall-and-pan elevation/plan aligning the **PF05 2 × 2** grid to **Brizo BT062415-BNX**, coordinating sloped pan, 12 × 24 field break, grout, curb and Sandstone niche.

**gate_flags:**
- **FAIL — exact main-floor DCOF.** Daltile's [Portfolio PF05 Ash Grey page](https://www.daltile.com/products/concrete-look/portfolio/ash-grey) marks **Wet & Level Interior Floors suitable** and prints **Target DCOF Wet >=0.42**. This is a **published intended-use target**, **not a measured value for the PF05 12 × 24 Matte SKU**. Exact measured DCOF = **null**; strict [board gate 2](../../../../board/BOARD.md) fails ([PF05 field evidence](../../../../research/products/daltile-portfolio-ash-grey-pf05-12x24-matte.md)).
- **FAIL — exact conditional pan DCOF.** The same Daltile PF05 page lists a **2 × 2 Matte mosaic** and **Shower Floors suitable, Target DCOF Wet >=0.42**. That application designation **does not provide an exact measured PF05 2 × 2 Matte wet DCOF**; result = **null**, so the numerical shower-pan floor gate fails until product/finish-specific test evidence ([PF05 mosaic evidence](../../../../research/products/daltile-portfolio-ash-grey-pf05-2x2-matte.md)).
- **HOLD — scope, pan geometry and cost null.** The current tub geometry conflicts with explicitly selected **walk-in shower/4-in point drain**. Pan SF, drain coordinates, slope, field-vs-pan split, pan quote and date-specific Chicago inventory remain **null**. A measured fatal cut cannot be asserted, and total material/budget gate cannot be calculated ([geometry](../../geometry.json), [plumbing](../../plumbing.json), [B packet](candidates/B.md)).
- **Wet-wall application supported.** [Emerald](../../../../research/products/elm-tones-emerald-2x20.md) and [Sandstone](../../../../research/products/elm-tones-sandstone-2x20.md) manufacturer evidence includes **Wet Areas** for the scheduled wall/niche uses.
- **No HIGH plumbing finish/form clash demonstrated.** Green/grey/Black Onyx is an intentional contrast; outstanding fixture issue is program/layout verification rather than competing fixture metals ([plumbing](../../plumbing.json)).

**confidence: medium-low.** More specific field/pan design logic is supplied, but correct shower geometry, two product-specific DCOF results, visual samples, pan price and actual niche/trim are unknown.
