# Round 002 | TX-BATH3 | critic-build

**Seat:** Installer / general contractor; **weight 0.25**. Independent 1–5 criteria; seat scores to one decimal. **Unresolved room identity and plumbing conflict is material:** [geometry.json](../../geometry.json) specifies a **tub alcove** with a provisional 5.10-ft (61.2-in.) back wall, two 2.60-ft (31.2-in.) returns, 7.75-ft tiled height above an assumed tub deck and 37-SF prior room floor. [plumbing.json](../../plumbing.json) explicitly identifies a **walk-in shower with no tub** and a Brizo **BT062415-BNX 4-in. tile-in square point drain**, plus Brizo Black Onyx valves/shower equipment. The model is 1527-named and only provisionally associated with 1529. **Verified shower pan area, pitch, elevation, drain coordinates, waterproofing perimeter and resulting shower wall height are all `null`**; do not extrapolate from the tub footprint or add a pan quantity.

## Candidate A — seat score: **2.4 / 5.0**

| Build criterion | Score | One-line evidence-based reason |
|---|---:|---|
| Wet walls, substrate and manufacturer use | **4 / 5** | [ELM Tones Emerald 2×20](https://www.elmsurfaces.com/product/emerald-tones) and [Sandstone](https://www.elmsurfaces.com/product/sandstone-tones) have Wet Areas evidence ([Emerald audit](../../../../research/products/elm-tones-emerald-2x20.md)), subject to proper waterproof shower/tub backup and actual vertical coverage. |
| Geometry, course cuts and offset/lippage | **1 / 5** | The [61.2-in. W1, 31.2-in. returns, 93-in. assumed tub-height tile datum](../../geometry.json) have **not been reconciled** to the [walk-in shower drain and fittings](../../plumbing.json); three 20-in. lengths on W1 would leave ~1.2 in. total before joints, so centered two-full-piece courses and a new verified shower elevation are needed. |
| Bath floor, pan fall and 12×24 compatibility | **1 / 5** | [Cortar Grey 12×24 Soft](candidates/A.md) has **unknown measured wet DCOF** and is only a level-floor allowance; it has no dimensioned four-plane pitch or smaller-tile shower-pan design to work with the [4-in. square point drain](../../plumbing.json). |
| Niche, terminations and plumbing penetrations | **3 / 5** | The [4.89-SF provisional Sandstone niche](candidates/A.md) must displace Emerald field tile, with sloped sill, waterproofed returns and Brizo valve/glass/curb penetrations still to be dimensioned against [geometry](../../geometry.json). |
| Waste, installation sequencing and schedule | **3 / 5** | [91.8-SF Emerald, 4.89-SF niche and 42.5-SF Cortar Grey gross](candidates/A.md) include 15% allowance but exclude an actual shower-pan tile quantity, water-management assembly and all revised field/pan separation, so labor and orders cannot be released. |

**top_fix:** Resolve the **tub-versus-walk-in-shower identity** by reconciling verified 1529 room geometry with the scheduled Brizo **BT062415-BNX** point drain; only then can the correct pan and wall layout be designed.

**gate_flags:**
- **FAIL — CORTAR_GREY_FLOOR_DCOF:** No published measured wet DCOF ≥0.42 for exact **Cortar Grey 12×24 Soft**, including the level bath floor ([candidate A](candidates/A.md); [board gate 2](../../../../board/BOARD.md)).
- **HOLD — SHOWER_VS_TUB / POINT_DRAIN_GEOMETRY:** [Geometry](../../geometry.json) describes a tub; [plumbing](../../plumbing.json) explicitly declares a walk-in shower with **BT062415-BNX**. An actual shower requires a separately detailed, positively sloped pan; the submitted floor schedule has no demonstrated pan material/layout. Treat the geometry gate as **unverified/conditional**, not an invented measured failure ([board gate 6](../../../../board/BOARD.md)).
- **OPEN — QUANTITIES / SUPPLY:** Shower pan area, finish quantity split, current ELM lot and Chicago ETA are `null`; no room budget was supplied for a numeric 125% evaluation ([candidate A](candidates/A.md)).

**confidence:** **low** — the build detail is dominated by unresolved shower/tub scope and absent live geometry.

## Candidate B — seat score: **2.8 / 5.0**

| Build criterion | Score | One-line evidence-based reason |
|---|---:|---|
| Wet walls, substrate and manufacturer use | **4 / 5** | [Tones Emerald](../../../../research/products/elm-tones-emerald-2x20.md) and [Sandstone](https://www.elmsurfaces.com/product/sandstone-tones) are manufacturer Wet Areas-listed for the wet walls/niche; waterproof system, wall termination and shower controls still need verified setting. |
| Geometry, course cuts and offset/lippage | **2 / 5** | [61.2-in. back and 31.2-in. returns](../../geometry.json) support a rearranged 2×20 straight stack avoiding nominal sub-3-in. edge pieces, but the **93-in. tub-origin height cannot be used as a verified walk-in elevation** ([candidate B](candidates/B.md); [plumbing](../../plumbing.json)). |
| Bath floor, 2×2 mosaic pan and drainage | **3 / 5** | The [PF05 12×24 Matte field](https://www.daltile.com/products/concrete-look/portfolio/ash-grey) is proposed on the **level** floor and the [PF05 2×2 matte straight-joint mosaic](../../../../research/products/daltile-portfolio-ash-grey-pf05-2x2-matte.md) only on a **conditional sloped point-drain pan**, a more workable four-way-slope arrangement; **both exact measured wet DCOF values and the actual pan design are missing**. |
| Niche, termination and plumbing penetration | **3 / 5** | [Sandstone niche 4.89 SF gross](candidates/B.md) needs a sloped sill and waterproof returns, and the Brizo Black Onyx valve, showerhead and 4-in. drain need exact rough coordinates before cuts ([plumbing](../../plumbing.json)). |
| Waste, differential floor build and sequence | **2 / 5** | [12×24 PF05 floor 42.5 SF gross](candidates/B.md) is a level-floor allowance; **2×2 mosaic area, rate, lead and split are `null`**, and its nominal 1/4-in. tile must be brought to a coordinated finished plane against nominal 5/16-in. 12×24 at pan/field transition ([mosaic evidence](../../../../research/products/daltile-portfolio-ash-grey-pf05-2x2-matte.md); [field evidence](../../../../research/products/daltile-portfolio-ash-grey-pf05-12x24-matte.md)). |

**top_fix:** Produce one **verified walk-in shower / 4-in. point-drain section and takeoff** that isolates the measured 2×2 mosaic pan from the level 12×24 field; floor DCOF reports remain a separate hard gate.

**gate_flags:**
- **FAIL — PF05_FIELD_EXACT_DCOF:** [Daltile PF05](https://www.daltile.com/products/concrete-look/portfolio/ash-grey) lists **Wet & Level Interior Floor: suitable** and **“Target DCOF Wet ≥0.42”**; the listed target is **not a measured PF05 12×24 Matte test value**; exact value `null` ([field evidence](../../../../research/products/daltile-portfolio-ash-grey-pf05-12x24-matte.md); [board gate 2](../../../../board/BOARD.md)).
- **FAIL — PF05_MOSAIC_EXACT_DCOF:** The same [PF05 manufacturer page](https://www.daltile.com/products/concrete-look/portfolio/ash-grey) shows **Shower Floors: suitable, Target ≥0.42** and lists **2×2 Straight Joint Matte**, supporting intended application but **not establishing an exact measured DCOF for this mosaic**; pan floor gate fails independently ([mosaic evidence](../../../../research/products/daltile-portfolio-ash-grey-pf05-2x2-matte.md)).
- **HOLD — SHOWER_GEOMETRY:** [Tub-derived area/height](../../geometry.json) conflicts with the [walk-in Brizo drain](../../plumbing.json); pan SF, actual drain location, slope, curb and membrane all `null`. A 2×2 concept mitigates the 12×24 compound-slope problem but does not itself prove a feasible built plan.
- **OPEN — QUOTE / FINISHED ELEVATIONS:** Exact mosaic manufacturer order SKU, project quote and Chicago inventory/ETA are `null`; no pan field deduction or material threshold can be released ([candidate B](candidates/B.md)). No budget violation is quantified.

**confidence:** **low** — confirmed mosaic format intent but the actual tub/shower configuration and pan dimensions are unknown.
