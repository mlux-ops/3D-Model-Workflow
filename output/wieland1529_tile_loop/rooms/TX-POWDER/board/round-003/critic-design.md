# TX-POWDER — blind Round 003 — critic-design

**Seat:** interior design; **weight: 0.25**. Five criteria each scored **1–5**, with one-decimal arithmetic-mean **overall seat score**. This is a **dry vanity-wall feature only**, with existing **wood floor and no tiled shower, tub, or bath floor** ([geometry](../../geometry.json)). The prior assumed W1 width is **2.99 ft = 35.88 in**, wall height **9.25 ft = 111 in**, and room area **22.5 SF**; live 1529 Revit geometry and openings are unverified ([geometry](../../geometry.json), [owner feedback](../../../../state/OWNER_FEEDBACK.md)). The [plumbing](../../plumbing.json) lists a wall-mounted **220-cross-handle faucet model 48140991**, with **manufacturer and finish unconfirmed**, and separate Hansgrohe **two-hole wall-faucet rough-in 32526141**. Do not assume a brass, chrome, gold, black or other finish for the cross-handle trim. Old Town comps **OT01–OT04** describe decorative hall-bath wall treatment as a **program feature**, not a tile color, grout or layout precedent ([comps](../../../../research/comps/COMPS.md)).

## Candidate B — 70% Camel / 30% Wheat, controlled central field

| Design criterion | Score | Evidence-based reason |
|---|---:|---|
| **Plumbing finish and fixture forms** | **4/5** | Flat matte **Haze Camel/Wheat 1.6 × 5** offers a restrained backdrop for a **wall-mounted cross-handle faucet**, but its **model 48140991 finish is not documented**, so neither accent color nor metal edge can be declared an exact finish match ([B packet](candidates/B.md), [plumbing](../../plumbing.json), [Camel evidence](../../../../research/products/elm-haze-camel-1p6x5.md)). |
| **Cross-unit palette cohesion** | **4/5** | Warm Camel/Wheat can relate to shared [Cortar Clay](../../../../research/products/elm-cortar-clay-flat-24x48-soft.md), while [Indigo Edge](../../../../research/products/elm-vera-forma-indigo-edge-6x6.md) offers a contrasting powder accent; this is composition from the shared material vocabulary, not knowledge of any other room's approved candidate ([B packet](candidates/B.md)). |
| **Light, color balance and room scale** | **4/5** | A **70:30** Camel-dominant wall with a bounded lighter Wheat center can brighten a compact **22.5-SF** powder without scattered color; warm-tone perception and possible mirror coverage of the Wheat field require a physical sample and mirror elevation ([B packet](candidates/B.md), [geometry](../../geometry.json), [Wheat evidence](../../../../research/products/elm-haze-wheat-1p6x5.md)). |
| **Grout, stack and cut planning** | **4/5** | A **vertical straight stack, zero offset**, trial **1/8-in warm-greige joint**, and defined 70:30 mix give a reviewable rhythm on a nominal **35.88-in-wide / 111-in-tall wall**; exact manufactured modules, center-panel width and balanced edge cuts remain unmeasured ([B packet](candidates/B.md), [geometry](../../geometry.json)). |
| **Mirror, faucet landing, exposed trim and boundaries** | **3/5** | Wheat is placed where the **rough-in and mirror may obscure it**, so the central panel and cross-handle escutcheons must be registered to actual elevations; selected trim finish, profile, mirror anchorage and dry tile-to-wood/paint terminations are still open ([B packet](candidates/B.md), [plumbing](../../plumbing.json)). |

**overall_score: 3.8/5.0** (19/25).

**top_fix:** Produce a **1:1 vanity elevation** with the actual 48140991 wall-faucet rough centers, mirror edges, basin/counter position and 70:30 Camel/Wheat panel boundary, then lock tonal grout and a compatible exposed-edge trim from physical samples.

**gate_flags:**
- **Wet-wall gate: N/A.** [Haze Camel](https://www.elmsurfaces.com/product/haze-camel) and [Haze Wheat](https://www.elmsurfaces.com/product/haze-wheat) are listed for **Walls**, and B uses them only on a **dry decorative vanity wall**. No Wet Areas assertion is made ([B packet](candidates/B.md), [Camel evidence](../../../../research/products/elm-haze-camel-1p6x5.md), [Wheat evidence](../../../../research/products/elm-haze-wheat-1p6x5.md)).
- **Wet-floor DCOF: N/A.** Floor is **wood**, with no tile wet-floor scope; the numerical **DCOF >=0.42** gate applies to neither color in this room ([geometry](../../geometry.json), [board](../../../../board/BOARD.md)).
- **No sourced HIGH plumbing finish/form clash.** The current **wall-mounted cross-handle model 48140991** and Hansgrohe **32526141** rough are recorded, but the trim's manufacturer and finish are not established. A warm Haze palette is not proof of incompatibility with an unknown metal ([plumbing](../../plumbing.json), [B packet](candidates/B.md)).
- **HOLD — visual/geometry coordination.** Provisional 70:30 split, mirror/rough-in placement, tile module/edge cuts and grout require measured 1529 elevations; a confirmed impossible layout or product discontinuation has not been established ([geometry](../../geometry.json), [B packet](candidates/B.md)).
- **Budget/availability unassessable.** The historical **31.8 SF × $11.93 = $379.37/unit** is a **combined two-color quote** and does not verify the proposed 70:30 color-specific allocation, box mix, current Chicago lot or delivery. No approved room cap exists for the **125%** gate ([B packet](candidates/B.md), [owner feedback](../../../../state/OWNER_FEEDBACK.md)).

**confidence: medium.** Wall application, fixture form and the proposed layout are documented; exact trim finish, color samples, mirror/fixture centers, per-color packing and local lead remain unknown.

## Candidate C — Camel/Wheat stacked wall, mix and alignment unresolved

| Design criterion | Score | Evidence-based reason |
|---|---:|---|
| **Plumbing finish and fixture forms** | **3/5** | Matte **Camel/Wheat 1.6 × 5** is compatible in principle with the wall-mounted **cross-handle form**, but candidate C lacks a composition tied to faucet **48140991** landing, and the actual metal finish remains **unknown** ([C packet](candidates/C.md), [plumbing](../../plumbing.json)). |
| **Cross-unit palette cohesion** | **4/5** | Warm Haze is within the shared [Cortar Clay](../../../../research/products/elm-cortar-clay-flat-24x48-soft.md) and [Wheat/Camel](../../../../research/products/elm-haze-wheat-1p6x5.md) color family, providing a contrast to [Indigo Edge](../../../../research/products/elm-vera-forma-indigo-edge-6x6.md) without any assumed approved other-room design ([C packet](candidates/C.md)). |
| **Light, color balance and room scale** | **4/5** | Small-format matte ceramic can read calm over the **35.88-in × 111-in** feature wall, but the undisclosed Camel/Wheat ratio makes the perceived lightness and placement of the accent impossible to assess precisely ([C packet](candidates/C.md), [geometry](../../geometry.json)). |
| **Grout, stack and cut planning** | **2/5** | Candidate specifies only a **stacked two-color feature**; joint orientation, actual pattern, mixed color counts, grout width/color, end-course alignment and mirror centerline are unspecified despite known provisional wall width ([C packet](candidates/C.md), [geometry](../../geometry.json)). |
| **Mirror, faucet landing, exposed trim and boundaries** | **2/5** | The wall-mounted rough-in, cross-handle escutcheon bearing surfaces, mirror, reveal/trim and termination above **wood floor** all remain **TBD**, preventing a complete dry-wall elevation ([C packet](candidates/C.md), [plumbing](../../plumbing.json), [geometry](../../geometry.json)). |

**overall_score: 3.0/5.0** (15/25).

**top_fix:** Convert the unspecified two-color stack into a centered, measured **Camel/Wheat color distribution and grout/trim elevation** that protects the wall-mounted cross-handle escutcheon and makes the lighter field visible outside the mirror.

**gate_flags:**
- **Dry-wall Wet Areas: N/A; floor DCOF: N/A.** [Camel](../../../../research/products/elm-haze-camel-1p6x5.md) and [Wheat](../../../../research/products/elm-haze-wheat-1p6x5.md) are manufacturer **Walls-only** finishes used only on the **dry** W1 feature. The floor remains **wood, no tile** ([C packet](candidates/C.md), [geometry](../../geometry.json)).
- **No sourced HIGH plumbing finish/form clash.** The fixture is **wall-mounted 48140991**, rough **32526141**, and trim metal finish **null**. Missing landings are design incompleteness, not an evidenced incompatible metal selection ([plumbing](../../plumbing.json)).
- **HOLD — cut and mirror scheme.** The physical color ratio, joint orientation, mirror/faucet coordinate and 1529 wall/door openings have not been measured. No demonstrated unavoidable cut or owner veto is recorded ([C packet](candidates/C.md), [geometry](../../geometry.json), [owner feedback](../../../../state/OWNER_FEEDBACK.md)).
- **No established cost/stock failure.** The original **$379.37/unit** is a blended Haze quote for the existing feature-wall allowance, not an approved current mix purchase; Chicago-specific lot/lead and owner-approved room cap remain unknown. A **125% budget failure cannot be computed** ([C packet](candidates/C.md), [owner feedback](../../../../state/OWNER_FEEDBACK.md)).

**confidence: medium-low.** Dry-wall suitability and two-color material identity are documented, but geometry, exact finish, mirror/escutcheon landing and pattern decisions are still unresolved.
