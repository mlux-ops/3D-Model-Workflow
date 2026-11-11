# Round 002 | TX-BATH4 | critic-build

**Seat:** Installer / general contractor; **weight 0.25**. Independent 1–5 criterion scores; one-decimal seat score. [Geometry](../../geometry.json) is **provisional drawing-derived** for a **tub alcove**: 5.00-ft (60.0-in.) rear wall, two 2.54-ft (30.48-in.) returns, 10.08-LF run, 7.75-ft (93-in.) tiled height above assumed tub deck, 38.5-SF bath floor. The 1527-named Revit model is provisionally readable but has not confirmed this room. [Plumbing](../../plumbing.json) records a **Duravit 59-in. built-in tub**, Hansgrohe **Matte White** shower/tub fittings and a conventional tub waste/overflow, with no separately specified point-drain shower pan. Shower-floor slope is **not applicable on the currently specified tub scope**; bath-floor measured wet DCOF remains mandatory.

## Candidate A — seat score: **3.2 / 5.0**

| Build criterion | Score | One-line evidence-based reason |
|---|---:|---|
| Tub wet-wall rating, substrate and flatness | **4 / 5** | [Cortar Charcoal Flat 24×48 Soft](https://www.elmsurfaces.com/product/cortar-charcoal) carries **Wet Areas** in the [product-specific project evidence](../../../../research/products/elm-cortar-charcoal-24x48-soft.md), but its large-format substrate flatness, tub flange and moisture system require measurement and waterproof detailing. |
| Large-format cuts, offset and lippage | **3 / 5** | The provisional [60-in. rear / 30.48-in. returns / 93-in. height](../../geometry.json) can use **vertically aligned 24×48 panels at zero offset** (or <=one-third of the 48-in. long dimension if staggered); one centered 24-in. return panel nominally leaves ~3.24-in. sides **before joints**, so check actual sub-3-in. cuts rather than presuming a pass. |
| Bath floor 12×24 suitability and performance | **2 / 5** | [Cortar Bone 12×24 Soft](https://www.elmsurfaces.com/product/cortar-bone) is wet-area-listed in the [product evidence](../../../../research/products/elm-cortar-bone-soft-12x24.md) but its **exact measured wet DCOF ≥0.42 is `null`**; zero-offset level-floor setting is practicable but does not satisfy the safety gate. |
| Niche, roughs, trims and tub waterproofing | **4 / 5** | [Soho Black 2×10 Glossy](https://www.elmsurfaces.com/product/soho-black) expressly lists **Wet Areas** and is simpler to wrap at a niche than an unapproved relief material, with sill fall to tub, wall/niche thickness transition (Soho ~9.5 mm), Hansgrohe Matte White escutcheon landing and trim still unmeasured ([candidate A](candidates/A.md)). |
| Waste, material handoff and schedule | **3 / 5** | [89.8-SF Charcoal wall, 44.3-SF Bone floor and provisional 8.63-SF niche allowance](candidates/A.md) need field-to-niche subtraction and box rounding; flat Charcoal's historical 10–12-week overseas lead/import minimum and **Soho price/Chicago ETA `null`** prevent installation release ([Charcoal evidence](../../../../research/products/elm-cortar-charcoal-24x48-soft.md); [Soho evidence](../../../../research/products/elm-soho-black-2x10.md)). |

**top_fix:** Obtain a **manufacturer-published measured wet DCOF report for exact Cortar Bone 12×24 Soft**, or change the bathroom floor to a tested >=0.42 wet-rated tile; preserve the wet-approved flat Charcoal/Soho tub wall scheme.

**gate_flags:**
- **FAIL — BONE_SOFT_FLOOR_DCOF:** [ELM Bone product](https://www.elmsurfaces.com/product/cortar-bone) has wet-area application but **no published exact measured wet DCOF ≥0.42 for 12×24 Soft** in the reviewed evidence; board floor gate fails ([product audit](../../../../research/products/elm-cortar-bone-soft-12x24.md); [board](../../../../board/BOARD.md)).
- **OPEN — CONDITIONAL_RIBBED_NOT_RELEASED:** Candidate A explicitly confines [Bone Ribbed](../../../../research/products/elm-cortar-bone-ribbed-24x48-relief.md) to a *future, separately measured dry-area possibility*, **not its wet tub surround**. Do not treat hypothetical dry-only Ribbed as a present wet-wall failure; **if moved to tub wet walls**, lack of Wet Areas listing **fails** independently ([candidate A](candidates/A.md)).
- **HOLD — CUTS / FINISHED ASSEMBLIES:** Live Revit identity, niche dimensions, exact 24×48 edge cuts, physical tile sample and tub flange/rough depth are unverified; no **impossibility** established from the nominal dimensions alone ([geometry](../../geometry.json); [plumbing](../../plumbing.json)).
- **OPEN — PRICING / AVAILABILITY:** Soho quote, current Charcoal lot and ETA are `null`; room budget cap unspecified. Do not mark discontinued or >125%-budget hard-fail without evidence ([candidate A](candidates/A.md); [owner feedback](../../../../state/OWNER_FEEDBACK.md)).

**confidence:** **medium** — wet-wall approvals are supported; floor testing and actual large-format cut plan remain unresolved.

## Candidate B — seat score: **1.8 / 5.0**

| Build criterion | Score | One-line evidence-based reason |
|---|---:|---|
| Tub wet-wall rating, substrate and flatness | **2 / 5** | Flat [Cortar Charcoal 24×48](../../../../research/products/elm-cortar-charcoal-24x48-soft.md) is Wet Areas-listed, but [Bone Ribbed 24×48 relief](../../../../research/products/elm-cortar-bone-ribbed-24x48-relief.md) is included in the wet-wall field allocation without a verified dry location and **has no Wet Areas listing**, prohibiting its release in this alcove ([candidate B](candidates/B.md)). |
| Large-format cuts, relief alignment and lippage | **2 / 5** | The [60-in. rear, 30.48-in. returns and 93-in. assumed height](../../geometry.json) lack real valve/niche locations and a measured split for Ribbed relief; a zero-offset/<=one-third-long-edge 24×48 course and flat/relief transition cannot be dimensioned as submitted ([candidate B](candidates/B.md)). |
| Bath floor 12×24 suitability and performance | **2 / 5** | [Cortar Bone 12×24 Soft](candidates/B.md) is on the nominal level bath floor without manufacturer-published **exact measured wet DCOF ≥0.42**, so slip approval fails irrespective of other wall finishes ([product evidence](../../../../research/products/elm-cortar-bone-soft-12x24.md)). |
| Niche, edge termination and plumbing coordination | **1 / 5** | [Clara Tierra Madre Caviar 2×8 zellige](candidates/B.md) is proposed for the **wet tub niche** but lacks manufacturer **Wet Areas** documentation; sloped sill, 24×48 field-to-niche transitions, matte-white valve landings and trims are also unverified ([plumbing](../../plumbing.json)). |
| Waste, scope split and lead sequence | **2 / 5** | The [89.8-SF Charcoal wall basis](candidates/B.md) includes an **unknown Bone Ribbed area**, plus the 8.63-SF niche and 44.3-SF floor allowances; missing field deductions, relief order split and historical long-lead terms prevent accurate release quantities ([Ribbed evidence](../../../../research/products/elm-cortar-bone-ribbed-24x48-relief.md)). |

**top_fix:** Replace the **unapproved wet-zone niche/relief package** with a completely manufacturer **Wet Areas-listed wall and niche assembly**; floor DCOF remains a separate hard gate.

**gate_flags:**
- **FAIL — CLARA_WET_NICHE:** Candidate B's Clara Caviar shower/tub niche has **no manufacturer Wet Areas listing**, and project quote/application category alone cannot pass [gate 1](../../../../board/BOARD.md) ([candidate B](candidates/B.md)).
- **FAIL — BONE_RIBBED_WET_WALL:** [Bone Ribbed product-specific source](../../../../research/products/elm-cortar-bone-ribbed-24x48-relief.md) lists only **Walls / Back Splashes**, while candidate B allocates the relief within an unlocated tub wall field; without a verified dry alternative or written wet approval, wet-wall release fails ([candidate B](candidates/B.md)).
- **FAIL — BONE_SOFT_FLOOR_DCOF:** No published exact **Cortar Bone 12×24 Soft wet DCOF ≥0.42**, notwithstanding Wet Areas floor application ([evidence](../../../../research/products/elm-cortar-bone-soft-12x24.md)).
- **HOLD — GEOMETRY / TAKEOFF:** Ribbed field split, niche opening, valve rough details, tub waterproofing and wall cuts from verified model all `null`; proposed 24×48 field cannot be assessed for focal slivers or accurate quantities ([geometry](../../geometry.json); [plumbing](../../plumbing.json)).
- **OPEN — LOCAL PROCUREMENT:** No independently verified current Chicago stock/lead or new order quote; missing budget cap prevents a numerical budget hard-gate determination ([candidate B](candidates/B.md)).

**confidence:** **medium** — wet-wall exclusions and floor DCOF failure documented; measured cutting and quantities still pending.
